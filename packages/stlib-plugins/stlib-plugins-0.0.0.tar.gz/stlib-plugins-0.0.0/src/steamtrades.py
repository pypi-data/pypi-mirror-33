#!/usr/bin/env python
#
# Lara Maia <dev@lara.click> 2015 ~ 2018
#
# The stlib is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# The stlib is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see http://www.gnu.org/licenses/.
#

import json
import os
from typing import Any, Dict, NamedTuple, Optional

import aiohttp
from bs4 import BeautifulSoup
from stlib import webapi


class TradeInfo(NamedTuple):
    id: str
    title: str
    html: str


class TradeClosedError(Exception):
    def __init__(self, trade_info: TradeInfo, message: str) -> None:
        super().__init__(message)

        self.id = trade_info.id
        self.title = trade_info.title


class TradeNotReadyError(Exception):
    def __init__(self, trade_info: TradeInfo, time_left: int, message: str) -> None:
        super().__init__(message)

        self.time_left = time_left
        self.id = trade_info.id
        self.title = trade_info.title


class NoTradesError(Exception): pass


class Main(webapi.SteamWebAPI):
    def __init__(
            self,
            session: aiohttp.ClientSession,
            server: str = 'https://www.steamtrades.com',
            bump_script: str = 'ajax.php',
            headers: Optional[Dict[str, str]] = None,
            *args: Any,
            **kwargs: Any,
    ) -> None:
        super().__init__(session, *args, **kwargs)

        self.session = session
        self.server = server
        self.bump_script = bump_script

        if not headers:
            headers = {'User-Agent': 'Unknown/0.0.0'}

        self.headers = headers

    async def get_trade_info(self, trade_id: str) -> TradeInfo:
        async with self.session.get(f'{self.server}/trade/{trade_id}/', headers=self.headers) as response:
            id = response.url.path.split('/')[2]
            title = os.path.basename(response.url.path).replace('-', ' ')
            html = await response.text()
            return TradeInfo(id, title, html)

    async def bump(self, trade_info: TradeInfo) -> bool:
        soup = BeautifulSoup(trade_info.html, 'html.parser')

        if not soup.find('a', class_='nav_avatar'):
            raise webapi.LoginError("User is not logged in")

        if soup.find('div', class_='js_trade_open'):
            raise TradeClosedError(trade_info, f"Trade {trade_info.id} is closed")

        form = soup.find('form')
        data = {}

        try:
            for input_ in form.findAll('input'):
                data[input_['name']] = input_['value']
        except AttributeError:
            raise NoTradesError("No trades available to bump")

        payload = {
            'code': data['code'],
            'xsrf_token': data['xsrf_token'],
            'do': 'trade_bump',
        }

        async with self.session.post(
                f'{self.server}/{self.bump_script}',
                data=payload,
                headers=self.headers,
        ) as response:
            html = await response.text()
            if 'Please wait another' in html:
                error = json.loads(html)['popup_heading_h2'][0]
                minutes_left = int(error.split(' ')[3])
                raise TradeNotReadyError(trade_info, minutes_left, f"Trade {trade_info.id} is not ready")
            else:
                async with self.session.post(f'{self.server}/trades', headers=self.headers) as response:
                    text = await response.text()

                if trade_info.id in text:
                    return True
                else:
                    return False
