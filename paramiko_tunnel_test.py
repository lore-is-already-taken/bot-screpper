import time

import paramiko


def main():
    local_tunnel_port = 2224

    proxy_host = "127.0.0.1"
    proxy_tunnel_port = 2223
    proxy_username = "proxyUser"
    proxy_password = "proxyPassword"

    hidden_host = "10.10.30.9"
    hidden_username = "proxyUser"
    hidden_password = "hiddenPassword"
    hidden_host_port = 2222

    ssh_tunnel = paramiko.SSHClient()
    ssh_tunnel.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_tunnel.connect(
        hostname=proxy_host,
        port=proxy_tunnel_port,
        username=proxy_username,
        password=proxy_password,
    )
    transport = ssh_tunnel.get_transport()
    if transport:
        port = transport.request_port_forward(address=hidden_host, port=0, handler=None)
        print(port)
        time.sleep(9)


if __name__ == "__main__":
    main()
