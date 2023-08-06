# Simple way to create API

# user.py
def GET_index():
    return {'name': 'User'}
    

def GET_info(str_id):
    return {'user_id': str_id}


# app.py
from flask_simpleapi
import user

api = flask_simpleapi(__name__)

api.register_api(user)

api.run('0.0.0.0', host=5000, debug=True)


# This API will generate 2 endpoints
/user/index
/user/index/<str:str_id>

# SocketIO
# Server part ============================================
Install package Flask-SocketIO
`pip install flask-socketio`

Install one of async lib below:
- gevent
- eventlet

# info.py
def ON_connect():
    return 'Connected to namespace info'

# Client part ============================================
Install SocketIO client ES6
`npm install socket.io-client`

# info.js
```
import io from "socket.io-client";

let np = io(HOST_URL + '/info');  # connect to namespace info
```

