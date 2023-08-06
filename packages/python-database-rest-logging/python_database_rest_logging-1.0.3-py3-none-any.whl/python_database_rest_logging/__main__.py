import os
import sys

sys.path.append(os.getcwd())

API_PORT = os.environ.get('API_PORT', 5001)

from python_database_rest_logging import app

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=API_PORT)
