import datetime
import json
from aiohttp import web
from aiohttp.web import Response
from .spider import get_grade
from .decorator import require_info_login
from .mongo_init import mongo_collection

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
        xnm = args.get('xnm')  # xnm: 学年 2016,2017...
        xqm = args.get('xqm')  # xqm:第一学期3，第二学期12,第三学期16
        key = sid + "_" + xnm + "_" + xqm  # 存入redis中的键
        # 查本学年成绩
        if (int(xnm) == current_year and xqm == "3" and datetime.date(current_year, 11, 1) < current_date <= datetime.date(current_year, 12, 30)) \
                or (int(xnm) + 1 == current_year and xqm == "3" and datetime.date(current_year, 1, 1) < current_date <= datetime.date(current_year, 3, 1)) \
                or (int(xnm) + 1 == current_year and xqm != "3" and datetime.date(current_year, 5, 1) < current_date <= datetime.date(current_year, 9, 1)):
            gradeList = await get_grade(s, sid, ip, xnm, xqm)
            val = mongo_collection.find_one({"key": key})
            if gradeList:
                if val and json.loads(val.get("val")) != gradeList:
                    mongo_collection.insert_one({"key":key,"val":json.dumps(gradeList)})
                return web.json_response(gradeList)
            elif val is not None:
                # 没有爬到数据,并且缓存中有数据，则返回缓存中的数据
                return web.json_response(json.loads(val))
        else:
            #查以往学年成绩
            val = mongo_collection.find_one({"key": key})
            if val is not None:  # 缓存中有存储
                return web.json_response(json.loads(val.get('val')))
            else:
                gradeList = await get_grade(s, sid, ip, xnm, xqm)
                if gradeList:
                    mongo_collection.insert_one({"key": key, "val": json.dumps(gradeList)})
                    return web.json_response(gradeList)
                else:
                    return Response(body=b'', content_type='application/json', status=403)



# ====== url --------- maps  ======
api.router.add_route('GET', '/grade/', grade_all_api, name='grade_all_api')
# ==============================
