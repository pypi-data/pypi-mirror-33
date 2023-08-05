# PyFNBR
Python API wrapper for the FNBR.co API

## Development Team
Category            | People
------------------- | --------------------------
Lead Developer      | JustMaffie#5001 ([@JustMaffie](https://github.com/JustMaffie))

## Installation
1. `sudo python3.5 -m pip install pyfnbr`

## Installation (Manual)
1. `git clone https://github.com/JustMaffie/PyFNBR && cd PyFNBR`
1. `sudo python3.5 setup.py install`

## API Key
To be able to use this API library, you must request an API key for FNBR.co, for more information, go to [the FNBR.co docs](https://fnbr.co/api/docs)

## Example
The following example shows how to grab the current shop rotation
```py
import fnbr
import asyncio

key = "api_key_here"

async def start():
    client = fnbr.FNBRClient(key)
    cosmetic = await client.get_shop()
    print(cosmetic)

loop = asyncio.get_event_loop()
loop.run_until_complete(start())
```
[Full Documentation](https://github.com/JustMaffie/PyFNBR/wiki)

## Licence

```
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
```

## Quick notes
- This is not an official API wrapper, I am not associated with FNBR.co!
- The API can change at any given moment, when it does, I'll try to update this API wrapper as soon as possible, I cannot guarantee this library is always up to date, but I will try to keep it so!