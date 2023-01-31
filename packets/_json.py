# -*- coding:utf-8 -*-

try:
    import ujson

    class json:
        @staticmethod
        def dumps(obj, ensure_ascii=False, *args, **kwargs):
            return ujson.dumps(obj, ensure_ascii=ensure_ascii, *args, **kwargs)

        @staticmethod
        def loads(s, *args, **kwargs):
            return ujson.loads(s, *args, **kwargs)

        @staticmethod
        def load(s, *args, **kwargs):
            return ujson.load(s, *args, **kwargs)
except ImportError:
    import json # type: ignore[no-redef]
    json._default_encoder.ensure_ascii = False # type: ignore[attr-defined]
