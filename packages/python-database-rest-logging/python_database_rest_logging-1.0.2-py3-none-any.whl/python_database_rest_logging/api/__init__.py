from .VersionAPI import VersionAPI
from .LoggingAPI import LogAPI, LogEntryAPI, LogInitAPI, LogEntryNameAPI

API_OPERATIONS = [VersionAPI, LogInitAPI, LogAPI, LogEntryAPI, LogEntryNameAPI]
