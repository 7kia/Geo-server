import socket
HOSTNAME = socket.gethostname()
if HOSTNAME == 'testvm' or HOSTNAME == 'vbiznese':
    ENV = 'production'
else:
    ENV = 'development'

if ENV == 'production':
    DB_DIR = '/home/ilya/war-on-map/Geo-server/bases/'
else:
    DB_DIR = '/home/ilya/war-on-map/Geo-server/bases/'
