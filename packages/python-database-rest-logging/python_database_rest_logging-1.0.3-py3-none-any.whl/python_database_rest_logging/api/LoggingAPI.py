from flask_restful import reqparse, Resource, abort
from ..services.LogEntryService import LogEntryService
from ..services.LogService import LogService
from ..model import *
from injector import inject


class LogInitAPI(Resource):
    DECORATORS = []
    ENDPOINT = "/log/init"

    @inject
    def __init__(self, service_log: LogService):
        self.postreqparse = reqparse.RequestParser()
        self.postreqparse.add_argument('name', type=str, required=True, help='Name is required')
        self.postreqparse.add_argument('enviroment', type=str, required=True, help="Enviroment is required")
        self.postreqparse.add_argument('description', type=str, default="")
        self.postreqparse.add_argument('data', type=dict)

        self._service_log = service_log

    def post(self):
        args = self.postreqparse.parse_args()

        log = self._service_log.init_log(args.name, args.enviroment, args.description, args.data)

        return self._service_log.to_dict(log)


class LogAPI(Resource):
    DECORATORS = []
    ENDPOINT = "/log"

    @inject
    def __init__(self, service_log: LogService):
        self.postreqparse = reqparse.RequestParser()
        self.postreqparse.add_argument('id', type=int)
        self.postreqparse.add_argument('name', type=str, required=True, help='Name is required')
        self.postreqparse.add_argument('enviroment', type=str, required=True, help="Enviroment is required")
        self.postreqparse.add_argument('description', type=str, default="")
        self.postreqparse.add_argument('data', type=dict)

        self._service_log = service_log

    def post(self):
        args = self.postreqparse.parse_args()
        log = self._service_log.add_update_log(args.id, args.name, args.enviroment, args.description, args.data)

        return self._service_log.to_dict(log)


class LogEntryNameAPI(Resource):
    DECORATORS = []
    ENDPOINT = "/log/<name>/entry"

    @inject
    def __init__(self, service_log_entry: LogEntryService):
        self.postreqparse = reqparse.RequestParser()
        self.postreqparse.add_argument('level', type=int, required=True, help='level is required')
        self.postreqparse.add_argument('message', type=str, required=True, help='message is required')
        self.postreqparse.add_argument('timestamp', type=str, required=True, help='timestamp is required')
        self.postreqparse.add_argument('user', type=dict, default="")
        self.postreqparse.add_argument('cause', type=str, default="")
        self.postreqparse.add_argument('data', type=dict)

        self._service_log_entry = service_log_entry

    def post(self, name):
        args = self.postreqparse.parse_args()

        timestamp_obj = datetime.strptime(args.timestamp, "%Y-%m-%d %H:%M:%S")

        try:
            log_entry = self._service_log_entry.add_log_entry_by_name(name, args.level, args.message, args.cause, args.user,
                                                              timestamp_obj, args.data)

            return self._service_log_entry.to_dict(log_entry)
        except Exception as e:
            abort(400, message=str(e))


class LogEntryAPI(Resource):
    DECORATORS = []
    ENDPOINT = "/log/entry"

    @inject
    def __init__(self, service_log_entry: LogEntryService):
        self.postreqparse = reqparse.RequestParser()
        self.postreqparse.add_argument('log_id', type=int, required=True, help="Log id is required")
        self.postreqparse.add_argument('level', type=int, required=True, help='level is required')
        self.postreqparse.add_argument('message', type=str, required=True, help='message is required')
        self.postreqparse.add_argument('timestamp', type=str, required=True, help='timestamp is required')
        self.postreqparse.add_argument('user', type=dict, default="")
        self.postreqparse.add_argument('cause', type=str, default="")
        self.postreqparse.add_argument('data', type=dict)

        self._service_log_entry = service_log_entry

    def post(self):
        args = self.postreqparse.parse_args()

        timestamp_obj = datetime.strptime(args.timestamp, "%Y-%m-%d %H:%M:%S")

        log_entry = self._service_log_entry.add_log_entry(args.log_id, args.level, args.message, args.cause, args.user,
                                                          timestamp_obj, args.data)

        return self._service_log_entry.to_dict(log_entry)
