import json
import math
import requests
from http import HTTPStatus

GE_API_GRPH_URL_FMT = " https://services.runescape.com/m=itemdb_oldschool/api/graph/%d.json"
GE_API_CAT_URL = "https://secure.runescape.com/m=itemdb_oldschool/api/catalogue/category.json?category=1"
GE_API_PAGE_URL = "https://secure.runescape.com/m=itemdb_oldschool/api/catalogue/items.json?category=1&alpha=%c&page=%d"
NUM_ITEMS_PER_PAGE = 12

"""
Ex:
{
    "icon":"https://secure.runescape.com/m=itemdb_oldschool/1728901201859_obj_sprite.gif?id=10344",
    "icon_large":"https://secure.runescape.com/m=itemdb_oldschool/1728901201859_obj_big.gif?id=10344",
    "id":10344,
    "type":"Default",
    "typeIcon":"https://www.runescape.com/img/categories/Default",
    "name":"3rd age amulet",
    "description":"Fabulously ancient mage protection enchanted in the 3rd Age.",
    "current":{"trend":"neutral","price":"176.8m"},
    "today":{"trend":"neutral","price":0},
    "members":"true"
}
"""
class Item:
    def __init__(self):
        self._name = ""
        self._id = 0
        self._description = ""
        self._members = False
        self._current_trend = ""
        self._current_price = ""
        self._today_trend = ""
        self._today_price = ""
        self._type = ""
        self._type_icon = ""
        self._icon = ""
        self._icon_large = ""

    @property
    def name(self):
        return self._name
    
    @property
    def id(self):
        return self._id

    @property
    def description(self):
        return self._description
    
    @property
    def members(self):
        return self._members
    
    @property
    def current_trend(self):
        return self._current_trend
    
    @property
    def current_price(self):
        return self._current_price
    
    @property
    def today_trend(self):
        return self._today_trend
    
    @property
    def today_price(self):
        return self._today_price
    
    @property
    def type(self):
        return self._type
    
    @property
    def type_icon(self):
        return self._type_icon
    
    @property
    def icon(self):
        return self._icon
    
    @property
    def icon_large(self):
        return self._icon_large
    
    def dict_to_item(d):
        item = Item()
        item._name = d["name"]
        item._id = d["id"]
        item._description = d["description"]
        item._members = d["members"]
        item._icon = d["icon"]
        item._icon_large = d["icon_large"]
        item._type = d["type"]
        item._type_icon = d["typeIcon"]
        item._current_trend = d["current"]["trend"]
        item._current_price = d["current"]["price"]
        item._today_trend = d["today"]["trend"]
        item._today_price = d["today"]["price"]
        return item

    def __str__(self):
        return f"""Item(id:{self.id} name:{self.name}, desc:\"{self.description}\", current price:{self.current_price})"""

class ItemsTradeHistory:
    def __init__(self, items: list, days=180):
        self._items = items
        self._days = days
        self._history = self.__get_json_payload()

    @property
    def items(self):
        return self._items
    
    @property
    def days(self):
        return self._days
    
    @property
    def history(self):
        return self._history

    def __get_json_payload(self):
        payload = {}
        for item in self._items:
            response = requests.get(GE_API_GRPH_URL_FMT % item.id)
            if response.status_code == HTTPStatus.OK:
                payload[item.id] = response.content.decode()
            else:
                print(f"Error: Unable to get graph history for {item.name}, skipping graph trend")
        return payload

class GrandExchange:

    def __init__(self):
        self.request_get_counter = 0
        self.first_chr_to_num_items = self.__get_first_chr_to_num_items()

    def __get_json_payload(self, url):
        response = requests.get(url)
        self.request_get_counter += 1
        # print(f"Call {self.request_get_counter}: {url}")
        if response.status_code == HTTPStatus.OK:
            return json.loads(response.content.decode())
        else:
            raise Exception(f"Unable to fetch payload for {url}")

    def __get_first_chr_to_num_items(self):
        payload = self.__get_json_payload(GE_API_CAT_URL)
        return {entry["letter"]: entry["items"] for entry in payload["alpha"]}

    def lookup_item(self, item_name):
        item_name = item_name.strip()
        first_chr = item_name[0]
        if not first_chr.isalnum():
            return None
        
        first_chr_key = '#' if first_chr.isnumeric() else first_chr.lower()
        total_items = self.first_chr_to_num_items[first_chr_key]
        num_pages = math.ceil(total_items / NUM_ITEMS_PER_PAGE)
        left_page_idx = 0
        right_page_idx = num_pages - 1
        item_found = None
        # page search
        while left_page_idx <= right_page_idx:
            # print(f"left page idx: {left_page_idx}, right page idx: {right_page_idx}")
            mid_page_idx = (left_page_idx + right_page_idx) // 2
            items_payload = self.__get_json_payload(GE_API_PAGE_URL % (first_chr_key, mid_page_idx+1))["items"]

            if not len(items_payload):
                break
            
            # internal items per page search
            left_item_idx = 0
            right_item_idx = len(items_payload) - 1

            if item_name >= items_payload[left_item_idx]["name"] and item_name <= items_payload[right_item_idx]["name"]:
                while left_item_idx <= right_item_idx:
                    # print(f"    left item idx: {left_item_idx}, right item idx: {right_item_idx}")
                    mid_item_idx = (left_item_idx + right_item_idx) // 2
                    if items_payload[mid_item_idx]["name"] == item_name:
                        item_found = items_payload[mid_item_idx]
                        break
                    elif item_name > items_payload[mid_item_idx]["name"]:
                        left_item_idx = mid_item_idx + 1
                    else:
                        right_item_idx = mid_item_idx - 1

            if item_found:
                break
            elif item_name > items_payload[-1]["name"]:
                left_page_idx = mid_page_idx + 1
            else:
                right_page_idx = mid_page_idx - 1

        if item_found is None:
            return None
        
        return Item.dict_to_item(item_found)

    def item_graph(self, item_name, days):
        item = self.lookup_item(item_name)
        return ItemTradeHistory(item, days)

ge = GrandExchange()
print(str(ge.lookup_item("Shrimps")))
print(ge.request_get_counter)
