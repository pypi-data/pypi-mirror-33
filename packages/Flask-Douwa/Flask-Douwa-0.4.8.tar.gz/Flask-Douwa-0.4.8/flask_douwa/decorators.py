import json
import requests

from functools import wraps
from flask import request, g, current_app
from flask_douwa import redis, Douwa
from flask_douwa import reqparse

TOKEN_PREFIX = "douwa:token:"
TOKEN_EXPIRES = 3600
TOKEN_EXPIRES2 = 3600 * 12 * 30
PERMISSION_PREFIX = "duowa:permission:"
KEY_PREFIX = 'douwa:key:'


def authorization(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        prefix = TOKEN_PREFIX
        key_prefix = KEY_PREFIX
        ttl = TOKEN_EXPIRES

        user = None
        token = None
        if 'Authorization' in request.headers:
            token = request.headers.get('Authorization')[7:]
        elif 'AuthKey' in request.headers:
            header_key = request.headers.get('AuthKey')[7:]
            if header_key:
                key = key_prefix + header_key
                # print(redis_key)
                user_cached = redis.get(key)
                if not user_cached:
                    # 发送激活key的请求
                    key_url = current_app.config.get('KEY_URL')
                    headers = {'AuthKey': 'bearer ' + header_key}
                    res = requests.get(url=key_url, headers=headers)
                    # print(res.status_code)
                    if not res.status_code == 200:
                        reqparse.abort(400, message='KEY配置错误')

                try:
                    user_cached = redis.get(key)
                    user = json.loads(user_cached)
                except Exception as e:
                    user = None
                    raise Exception(e)

        else:
            parserd = reqparse.RequestParser()
            parserd.add_argument('access_token', "token", type=str, location='args')
            urlargs = parserd.parse_args()
            if "access_token" in urlargs:
                token = urlargs["access_token"]
            else:
                token = None
        if token:
            key = prefix + token
            user_cached = redis.get(key)
            if user_cached:
                try:
                    user = json.loads(user_cached)
                except Exception as e:
                    user = None
                    raise Exception(e)
        if not user:
            error_str = "用户没有登录!"
            reqparse.abort(401, message=error_str)
        if token not in Douwa.client_access:
            expired = redis.ttl(key)
            if expired:
                redis.expire(key, ttl)
        else:
            redis.expire(key, TOKEN_EXPIRES2)

        g.user = user
        return f(*args, **kwargs)

    return decorated_function


def permission(name):
    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            userrole = set(g.user["roles"])
            key = PERMISSION_PREFIX + name
            dd = redis.smembers(key)
            if userrole & dd:
                return func(*args, **kwargs)
            else:
                error_str = "没有操作权限!"
                reqparse.abort(401, message=error_str)

        return inner

    return wrapper


def error(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            data = f(*args, **kwargs)
            return data
        except Exception as e:
            if hasattr(e, "data"):
                return json.dumps(e.data, ensure_ascii=False)
            else:
                raise e

    return decorated_function
