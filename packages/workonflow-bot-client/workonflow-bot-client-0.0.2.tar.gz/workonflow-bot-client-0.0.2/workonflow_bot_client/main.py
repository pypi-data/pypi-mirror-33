import logging
import os
import sys
from socketIO_client_nexus import SocketIO

from workonflow_bot_client.login_info import LoginInfo

from workonflow_bot_client.lib.comment.index import Comment
from workonflow_bot_client.lib.thread.index import Thread
from workonflow_bot_client.lib.stream.index import Stream

# logging.getLogger('socketIO-client-nexus').setLevel(logging.DEBUG)
# logging.basicConfig(level=logging.DEBUG)

def on_connect():
    print('Connected to ', os.environ.get('WS_ENDPOINT'))

def on_reconnect():
    print('[Reconnected]')

def on_disconnect():
    print('[Disconnected]')

def on_login(*args):
    print('[logged]', args)
    loginInfo.setContacts(args)

def on_connect_error():
    print('connect_error')

def error(*args):
    print('connect error', *args)

def reconnect(*args):
    print('socket reconnect_attempt ', args)

def connect(creds=None):
    endpoint = 'http://wss-bots.bots:3000'
    global loginInfo
    global socket

    if creds == None or not 'email' in creds or not 'password' in creds:
        print('\n[ERRO] --->Credentials is required\n')
        sys.exit()
    else:
        email = creds['email']
        password = creds['password']

    if os.environ.get('WS_ENDPOINT') != None:
        endpoint = os.environ.get('WS_ENDPOINT')
        print(f'get env: {endpoint}')

    socket = SocketIO(endpoint, params={"email": email, "password": password})

    socket.on('connect', on_connect)
    socket.on('reconnect', on_reconnect)
    socket.on('disconnect', on_disconnect)
    socket.on('connect_error', error)
    socket.on('reconnect_attempt', reconnect)

    loginInfo = LoginInfo()

    socket.on('login', on_login)

    return socket

if __name__ == "__main__":
    connect()
