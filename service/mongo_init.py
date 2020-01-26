import os
from pymongo import MongoClient

#建立和数据库系统的连接,指定host及port参数
MONGO_URI=os.environ.get("MONGO_URI") or "mongodb://username:secret@localhost:27017/?authSource=admin"

# client = AsyncIOMotorClient(MONGODB_HOST, MONGODB_PORT)
mongo_uri = MONGO_URI
client = MongoClient(mongo_uri)
#连接gradedb数据库,账号密码认证
db = client.gradedb

#集合
mongo_collection=db.gradeset
