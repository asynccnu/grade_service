import json
from aiohttp import web
from aiohttp.web import Response
from .spider import get_grade
from .decorator import require_info_login
from .redis import redis_client

api = web.Application()

# ====== async view handlers ======
@require_info_login
async def grade_all_api(request, s, sid, ip):
    query_string = request.rel_url.query_string
    if query_string:
        keys = []; vals = []
        for _ in query_string.split('&'):
            keys.append(_.split('=')[0])
            vals.append(_.split('=')[1])
        args = dict(zip(keys, vals))
        #xqm:第一学期３，第二学期12
        # xnm: 学年 2016,2017...　
        xnm = args.get('xnm'); xqm = args.get('xqm')
        key=sid+"_"+xnm+"_"+xqm
        val=redis_client.get(key)
        if val is not None:
            return web.json_response(json.loads(val))
        else:
            gradeList = await get_grade(s, sid, ip, xnm, xqm)
            if gradeList:
                redis_client.set(key,json.dumps(gradeList),ex=126144000)#过期时间为4年
                return web.json_response(gradeList)
            else:
                return Response(body=b'', content_type='application/json', status=403)
    # =================================

# ====== url --------- maps  ======
api.router.add_route('GET', '/grade/', grade_all_api, name='grade_all_api')
# ==============================