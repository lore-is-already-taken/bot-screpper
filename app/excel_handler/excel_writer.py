import xlsxwriter

import app.excel_handler.styles as exel_style
from app.excel_handler.log_manager import create_machines


def create_header(header_first_row, header_last_row, workSheet, header_format):
    # this creates the first headers
    headers = ["WORK", "NODO", "HOSTNAME", "LAYER"]
    for i in range(len(headers)):
        workSheet.merge_range(
            first_row=header_first_row,
            last_row=header_last_row,
            first_col=i,
            last_col=i,
            data=headers[i],
            cell_format=header_format,
        )

    # creates header for the current state of the machine
    workSheet.merge_range(
        first_row=header_first_row,
        last_row=header_first_row,
        first_col=len(headers) + 1,
        last_col=len(headers) + 5,
        data="CURRENT",
        cell_format=header_format,
    )

    # create header for the new state of the machine
    workSheet.merge_range(
        first_row=header_first_row,
        last_row=header_first_row,
        first_col=len(headers) * 2 + 2,
        last_col=len(headers) * 2 + 6,
        data="NEW",
        cell_format=header_format,
    )

    # since the headers of 'current' and 'new' are the same
    # this write the same information on each.
    descriptions = ["QTY Used", "MXM QTY", "BW", "LPU", "PIC"]
    for i in range(len(headers) + 1, len(headers) + len(descriptions) + 1):
        # current section
        workSheet.write(
            header_last_row, i, descriptions[i - (len(headers) + 1)], header_format
        )
        # new section
        workSheet.write(
            header_last_row,
            i + len(headers) + 1,
            descriptions[i - (len(headers) + 1)],
            header_format,
        )

    # the machine description like ram memory, software version, etc.
    machine_description = [
        "NODOS/KIT UPGRADE",
        "RAM MEMORY SIZE",
        "CFCARD SIZE",
        "VERSION AND PATCH",
    ]
    for i in range(len(machine_description)):
        workSheet.merge_range(
            first_row=header_first_row,
            last_row=header_last_row,
            first_col=i + 17,
            last_col=i + 17,
            data=machine_description[i],
            cell_format=header_format,
        )


def write():
    machines = create_machines()
    workbook = xlsxwriter.Workbook("ensayo.xlsx")

    workSheet = workbook.add_worksheet()

    header_format = workbook.add_format(exel_style.headers_style)
    lpu_slot_format = workbook.add_format(exel_style.slot_number_format)
    lpu_format = workbook.add_format(exel_style.lpu)
    nodo_format = workbook.add_format(exel_style.nodo_format_config)

    # setting the first row of the header
    header_first_row = 2
    header_last_row = 3

    # create main headers
    create_header(header_first_row, header_last_row, workSheet, header_format)

    row = 6
    initial_col = 2
    last_current_machine_column = 10

    for i in range(len(machines)):
        slots = machines[i].get_total_lpus()
        hostname = machines[i].get_hostname()
        lpu_list = machines[i].list_lpus()
        layer = machines[i].get_layer()
        model = machines[i].get_model()
        sfu = machines[i].get_sfu().get_model()

        master_ram = machines[i].get_masterMpu().get_ram()
        master_model = machines[i].get_masterMpu().get_model()
        slave_ram = machines[i].get_slaveMpu().get_ram()

        master_cfCard = machines[i].get_masterMpu().get_cfCard()
        slave_cfCard = machines[i].get_slaveMpu().get_cfCard()

        master_version = machines[i].get_masterMpu().get_version()
        master_patch = machines[i].get_masterMpu().get_patch()

        new_range = row

        for i in range(new_range, new_range + slots * 2, 1):
            if i - new_range == 0:
                workSheet.write(
                    row, 17, "{0} / {1} / {2}".format(model, master_model, sfu)
                )
                workSheet.write(row, 18, "{0}/{1}".format(master_ram, slave_ram))

                workSheet.write(row, 19, "{0}/{1}".format(master_cfCard, slave_cfCard))

                workSheet.write(row, 20, "{0}/{1}".format(master_version, master_patch))

            for col in range(initial_col, last_current_machine_column, 1):
                current_slot = int((i - new_range) / 2)
                if col == initial_col:
                    # this is writting the hostname
                    nodo_name = "desconocido"
                    workSheet.write(i, col, hostname)
                    workSheet.write(
                        i,
                        col - 1,
                        nodo_name,
                        nodo_format,
                    )

                elif col == initial_col + 1:
                    # this is writing the layer
                    workSheet.write(i, col, layer)

                elif col == initial_col + 2 and i % 2 == 0:
                    # this is just the lpu number
                    # is for easy identification de slot number
                    workSheet.merge_range(
                        first_row=i,
                        last_row=i + 1,
                        first_col=col,
                        last_col=col,
                        data=current_slot + 1,
                        cell_format=lpu_slot_format,
                    )

                elif col == initial_col + 3:
                    if i % 2 == 0:
                        value = lpu_list[current_slot].get_pic0().get_total_used_ports()
                        data = "---" if value == 0 else value
                        bw = lpu_list[current_slot].get_pic0().get_bw()
                        total_ports = lpu_list[current_slot].get_pic0().get_max_port()

                        # current
                        # data is the total ports used on [slot][pic]
                        workSheet.write(i, col, data)
                        # write total ports
                        workSheet.write(i, col + 1, total_ports)

                        # bw is the band width, can be 100Gb, 10Gb, 1Gb.
                        # it is written in the same iteracion
                        # for performance purposes
                        workSheet.write(i, initial_col + 5, bw)

                    else:
                        bw = lpu_list[current_slot].get_pic1().get_bw()
                        value = lpu_list[current_slot].get_pic1().get_total_used_ports()
                        data = "---" if value == 0 else value
                        total_ports = lpu_list[current_slot].get_pic1().get_max_port()

                        workSheet.write(i, col, data)
                        # write total ports
                        workSheet.write(i, col + 1, total_ports)
                        workSheet.write(i, initial_col + 5, bw)

                elif col == initial_col + 6 and i % 2 == 0:
                    # this write the lpu model, and merge two rows
                    # this again for pic identification
                    workSheet.merge_range(
                        first_row=i,
                        last_row=i + 1,
                        first_col=col,
                        last_col=col,
                        data="---"
                        if lpu_list[current_slot].get_model() == "0"
                        else lpu_list[current_slot].get_model(),
                        cell_format=lpu_format,
                    )

                elif col == initial_col + 7:
                    # writting pics models
                    if i % 2 == 0:
                        value = lpu_list[current_slot].get_pic0().get_name()
                        data = "---" if value == 0 else value
                        workSheet.write(i, col, data)

                    else:
                        value = lpu_list[current_slot].get_pic1().get_name()
                        data = "---" if value == 0 else value
                        workSheet.write(i, col, data)

            row = row + 1
        row = row + 2

    workbook.close()


if __name__ == "__main__":
    write()
