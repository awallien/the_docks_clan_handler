import textdistance as td
import re

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from discord import app_commands, Thread, EntityType, PrivacyLevel, EventStatus

from discord_bot import err_embed, info_embed
from util import RESPONSE_ERR, err_print, debug_print


OPTIONS = ["add", "update", "delete", "notify"]


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
    "notify": ["Notifying event...", "Notify event completed"],
}


EVENTS_SET = set()

def validate_date_times(option, start_time, end_time, tzone):
    format_str = "%m-%d-%Y %I:%M %p"
    if option == "add":
        if start_time is None:
            return RESPONSE_ERR("`start_datetime` is mandatory when creating a new event.")
        if tzone is None or tzone not in TZ_OPTIONS:
            return RESPONSE_ERR("A valid `timezone` is mandatory when creating a new event.")

        tz = ZoneInfo(TZ_OPTIONS[tzone])
        parse_str = "start_datetime"
        try:
            start_time = datetime.strptime(start_time, format_str).replace(tzinfo=tz)
            if end_time is not None:
                parse_str = "end_datetime"
                end_time = datetime.strptime(end_time, format_str).replace(tzinfo=tz)
        except ValueError:
            return RESPONSE_ERR(f"`{parse_str}` is NOT in a valid format. Expecting [MM-DD-YYYY HH:MM AM/PM]")
        
        dt_now = datetime.now(tz=tz)

        if start_time <= dt_now:
            return RESPONSE_ERR("`start_datetime` cannot occur in the past.")
        if end_time:
            if end_time <= dt_now:
                return RESPONSE_ERR("`end_datetime` cannot occur in the past.")
            if end_time <= start_time:
                return RESPONSE_ERR("`end_datetime` cannot be the same as or occur before `start_datetime`.")
    
    elif option == "update":
        if (start_time or end_time) and (not tzone or tzone not in TZ_OPTIONS):
            return RESPONSE_ERR("Please provide a valid `timezone` when updating `start_datetime` or `end_datetime`.")
        
        tz = ZoneInfo(TZ_OPTIONS[tzone])        
        parse_str = "start_datetime"
        try:
            if start_time:
                start_time = datetime.strptime(start_time, format_str).replace(tzinfo=tz)
            parse_str = "end_datetime"
            if end_time:
                end_time = datetime.strptime(end_time, format_str).replace(tzinfo=tz)
        except ValueError:
            return RESPONSE_ERR(f"`{parse_str}` is NOT valid or in a valid format. Expecting [MM-DD-YYYY HH:MM AM/PM]")
    else: # delete, notify
        if any([start_time, end_time, tzone]):
            return RESPONSE_ERR(f"No need to set any time parameters when deleting/notifying an event")

    return (start_time, end_time)


async def event_cb(BOT, ctx, option, start_time, end_time, tzone):
    if option not in OPTIONS:
        await ctx.send(embed=err_embed(f"{option} is not a valid option!"), ephemeral=True)
        return
    
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

            valid_times = validate_date_times(option, start_time, end_time, tzone)
            if not valid_times:
                await reply_msg.edit(embed=err_embed(msg=valid_times.err))
                raise Exception(valid_times.err)

            start_time,end_time = valid_times

            if option == "add":
                scheduled_events = await BOT.guild.fetch_scheduled_events()
                res = await add_event(BOT, ctx, forum_thread, scheduled_events, start_time, end_time)
            elif option == "update":
                res = await update_event(BOT, ctx, forum_thread, start_time, end_time)
            elif option == "delete":
                res = await delete_event(BOT, ctx, forum_thread)
            else:
                res = await notify_event(BOT, forum_thread) # notify
            
            if not res:
                err = err_embed(f"{res.err}", "Something went wrong")
                await reply_msg.edit(embeds=[err])
            else:
                success = info_embed(f"{OPTIONS_TO_MSG[option][1]}\nEvent ID: {res}\nDO NOT DELETE THIS MESSAGE!", f"Success!")
                await reply_msg.edit(embeds=[success])
        
        except Exception as e:
            err_print(f"Error caught in {option}: {str(e)}")
        
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
        return RESPONSE_ERR(f"Hmmm... it appears there's already an event created for this thread forum, Event ID: {event.id}")
    
    event = check_event_exists(thr_name, thr_content, scheduled_events)
    if event:
        return RESPONSE_ERR(f"Hmmm... it appears there's a similar event already existing,\nEvent: {event}. \n"
                             "If they are not the same, please reword your event thread.")

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
            f"{BOT.allowed_role.mention} {ctx.author.mention} created an event, check it out!\n"
            f"Event URL: {new_event.url}\n{thr_discussion}"
        )
    else:
        return RESPONSE_ERR(f"Hmmm... I'm not able to create this event. {BOT.mod.mention}, help!")

    return new_event.id


