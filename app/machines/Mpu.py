class Mpu:
    def __init__(self, ram="", cfCard="", version="", patch="", model=""):
        self.ram = ram
        self.cfCard = cfCard
        self.version = version
        self.patch = patch
        self.model = model

    def set_model(self, new_model):
        self.model = new_model

    def set_ram(self, new_ram):
        self.ram = new_ram

    def set_cfCard(self, new_cfCard):
        self.cfCard = new_cfCard

    def set_version(self, new_version):
        self.version = new_version

    def set_patch(self, new_patch):
        self.patch = new_patch

    def get_propertys(self):
        propertys = [self.model, self.ram, self.cfCard, self.version, self.patch]
        return propertys

    def get_ram(self):
        return self.ram

    def get_cfCard(self):
        return self.cfCard

    def get_version(self):
        return self.version

    def get_patch(self):
        return self.patch

    def get_model(self):
        return self.model
