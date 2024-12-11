import datetime
import re
import signal
import sys
import threading
import time
from typing import List

from app.conection_handler.Proxy import Proxy
from app.dibujos.Dibujos import Dibujo
from app.excel_handler.excel_writer import write
from app.utils.host_ips import ips
from app.utils.host_names import hostname


def def_handler(sig, frame):
    sys.exit(0)


signal.signal(signal.SIGINT, def_handler)


def main():
    # proxy = Proxy_server_new(
    # port=2222,
    # ip_proxy='127.0.0.1',
    # user='proxyUser',
    # proxy_pass='proxyPassword',
    # host_pass='hiddenPassword',
    # )
    num_processes = 5
    proxys: List[Proxy] = [
        Proxy(
            port=2222,
            ip_proxy="127.0.0.1",
            user="proxyUser",
            proxy_pass="proxyPassword",
            host_pass="hiddenPassword",
            alias=f"proxy_{_}",
        )
        for _ in range(num_processes)
    ]

    isConnected: List[bool] = [proxy.connect_to_proxy() for proxy in proxys]
    draw = Dibujo()

    f = None
    test_ips: List[List[str]] = [[""]]
    try:
        f = open("./app/utils/ips_test.txt", "r")
        aux = f.read()
        test_ips = [i.split(",") for i in aux.split("\n") if i != ""]
    except Exception as e:
        print(e)

    finally:
        if f:
            f.close()

    if False in isConnected:
        print(draw.get_camello())
        print("at least one proxy is not connected")
        def_handler(signal.SIGINT, None)

    else:
        print(draw.get_elefante())
        print(f"all Proxys ok ({num_processes})")

    shells = []
    for proxy in proxys:
        proc = threading.Thread(target=proxy.invoke_shell, args=())
        shells.append(proc)
        proc.start()

    for shell in shells:
        shell.join()

    aviable_ip = split_list(
        check_host_up(
            proxys[0],
            test_ips,
        ),
        num_processes,
    )
    print(aviable_ip)
    processess = [
        threading.Thread(target=proxy_handler, args=[proxys[i], aviable_ip[i]])
        for i in range(num_processes)
    ]

    start = time.time()

    for proc in processess:
        proc.start()

    for proc in processess:
        proc.join()

    end = time.time()

    print(f"tiempo de ejecucion: {end - start}")


def proxy_handler(proxy: Proxy, host_ip: List[str]):
    commands = [
        "screen-length 0 temporary",
        "dir",
        # "display version",
        # "display startup",
        # "display interface",
        # "display interface brief",
        # "display interface des",
        # "display current",
        # "display alarm all",
        # "display logbuffer",
        # "display ospf pee",
        # "display bgp peer",
        # "display esn",
        # "display device",
        # "display device pic",
        # "display elabel optical-module brief",
        # "display patch-information",
        # "display license",
        # "display license resource usage",
        # "display voltage",
        # "display power",
        # "display arp all",
        # "display alarm his",
        # "display stp brief",
        # "display multicast routing-table",
        # "display elabel brief",
        # "display mpls ldp peer",
        # "display mpls ldp session",
        # "display bgp vpnv4 all peer",
        # "display ospf pee brief",
        # "display bfd sess all",
        # "display access-user domain default1 summary",
        # "display ip pool all used",
        # "display ip vpn-instance",
        # "display ip vpn-instance verbose",
        # "display bgp vpnv4 all routing-table statistics",
        # "display bgp  vpnv4 all brief",
        # "display ip routing-table all-vpn-instance statistics",
        # "display ip routing statistics",
        # "display arp all",
        # "display mpls l2vc remote-info verbose",
        # "display mpls l2vc",
        # "display mpls l2vc brief",
        # "display vsi verbose",
        # "display vsi remote bgp",
        # "display vsi e-tree",
        # "display vsi services all",
        # "display health",
        # "display access-user domain default1",
        # "display ntp-service status",
        "display clock",
    ]

    dir_path = "./app/test"
    for ip in host_ip:
        print(f"working with {ip[1]}")
        current_time = datetime.datetime.now().strftime(
            "%Y-%m-%d_Data_Collection_%I-%M_%p"
        )
        filename = f"{dir_path}/{ip[0]}_{current_time}.log"

        with open(filename, "w"):
            pass
        with open(filename, "a") as f:
            ############### check if connection ssh or stelnet ###################

            ### attempting to connect via SSH ##############
            output = proxy.host_exec_command(f"ssh '{ip[1]}'")

            if "can't be established." in output:
                proxy.host_exec_command("yes")
            time.sleep(2)

            chunk = proxy.host_exec_command(f"{proxy.get_host_passwd()}")
            output += chunk

            ### check ssh connection successfull
            if f"<{ip[0]}>" not in chunk:
                print(f"SSH failed, trying telnet conection: {ip[0]} - {ip[1]}")

                # send ^C signal
                output += proxy.host_exec_command("\x03")

                output += proxy.host_exec_command(f"telnet {ip[1]}")
                passwords = [
                    "test124",
                    "test123",
                ]
                for password in passwords:
                    chunk = proxy.host_exec_command(password)
                    time.sleep(1)
                    output += chunk
                    if ip[0] in chunk:
                        break

            ################### checking ssh or telnet end ####################
            ################### checking ssh or telnet end ####################

            f.write(sanitize_output(output))
            ## end ssh connection process

            for com in commands:  # executing commands
                chunk = proxy.host_exec_command(
                    command=f"echo {com}", finish_prompt=f"<{ip[0]}>"
                )
                f.write(sanitize_output(chunk))
            f.flush()
            f.close()


def check_host_up(proxy: Proxy, ips: List[List[str]]):
    aviable = []

    for ip in ips:
        output: str = proxy.host_exec_command("/bin/ping -c 1 -W 1 {}".format(ip[1]))
        if "0 received" in output:
            print("{} -> down".format(ip[1]))
        else:
            print("{} -> up".format(ip[1]))
            aviable.append(ip)
    return aviable


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


def sanitize_output(raw_output):
    # # Elimina códigos de escape ANSI y otros caracteres no imprimibles
    # clean_output = re.sub(r"\x1b\[[0-9;]*[a-zA-Z]", "", raw_output)

    # # Reemplaza los saltos de línea con un espacio en blanco
    # clean_output = clean_output.replace("\n", " ")

    # # Elimina caracteres no imprimibles adicionales
    # clean_output = re.sub(r"[^ -~\t\r]+", "", clean_output)

    # # Aplicar la expresión regular y devolver el texto modificado
    # return clean_output
    return raw_output


if __name__ == "__main__":
    # main()
    write()
