import textdistance as td
import re

from datetime import datetime
from zoneinfo import ZoneInfo
from discord import app_commands, Thread, EntityType, PrivacyLevel, EventStatus
from discord_bot import err_embed, info_embed
from util import RESPONSE_ERR, RESPONSE_OK, err_print

OPTIONS = ["add", "update", "delete"]

TZ_OPTIONS = {
    "PST/USA":  "America/Los_Angeles",
    "MST/USA":  "America/Denver",
    "CST/USA":  "America/Chicago",
    "EST/USA":  "America/New_York",
    "GMT/UK":   "Europe/London",
    "CET/NL":   "Europe/Brussels"
}

OPTIONS_TO_MSG = {
    "add": ["Adding event...", "Add event completed"],
    "update": ["Updating event...", "Update event completed"],
    "delete": ["Deleting event...", "Delete event completed"],
}

EVENTS_SET = set()

def validate_date_times(option, start_time, end_time, tzone):
    format_str = "%m-%d-%Y %I:%M %p"
    if option == "add":
        if start_time is None:
            return RESPONSE_ERR("`start_time` is mandatory when creating a new event.")
        if tzone is None or tzone not in TZ_OPTIONS:
            return RESPONSE_ERR("A valid `timezone` is mandatory when creating a new event")

        tz = ZoneInfo(TZ_OPTIONS[tzone])
        parse_str = "start_time"
        try:
            start_time = datetime.strptime(start_time, format_str).replace(tzinfo=tz)
            if end_time is not None:
                parse_str = "end_time"
                end_time = datetime.strptime(end_time, format_str).replace(tzinfo=tz)
        except ValueError:
            return RESPONSE_ERR(f"`{parse_str}` is NOT in a valid format. Expecting [MM-DD-YYYY HH:MM AM/PM]")
        
        if start_time <= datetime.now(tz=tz):
            return RESPONSE_ERR("`start_time` cannot occur in the past.")
        if end_time:
            if end_time <= datetime.now(tz=tz):
                return RESPONSE_ERR("`end_time` cannot occur in the past.")
            if end_time <= start_time:
                return RESPONSE_ERR("`end_time` cannot occur or be the same as `start_time`.")
    
    elif option == "update":
        if (start_time or end_time) and not tzone:
            return RESPONSE_ERR("Please provide `timezone` when updating `start_time` or `end_time`.")
        
        if tzone:
            tz = ZoneInfo(TZ_OPTIONS[tzone])
        
        parse_str = "start_time"
        try:
            if start_time:
                start_time = datetime.strptime(start_time, format_str).replace(tzinfo=tz)
            parse_str = "end_time"
            if end_time:
                end_time = datetime.strptime(end_time, format_str).replace(tzinfo=tz)
        except ValueError:
            return RESPONSE_ERR(f"`{parse_str}` is NOT in a valid format. Expecting [MM-DD-YYYY HH:MM AM/PM]")
    
    return (start_time, end_time)

async def event_cb(BOT, ctx, option, start_time, end_time, tzone):
    if option not in OPTIONS:
        await ctx.send(embed=err_embed(f"{option} is not a valid option!"), ephemeral=True)
        return
    
    valid_times = validate_date_times(option, start_time, end_time, tzone)
    if not valid_times:
        await ctx.send(embed=err_embed(msg=valid_times.err))
        return

    start_time,end_time = valid_times
    forum_thread = ctx.channel
    
    if not type(forum_thread) == Thread or \
       not forum_thread.parent == BOT.forum_channel or \
       not next((tag for tag in forum_thread.applied_tags if tag.name == "Event"), None):
        msg = f"This command only works on an event forum thread under '{BOT.forum_channel}'.\n" \
              f"If you are creating an event, please create a forum thread tagged as an 'Event' under '{BOT.forum_channel}', and " \
              f"execute this command under that thread."
        await ctx.send(embed=err_embed(msg=msg), ephemeral=True)
    else:
        """
        The API to fetch the guild's event takes forever, so send a message in the meantime and update it later
        """
        if forum_thread.id in EVENTS_SET:
            await ctx.send(embed=err_embed(msg="A previous executed event command is in progress. Please wait until it is done before executing a new event command.", 
                                           title="Woah there!"))
            return

        EVENTS_SET.add(forum_thread.id)

        try:
            reply_msg = await ctx.send(embed=info_embed("Please wait for this message to be updated", f"_{OPTIONS_TO_MSG[option][0]}_"))
            
            if option == "add":
                scheduled_events = await BOT.guild.fetch_scheduled_events()
                res = await add_event(BOT, ctx, forum_thread, scheduled_events, start_time, end_time)
            elif option == "update":
                res = await update_event(BOT, ctx, forum_thread, start_time, end_time)
            # else:
            #     await delete_event(BOT, ctx)
            if not res:
                err = err_embed(f"{res.err}", "Something went wrong")
                await reply_msg.edit(embeds=[err])
            else:
                success = info_embed(f"{OPTIONS_TO_MSG[option][1]}\nEvent ID: {res}\nDO NOT DELETE THIS MESSAGE!", f"Success!")
                await reply_msg.edit(embeds=[success])
        except Exception as e:
            err_print(str(e))
        
        if forum_thread.id in EVENTS_SET:
            EVENTS_SET.remove(forum_thread.id)

