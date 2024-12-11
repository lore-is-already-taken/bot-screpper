import paramiko
import sshtunnel


class SSHConnection_tunnel:
    def __init__(
        self,
        proxy_server_ip: str,
        proxy_username: str,
        proxy_password: str,
        proxy_port: int,
        private_server_ip: str,
        private_server_port: int,
        private_server_password: str,
        local_port: int,
    ):
        self.proxy_server_ip = proxy_server_ip
        self.proxy_username = proxy_username
        self.proxy_password = proxy_password
        self.proxy_port = proxy_port
        self.private_server_ip = private_server_ip
        self.private_server_port = private_server_port
        self.private_server_password = private_server_password
        self.local_port = local_port
        self.tunnel = None
        self.client = None

    def create_tunnel(self):
        try:
            self.tunnel = sshtunnel.open_tunnel(
                (self.proxy_server_ip, 22),
                ssh_username=self.proxy_username,
                ssh_password=self.proxy_password,
                remote_bind_address=(self.private_server_ip, 22),
                local_bind_address=("127.0.0.1", self.local_port),
            )
            self.tunnel.start()
            return self.tunnel.is_active
        except Exception as e:
            print(f"[-] Tunnel creation error: {e}")
            return False

    def connect_to_remote(self):
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.load_system_host_keys()
            self.client.connect(
                hostname="127.0.0.1",
                port=self.local_port,
                username=self.proxy_username,
                password=self.private_server_password,
            )
            print(
                f"[+] Connection to private server {self.private_server_ip}:{self.local_port} success"
            )
            return True
        except Exception as e:
            print(f"[-] Connection to private server error: {e}")
            return False

    def exec_command(self, command: str):
        if self.client:
            stdin, stdout, stderr = self.client.exec_command(command)
            return stdin, stdout, stderr
        else:
            print(f"[-] EXEC COMMAND: error, client is None")

    def close_tunnel_and_client(self):
        if self.client:
            self.client.close()
        if self.tunnel:
            self.tunnel.close()
        print(f"[+] close tunnel and client success to {self.private_server_ip}")

    def __enter__(self):
        self.create_tunnel()
        self.connect_to_remote()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_tunnel_and_client()
