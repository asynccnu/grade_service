import os
from pymongo import MongoClient

#建立和数据库系统的连接,指定host及port参数
MONGO_HOST=os.environ.get("MONGO_HOST") or "127.0.0.1"
MONGO_PORT=os.environ.get("MONGO_PORT") or 27017
MONGO_ACCOUNT=os.environ.get("MONGO_ACCOUNT") or None
MONGO_PASSWORD=os.environ.get("MONGO_PASSWORD") or None


client = MongoClient(MONGO_HOST, MONGO_PORT)

#连接gradedb数据库,账号密码认证
db = client.gradedb

if MONGO_ACCOUNT and MONGO_PASSWORD:
    db.authenticate(MONGO_ACCOUNT, MONGO_PASSWORD)

#集合
mongo_collection=db.gradeset