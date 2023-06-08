import copy
import json

class SyncStatusException(Exception):
    def __init__(self, status, result, trace):
        self.status = status
        self.result = result
        self.trace = trace
    def __str__(self):
        return self.status

def get_children(meta):
    return [t[0][0] for t in json.loads(meta).get('children')]

class SyncTaskChildrenNone(Exception):
    def __init__(self, task):
        self.task = task

    def __str__(self):
        return 'Task not children'

def get_children(meta):
    return [t[0][0] for t in json.loads(meta).get('children')]

def auth(source: str):
    def decorator(func):
        def wrapper(*args, **kwargs):
            headers = (kwargs['headers'] or {}) if 'headers' in kwargs else {}
            from .wp_auth import WPAuth
            a = WPAuth()
            print(headers)
            auth_header = a.get_auth_header()
            if auth_header:
                headers.update(auth_header)
            k = copy.deepcopy(kwargs)
            k['headers'] = headers
            res = func(*args, **k)
            res.raise_for_status()
            if res.status_code == 204:
                return True
            try:
                return res.json()
            except json.JSONDecodeError:
                if res.status_code == 200:
                    return True
                else:
                    return res
             
        return wrapper
    
    return decorator
