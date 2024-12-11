import time

from paramiko import AutoAddPolicy, SSHClient, SSHException


class HOST_UNREACHABLE(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class Proxy:
    def __init__(
        self,
        port: int = 2222,
        ip_proxy: str = "",
        user: str = "",
        proxy_pass: str = "",
        host_pass="",
        alias="",
    ):
        """
        Initialize a Proxy object.

        Parameters:
        - port (int): Port number for the SSH connection to the proxy.
        - ip-proxy (str): IP address of the proxy.
        - user (str): Username for connecting to the proxy.
        - proxy-pass (str): Password for the proxy.
        - host-pass (str): Password for the host.
        - alias (str): Alias for the proxy (optional).
        """
        self.port = port
        self.ip_proxy = ip_proxy
        self.user = user
        self.proxy_pass = proxy_pass
        self.client = SSHClient()
        self.host_pass = host_pass
        self.alias = alias

    def get_alias(self):
        """
        Get the alias of the proxy.

        Returns:
        str: Alias of the proxy.
        """
        return self.alias

    def get_user(self):
        return self.user

    def connect_to_proxy(self) -> bool:
        """this will try the proxy connection, if success return True else return False"""
        try:
            self.client.set_missing_host_key_policy(AutoAddPolicy())
            self.client.load_system_host_keys()
            self.client.connect(
                self.ip_proxy,
                self.port,
                self.user,
                self.proxy_pass,
            )
            return True

        except SSHException as e:
            print(f"SSH Exception: {e}")
            return False

        except Exception as e:
            print(f"An exception occurred: {e}")
            return False

    def invoke_shell(self) -> None:
        """start a interactive shell in the proxy object"""
        self.shell = self.client.invoke_shell(term="xterm", width=173, height=50)

    def host_exec_command(
        self, command: str, show: bool = False, finish_prompt="$"
    ) -> str:
        """Execute a remote command against the proxy.

        Parameters:
        - command (str): The command to be executed.
        - show (bool): Whether to print the output.

        Returns:
        str: Output of the command.
        """

        chunk: str = ""
        shell = self.shell
        shell.send("{}\r".format(command).encode("utf-8"))
        time.sleep(0.5)
        output = ""

        while True:
            if self.shell.recv_ready():
                output = shell.recv(2048).decode("utf-8")
                chunk += output
            if show:
                print(output)

        return chunk

    def get_transport(self):
        return self.client.get_transport()

    def get_host_passwd(self) -> str:
        return self.host_pass

    def get_passwd(self) -> str:
        return self.proxy_pass

    def get_client(self):
        return self.client

    def close_connections(self) -> None:
        """close all proxy connections"""
        if self.client:
            self.client.close()
