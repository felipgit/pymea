import socket, threading, time

class ThreadedServer(object):
    def __init__(self, host, port, data):
        print("threaded: started")
        self.host = host
        self.port = port
        self.file = data
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))

    def listen(self):
        self.sock.listen(5)
        while True:
            print("threaded: waiting for new connection")
            client, address = self.sock.accept()
            client.settimeout(5)
            threading.Thread(target = self.listenToClient,args = (client,address)).start()

    def send(self, client):
        ip, port = client.getpeername()
        content = open(self.file, "r")
        content = bytes(content.read(), encoding="utf-8")
        try:
            print(f"threaded: send to {ip}:{port}")
            client.sendall(content)
            return True
        except:
            print(f"threaded: failed connection {ip}:{port}")
            return False

    def listenToClient(self, client, address):
        print(f"threaded: client connected")
        while True:
            try:
                if not self.send(client):
                    client.close()
                    break
            except:
                print("threaded: client disconnected")
                client.close()
                return False
            time.sleep(2)

if __name__ == "__main__":
    print("main: started")
    while True:
        data = "data.file"
        port_num = 5555
        try:
            port_num = int(port_num)
            break
        except ValueError:
            pass
    ThreadedServer('',port_num,data).listen()
