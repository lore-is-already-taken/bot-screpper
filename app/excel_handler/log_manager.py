import os
import re
from enum import Enum
from typing import Dict, List

from app.machines.Lpus import Lpu
from app.machines.Machine import Equipo
from app.machines.Mpu import Mpu
from app.machines.Pic import Pic
from app.machines.Sfu import Sfu
from app.utils.commands import commands as Commands

interestCommands = [i.value for i in Commands]


def delete_empty(item):
    filtered_array: List[str] = [i for i in item if i != "" and i != " "]
    return filtered_array


def get_section(section: str, content: list):
    desired_section = ""

    for i in content:
        if section in i[0]:
            desired_section = i
            break

    return delete_empty(desired_section)


def searchFiles(path):
    files = os.listdir(path)
    return files


def readContent(fileName) -> Dict[str, str]:
    path = "./app/files/" + fileName
    section_dictionary = {}
    content = "".join([line for line in open(path, "r")])
    splitContent: List[str] = split_sections(content)
    section_array: List[List[str]] = [
        delete_empty(item.split("\n"))
        for item in splitContent
        if item.split("\n")[0] in [i.value for i in Commands]
    ]
    for section in section_array:
        object = {section[0]: section[1:]}
        section_dictionary.update(object)
    return section_dictionary


def split_sections(content) -> List[str]:
    content = re.split(r"<.*>", content)
    return content


def get_hostname(content):
    name = content.split("_")[0]
    return name


def get_softwareVersion_and_lpu(content):
    util_section = content[Commands.displayVersion.value]
    lpus = 0
    version = ""

    for section in util_section[0:20]:
        if "LPU" in section and "Slot" in section and "Quantity" in section:
            lpus = int(section.split(":")[-1])
        elif "Patch Version" in section:
            version = section.split(":")[-1].strip()

    return version, lpus


def get_LPU(content):
    lpus = []
    section = content[Commands.displayElabelBrief.value]
    section = [delete_empty(item.split("  ")) for item in section]

    for i in range(len(section)):
        aux_section = [item for item in section[i] if item != " "]
        aux_name = ""
        aux_model = ""
        aux_pic0 = Pic()
        aux_pic1 = Pic()

        if re.match(r"LPU.*?", aux_section[0]):
            aux_name = aux_section[0]
            if " " in aux_section[-1]:
                aux_model = aux_section[-1].split(" ")[1]
            else:
                aux_model = aux_section[-1]

            if i + 1 <= len(section) and section[i + 1][0] == "PIC 0":
                aux_pic0.set_name([item for item in section[i + 1] if item != " "][-1])
                max_port = port_in_pic(section[i + 1])
                aux_pic0.set_max_port(max_port)

            elif i + 1 <= len(section) and section[i + 1][0] == "PIC 1":
                aux_pic1.set_name([item for item in section[i + 1] if item != " "][-1])
                max_port = port_in_pic(section[i + 1])
                aux_pic1.set_max_port(max_port)

            if i + 2 < len(section) and section[i + 2][0] == "PIC 1":
                aux_pic1.set_name([item for item in section[i + 2] if item != " "][-1])
                max_port = port_in_pic(section[i + 2])
                aux_pic1.set_max_port(max_port)
            else:
                aux_pic0.set_name([item for item in section[i + 1] if item != " "][-1])
                max_port = port_in_pic(section[i + 1])
                aux_pic0.set_max_port(max_port)

            lpu = Lpu(
                lpuName=aux_name, lpuModel=aux_model, pic0=aux_pic0, pic1=aux_pic1
            )
            lpus.append(lpu)

    return lpus


def port_in_pic(content) -> str:
    try:
        return str(int(content[-1].split("x")[0].split("-")[-1]))
    except:
        return "---"


def define_bw(band_width):
    class bw_values(Enum):
        hundredGb = "100Gb"
        tenGb = "10300Mb"

    if band_width == bw_values.hundredGb.value or len(band_width) > 7:
        return "100 GB"
    elif band_width == bw_values.tenGb.value:
        return "10 GB"
    else:
        return "1 GB"


def get_ports(content, lpus):
    aux_section = content[Commands.displayOpticalModuleBrief.value]

    sections = [delete_empty(item.split(" ")) for item in aux_section if "ETH" in item]

    for i in range(len(lpus)):
        lpu_number = (
            int(lpus[i].get_name().split(" ")[1])
            if len(lpus[i].get_name().split(" ")) > 1
            else 0
        )
        aux_pic0 = Pic(
            picName=lpus[i].get_pic0().get_name(),
            max_port=lpus[i].get_pic0().get_max_port(),
        )
        aux_pic1 = Pic(
            picName=lpus[i].get_pic1().get_name(),
            max_port=lpus[i].get_pic1().get_max_port(),
        )

        for section in sections:
            eth = section[0].split("/")
            if ":" in eth[-1] and int(eth[-1].split(":")[-1]) == 0:
                eth_id = int(eth[-1].split(":")[0])
            elif ":" not in eth[-1]:
                eth_id = int(eth[-1])
            else:
                continue

            eth_lpu = int(eth[0].split("H")[-1])
            eth_pic = int(eth[1])

            if lpu_number == 0:
                continue

            if (lpu_number == eth_lpu and eth_pic == 0) and (
                eth_id == 0 or eth_id == 1
            ):
                band = define_bw(section[-1])
                aux_pic0.set_bw(band)

            if lpu_number == eth_lpu and eth_pic == 1 and (eth_id == 0 or eth_id == 1):
                band = define_bw(section[-1].split("/")[0])
                aux_pic1.set_bw(band)

            if lpu_number == eth_lpu and eth_pic == 0:
                aux_pic0.add_port()

            if lpu_number == eth_lpu and eth_pic == 1:
                aux_pic1.add_port()

        lpus[i].set_pic0(aux_pic0)
        lpus[i].set_pic1(aux_pic1)


