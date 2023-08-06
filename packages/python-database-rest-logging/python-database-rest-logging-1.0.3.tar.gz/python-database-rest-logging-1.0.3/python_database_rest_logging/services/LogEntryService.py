from ..model import LogEntry, Log
from ..services.CrudService import CrudService
from pony.orm import *
from datetime import datetime


class LogEntryService(CrudService):
    def __init__(self):
        super(LogEntryService, self).__init__(LogEntry)

    @db_session(serializable=True)
    def add_log_entry_by_name(self, name, level, message, cause="", user="", timestamp=datetime.now(), data=None):
        log = Log.get(name=name)

        if log is None:
            raise Exception("Log with name '"+name+"' does not exist")

        if log.data is not None and "level" in log.data:
            log_level = log.data["level"]
        else:
            log_level = 4

        log_entry = None
        if log_level >= level:
            log_entry = LogEntry(
                log=log,
                level=level,
                message=message,
                timestamp=timestamp,
                data=data,
                cause=cause,
                user=user
            )

        return log_entry

    @db_session(serializable=True)
    def add_log_entry(self, log_id, level, message, cause="", user="", timestamp=datetime.now(), data=None):
        log = Log[log_id]

        if log.data is not None and "level" in log.data:
            log_level = log.data["level"]
        else:
            log_level = 4

        log_entry = None
        if log_level >= level:
            log_entry = LogEntry(
                log=log,
                level=level,
                message=message,
                timestamp=timestamp,
                data=data,
                cause=cause,
                user=user
            )

        return log_entry

    @db_session(serializable=True)
    def to_dict(self, obj):
        if obj == None:
            return None
        elif isinstance(obj, list):
            return [self.to_dict(c) for c in obj]
        else:
            log_entry_dict = self.db_object[obj.id].to_dict()
            log_entry_dict["timestamp"] = log_entry_dict["timestamp"].strftime('%Y-%m-%d %H:%M:%S')

            return log_entry_dict
