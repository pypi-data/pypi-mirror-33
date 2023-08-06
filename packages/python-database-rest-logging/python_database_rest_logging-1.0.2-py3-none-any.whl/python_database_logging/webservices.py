from flask import Flask
from flask_restful import reqparse, abort, Resource, fields,marshal_with
from .services import *
from .model import *
import werkzeug

class VersionAPI(Resource):

    def get(self):
        return "Python database logging - version 1.0.0"

class LogInitAPI(Resource):

    def __init__(self):

        self.postreqparse = reqparse.RequestParser()
        self.postreqparse.add_argument('name', type=str, required=True,help='Name is required')
        self.postreqparse.add_argument('enviroment', type=str, required=True, help="Enviroment is required")
        self.postreqparse.add_argument('description', type=str, default="")
        self.postreqparse.add_argument('data', type=dict)

    def post(self):

        args = self.postreqparse.parse_args()

        log = service_log.init_log(args.name,args.enviroment,args.description,args.data)

        return service_log.to_dict(log)

class LogAPI(Resource):

    def __init__(self):

        self.postreqparse = reqparse.RequestParser()
        self.postreqparse.add_argument('id', type=int)
        self.postreqparse.add_argument('name', type=str, required=True,help='Name is required')
        self.postreqparse.add_argument('enviroment', type=str, required=True, help="Enviroment is required")
        self.postreqparse.add_argument('description', type=str, default="")
        self.postreqparse.add_argument('data', type=dict)

    def post(self):

        args = self.postreqparse.parse_args()
        log = service_log.add_update_log(args.id,args.name,args.enviroment,args.description,args.data)

        return service_log.to_dict(log)

class LogEntryAPI(Resource):

    def __init__(self):

        self.postreqparse = reqparse.RequestParser()
        self.postreqparse.add_argument('log_id', type=int, required=True, help="Log id is required")
        self.postreqparse.add_argument('level', type=int, required=True,help='level is required')
        self.postreqparse.add_argument('message', type=str, required=True,help='message is required')
        self.postreqparse.add_argument('timestamp', type=str, required=True,help='timestamp is required')
        self.postreqparse.add_argument('user', type=str, default="")
        self.postreqparse.add_argument('cause', type=str, default="")
        self.postreqparse.add_argument('data', type=dict)

    def post(self):

        args = self.postreqparse.parse_args()

        timestamp_obj = datetime.strptime(args.timestamp, "%Y-%m-%d %H:%M:%S")

        log_entry = service_log_entry.add_log_entry(args.log_id,args.level,args.message,args.cause,args.user,timestamp_obj,args.data)

        return service_log_entry.to_dict(log_entry)
