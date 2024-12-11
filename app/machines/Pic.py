class Pic:
    def __init__(
        self,
        picName: str = "---",
        ports: int = 0,
        bw: str = "",
        max_port: str = "---",
    ):
        self.picName = picName
        self.ports = ports
        self.bw = bw
        self.max_port = max_port

    def get_total_used_ports(self) -> int:
        return self.ports

    def set_max_port(self, ports: str):
        self.max_port = ports

    def get_max_port(self):
        return self.max_port

    def get_resume(self):
        return [self.picName, self.get_total_used_ports(), self.get_max_port()]

    def get_ports(self):
        return self.ports

    def add_port(self):
        self.ports += 1

    def set_name(self, name: str):
        self.picName = name

    def get_name(self):
        return self.picName

    def set_bw(self, bw):
        self.bw = bw

    def get_bw(self):
        return self.bw
