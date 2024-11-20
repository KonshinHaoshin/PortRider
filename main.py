import time
from threading import Thread

import paramiko
import socket

from paramiko.client import SSHClient, AutoAddPolicy


class SSHTunnel:
    def __init__(self, ssh_host, ssh_port, ssh_user, ssh_password, local_port, remote_host, remote_port):
        self.ssh_host = ssh_host
        self.ssh_port = ssh_port
        self.ssh_user = ssh_user
        self.ssh_password = ssh_password
        self.local_port = local_port
        self.remote_host = remote_host
        self.remote_port = remote_port
        self.client = None

    def forward(self, client_socket):
        print("Starting data forwarding...")
        buffer_size = 4096  # 增大缓冲区大小
        try:
            remote_channel = self.client.get_transport().open_channel(
                'direct-tcpip',
                (self.remote_host, self.remote_port),
                ('127.0.0.1', self.local_port)
            )
            if remote_channel is None or not remote_channel.active:
                print("Failed to open remote channel.")
                return

            print("Remote channel established.")

            while True:
                start_time = time.time()

                # 从本地接收数据
                data = client_socket.recv(buffer_size)
                if not data:
                    print("No data received from local client. Closing connection.")
                    break
                print(f"Received {len(data)} bytes from local client.")

                # 转发到远程
                remote_channel.sendall(data)

                # 从远程接收数据
                remote_data = remote_channel.recv(buffer_size)
                if not remote_data:
                    print("No data received from remote channel. Closing connection.")
                    break
                print(f"Received {len(remote_data)} bytes from remote server.")
                client_socket.sendall(remote_data)

                end_time = time.time()
                print(f"Data forwarding took {end_time - start_time:.2f} seconds.")
        except Exception as e:
            print(f"Error during forwarding: {e}")
        finally:
            client_socket.close()
            print("Client connection closed.")


if __name__ == '__main__':
    print("Starting PortRider")
    print("请配置 SSH 隧道所需的参数。")

    # 获取 SSH 服务器地址
    ssh_host = input("请输入你的 SSH 服务器地址（例如 ssh-server.com）： ").strip()
    if not ssh_host:
        print("SSH 服务器地址不能为空！！")
        exit(1)
    ssh_port=input("请输入ssh_port：").strip()
    # 获取 SSH 用户名
    ssh_user = input("请输入你的 SSH 用户名： ").strip()
    if not ssh_user:
        print("用户名不能为空！")
        exit(1)
    # 获取 SSH 密码
    ssh_password = input("请输入你的 SSH 密码： ").strip()
    if not ssh_password:
        print("密码不能为空！")
        exit(1)
    local_port = 8000
    remote_host = "127.0.0.1"
    remote_port = 6006

    tunnel = SSHTunnel(ssh_host, ssh_port, ssh_user, ssh_password, local_port, remote_host, remote_port)
    tunnel.start_tunnel()