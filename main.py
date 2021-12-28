from server.server1 import Server


class App:
    def __init__(self):
        self.server = Server()

    def start(self):
        self.server.run()


if __name__ == '__main__':
    app = App()
    app.start()
