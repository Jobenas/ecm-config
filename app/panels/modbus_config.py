import time
import wx


class ModbusConfigPanel(wx.ScrolledWindow):
    def __init__(self, parent, modbus_controller):
        super().__init__(parent)
        self.controller = modbus_controller

        # We'll store an address for the slave, e.g., "1"
        self.slave_address_value = ""

        # We'll store the list of rows for the modbus registers
        self.modbus_info = []

        self.data_type_choices = [
            "char", "int", "float",
            "unsigned char", "unsigned int",
            "long", "unsigned long"
        ]
        self.cumulative_choices = ["instantanea", "acumulado"]

        # This will hold references to row controls for enabling/disabling, etc.
        self.row_controls = []

        self.init_ui()
        # Make it scrollable
        self.SetScrollRate(5, 5)

    def init_ui(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # ----- Title -----
        main_sizer.Add(
            self.create_title("Configuración de registros Modbus"),
            flag=wx.EXPAND | wx.ALL,
            border=5
        )

        # ====================
        #  CARD #1: Slave Address
        # ====================
        slave_box = wx.StaticBox(self, label="Dirección de Slave Modbus")
        slave_box_sizer = wx.StaticBoxSizer(slave_box, wx.VERTICAL)

        # We'll place the label, textctrl, and "Actualizar" horizontally
        slave_hsizer = wx.BoxSizer(wx.HORIZONTAL)

        slave_label = wx.StaticText(self, label="Dirección de slave:")
        slave_hsizer.Add(slave_label, flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=5)

        # TextCtrl to hold the slave address
        self.slave_address_ctrl = wx.TextCtrl(self, value=self.slave_address_value, size=(60, -1))
        slave_hsizer.Add(self.slave_address_ctrl, flag=wx.RIGHT, border=10)

        # Button for updating the slave address
        slave_update_btn = wx.Button(self, label="Actualizar")
        slave_update_btn.Bind(wx.EVT_BUTTON, self.on_slave_update)
        slave_hsizer.Add(slave_update_btn, flag=wx.LEFT, border=5)

        slave_box_sizer.Add(slave_hsizer, flag=wx.ALL, border=10)

        # Add the entire "Card #1" to the main_sizer
        main_sizer.Add(slave_box_sizer, flag=wx.EXPAND | wx.ALL, border=5)

        # ====================
        #  CARD #2: Modbus Register Table
        # ====================
        regs_box = wx.StaticBox(self, label="Registros Modbus")
        regs_box_sizer = wx.StaticBoxSizer(regs_box, wx.VERTICAL)

        # Inside this card, we have the table (headers + data rows).
        # Create a FlexGridSizer for table
        self.table_sizer = wx.FlexGridSizer(rows=0, cols=8, hgap=5, vgap=5)
        self.table_sizer.AddGrowableCol(2)  # Let column #2 expand if needed
        self.table_sizer.SetFlexibleDirection(wx.HORIZONTAL)

        # HEADERS ROW
        headers = [
            "Posición",
            "Habilitar",
            "Dir. Registro (HEX - 0x)",
            "Tipo de Dato",
            "Número de Bytes",
            "Frec. Muestreo",
            "Posiciones Decimales",
            "Tipo Variable"
        ]
        for header in headers:
            header_text = wx.StaticText(self, label=header, style=wx.ALIGN_CENTER)
            self.table_sizer.Add(header_text, flag=wx.EXPAND | wx.ALL, border=5)

        # Add the table sizer to the regs_box_sizer
        regs_box_sizer.Add(self.table_sizer, flag=wx.EXPAND | wx.ALL, border=5)

        # Horizontal line (optional)
        divider = wx.StaticLine(self)
        regs_box_sizer.Add(divider, flag=wx.EXPAND | wx.ALL, border=5)

        # Table data rows get populated dynamically (see populate_data_rows()).

        # Buttons for the register table
        regs_button_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # The existing “Actualizar” button for the register config
        regs_update_button = wx.Button(self, label="Actualizar Registros")
        regs_update_button.Bind(wx.EVT_BUTTON, self.on_save)
        regs_button_sizer.Add(regs_update_button, flag=wx.ALIGN_CENTER | wx.ALL, border=5)

        regs_box_sizer.Add(regs_button_sizer, flag=wx.ALIGN_RIGHT | wx.ALL, border=5)

        # Add the “Card #2” box to the main_sizer
        main_sizer.Add(regs_box_sizer, flag=wx.EXPAND | wx.ALL, border=5)

        self.SetSizer(main_sizer)

    def create_title(self, title):
        title_text = wx.StaticText(self, label=title)
        title_text.SetFont(wx.Font(wx.FontInfo(12).Bold()))

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add((20, 0))  # left padding
        sizer.Add(title_text)

        v_sizer = wx.BoxSizer(wx.VERTICAL)
        v_sizer.Add((0, 20))  # top padding
        v_sizer.Add(sizer)

        return v_sizer

    # ====================
    #  CARD #1 METHODS
    # ====================

    def on_slave_update(self, event):
        """
        Called when the user clicks the “Actualizar” button in Card #1.
        Here you can send the new slave address to the device, e.g.
        AT+MBADDR=<value>
        """
        new_addr_str = self.slave_address_ctrl.GetValue().strip()
        if not new_addr_str.isdigit():
            wx.MessageBox("La dirección de slave debe ser un número entero.", "Error", wx.OK | wx.ICON_ERROR)
            return

        # Optionally send to device, e.g.:
        if self.controller.is_open():
            self.controller.send_command("AT+PROGMODE=1\r\n", False)
            cmd = f"AT+MBADDR={new_addr_str}\r\n"
            response = self.controller.send_command(cmd)
            self.controller.send_command("AT+PROGMODE=0\r\n", False)
            if response.strip() == "OK":
                wx.MessageBox("Dirección de slave actualizada correctamente.", "Info", wx.OK | wx.ICON_INFORMATION)
            else:
                wx.MessageBox(f"Error actualizando dirección de slave.\nRespuesta: {response}",
                              "Error",
                              wx.OK | wx.ICON_ERROR)
        else:
            wx.MessageBox(
                "No se puede actualizar la dirección de slave.\nEl puerto serial no está abierto.",
                "Error",
                wx.OK | wx.ICON_ERROR
            )

    # ====================
    #  CARD #2 METHODS
    # ====================

    def populate_data_rows(self):
        """
        Creates the table rows for each entry in self.modbus_info,
        showing the register address in hex form (e.g. 0x64).
        """
        for register in self.modbus_info:
            # 1) Position
            position_text = wx.StaticText(self, label=str(register["register_position"]))
            self.table_sizer.Add(position_text, flag=wx.EXPAND | wx.ALL, border=2)

            # 2) Enable Flag
            enable_checkbox = wx.CheckBox(self)
            enable_checkbox.SetValue(bool(register["enable_flag"]))
            enable_checkbox.Bind(
                wx.EVT_CHECKBOX,
                lambda evt, c=enable_checkbox: self.on_enable_flag_change(evt, c)
            )
            self.table_sizer.Add(enable_checkbox, flag=wx.EXPAND | wx.ALL, border=2)

            # 3) Modbus Address (shown as hex)
            addr_dec = 0
            try:
                # If your data is stored as a string with decimal:
                addr_dec = int(register["modbus_register_address"])
            except ValueError:
                addr_dec = 0
            addr_hex_str = f"0x{addr_dec:X}"  # e.g. 0x64 if decimal is 100

            modbus_address_ctrl = wx.TextCtrl(self, value=addr_hex_str)
            self.table_sizer.Add(modbus_address_ctrl, flag=wx.EXPAND | wx.ALL, border=2)

            # 4) Data type
            data_type = wx.ComboBox(self, choices=self.data_type_choices, style=wx.CB_READONLY)
            data_type_idx = max(
                0,
                min(register["data_type"] - 1, len(self.data_type_choices) - 1)
            )
            data_type.SetSelection(data_type_idx)
            self.table_sizer.Add(data_type, flag=wx.EXPAND | wx.ALL, border=2)

            # 5) Num bytes
            num_bytes = wx.TextCtrl(self, value=str(register["num_bytes"]))
            self.table_sizer.Add(num_bytes, flag=wx.EXPAND | wx.ALL, border=2)

            # 6) Sampling frequency
            sampling_frequency = wx.TextCtrl(self, value=str(register["sampling_frequency"]))
            self.table_sizer.Add(sampling_frequency, flag=wx.EXPAND | wx.ALL, border=2)

            # 7) Decimal positions
            decimal_positions = wx.TextCtrl(self, value=str(register["decimal_positions"]))
            self.table_sizer.Add(decimal_positions, flag=wx.EXPAND | wx.ALL, border=2)

            # 8) Cumulative flag
            cumu_choice_idx = max(
                0,
                min(register["cumulative_flag"], len(self.cumulative_choices) - 1)
            )
            cumulative_flag = wx.ComboBox(self, choices=self.cumulative_choices, style=wx.CB_READONLY)
            cumulative_flag.SetSelection(cumu_choice_idx)
            self.table_sizer.Add(cumulative_flag, flag=wx.EXPAND | wx.ALL, border=2)

            # Store references
            controls_for_this_row = {
                "position_text": position_text,
                "enable_checkbox": enable_checkbox,
                "modbus_address": modbus_address_ctrl,  # now has hex
                "data_type": data_type,
                "num_bytes": num_bytes,
                "sampling_frequency": sampling_frequency,
                "decimal_positions": decimal_positions,
                "cumulative_flag": cumulative_flag
            }
            self.row_controls.append(controls_for_this_row)

            # enable/disable
            self.update_controls_state(controls_for_this_row, bool(register["enable_flag"]))

        self.Layout()

    def clear_data_rows(self):
        """
        Remove existing data-row widgets from self.table_sizer, destroy them,
        and clear self.row_controls so we can repopulate fresh data.
        """
        for row_ctrls in self.row_controls:
            for widget in row_ctrls.values():
                self.table_sizer.Detach(widget)
                widget.Destroy()
        self.row_controls.clear()
        self.Layout()

    def on_enter(self):
        """
        Called when this panel becomes the selected tab in the notebook.
        Re-read modbus_info and show them in hex form in the address field.
        """
        print("Inside the modbus config panel")
        self.modbus_info = []

        if self.controller.is_open():
            self.controller.send_command("AT+PROGMODE=1\r\n", False)
            dlg = wx.ProgressDialog(
                "Leyendo parámetros",
                "Por favor espere mientras se realiza la lectura",
                maximum=2,
                parent=self,
                style=wx.PD_APP_MODAL | wx.PD_AUTO_HIDE
            )
            time.sleep(0.5)  # optional delay
            self.controller.flush_buffer()

            modbus_slave_addr = self.controller.send_command("AT+MBADDR?\r\n")
            dlg.Update(1, "Leyendo la dirección del Esclavo Modbus...")
            print(f"Received Modbus Slave Address: {modbus_slave_addr}")
            self.slave_address_ctrl.SetValue(modbus_slave_addr.split("\r\n")[0])

            modbus_reg_data = self.controller.send_command("AT+MBREGCFG?\r\n")
            print(f"Received Modbus Reg Data: {modbus_reg_data}")
            dlg.Update(2, "Leyendo la configuración Registros Modbus...")
            modbus_reg_data_array = modbus_reg_data.split("\r\n")
            print(f"Modbus Reg Data: {modbus_reg_data_array}")

            for item in modbus_reg_data_array:
                if item:
                    parts = item.split(",")
                    self.modbus_info.append({
                        "register_position": int(parts[0]),
                        "enable_flag": int(parts[1]),
                        "modbus_register_address": parts[2],  # decimal (string), we'll show as hex
                        "data_type": int(parts[3]),
                        "num_bytes": parts[4],
                        "sampling_frequency": parts[5],
                        "decimal_positions": parts[6],
                        "cumulative_flag": int(parts[7]),
                    })

            self.clear_data_rows()
            self.populate_data_rows()

            dlg.Destroy()
            self.controller.send_command("AT+PROGMODE=0\r\n", False)
        else:
            # fallback or demo data
            for i in range(10):
                self.modbus_info.append({
                    "register_position": i,
                    "enable_flag": 0,
                    "modbus_register_address": "0x00",  # e.g. "0", "10", ...
                    "data_type": 1,
                    "num_bytes": "0",
                    "sampling_frequency": "0",
                    "decimal_positions": "0",
                    "cumulative_flag": 0
                })
            self.clear_data_rows()
            self.populate_data_rows()

            wx.MessageBox(
                "No se puede leer la configuración de registros Modbus.\n"
                "El puerto serial no está abierto.",
                "Error",
                wx.OK | wx.ICON_ERROR
            )

    def on_enable_flag_change(self, event, checkbox):
        """
        If user toggles the checkbox, we enable or disable the row's controls.
        """
        is_enabled = event.IsChecked()
        for row in self.row_controls:
            if row["enable_checkbox"] is checkbox:
                self.update_controls_state(row, is_enabled)
                break

    def update_controls_state(self, controls_dict, is_enabled):
        for key, ctrl in controls_dict.items():
            if key == "enable_checkbox":
                continue
            ctrl.Enable(is_enabled)

    def on_save(self, event):
        """
        The 'Actualizar Registros' button. Gathers row data and sends to device.
        """
        if not self.controller.is_open():
            wx.MessageBox(
                "No se puede guardar la configuración.\n"
                "El puerto serial está cerrado.",
                "Error",
                wx.OK | wx.ICON_ERROR
            )
            return

        rows_for_sending = []
        for row in self.row_controls:
            line = self.extract_data_from_row(row)
            print(f"Row data: {line}")
            rows_for_sending.append(line)

        if not rows_for_sending:
            wx.MessageBox("No hay filas para guardar.", "Info", wx.OK | wx.ICON_INFORMATION)
            return

        total_rows = len(rows_for_sending)
        dialog = wx.ProgressDialog(
            "Guardando parámetros",
            "En proceso...",
            maximum=total_rows,
            parent=self,
            style=wx.PD_APP_MODAL | wx.PD_AUTO_HIDE | wx.PD_SMOOTH
        )

        self.controller.send_command("AT+PROGMODE=1\r\n", False)

        for i, row_str in enumerate(rows_for_sending, start=1):
            register_position = row_str.split(",")[0]
            dialog_msg = f"Guardando parámetros para el registro {register_position}..."
            dialog.Update(i, dialog_msg)

            cmd = f"AT+MBREGCFG={row_str}\r\n"
            response = self.controller.send_command(cmd)
            print(f"Sent: {cmd.strip()}, Received: {response.strip()}")
            time.sleep(0.5)  # optional delay

            if response.strip() != "OK":
                wx.MessageBox(
                    f"Error al guardar registro {register_position}.\n"
                    f"Respuesta del dispositivo: {response}",
                    "Error",
                    wx.OK | wx.ICON_ERROR
                )
                dialog.Destroy()
                self.controller.send_command("AT+PROGMODE=0\r\n", False)
                return

        self.controller.send_command("AT+PROGMODE=0\r\n", False)
        dialog.Destroy()

        wx.MessageBox(
            "Todos los parámetros han sido enviados correctamente.",
            "Info",
            wx.OK | wx.ICON_INFORMATION
        )

    def extract_data_from_row(self, row: dict) -> str:
        """
        Builds a comma-separated string from the row widgets, removing
        the '0x' prefix and sending the decimal integer instead.

        e.g., if the user typed '0x160', we parse it as hex (352),
        then store '352' in the final CSV line.
        """
        # 1) register_position
        register_position = int(row["position_text"].GetLabel())

        # 2) enable_flag
        enable_flag = 1 if row["enable_checkbox"].GetValue() else 0

        # 3) modbus_register_address
        addr_str = row["modbus_address"].GetValue().strip()
        # remove the 0x prefix if present
        addr_str = addr_str.replace("0x", "").replace("0X", "")

        modbus_register_address_str = addr_str

        # 4) data_type
        data_type_str = row["data_type"].GetValue()
        if data_type_str in self.data_type_choices:
            data_type_index = self.data_type_choices.index(data_type_str) + 1
        else:
            data_type_index = 0

        # 5) num_bytes
        num_bytes_str = row["num_bytes"].GetValue()
        try:
            num_bytes_int = int(num_bytes_str)
        except ValueError:
            num_bytes_int = 0
        num_bytes = str(num_bytes_int)

        # 6) sampling_frequency
        sampling_freq_str = row["sampling_frequency"].GetValue()
        try:
            sampling_freq_int = int(sampling_freq_str)
        except ValueError:
            sampling_freq_int = 0
        sampling_frequency = str(sampling_freq_int)

        # 7) decimal_positions
        decimal_str = row["decimal_positions"].GetValue()
        try:
            decimal_int = int(decimal_str)
        except ValueError:
            decimal_int = 0
        decimal_positions = str(decimal_int)

        # 8) cumulative_flag
        cumu_str = row["cumulative_flag"].GetValue()
        if cumu_str in self.cumulative_choices:
            cumu_choice_idx = self.cumulative_choices.index(cumu_str)
        else:
            cumu_choice_idx = 0

        # Build the line with the *decimal* register address (no '0x')
        line = (
            f"{register_position},"
            f"{enable_flag},"
            f"{modbus_register_address_str},"
            f"{data_type_index},"
            f"{num_bytes},"
            f"{sampling_frequency},"
            f"{decimal_positions},"
            f"{cumu_choice_idx}"
        )
        return line
