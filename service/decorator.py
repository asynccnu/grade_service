import json
import functools
import aiohttp
from aiohttp.web import Response

info_login_service = "https://ccnubox.muxixyz.com/api/info/login/"

def require_info_login(f):
    @functools.wraps(f)
    async def decorator(request, *args, **kwargs):
        headers = request.headers
        req_headers = dict(headers)
        BIGipServerpool_jwc_xk = req_headers.get("Bigipserverpool")
        JSESSIONID = req_headers.get("Jsessionid")
        sid = req_headers.get("Sid")
        auth = req_headers.get("Authorization")

        if BIGipServerpool_jwc_xk and JSESSIONID and sid:
            cookies = {'BIGipServerpool_jwc_xk': BIGipServerpool_jwc_xk, 'JSESSIONID': JSESSIONID}
            return await f(request, cookies, sid, None, *args, **kwargs)

        elif auth: # 兼容V1版API
            # 网络请求info_login_service拿到cookie进行
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.96 Safari/537.36',
                'Authorization': auth,
                'Tag': 'v1'
            }
            conn = aiohttp.TCPConnector(verify_ssl=False)
            async with aiohttp.ClientSession(headers=headers, connector=conn) as session:
                async with session.get(info_login_service) as resp:
                    if resp.status == 200:
                        json_data = await resp.json()
                        BIGipServerpool_jwc_xk = json_data.get('BIGipServerpool_jwc_xk')
                        JSESSIONID = json_data.get('JSSESIONID')
                        sid = json_data.get('sid')
                        cookies = {'BIGipServerpool_jwc_xk': BIGipServerpool_jwc_xk, 'JSESSIONID': JSESSIONID}
                        return await f(request, cookies, sid, None, *args, **kwargs)
                    elif resp.status == 403:
                        return Response(body=b'', content_type='application/json', status=403)
        else: return Response(
            body = b'', content_type = 'application/json',
            status = 401
        )
    return decorator
