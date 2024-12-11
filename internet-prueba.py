import datetime
import threading
from typing import List

from app.conection_handler.Proxy import Proxy
from app.conection_handler.Tunnel import SSHConnection_tunnel

# logging.basicConfig(level=logging.DEBUG)
PROXY_IP: str = "10.10.50.2"
PROXY_USERNAME: str = "proxyUser"
PROXY_PASSWORD: str = "proxyPassword"
PROXY_PORT: int = 22
# private_server_ip: str = "10.10.30.8"
PRIVATE_SERVER_PORT: int = 22
PRIVATE_SERVER_PASSWORD: str = "hiddenPassword"


def main():
    workers = 3

    available_machines = split_list(ping_machines(), workers)
    works_list = []
    for i in range(workers):
        proc = threading.Thread(
            target=ssh_tunnel_connection, args=(available_machines[i], 65500 + i)
        )
        works_list.append(proc)
        proc.start()

    for worker in works_list:
        worker.join()


def ping_machines():
    machines_to_test = [
        line.strip() for line in open("./app/utils/ips_test.txt") if line.strip()
    ]
    proxy = Proxy(
        port=PROXY_PORT,
        ip_proxy=PROXY_IP,
        user=PROXY_USERNAME,
        proxy_pass=PROXY_PASSWORD,
    )
    proxy.connect_to_proxy()
    available_machines = []

    for data in machines_to_test:
        hola = data.split(",")
        ip = hola[1]
        nemonico = hola[0]

        _, stdout, stderr = proxy.client.exec_command(f"/usr/bin/ping -c 1 -W 2 {ip}")
        out = f'{stdout.read().decode("utf-8")}\n{stderr.read().decode("utf-8")}'
        if "0 received, 100% packet loss" in out:
            print(f"{nemonico} -> {ip} is down")
        else:
            print(f"{nemonico} -> {ip} is up")
            available_machines.append(data)
    proxy.close_connections()

    return available_machines


def split_list(ip_list, sections: int) -> List[str]:
    if sections <= 0:
        raise ValueError("Number of sections (m) must be greater than 0")

    section_size = len(ip_list) // sections
    remainder = len(ip_list) % sections

    new_list = []
    start_index = 0

    for _ in range(sections):
        end_index = start_index + section_size + (1 if remainder > 0 else 0)
        new_list.append(ip_list[start_index:end_index])
        start_index = end_index
        remainder -= 1

    return new_list


def ssh_tunnel_connection(ips, host_port):
    commands = [
        # "screen-length 0 temporary",
        # "display health",
        # "display current",
        # "display clock",
        "whoami",
        "ifconfig",
        "ping -c 10 google.com",
        "cat /etc/passwd | grep sh",
        "echo 'hola amigo'",
    ]
    dir_path = "./app/test/"
    for line in ips:
        data = line.split(",")
        ip = data[1]
        nemonico = data[0]
        current_time = datetime.datetime.now().strftime(
            "%Y-%m-%d_Data_Collection_%I-%M_%p"
        )
        filename = f"{dir_path}/{nemonico}_{current_time}.log"

        with open(filename, "w"):
            pass

        with open(filename, "a") as file:
            tunnel = SSHConnection_tunnel(
                proxy_server_ip=PROXY_IP,
                proxy_username=PROXY_USERNAME,
                proxy_password=PROXY_PASSWORD,
                proxy_port=PROXY_PORT,
                private_server_ip=ip,
                private_server_port=PRIVATE_SERVER_PORT,
                private_server_password=PRIVATE_SERVER_PASSWORD,
                local_port=host_port,
            )
            is_tunnel_ok = tunnel.create_tunnel()
            is_remote_connection_ok = tunnel.connect_to_remote()
            if is_tunnel_ok and is_remote_connection_ok and tunnel != None:
                for comm in commands:
                    output = ""
                    stdin, stdout, stderr = tunnel.exec_command(comm)
                    del stdin
                    output = f'<{nemonico}> {comm}\n{stdout.read().decode("utf-8")}\n{stderr.read().decode("utf-8")}'
                    file.write(output)

        tunnel.close_tunnel_and_client()


if __name__ == "__main__":
    main()
