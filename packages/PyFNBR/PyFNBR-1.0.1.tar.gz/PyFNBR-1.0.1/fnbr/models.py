"""
    PyFNBR
    Copyright (C) 2018 JustMaffie

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import datetime

_images_base_url = "https://image.fnbr.co"

def format_date(date):
    if not date:
        return None
    return datetime.datetime.strptime(date[:-5], "%Y-%m-%dT%H:%M:%S")

class PriceIcon:
    def __init__(self, icon):
        self.__icon = icon

    def __repr__(self):
        return "<PriceIcon icon={}>".format(self.__icon)

    @property
    def icon(self):
        return self.__icon
    
    @property
    def icon_url(self):
        if self.__icon:
            return "{}/price/icon_{}.png".format(_images_base_url, self.__icon)
        return None

class FortniteImages:
    def __init__(self, name, icon, png, gallery, featured):
        self.__name = name
        self.__icon = icon
        self.__png = png
        self.__gallery = gallery
        self.__featured = featured

    def __repr__(self):
        return "<FortniteImages name={}>".format(self.__name)

    @property
    def icon(self):
        return self.__icon

    @property
    def png(self):
        return self.__png

    @property   
    def gallery(self):
        return self.__gallery

    @property
    def featured(self):
        return self.__featured

class APIResult:
    def __init__(self, status):
        self.__status = status

    def __repr__(self):
        return "<APIResult status={}>".format(self.__status)

    @property
    def status(self):
        return self.__status

class FortniteCosmetic(APIResult):
    def __init__(self, client, status, data):
        super().__init__(status)
        self.__data = data
        self.__client = client
    
    def __repr__(self):
        return "<FortniteCosmetic name={} id={}>".format(self.name, self.id)

    @property
    def id(self):
        return self.__data.get("id", None)
    
    @property
    def name(self):
        return self.__data.get("name", None)
    
    @property
    def price(self):
        return self.__data.get("price", None)
    
    @property
    def price_icon(self):
        return PriceIcon(self.__data.get("priceIcon", None))
    
    @property
    def images(self):
        return FortniteImages(self.name, **self.__data.get("images", None))
    
    @property
    def rarity(self):
        return self.__data.get("rarity", None)
    
    @property
    def type(self):
        return self.__data.get("type", None)
    
    @property
    def readable_type(self):
        return self.__data.get("readableType", None)

class FortniteShop(APIResult):
    def __init__(self, client, status, data):
        super().__init__(status)
        self.__data = data
        self.__client = client
    
    def __repr__(self):
        return "<FortniteShop date={}>".format(self.date)

    @property
    def date(self):
        return format_date(self.__data.get("date"))

    @property
    def featured(self):
        featured = self.__data.get("featured", [])
        _featured = []
        for item in featured:
            _featured.append(self.__client.__cosmetic(self.__client, self.status, self.__data))
        return _featured

    @property
    def daily(self):
        daily = self.__data.get("daily", [])
        _daily = []
        for item in daily:
            _daily.append(self.__client.__cosmetic(self.__client, self.status, self.__data))
        return _daily

class UpcomingItems(APIResult):
    def __init__(self, client, status, data):
        super().__init__(status)
        self.__data = data
        self.__client = client

    def __repr__(self):
        return "<UpcomingItems>"
    
    @property
    def items(self):
        if not isinstance(self.__data, list):
            return []
        items = []
        for item in self.__data:
            items.append(self.__client.__cosmetic(self.__client, self.status, item))
        return items