async def option_event_autocompletion(_, current):
    return [
        app_commands.Choice(name=option, value=option)
        for option in OPTIONS if current.lower() in option.lower()
    ]

async def timezone_event_autocompletion(_, current):
    return [
        app_commands.Choice(name=option, value=option)
        for option in TZ_OPTIONS.keys() if current.lower() in option.lower()
    ]

async def add_event(BOT, ctx, forum_thread, scheduled_events, start_time, end_time):
    """
    When user requests to add an event:
     1. check if the event is already created using a similiarity score, or check if ID already created within the forum
     2. if no event exists: create event based on user's input and notify general space of new event
        else: notify user that a similar event already exists
    """
    thr_name = forum_thread.name
    thr_message = await forum_thread.fetch_message(forum_thread.id)
    thr_content = thr_message.content

    sch_event = await find_thread_scheduled_event(BOT, forum_thread)
    if sch_event:
        return RESPONSE_ERR(f"Hmmm... it appears there's already an event created for this thread forum, Event ID: {event_id}")
    
    event = check_event_exists(thr_name, thr_content, scheduled_events)
    if event:
        return RESPONSE_ERR(f"Hmmm... it appears there's a similar event already existing,\nEvent: {event}. \n"
                             "If they are not the same, please reword your thread.")

    thr_discussion = f"Thread Discussion: {forum_thread.mention}"
    thr_image = None
    if thr_message.attachments:
        thr_att = thr_message.attachments[0]
        thr_image = await thr_att.read()

    new_event = await BOT.guild.create_scheduled_event(
        name=thr_name,
        description=thr_content + f"\n\n{thr_discussion}",
        channel=BOT.voice_channel,
        entity_type=EntityType.voice,
        privacy_level=PrivacyLevel.guild_only,
        start_time=start_time,
        end_time=end_time
    )

    if thr_image:
        await new_event.edit(image=thr_image)

    if new_event.status == EventStatus.scheduled:
        await BOT.general_channel.send(
            f"{BOT.members_role.mention} {ctx.author.mention} created an event, check it out!\n"
            f"Event URL: {new_event.url}\n{thr_discussion}"
        )
    else:
        return RESPONSE_ERR("Hmmm... I'm not able to create this event. Please reach out to Goose.")

    return new_event.id


async def delete_event(BOT, ctx):
    """
    When user requests to delete event:
     1.   fetch the event that was created within the forum thread and delete it
    """

async def update_event(BOT, _, forum_thread, start_time, end_time):
    """
    When user requests to update event:
     1. get updated start and end time, if any
     2. get thread name, content, image, and start and end times
     3. Update the event
    """
    event = await find_thread_scheduled_event(BOT, forum_thread)
    if not event:
        return RESPONSE_ERR("Hmmm... it looks like I can't find the event id in this forum thread. Did you delete it by accident?")

    thr_discussion = f"Thread Discussion: {forum_thread.mention}"
    thr_name = forum_thread.name
    thr_message = await forum_thread.fetch_message(forum_thread.id)
    thr_content = thr_message.content
    
    thr_image = None
    if thr_message.attachments:
        thr_att = thr_message.attachments[0]
        thr_image = await thr_att.read()

    ev_start_time = event.start_time
    ev_end_time = event.end_time

    edit_event = await event.edit(
        name=thr_name,
        description=thr_content + f"\n\n{thr_discussion}",
        start_time=start_time if start_time else ev_start_time,
        end_time=end_time if end_time else ev_end_time,
        image=thr_image
    )

    if not edit_event.status == EventStatus.scheduled:
        return RESPONSE_ERR("Hmmm... I'm not able to update this event. Please reach out to Goose.")

    return event.id


def check_event_exists(thr_name, thr_content, scheduled_events):
    """
    uses cosine similarity to evaluate if forum thread and any scheduled events are similar
    """
    thr_name_lst = thr_name.split()
    thr_content_lst = thr_content.split()
    for event in scheduled_events:
        ev_name = event.name.split()
        ev_desc = event.description.split()
        # TODO: may need to re-evaluate these values
        if td.cosine(thr_name_lst, ev_name) > 0.25 or td.cosine(thr_content_lst, ev_desc) > 0.5:
            return event.name
    return None

async def find_thread_scheduled_event(BOT, forum_thread):
    async for message in forum_thread.history(limit=None):
        if message.author.name == BOT.user.display_name:
            if len(message.embeds) == 1:
                desc = message.embeds[0].description
                match = re.search(r"Event ID:\s*(\d+)", desc)
                if match:
                    event_id = int(match.group(1))
                    try:
                        event = await BOT.guild.fetch_scheduled_event(event_id, with_counts=False)
                        return event
                    except Exception as e:
                        err_print(e)

    return None
