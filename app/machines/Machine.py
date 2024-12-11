from app.machines.Lpus import Lpu
from app.machines.Mpu import Mpu
from app.machines.Sfu import Sfu
from typing import List


def generar_lpu(totalSlots: int, slotsOcupados: List[Lpu]):
    fixed_array = []
    count = 0
    delay = 0

    while count < totalSlots:
        if count - delay < len(slotsOcupados):
            number = int(slotsOcupados[count - delay].get_name().split(" ")[1])

            if number == count + 1:
                fixed_array.append(slotsOcupados[count - delay])
                count += 1

            else:
                empty_lpu = Lpu(lpuName="0", lpuModel="0")
                fixed_array.append(empty_lpu)
                count += 1
                delay += 1

        else:
            empty_lpu = Lpu(lpuName="0", lpuModel="0")
            fixed_array.append(empty_lpu)
            count += 1

    return fixed_array


def get_layer(hostname: str):
    layer = ""
    if "PE" in hostname:
        layer = ("HL4",)
    elif "NB in hostname":
        layer = "HL3"
    return layer


class Equipo:
    def __init__(
        self,
        hostname: str = "",
        softwareVersion: str = "",
        model: str = "",
        totalLpu: int = 0,
        Lpus: List[Lpu] = [],
        masterMpu: Mpu = Mpu(),
        slaveMpu: Mpu = Mpu(),
        sfu: Sfu = Sfu(),
    ):
        self.hostname = hostname
        self.softwareVersion = softwareVersion
        self.totalLpu = int(totalLpu)
        self.Lpus = generar_lpu(self.totalLpu, Lpus)
        self.layer = "HL4" if "PE" in hostname else "HL3"
        self.masterMpu = masterMpu
        self.slaveMpu = slaveMpu
        self.model = model
        self.sfu = sfu

    def get_slaveMpu(self):
        return self.slaveMpu

    def get_masterMpu(self):
        return self.masterMpu

    def get_sfu(self):
        return self.sfu

    def set_sfu(self, new_sfu):
        self.sfu = new_sfu

    def get_propertys(self):
        print("Hostname: {}".format(self.hostname))
        print("Model: {}".format(self.model))
        print("software Version: {}".format(self.softwareVersion))
        print("slots disponibles: {}".format(self.totalLpu))
        print("lpus Info: ")
        for lpu in self.Lpus:
            print("\t", lpu.get_propertys())
        print("Master Mpu: {}".format(self.masterMpu.get_propertys()))
        print("Slave Mpu: {}".format(self.slaveMpu.get_propertys()))
        print("Sfu: {}".format(self.sfu.get_model()))

    def get_layer(self):
        return self.layer

    def get_model(self):
        return self.model

    def get_lpu(self, index: int):
        if self.Lpus[index] and index >= len(self.Lpus):
            return self.Lpus[index].get_properctys()
        else:
            return "no exist lpu in position {}".format(index)

    def getLpuModels(self):
        return [item.get_model() for item in self.Lpus]

    def list_lpus(self):
        return [item for item in self.Lpus]

    def get_hostname(self):
        return self.hostname

    def get_total_lpus(self):
        return self.totalLpu

    def get_softwareVersion(self):
        return self.softwareVersion
