"""
Серверное приложение для соединений
"""
import asyncio
from asyncio import transports


class ClientProtocol(asyncio.Protocol):
    login: str
    server: 'Server'
    transport: transports.Transport
    

    def __init__(self, server: 'Server'):
        self.server = server
        self.login = None

    def data_received(self, data: bytes):
        decoded = data.decode()
        print(decoded)

        if self.login is None:
            # login:User
            if decoded.startswith("login:"):
                login = decoded.replace("login:", "").replace("\r\n", "")
                clients_login = []
                for client in self.server.clients:
                    clients_login.append(client.login)
                if login not in clients_login:
                    self.login = login
                    self.transport.write(
                        f"Привет, {self.login}!".encode()
                    )
                    if self.server.histori:
                        histori = self.server.histori[-1:-11:-1]
                        histori.reverse()
                        for i in histori:
                            self.transport.write(
                                f"{i}\n".encode()
                                )
                else:
                    self.transport.write(
                        f"Логин {login} занят, попробуйте другой".encode()
                    )
            else:
                self.transport.write(
                        f'Пожалуста зарегистрируйте себя в данном чате.\nДля этого ведите команду "login:Ваш ник"'.encode()
                    )
        else:
            self.send_message(decoded)

    def send_message(self, message):
        format_string = f"<{self.login}> {message}"
        self.server.histori.append(format_string)
        encoded = format_string.encode()

        for client in self.server.clients:
            if client.login != self.login and client.login != None:
                client.transport.write(encoded)

    def connection_made(self, transport: transports.Transport):
        self.transport = transport
        self.server.clients.append(self)
        print("Соединение установлено")

    def connection_lost(self, exception):
        self.server.clients.remove(self)
        print("Соединение разорвано")


class Server:
    clients: list
    histori: list
    def __init__(self):
        self.clients = []
        self.histori = []

    def create_protocol(self):
        return ClientProtocol(self)

    async def start(self):
        loop = asyncio.get_running_loop()

        coroutine = await loop.create_server(
            self.create_protocol,
            "127.0.0.1",
            8888
        )

        print("Сервер запущен ...")

        await coroutine.serve_forever()


process = Server()
try:
    asyncio.run(process.start())
except KeyboardInterrupt:
    print("Сервер остановлен вручную")