from os import path
#DATABASE_URL = path.join("logs.db")
DATABASE_URL = ':memory:'
API_PREFIX = "/logs/api/1.0"

#security
SECURITY_PASSWORD_HASH = 'pbkdf2_sha512'
SECURITY_TRACKABLE = True
SECURITY_PASSWORD_SALT = 'pocosi12!'
SECRET_KEY='pocosi12!'
WTF_CSRF_ENABLED = False
SECURITY_URL_PREFIX = API_PREFIX
