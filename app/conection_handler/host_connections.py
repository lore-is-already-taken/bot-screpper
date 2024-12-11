import socket
from typing import Union

from paramiko import AutoAddPolicy, SSHClient


class Handle_host_connection:
    def __init__(
        self,
        hidden_host: str,
        hidden_port: int,
        hidden_password: str,
        hidden_user: str,
        hidden_ip: str,
        tunnel,
    ) -> None:
        self.hidden_ip = hidden_ip
        self.hidden_host = hidden_host
        self.hidden_port = hidden_port
        self.hidden_password = hidden_password
        self.hidden_user = hidden_user
        self.ssh_client = None
        self.telnet_client = None
        self.tunnel = tunnel

    def ssh_connect(self) -> Union[SSHClient, None]:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tunnel_sock:
                tunnel_sock.bind(("127.0.0.1", 2223))

                ssh = SSHClient()
                ssh.set_missing_host_key_policy(AutoAddPolicy())

                ssh.connect(
                    self.hidden_ip,
                    port=self.hidden_port,
                    username=self.hidden_user,
                    password=self.hidden_password,
                    sock=tunnel_sock,
                )
                return ssh
        except Exception as e:
            print(f"[-] SSH connection Error: {e}")
            print(f"\t{self.hidden_host} -> can't connect over ssh ")
            return None
