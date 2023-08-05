"""
Message Parse Module
Author: Noah Gao
Updated at: 2018-2-2
"""
from bson import DBRef, ObjectId
from datetime import datetime
from .. import Constant
from . import sys, mongo

def before_check(d_id):
    """ Before Check Function """
    if not ObjectId.is_valid(d_id):
        print(d_id + " is invalid!")
        return
    else:
        d_id = ObjectId(d_id)
    result = mongo.db.devices.find_one({"_id": d_id})
    if result is not None:
        if "status" not in dict(result).keys():
            return False
        if result.get("status") == Constant.Status.STATUS_UNKNOWN:
            r = mongo.db.devices.update_one({"_id": d_id},{ "$set": { "status":  Constant.Status.STATUS_WAIT }})
    return result

def main(client, topic, payload):
    """ Parse Engine Main Function """
    print("Parsing ", topic, payload)
    if topic[0]=='SYS':
        if not before_check(payload["id"]):
            return
        if topic[1]=='online':
            sys.online(client, payload)
        elif topic[1]=='will':
            sys.offline(client, payload)
    else:
        if not before_check(topic[0]):
            return
        res = mongo.db.datas.insert_one({
            "device": DBRef("devices", topic[0]),
            "topic": topic[1],
            "flag": topic[2],
            "content": payload,
            "created_at": datetime.utcnow()
        })
        mongo.db.devices.update_one({"_id": ObjectId(topic[0])},
        {
            "$set": {
                "lastdata." + topic[1]: {
                    "flag": topic[2],
                    "content": payload,
                    "original": DBRef("datas", res.inserted_id),
                    "created_at": datetime.utcnow()
                }
            }
        })
        print(topic, payload, "Created at:", datetime.now())
