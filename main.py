import re
import time
from threading import Thread
import socket
from sshtunnel import SSHTunnelForwarder


class SSHTunnel:
    def __init__(self, ssh_host, ssh_port, ssh_user, ssh_password, local_port, remote_host, remote_port):
        self.ssh_host = ssh_host
        self.ssh_port = ssh_port
        self.ssh_user = ssh_user
        self.ssh_password = ssh_password
        self.local_port = local_port
        self.remote_host = remote_host
        self.remote_port = remote_port
        self.server = None

    def start_tunnel(self):
        try:
            # 使用 sshtunnel 库建立 SSH 隧道
            self.server = SSHTunnelForwarder(
                (self.ssh_host, self.ssh_port),
                ssh_username=self.ssh_user,
                ssh_password=self.ssh_password,
                remote_bind_address=(self.remote_host, self.remote_port),
                local_bind_address=('127.0.0.1', self.local_port)
            )
            self.server.start()
            print(f"Tunnel established: localhost:{self.local_port}->{self.remote_host}:{self.remote_port}")

            # 本地端口监听
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
                server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 设置重用地址
                server.bind(('127.0.0.1', self.local_port))
                server.listen(5)
                print(f"Listening on localhost:{self.local_port} for connections...")

                while True:
                    client_socket, addr = server.accept()
                    print(f"Accepted connection from {addr}")
                    # 启动新线程进行数据转发
                    Thread(target=self.forward, args=(client_socket,)).start()

        except Exception as e:
            print(f"Error: {e}")
        finally:
            if self.server:
                self.server.stop()

    def forward(self, client_socket):
        print("Starting data forwarding...")
        buffer_size = 4096  # 增大缓冲区大小
        try:
            remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            remote_socket.connect(('127.0.0.1', self.server.local_bind_port))

            while True:
                start_time = time.time()

                # 从本地接收数据
                data = client_socket.recv(buffer_size)
                if not data:
                    print("No data received from local client. Closing connection.")
                    break
                print(f"Received {len(data)} bytes from local client.")

                # 将数据发送到远程
                remote_socket.sendall(data)

                # 从远程接收数据
                remote_data = remote_socket.recv(buffer_size)
                if not remote_data:
                    print("No data received from remote. Closing connection.")
                    break
                print(f"Received {len(remote_data)} bytes from remote server.")

                # 将远程数据发送回本地
                client_socket.sendall(remote_data)

                end_time = time.time()
                print(f"Data forwarding took {end_time - start_time:.2f} seconds.")
        except Exception as e:
            print(f"Error during forwarding: {e}")
        finally:
            # 确保关闭套接字
            client_socket.close()
            print("Client connection closed.")


if __name__ == '__main__':
    print("Starting PortRider")
    print("请配置 SSH 隧道所需的参数。")

    ssh_input = input("请输入ssh命令:").strip()

    # 正则表达式解析 ssh 命令
    pattern = r"ssh\s+-p\s+(\d+)\s+(\w+@[\w\.]+)"
    match = re.match(pattern, ssh_input)
    if not match:
        print("输入格式错误！请正确输入!")
        exit(1)

    # 提取 ssh_user, ssh_host 和 ssh_port
    ssh_port = int(match.group(1))
    ssh_user_host = match.group(2)
    ssh_user, ssh_host = ssh_user_host.split('@')

    print(f"SSH 用户名：{ssh_user}")
    print(f"SSH 主机：{ssh_host}")
    print(f"SSH 端口：{ssh_port}")

    # 获取 SSH 密码
    ssh_password = input("请输入你的 SSH 密码： ").strip()
    if not ssh_password:
        print("密码不能为空！")
        exit(1)

    # 获取远程端口并验证是否是数字
    remote_port = input("输入需要接入的端口:").strip()
    if not remote_port.isdigit():
        print("远程端口必须是一个数字！")
        exit(1)
    remote_port = int(remote_port)

    # 设置默认本地端口
    local_port = 8000
    print("默认本地接口为：8000")
    print("请打开：http://localhost:8000/")

    # 创建隧道对象并启动
    tunnel = SSHTunnel(ssh_host, ssh_port, ssh_user, ssh_password, local_port, "127.0.0.1", remote_port)
    tunnel.start_tunnel()
