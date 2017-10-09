from websocket import ConsoleWS
from threading import Thread
from subprocess import Popen, PIPE, STDOUT
import docker


class console:
    node = ""
    running = True
    websocket = None
    stdin = None
    stdout = None
    dc = docker.from_env()

    def setNode(self, new):
        self.node = new
        p = Popen(['docker', 'exec', '-i', self.node, 'bash'], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
        self.stdin = p.stdin
        self.stdout = p.stdout
        exec_thread = Thread(target=self.exec_loop)
        reply_thread = Thread(target=self.reply_loop)
        exec_thread.start()
        reply_thread.start()
        self.websocket.send("Connected to node "+self.node)

    def start(self):
        print("Starting websocket")
        self.websocket = ConsoleWS.start()
        print("starting listeners")

    def exec_loop(self):
        while self.running:
            message = self.websocket.receive()
            if message.startswith("___CHANGENODE___"):
                message = message.replace("___CHANGENODE___","")
                message = message.replace("\n", "")
                self.setNode(message)
            else:
                self.stdin.write(message.encode('UTF-8')
                self.stdin.flush()

    def reply_loop(self):
        print("start reading")
        for line in iter(self.stdout.readline, b''):
            self.websocket.send(line)
        self.stdout.close()

    def stop(self):
        self.running = False
        self.websocket.stop()
        print("Closing server")
