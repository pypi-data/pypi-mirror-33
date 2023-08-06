from ..model import Log
from ..services.CrudService import CrudService
from pony.orm import *


class LogService(CrudService):
    def __init__(self):
        super(LogService, self).__init__(Log)

    @db_session(serializable=True)
    def init_log(self, name, enviroment, description="", data=None):

        log = Log.get(name=name, enviroment=enviroment)

        if data is None:
            data = {
                "level": 4
            }
        elif "level" not in data:
            data["level"] = 4

        if log is None:
            log = Log(
                name=name,
                enviroment=enviroment,
                description=description,
                data=data
            )

        return log

    @db_session(serializable=True)
    def add_update_log(self, id, name, enviroment, descritpion="", data=None):

        if id is None:
            Log(
                name=name,
                descritpion=descritpion,
                data=data,
                enviroment=enviroment
            )
        else:
            log = Log[id]
            log.name = name
            log.description = descritpion
            log.data = data
            log.enviroment = enviroment

        return log
