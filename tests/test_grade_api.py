import os
import base64
import aiohttp
from aiohttp.test_utils import TestClient, loop_context

def test_grade_api(app):
    with loop_context() as loop:
        with TestClient(app, loop=loop) as client:
            
            async def get_headers():
                nonlocal client
                auth_header = {'Authorization': 'Basic %s' % base64.b64encode(b'2014210761:2014210761').decode()}
                async with aiohttp.ClientSession(headers=auth_header) as session:
                    async with session.get('http://info_login_service:8080/api/info/login/') as resp:
                        assert resp.status == 200
                        json_data = await resp.json()
                        auth_header.update(json_data.get('cookie'))
                        cookie_header = auth_header
                        cookie_header['Sid'] = json_data.get('sid')
                        return cookie_header

            async def _test_grade_get_api():
                nonlocal client
                cookie_header = await get_headers()
                resp = await client.get('/api/grade/?xnm=2014&xqm=3', headers=cookie_header)
                assert resp.status == 200
                print(".... grade get api [OK]")

            loop.run_until_complete(_test_grade_get_api())