async def delete_event(BOT, _, forum_thread):
    """
    When user requests to delete event:
     1.   fetch the event that was created within the forum thread and delete it
    """
    event = await find_thread_scheduled_event(BOT, forum_thread)
    if not event:
        return RESPONSE_ERR("Hmmm... I can't find a valid event ID in this forum thread. Did you delete it by accident?")

    event_id = event.id
    
    try:
        await event.delete()
    except:
        return RESPONSE_ERR(f"Hmmm... I wasn't able to delete this event. {BOT.mention}, help!")
    
    return event_id


async def update_event(BOT, _, forum_thread, start_time, end_time):
    """
    When user requests to update event:
     1. get updated start and end time, if any
     2. get thread name, content, image, and start and end times
     3. Update the event
    """
    event = await find_thread_scheduled_event(BOT, forum_thread)
    if not event:
        return RESPONSE_ERR("Hmmm... I can't find a valid event ID in this forum thread. Did you delete it by accident?")

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

    try:
        edit_event = await event.edit(
            name=thr_name,
            description=thr_content + f"\n\n{thr_discussion}",
            start_time=start_time if start_time else ev_start_time,
            end_time=end_time if end_time else ev_end_time,
            image=thr_image
        )
    except Exception as e:
        return RESPONSE_ERR(str(e))

    if not edit_event.status == EventStatus.scheduled:
        return RESPONSE_ERR(f"Hmmm... I'm not able to update this event. {BOT.mod.mention}, help!")

    return event.id

async def notify_event(BOT, forum_thread):
    event = await find_thread_scheduled_event(BOT, forum_thread)
    if not event:
        return RESPONSE_ERR("Hmmm... I can't find a valid event ID in this forum thread. Did you delete it by accident?")
    
    event_name = event.name
    ev_datetime_diff = event.start_time.replace(tzinfo=None) - datetime.now()
    print(ev_datetime_diff, ":::", ev_datetime_diff.total_seconds())
    event_starts_in = ""

    if ev_datetime_diff > timedelta(weeks=1):
        return RESPONSE_ERR("Sorry, I can only begin notifying an event a week before the event starts.")
    
    if ev_datetime_diff.total_seconds() <= 0:
        event_starts_in = f"has just started!"
    else:
        days = ev_datetime_diff.days
        seconds = ev_datetime_diff.seconds
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds %= 60
        event_starts_in = f"is starting in {days} days, {hours} hours, {minutes} minutes, and {seconds} seconds!"
        
    await BOT.general_channel.send(
        f"Just a reminder {BOT.allowed_role.mention}, Event '{event_name}' {event_starts_in}\n"
        f"More info about this event is found here: {forum_thread.mention}\n"
        f"{event.url}"
    )
    
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
    async for message in forum_thread.history(limit=None, oldest_first=False):
        if message.author.name == BOT.user.display_name:
            if len(message.embeds) == 1:
                desc = message.embeds[0].description
                match = re.search(r"Event ID:\s*(\d+)", desc)
                if match:
                    event_id = int(match.group(1))
                    try:
                        event = await BOT.guild.fetch_scheduled_event(event_id, with_counts=False)
                        return event
                    except:
                        debug_print(f"No event found with {event_id}, keep searching")

    return None
