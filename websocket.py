from threading import Thread
from tornado import websocket, web, ioloop, httpserver
from queue import Queue
import datetime


class ConsoleWS:
    r_queue = Queue()
    s_queue = Queue()
    server = None

    @staticmethod
    def start():
        cws = ConsoleWS()
        t = Thread(target=cws.run)
        t.start()
        return cws

    def run(self):
        application = web.Application([
            (r'/', ConsoleWebSocketHandler, {'rqueue': self.r_queue,'squeue': self.s_queue}),
        ])
        self.server = httpserver.HTTPServer(application)
        self.server.listen(8081)
        ioloop.IOLoop.current().start()

    def stop(self):
        self.server.stop()
        ioloop.IOLoop.current().stop()

    def send(self, txt):
        self.s_queue.put(txt)

    def receive(self):
        return self.r_queue.get()


class ConsoleWebSocketHandler(websocket.WebSocketHandler):
    rqueue = None
    qeueue = None

    def __init__(self,*args, **kwargs):
        self.rqueue = kwargs.pop('rqueue')
        self.squeue = kwargs.pop('squeue')
        super(ConsoleWebSocketHandler,self).__init__(*args, **kwargs)

    def open(self):
        self.flush_squeue()
        pass

    def on_message(self, message):
            self.rqueue.put(message)

    def flush_squeue(self):
        while not self.squeue.empty():
            r = self.squeue.get()
            self.write_message(r)
        d = datetime.timedelta(milliseconds=500)
        ioloop.IOLoop.current().add_timeout(deadline=d, callback=self.flush_squeue)

    def on_close(self):
        pass

    def check_origin(self, origin):
        return True
