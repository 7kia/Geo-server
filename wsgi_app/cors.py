import falcon
from falcon_cors import CORS

cors = CORS(allow_origins_list=[
    'http://localhost:8080',
    'http://localhost:80',
    'http://waronmap.com:8080',
    'http://waronmap.com:80'
])
api = falcon.API(middleware=[cors.middleware])
public_cors = CORS(allow_all_origins=True)

