from typing import Union

from paramiko import SSHClient
from sshtunnel import paramiko


class Paramiko_tunnel:
    def __init__(
        self,
        proxy_host: str,
        proxy_port: int,
        proxy_username: str,
        proxy_password: str,
        local_port: int,
    ) -> None:
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self.proxy_username = proxy_username
        self.proxy_password = proxy_password
        self.local_port = local_port
        self.ssh = None

    def ssh_connect(self, destination_address, destination_port):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            ssh.connect(
                hostname=self.proxy_host,
                port=self.proxy_port,
                username=self.proxy_username,
                password=self.proxy_password,
            )
            transport = ssh.get_transport()
            source_address = ("0.0.0.0", self.local_port)
            if transport:
                transport.request_port_forward(
                    "",
                    port=self.local_port,
                    handler=destination_address,
                )
                print(
                    f"Tunnel established: localhost:{self.local_port} -> {destination_address}:{destination_port}"
                )
                return transport
        except Exception as e:
            print(f"[-] Error creating SSHClient: {e}")
            return None
