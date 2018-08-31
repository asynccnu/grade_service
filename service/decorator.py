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

        else: return Response(
            body = b'', content_type = 'application/json',
            status = 401
        )
    return decorator
