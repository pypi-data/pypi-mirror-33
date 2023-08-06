from flask_restful import Resource


class VersionAPI(Resource):
    DECORATORS = []
    ENDPOINT = "/version"

    def get(self):
        return "Python database rest logging - version 1.0.0"
