from app.machines.Pic import Pic


class Lpu:
    def __init__(
        self,
        lpuName: str,
        lpuModel: str,
        pic0=Pic(),
        pic1=Pic(),
    ):
        self.pic0 = pic0
        self.pic1 = pic1
        self.lpuName = lpuName
        self.lpuModel = lpuModel

    def get_propertys(self):
        propertys = [
            self.lpuName,
            self.lpuModel,
            self.pic0,
            self.pic1,
        ]

        return propertys

    def get_model(self):
        return self.lpuModel

    def get_pic0(self):
        return self.pic0

    def get_pic1(self):
        return self.pic1

    def get_name(self):
        return self.lpuName

    def set_pic0(self, new_pic: Pic):
        self.pic0 = new_pic

    def set_pic1(self, new_pic: Pic):
        self.pic1 = new_pic

    def print_bonito(self):
        nombre = "{0}: {1}\n".format(self.lpuName, self.lpuModel)
        pic0 = "\tpic0: {0}\n".format(self.pic0)
        pic1 = "\tpic1: {0}\n".format(self.pic1)

        return nombre + pic0 + pic1
