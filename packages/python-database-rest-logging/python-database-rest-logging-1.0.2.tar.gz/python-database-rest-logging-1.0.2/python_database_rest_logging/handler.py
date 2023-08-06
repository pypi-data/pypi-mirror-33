from logging import *
import requests
import datetime
import json
from .model import STATES

class RequestsHandler(Handler):



    def __init__(self,
                 log_name,
                 log_enviroment,
                 log_description="",
                 log_params={},
                 endpoint="http://localhost:5001",
                 api="/logs/api/1.0"):

        self.log_name = log_name
        self.log_enviroment = log_enviroment
        self.log_description = log_description
        self.log_params = log_params

        self.endpoint = endpoint
        self.api = api
        self.ENDPOINT_INIT = "/log/init"
        self.ENDPOINT_LOG_ENTRY = "/log/entry"

        self._get_log_data()

        super(RequestsHandler, self).__init__()

    def _get_endpoint(self,endpoint):

        return self.endpoint+self.api+endpoint

    def _get_log_data(self):
        request_params = {
            "name":self.log_name,
            "enviroment":self.log_enviroment,
            "description":self.log_description,
            "data":self.log_params
        }

        try:
            result = requests.post(
                self._get_endpoint(self.ENDPOINT_INIT),
                json.dumps(request_params).encode('utf8'),
                headers={"Content-type": "application/json"}
            )

            if result.status_code == 200:
                self.log_data = json.loads(result.content.decode('utf-8'))
            else:
                print("Failed init log HTTP status not 200: {0}".format(result.content))
        except Exception as e:
            print("Failed init log got exeption: {0}".format(e))

    def emit(self, record):

        if not hasattr(self, 'log_data'):
            self._get_log_data()

        if hasattr(self, 'log_data'):
            if isinstance(record.args,tuple):
                record.args = {}

            args = record.args
            args["id"] = self.log_data["id"]
            record.args = args

            log_entry = self.format(record)

            try:
                result = requests.post(self._get_endpoint(self.ENDPOINT_LOG_ENTRY),
                              log_entry,
                              headers={"Content-type": "application/json"})

                if result.status_code == 200:
                    return result.content
                else:
                    print("Failed adding log entry HTTP status not 200: {0}".format(result.content))
            except Exception as e:
                print("Exception adding log entry: {0}".format(e))
        else:
            print("Failed adding log entry has no log_data attr")



class LogstashFormatter(Formatter):
    def __init__(self):
        super(LogstashFormatter, self).__init__()

    def format(self, record):

        timestamp_formated = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        loglevel = STATES[record.levelname]

        log_id = record.args["id"]

        if "data" in record.args:
            data = record.args["data"]
        else:
            data = {}

        if "user" in record.args:
            user = record.args["user"]
        else:
            user = {}

        if "cause" in record.args:
            cause = record.args["cause"]
        else:
            cause = ""



        data = {
            "log_id":log_id,
            "message": record.msg,
            "timestamp": timestamp_formated,
            "data":data,
            "user":user,
            "cause":cause,
            "level":loglevel
        }

        return json.dumps(data).encode('utf8')