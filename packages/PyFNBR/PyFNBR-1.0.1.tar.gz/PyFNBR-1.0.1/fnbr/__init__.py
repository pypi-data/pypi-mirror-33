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


__title__ = 'PyFNBR'
__author__ = 'JustMaffie'
__license__ = 'AGPL'
__copyright__ = 'Copyright 2017 - 2018 JustMaffie'
__github__ = "https://github.com/JustMaffie/PyFNBR"
__major__ = "1"
__minor__ = "0"
__patch__ = "1"
__version__ = "{}.{}.{}".format(__major__, __minor__, __patch__)

import aiohttp
from fnbr.models import FortniteShop, FortniteCosmetic, UpcomingItems

class FNBRClient:
    __base_url = "https://fnbr.co/api"
    def __init__(self, _key, ShopDataClass=FortniteShop, CosmeticDataClass=FortniteCosmetic, UpcomingItemsClass=UpcomingItems):
        self.__key = _key
        self.__shop = ShopDataClass
        self.__cosmetic = CosmeticDataClass
        self.__upcoming = UpcomingItemsClass

    async def get_shop(self):
        async with aiohttp.ClientSession() as session:
            async with session.get("{}/shop".format(self.__base_url), headers={"X-API-Key":self.__key}) as resp:
                try:
                    content = await resp.json()
                except:
                    # With shop the API usually breaks for the first few minutes after the shop reset, better safe than sorry
                    return None
        return self.__shop(self, **content)

    async def get_cosmetic(self, search):
        async with aiohttp.ClientSession() as session:
            async with session.get("{}/images?search={}".format(self.__base_url, search), headers={"X-API-Key":self.__key}) as resp:
                try:
                    content = await resp.json()
                except:
                    return None
        if len(content['data']) > 0:
            return self.__cosmetic(self, content['status'], content['data'][0])
        return None

    async def upcoming_items(self):
        async with aiohttp.ClientSession() as session:
            async with session.get("{}/upcoming".format(self.__base_url), headers={"X-API-Key":self.__key}) as resp:
                try:
                    content = await resp.json()
                except:
                    return None
        return self.__upcoming(self, **content)