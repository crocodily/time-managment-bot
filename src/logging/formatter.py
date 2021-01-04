import json
import logging
import traceback
from datetime import datetime


class JsonFormatter(logging.Formatter):
    @classmethod
    def format_exception(cls, exc_info):
        return ''.join(traceback.format_exception(*exc_info)) if exc_info else ''

    def format(self, record):
        log_object = {
            'level': record.levelname,
            'time': datetime.now().astimezone().isoformat(),
            'process': record.process,
            'thread': record.threadName,
            'function': record.funcName,
            'line_no': record.lineno,
            'module': record.module,
            'msg': record.getMessage(),
        }
        if record.exc_info:
            log_object['exc_info'] = self.format_exception(record.exc_info)
        elif record.exc_text:
            log_object['exc_info'] = record.exc_text
        return json.dumps(log_object, ensure_ascii=False)
