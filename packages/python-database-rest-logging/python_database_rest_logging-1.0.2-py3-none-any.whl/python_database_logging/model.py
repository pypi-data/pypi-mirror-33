from __future__ import absolute_import, print_function

import json
from datetime import date,datetime
from pony.orm import *

from flask_security import UserMixin,RoleMixin;

ERROR = 0
INFO = 1
WARNING = 2
DEBUG = 3
TRACE = 4

STATES = {
    "ERROR":0,
    "INFO":1,
    "WARNING":2,
    "DEBUG":3,
    "TRACE":4
}

dbop = Database()

class User(dbop.Entity,UserMixin):
    id = PrimaryKey(int, auto = True)
    email = Required(str, unique = True, index = True) #User email
    password = Required(str) #User pwd
    first_name = Required(str) #User first name
    last_name = Required(str)  #User last name
    data = Optional(Json) #Dictionary of user defined attributes

    active = Optional(bool,default=True)
    confirmed_at = Optional(datetime)
    last_login_at = Optional(datetime)
    current_login_at = Optional(datetime)
    last_login_ip = Optional(str)
    current_login_ip = Optional(str)
    login_count = Optional(int)

    roles = Set("Role", reverse ="users" )


class Role(dbop.Entity,UserMixin):
    id = PrimaryKey(int, auto = True)
    name = Required(str)
    description = Optional(str)
    visible = Required(bool,default=True)

    users = Set("User", reverse = "roles")


class Log(dbop.Entity):
    id = PrimaryKey(int, auto = True)
    name = Required(str)
    description = Optional(str,1000)
    enviroment = Required(str)
    data = Optional(Json)

    composite_key(name,enviroment)

    log_entries = Set("LogEntry", reverse = "log")


class LogEntry(dbop.Entity):
    id = PrimaryKey(int, auto = True)
    timestamp = Required(datetime)
    level = Required(int)
    message = Required(str,1000)
    cause = Optional(str)
    user = Optional(Json)
    data = Optional(Json)

    log = Required("Log")