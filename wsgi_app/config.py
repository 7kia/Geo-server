import socket
HOSTNAME = socket.gethostname()
if HOSTNAME == 'testvm' or HOSTNAME == 'vbiznese':
    ENV = 'production'
else:
    ENV = 'development'

if ENV == 'production':
    DB_DIR = '/home/ilya/war-on-map/bases/'
else:
    DB_DIR = '/home/ilya/war-on-map/bases/'
