# -*- coding:utf-8 -*-
from typing import Any

try:
    import ujson
    from json import JSONEncoder

    def dumps(obj, ensure_ascii=False, *args, **kwargs):
        return ujson.dumps(obj, ensure_ascii=ensure_ascii, *args, **kwargs)

    def loads(s, *args, **kwargs):
        return ujson.loads(s, *args, **kwargs)

    def load(s, *args, **kwargs):
        return ujson.load(s, *args, **kwargs)
    
    class UJSONEncoder(JSONEncoder):
        def encode(self, o: Any) -> str:
            return ujson.encode(o)
        
except ImportError:
    from json import * # type: ignore
    _default_encoder.ensure_ascii = False # type: ignore
