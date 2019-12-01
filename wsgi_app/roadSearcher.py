import sys


class RoadSearcher:
    @classmethod
    def get_response(cls, function1, environ):
        response = ""
        try:
            response = "".join(
                [str(function1(environ))]
            )
        except BaseException as e:
            response = "Error: " + str(e)
        except:
            response = "Unexpected error:" + str(sys.exc_info()[0])
        return response

    @classmethod
    def handle_request(cls, environ, start_response, function1):
        # try:
            status = '200 OK'
            response = cls.get_response(function1, environ)
            response_headers = [
                ('Content-type', 'text/html'),
                ('Access-Control-Allow-Origin', '*'),
                ('Content-Length', str(len(response)))
            ]
            start_response(status, response_headers)
            return [response]
        # except:
        #     # print("Unexpected error:", sys.exc_info()[0])
        #     return [sys.exc_info()[0]]