def get_Mpus(content):
    slave_mpu = Mpu()
    master_mpu = Mpu()

    elabel = content[Commands.displayElabelBrief.value]
    startup = content[Commands.displayStartup.value]
    version = content[Commands.displayVersion.value]

    for card in elabel:
        if "MPU" in card:
            info = delete_empty(card.split(" "))
            master_mpu.set_model(info[-1])
            slave_mpu.set_model(info[-1])
            break

    def get_memory_type(content):
        sdRam_partial_match = "SDRAM Memory Size"
        cfCard_partial_match = "CFCARD Memory Size"

        # this is getting the 'i' index
        # where the 'SDRAM Memory...' word is located
        sdRam_index = next(
            (i for i, item in enumerate(content) if sdRam_partial_match in item), -1
        )

        # this is getting the 'i' index
        # where the 'CFCARD Memory ...' word is located
        cfCard_index = next(
            (i for i, item in enumerate(content) if cfCard_partial_match in item), -1
        )

        sdRam = get_memory_size(content[sdRam_index])

        cfCard = get_memory_size(content[cfCard_index])

        return sdRam, cfCard

    mpu = "MPU"
    master = "(Master)"
    slave = "(Slave)"
    vmpu = "VMPU"
    for i in range(len(version)):
        if (
            mpu in version[i]
            and slave in version[i]
            or vmpu in version[i]
            and slave in version[i]
        ):
            sdRam, cfCard = get_memory_type(version[i:])
            slave_mpu.set_ram("{}G".format(sdRam))
            slave_mpu.set_cfCard("{}G".format(cfCard))

        if (
            mpu in version[i]
            and master in version[i]
            or vmpu in version[i]
            and master in version[i]
        ):
            sdRam, cfCard = get_memory_type(version[i : i + 16])
            master_mpu.set_ram("{}G".format(sdRam))
            master_mpu.set_cfCard("{}G".format(cfCard))

    next_software = "Next startup system software:"
    next_patch = "Next startup patch package:"
    for i in range(len(startup)):
        if "MainBoard" in startup[i]:
            for j in range(len(startup)):
                h = i + j
                if next_software in startup[h]:
                    master_mpu.set_version(startup[i + j].split("/")[-1])

                if next_patch in startup[h]:
                    master_mpu.set_patch(startup[i + j].split("/")[-1])

        if "SlaveBoard" in range(len(startup)):
            for j in range(len(startup) - i):
                h = i + j
                if next_software in startup[h]:
                    slave_mpu.set_version(startup[h].split("/")[-1])

                if next_patch in startup[h]:
                    slave_mpu.set_patch(startup[h].split("/")[-1])

    return master_mpu, slave_mpu


def get_memory_size(content: str):
    # round(int(content.split(":")[1].strip().split(" ")[0]) / 1000)
    new_content = delete_empty(content.split(":")[1].split(" "))[0]
    if new_content.isdigit():
        return round(int(new_content) / 1000)
    else:
        return round(int(new_content[:-1]) / 1000)


def get_model(content):
    version = content[Commands.displayVersion.value]
    model = ""

    for i in version[0:10]:
        if "uptime" in i:
            model = i.split(" ")[1].strip()
            break

    return model


def get_sfu(content):
    elabel = content[Commands.displayElabelBrief.value]
    sfu = Sfu()
    for item in elabel:
        data = delete_empty(item.split("  "))
        if "SFU" in data[0]:
            sfu.set_model(data[-1])
            break

    return sfu


def create_machines():
    path = "./app/files/"
    file = searchFiles(path)
    machines = []

    # for item in file[:4]:
    for item in file:
        content = readContent(item)
        try:
            hostname = get_hostname(item)
            print("current machine: {}".format(hostname))

            softwareVersion, lpusSlots = get_softwareVersion_and_lpu(content)
            lpus = get_LPU(content)
            masterMpu, slaveMpu = get_Mpus(content)
            model = get_model(content)
            sfu = get_sfu(content)

            new_machine = Equipo(
                hostname=hostname,
                softwareVersion=softwareVersion,
                model=model,
                totalLpu=lpusSlots,
                Lpus=lpus,
                masterMpu=masterMpu,
                slaveMpu=slaveMpu,
                sfu=sfu,
            )
            # new_machine.get_propertys()
            machines.append(new_machine)
        except Exception as err:
            print("item: {0} skipped -> {1}".format(item, err))

    return machines
