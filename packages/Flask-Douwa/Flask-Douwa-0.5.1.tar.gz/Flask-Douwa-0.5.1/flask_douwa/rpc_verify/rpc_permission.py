import json


def permission_verify(user):
    from flask_douwa import redis

    if isinstance(user, dict):
        PERMISSION_PREFIX = "duowa:permission:"
        userrole = set(user["roles"])
        key = PERMISSION_PREFIX + "角色与权限"
        dd = redis.smembers(key)

        return userrole & dd

    elif isinstance(user, str):
        try:
            _user = json.loads(user)
        except Exception as e:
            _user = None
            raise Exception(e)
        if _user:
            PERMISSION_PREFIX = "duowa:permission:"
            userrole = set(_user["roles"])
            key = PERMISSION_PREFIX + "角色与权限"
            dd = redis.smembers(key)

            return userrole & dd