import datetime
import json
from aiohttp import web
from aiohttp.web import Response
from .spider import get_grade
from .decorator import require_info_login
from ._redis import redis_client

api = web.Application()


# ====== async view handlers ======
@require_info_login
async def grade_all_api(request, s, sid, ip):
    current_date = datetime.datetime.now().date()
    current_year = current_date.year
    query_string = request.rel_url.query_string
    if query_string:
        keys = []
        vals = []
        for _ in query_string.split('&'):
            keys.append(_.split('=')[0])
            vals.append(_.split('=')[1])
        args = dict(zip(keys, vals))
        #xqm:第一学期３，第二学期12,第三学期16
        #xnm: 学年 2016,2017...
        xnm = args.get('xnm')
        xqm = args.get('xqm')
        if (int(xnm) + 1 == current_year and xqm == "3"
                and datetime.date(current_year, 1, 15) < current_date <
                datetime.date(current_year, 2, 28)) or (
                    int(xnm) + 1 == current_year and xqm != "3"
                    and datetime.date(current_year, 6, 1) < current_date <
                    datetime.date(current_year, 9, 1)):
            gradeList = await get_grade(s, sid, ip, xnm, xqm)
            if gradeList:
                return web.json_response(gradeList)
            else:
                return Response(
                    body=b'', content_type='application/json', status=403)
        else:
            print("ppapppapap")
            key = sid + "_" + xnm + "_" + xqm
            val = redis_client.get(key)
            if val is not None:
                return web.json_response(json.loads(val))
            else:
                print("pspsppsppa")
                gradeList = await get_grade(s, sid, ip, xnm, xqm)
                print(gradeList)
                if gradeList:
                    redis_client.set(
                        key, json.dumps(gradeList), ex=126144000)  #过期时间为4年
                    return web.json_response(gradeList)
                else:
                    return Response(
                        body=b'', content_type='application/json', status=403)


# =================================

# ====== url --------- maps  ======
api.router.add_route('GET', '/grade/', grade_all_api, name='grade_all_api')
# ==============================
