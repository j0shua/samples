import tornado.ioloop
import tornado.web
import tornado.httpserver
import tornado.httpclient
import json

'''
on 1st request cache is empty so
    - fetch both
    - compare to each other
    - return the smaller one
    - delete smaller one from the cache

now the cache will have the bigger one so next request:
    - fetch one not in the cache
    - compare to each other
    - return the smaller one
    - delete the smaller one from the cache

-- more generally --
foreach stream:
    if not in cache:
        fetch(stream, handle_request)

handle_request:
    if both streams are not in cache -- get them
        if its the 1st request:
            do nothing / pass
        else:
            compare
            return smaller
            delete smaller from cache
'''


API_ENDPOINT = "https://api.xxxxxxxxxxxx.com/quiz/next/"
# needs to be in higher scope so we can preserve this between requests
lastReturned = None
responseCache = {}


class MainHandler(tornado.web.RequestHandler):

    @tornado.web.asynchronous
    def get(self):
        ''' handles response from async api call
            this can be called by either the 1st or 2nd request
            so we need to parse the stream name to know which this is
            and then we check the cache to make sure the other one is
            there already
        '''
        def handle_request(response):
            global lastReturned
            global responseCache

            self.set_header("Content-Type", "application/json")
            if response.error:
                self.write(response.error)
            else:
                # parse the response
                vals = json.loads(response.body)
                # use stream name to know which request this is
                streamName = vals['stream']
                responseCache[streamName] = vals
                # if this is 2nd item
                # compare it to the other
                # return the smaller one and remove it from the cache
                vals1 = responseCache.get(stream1)
                vals2 = responseCache.get(stream2)
                if vals1 and vals2:
                    print('2nd request')
                    print(responseCache)
                    print(lastReturned)

                    if vals1['current'] < vals2['current']:
                        responseVals = {
                            'last': lastReturned,
                            'current': vals1['current']
                        }
                        del responseCache[vals1['stream']]
                    else:
                        responseVals = {
                            'last': lastReturned,
                            'current': vals2['current']
                        }
                        del responseCache[vals2['stream']]

                    lastReturned = responseVals['current']
                    print('returning:')
                    print(responseVals)
                    self.write(responseVals)
                    self.finish()
                else:
                    print('first request')
                    print(responseCache)
                    pass

        # todo: should probably validate stream names
        stream1 = self.get_query_argument('stream1')
        stream2 = self.get_query_argument('stream2')

        if stream1 and stream2:
            http_client = tornado.httpclient.AsyncHTTPClient()
            # if stream data is not in the cache, fetch next item
            if not responseCache.get(stream1):
                http_client.fetch(API_ENDPOINT+stream1, handle_request)
            if not responseCache.get(stream2):
                http_client.fetch(API_ENDPOINT+stream2, handle_request)
        else:
            self.send_error(400)
            self.finish

if __name__ == "__main__":
    app = tornado.web.Application(
        handlers=[(r"/quiz/merge", MainHandler)],
        debug=True
    )
    httpserver = tornado.httpserver.HTTPServer(app)
    httpserver.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
