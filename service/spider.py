import json
import aiohttp
from bs4 import BeautifulSoup
grade_index_url = "http://122.204.187.6/cjcx/cjcx_cxDgXscj.html?doType=query&gnmkdmKey=N305005&sessionUserKey=%s"

grade_detail_url = "http://122.204.187.6/cjcx/cjcx_cxCjxq.html?time=1492911913954&gnmkdmKey=N305005&sessionUserKey=%s"
link_index_url = "http://portal.ccnu.edu.cn/roamingAction.do?appId=XK"
login_ticket_url = "http://122.204.187.6/xtgl/login_tickitLogin.html"
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36",
}

headers2 = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, sdch",
    "Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Cookie": "JSESSIONID=aaaVXuZqChRsa9iHtIvTv; BIGipServerpool_portal=173058240.20480.0000; UM_distinctid=15b5d8be64f12e-0bf2dfe294ca19-396a7805-13c680-15b5d8be65e45",
    "Host": "portal.ccnu.edu.cn",
    "Pragma": "no-cache",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36"
}

async def get_grade_perpage(s, sid, ip, xnm, xqm, payload):
    grade_url = grade_index_url % sid
    async with aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar(unsafe=True),
            cookies=s, headers=headers) as session:
        async with session.post(grade_url, data=payload) as resp:
            try:
                json_data = await resp.json()
                gradeList = []
                _gradeList = json_data.get('items')
                for _ in _gradeList:
                    grade = {
                        'course'  : _.get('kcmc'),#课程名
                        'credit'  : _.get('xf'),
                        'grade'   : _.get('cj'),
                        'category': _.get('kclbmc'),
                        'type'    : _.get('kcgsmc'),
                        'jxb_id'  : _.get('jxb_id'),#514C496E56E25636E0531D50A8C0F546,不知道这一项是干什么的？？？
                        'kcxzmc'  : _.get('kcxzmc')
                    }
                    if xqm == "":
                        _xqm = _.get('xqm')
                    else: _xqm = xqm
                    await get_grade_detail(session, sid, xnm, _xqm, grade) 
                    gradeList.append(grade)
                return gradeList
            except aiohttp.client_exceptions.ClientResponseError:
                return None

async def get_grade(s, sid, ip, xnm, xqm):
    payload = {
        'xnm': xnm, 'xqm': xqm,
        '_search': 'false', 'nd': '1487928673156',
        'queryModel.showCount': 100, 'queryModel.currentPage': 1,
        'queryModel.sortName': "", 'queryModel.sortOrder': 'asc',
        'time': 0
    }
    rv = await get_grade_perpage(s, sid, ip, xnm, xqm, payload)
    return rv

async def get_grade_detail(session, sid, xnm, xqm, grade):
    grade_detail = grade_detail_url % sid
    async with session.post(grade_detail, data={
        'xh_id': sid, 'jxb_id': grade['jxb_id'],
        'xnm': xnm, 'xqm': xqm, 'kcmc': grade['course']}) as resp:
        data = await resp.text()
        soup = BeautifulSoup(data, 'lxml')
        tbody = soup.tbody
        tr = tbody.find_all('tr')
        if (len(tr) == 1): # 总评
            grade.update({'usual': '', 'ending': ''})
        elif (len(tr) == 3): # 平时、期末、总评
            usual = tr[0].find_all('td')[-1].string[:-1]
            ending = tr[1].find_all('td')[-1].string[:-1]
            grade.update({'usual': usual, 'ending': ending})
        return grade
