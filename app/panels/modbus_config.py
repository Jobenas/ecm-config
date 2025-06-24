import time
import wx


class ModbusConfigPanel(wx.ScrolledWindow):
    def __init__(self, parent, modbus_controller):
        super().__init__(parent)
        self.controller = modbus_controller

        # We'll store the list of rows for the modbus registers
        self.modbus_info = []

        # Additional combos:
        self.data_type_choices = [
            "char", "int", "float",
            "unsigned char", "unsigned int",
            "long", "unsigned long"
        ]
        self.cumulative_choices = ["instantanea", "acumulado"]

        # New combos for "Formato de Float" and "Tipo de Operación":
        self.float_format_choices = [
            "Little Endian",
            "Big Endian",
            "Little Endian Byte swapped",
            "Big Endian Byte swapped"
        ]
        self.op_type_choices = [
            "Average",
            "Max. Value",
            "Min. Value"
        ]

        # This will hold references to row controls for enabling/disabling, etc.
        self.row_controls = []

        self.init_ui()
        # Make it scrollable
        self.SetScrollRate(5, 5)

    def init_ui(self):
        # Main sizer for the scrolled window
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Set the scroll rate for the scrolled window
        self.SetScrollRate(10, 10)
        
        # Add title
        title_sizer = self.create_title(self, "Configuración de registros Modbus")
        main_sizer.Add(title_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # ====================
        #  CARD #1: Modbus Register Table
        # ====================
        regs_box = wx.StaticBox(self, label="Registros Modbus")
        regs_box_sizer = wx.StaticBoxSizer(regs_box, wx.VERTICAL)
        
        # 11 columns table
        self.table_sizer = wx.FlexGridSizer(rows=0, cols=11, hgap=5, vgap=5)
        self.table_sizer.AddGrowableCol(2)  # Let column #2 expand
        self.table_sizer.SetFlexibleDirection(wx.HORIZONTAL)

        # HEADERS ROW (11 columns)
        headers = [
            "Posición",
            "Habilitar",
            "Dir. Registro (HEX - 0x)",
            "Tipo de Dato",
            "Número de Bytes",
            "Frec. Muestreo",
            "Formato de Float",
            "Tipo Variable",
            "Dir. Esclavo",
            "Func. Code",
            "Tipo de Operación"
        ]
        for header in headers:
            header_text = wx.StaticText(self, label=header, style=wx.ALIGN_CENTER)
            self.table_sizer.Add(header_text, flag=wx.EXPAND | wx.ALL, border=5)
        
        # Add the table sizer to the box sizer
        regs_box_sizer.Add(self.table_sizer, 1, wx.EXPAND | wx.ALL, 5)
        
        # Add a divider
        divider = wx.StaticLine(self)
        regs_box_sizer.Add(divider, 0, wx.EXPAND | wx.ALL, 5)

        # Add buttons with proper alignment
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        regs_update_button = wx.Button(self, label="Actualizar Registros")
        regs_update_button.Bind(wx.EVT_BUTTON, self.on_save)
        button_sizer.Add(regs_update_button, 0, wx.ALL, 5)
        
        # Add the button sizer to the box sizer with right alignment
        button_sizer_container = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer_container.AddStretchSpacer()
        button_sizer_container.Add(button_sizer, 0, wx.ALL, 0)
        regs_box_sizer.Add(button_sizer_container, 0, wx.EXPAND | wx.ALL, 5)
        
        # Add the box sizer to the main sizer
        main_sizer.Add(regs_box_sizer, 1, wx.EXPAND | wx.ALL, 5)
        
        # Set the sizer for the scrolled window
        self.SetSizer(main_sizer)
        
        # Set minimum size for the window
        self.SetMinSize((1000, 600))
        
        # Force a layout update
        self.Layout()
        self.FitInside()

    def create_title(self, parent, title):
        # Create a simple sizer with the title text
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add((20, 0))  # left padding
        title_text = wx.StaticText(parent, label=title)
        title_text.SetFont(wx.Font(wx.FontInfo(12).Bold()))
        sizer.Add(title_text)
        return sizer

    # ====================
    #  CARD #1 METHODS
    # ====================

    def on_slave_update(self, event):
        """
        Called when the user clicks the “Actualizar” button in Card #1.
        We show a progress dialog, enter program mode, update the slave address,
        then exit program mode and show success/error.
        """
        new_addr_str = self.slave_address_ctrl.GetValue().strip()
        if not new_addr_str.isdigit():
            wx.MessageBox(
                "La dirección de slave debe ser un número entero.",
                "Error",
                wx.OK | wx.ICON_ERROR
            )
            return

        if self.controller.is_open():
            # 1) Show a small progress dialog (one-step process)
            dlg = wx.ProgressDialog(
                "Actualizando dirección del esclavo",
                "Por favor espere mientras se actualiza el equipo",
                maximum=1,
                parent=self,
                style=wx.PD_APP_MODAL | wx.PD_AUTO_HIDE
            )

            # 2) Enter Program Mode
            self.controller.send_command("AT+PROGMODE=1\r\n", False)
            time.sleep(0.5)
            self.controller.flush_buffer()

            # 3) Update the dialog text
            dlg.Update(0, "Enviando nueva dirección al equipo...")

            # 4) Send the new slave address command
            cmd = f"AT+MBADDR={new_addr_str}\r\n"
            response = self.controller.send_command(cmd)

            # 5) Exit Program Mode
            self.controller.send_command("AT+PROGMODE=0\r\n", False)

            # 6) Close the dialog
            dlg.Update(1, "Dirección del esclavo actualizada.")
            dlg.Destroy()

            # 7) Check response from device
            if response.strip() == "OK":
                wx.MessageBox(
                    "Dirección de slave actualizada correctamente.",
                    "Info",
                    wx.OK | wx.ICON_INFORMATION
                )
            else:
                wx.MessageBox(
                    f"Error actualizando dirección de slave.\nRespuesta del dispositivo: {response}",
                    "Error",
                    wx.OK | wx.ICON_ERROR
                )
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
        Creates rows for each entry in self.modbus_info,
        expecting 11 fields:
          [pos, enable, reg_addr, data_type, num_bytes, freq,
           float_format, cumulative_flag, slave_addr, func_code, op_type]
        Where float_format is a 4-value combo, and op_type is a 3-value combo.
        """
        for register in self.modbus_info:
            # 1) Position
            pos_txt = wx.StaticText(self, label=str(register["register_position"]))
            self.table_sizer.Add(pos_txt, flag=wx.EXPAND | wx.ALL, border=2)

            # 2) Enable
            en_chk = wx.CheckBox(self)
            en_chk.SetValue(bool(register["enable_flag"]))
            en_chk.Bind(wx.EVT_CHECKBOX, lambda evt, c=en_chk: self.on_enable_flag_change(evt, c))
            self.table_sizer.Add(en_chk, flag=wx.EXPAND | wx.ALL, border=2)

            # 3) Reg. Address (hex display)
            dec_val = int(register.get("modbus_register_address", 0))
            addr_hex = f"0x{dec_val:X}"
            addr_ctrl = wx.TextCtrl(self, value=addr_hex)
            self.table_sizer.Add(addr_ctrl, flag=wx.EXPAND | wx.ALL, border=2)

            # 4) Data type
            dt_combo = wx.ComboBox(self, choices=self.data_type_choices, style=wx.CB_READONLY)
            dt_idx = max(0, min(int(register.get("data_type", 1)) - 1, len(self.data_type_choices) - 1))
            dt_combo.SetSelection(dt_idx)
            self.table_sizer.Add(dt_combo, flag=wx.EXPAND | wx.ALL, border=2)

            # 5) Num bytes
            nb_ctrl = wx.TextCtrl(self, value=str(register.get("num_bytes", "0")))
            self.table_sizer.Add(nb_ctrl, flag=wx.EXPAND | wx.ALL, border=2)

            # 6) Sampling freq
            freq_ctrl = wx.TextCtrl(self, value=str(register.get("sampling_frequency", "0")))
            self.table_sizer.Add(freq_ctrl, flag=wx.EXPAND | wx.ALL, border=2)

            # 7) Formato de Float (4-value combo)
            float_val = int(register.get("float_format", 0))
            float_combo = wx.ComboBox(self, choices=self.float_format_choices, style=wx.CB_READONLY)
            # clamp index if needed
            if float_val < 0 or float_val >= len(self.float_format_choices):
                float_val = 0
            float_combo.SetSelection(float_val)
            self.table_sizer.Add(float_combo, flag=wx.EXPAND | wx.ALL, border=2)

            # 8) Cumulative / Tipo Variable
            cumu_val = int(register.get("cumulative_flag", 0))
            cumu_combo = wx.ComboBox(self, choices=self.cumulative_choices, style=wx.CB_READONLY)
            if cumu_val < 0 or cumu_val >= len(self.cumulative_choices):
                cumu_val = 0
            cumu_combo.SetSelection(cumu_val)
            self.table_sizer.Add(cumu_combo, flag=wx.EXPAND | wx.ALL, border=2)

            # 9) Slave Addr (decimal)
            slav_txt = wx.TextCtrl(self, value=str(register.get("slave_address", 0)))
            self.table_sizer.Add(slav_txt, flag=wx.EXPAND | wx.ALL, border=2)

            # 10) Function Code
            func_txt = wx.TextCtrl(self, value=str(register.get("function_code", 0)))
            self.table_sizer.Add(func_txt, flag=wx.EXPAND | wx.ALL, border=2)

            # 11) Tipo de Operación (3-value combo)
            op_val = int(register.get("op_type", 0))
            op_combo = wx.ComboBox(self, choices=self.op_type_choices, style=wx.CB_READONLY)
            if op_val < 0 or op_val >= len(self.op_type_choices):
                op_val = 0
            op_combo.SetSelection(op_val)
            self.table_sizer.Add(op_combo, flag=wx.EXPAND | wx.ALL, border=2)

            # Store references
            row_dict = {
                "position_text": pos_txt,
                "enable_checkbox": en_chk,
                "modbus_address": addr_ctrl,
                "data_type": dt_combo,
                "num_bytes": nb_ctrl,
                "sampling_frequency": freq_ctrl,
                "float_format": float_combo,  # new
                "cumulative_flag": cumu_combo,
                "slave_address": slav_txt,
                "function_code": func_txt,
                "op_type": op_combo           # new
            }
            self.row_controls.append(row_dict)

            # enable/disable row
            self.update_controls_state(row_dict, bool(register["enable_flag"]))

        self.Layout()

    def clear_data_rows(self):
        """Remove existing data-row widgets from the table_sizer, destroy them,
           and clear self.row_controls so we can repopulate fresh data."""
        for row_ctrls in self.row_controls:
            for widget in row_ctrls.values():
                self.table_sizer.Detach(widget)
                widget.Destroy()
        self.row_controls.clear()
        self.Layout()

    def on_enter(self):
        """Read your 20 rows from device or fallback if not open."""
        print("Inside the modbus config panel (on_enter)")

        self.modbus_info = []

        if self.controller.is_open():
            # We'll read the slave address, then the regs
            dlg = wx.ProgressDialog(
                "Leyendo parámetros",
                "Por favor espere mientras se realiza la lectura",
                maximum=2,  # two steps: slave address, then regs
                parent=self,
                style=wx.PD_APP_MODAL | wx.PD_AUTO_HIDE
            )
            self.controller.send_command("AT+PROGMODE=1\r\n", False)
            time.sleep(0.5)
            self.controller.flush_buffer()

            # ---- 1) Read the slave address
            dlg.Update(0, "Leyendo la dirección del esclavo...")
            slave_response = self.controller.send_command("AT+MBADDR?\r\n")
            # Store the slave address in the first row's slave address field if it exists
            slave_value = slave_response.strip().split("\r\n")[0]
            if not slave_value.isdigit():
                print(f"Unexpected slave address response: {slave_response}")
                slave_value = "1"  # Default to 1 if invalid

            dlg.Update(1, "Dirección del esclavo leída exitosamente...")
            self.default_slave_address = slave_value  # Store for later use

            # ---- 2) Read the register table
            regs_response = self.controller.send_command("AT+MBREGCFG?\r\n")
            dlg.Update(2, "Leyendo la configuración de registros Modbus...")

            lines = regs_response.strip().split("\n")
            print(f"Device returned {len(lines)} lines for MBREGCFG: {lines}")

            for line in lines:
                parts = line.split(",")
                if len(parts) < 11:
                    continue  # skip or handle malformed lines

                self.modbus_info.append({
                    "register_position": int(parts[0]),
                    "enable_flag": int(parts[1]),
                    "modbus_register_address": int(parts[2]),  # or keep as string if you prefer
                    "data_type": int(parts[3]),
                    "num_bytes": parts[4],
                    "sampling_frequency": parts[5],
                    "float_format": int(parts[6]),  # 0..3 (Little Endian, etc.)
                    "cumulative_flag": int(parts[7]),  # 0..1
                    "slave_address": int(parts[8]),
                    "function_code": int(parts[9]),
                    "op_type": int(parts[10])  # 0..2
                })

            dlg.Destroy()
            self.controller.send_command("AT+PROGMODE=0\r\n", False)
            time.sleep(0.5)
            self.controller.flush_buffer()
        else:
            # fallback example with 20 rows
            for i in range(20):
                self.modbus_info.append({
                    "register_position": i,
                    "enable_flag": 0,
                    "modbus_register_address": 0x100 + i,
                    "data_type": 1,
                    "num_bytes": 2,
                    "sampling_frequency": 60,
                    "float_format": 0,     # new 4-value combo
                    "cumulative_flag": 0,
                    "slave_address": 0,
                    "function_code": 0,
                    "op_type": 0          # new 3-value combo
                })

        self.clear_data_rows()
        self.populate_data_rows()

    def on_enable_flag_change(self, event, checkbox):
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
        The 'Actualizar Registros' button.
        Gathers row data, shows a progress dialog, enters program mode,
        sends each line to the device, then exits program mode.
        """
        if not self.controller.is_open():
            wx.MessageBox(
                "No se puede guardar la configuración.\n"
                "El puerto serial no está abierto.",
                "Error",
                wx.OK | wx.ICON_ERROR
            )
            return

        # Gather rows
        rows_for_sending = []
        for row in self.row_controls:
            line = self.extract_data_from_row(row)
            rows_for_sending.append(line)

        if not rows_for_sending:
            wx.MessageBox("No hay filas para guardar.", "Info", wx.OK | wx.ICON_INFORMATION)
            return

        # 1) Show a progress dialog
        total_rows = len(rows_for_sending)
        dlg = wx.ProgressDialog(
            "Guardando parámetros",
            "Por favor espere mientras se envía la configuración...",
            maximum=total_rows,
            parent=self,
            style=wx.PD_APP_MODAL | wx.PD_AUTO_HIDE
        )

        # 2) Enter program mode
        self.controller.send_command("AT+PROGMODE=1\r\n", False)
        time.sleep(0.5)
        self.controller.flush_buffer()

        # 3) Send each line
        for i, row_str in enumerate(rows_for_sending, start=1):
            register_position = row_str.split(",")[0]
            dialog_msg = f"Guardando registro #{register_position}..."
            dlg.Update(i - 1, dialog_msg)

            cmd = f"AT+MBREGCFG={row_str}\r\n"
            response = self.controller.send_command(cmd)
            print(f"Sent: {cmd.strip()}, Received: {response.strip()}")

            time.sleep(0.3)  # optional delay between commands
            if response.strip() != "OK":
                # Error, close dialog and revert program mode
                dlg.Destroy()
                self.controller.send_command("AT+PROGMODE=0\r\n", False)
                wx.MessageBox(
                    f"Error al guardar registro {register_position}.\n"
                    f"Respuesta del dispositivo: {response}",
                    "Error",
                    wx.OK | wx.ICON_ERROR
                )
                return

        # 4) Exit program mode
        self.controller.send_command("AT+PROGMODE=0\r\n", False)

        # 5) Mark final step complete
        dlg.Update(total_rows, "Todos los registros han sido enviados...")
        dlg.Destroy()

        wx.MessageBox(
            "Todos los parámetros han sido enviados correctamente.",
            "Info",
            wx.OK | wx.ICON_INFORMATION
        )

    def extract_data_from_row(self, row):
        """
        Builds an 11-value comma-separated string:
        [position, enable_flag, address(hex), data_type_index,
         num_bytes, sampling_frequency, float_format_value,
         cumulative_flag, slave_address, function_code, op_type_value]

        Here we specifically convert the modbus address to a hex string (0xNNN).
        """
        # 1) Position
        pos_val = int(row["position_text"].GetLabel())

        # 2) Enable
        en_val = 1 if row["enable_checkbox"].GetValue() else 0

        # 3) Address from text ctrl (like '0x1A'), ensure final line is hex
        addr_str = row["modbus_address"].GetValue().strip().lower().replace("0x", "")
        try:
            addr_dec = int(addr_str, 16)
        except ValueError:
            addr_dec = 0

        # We re-create it as e.g. "0x160"
        addr_hex = f"0x{addr_dec:X}"

        # 4) data_type
        dt_str = row["data_type"].GetValue()
        dt_idx = 0
        if dt_str in self.data_type_choices:
            dt_idx = self.data_type_choices.index(dt_str) + 1

        # 5) num_bytes
        nb_val = row["num_bytes"].GetValue().strip()
        try:
            nb_int = int(nb_val)
        except ValueError:
            nb_int = 0

        # 6) sampling_frequency
        freq_val = row["sampling_frequency"].GetValue().strip()
        try:
            freq_int = int(freq_val)
        except ValueError:
            freq_int = 0

        # 7) float_format
        ff_str = row["float_format"].GetValue()
        ff_idx = 0
        if ff_str in self.float_format_choices:
            ff_idx = self.float_format_choices.index(ff_str)

        # 8) cumulative_flag
        cumu_str = row["cumulative_flag"].GetValue()
        if cumu_str in self.cumulative_choices:
            cumu_idx = self.cumulative_choices.index(cumu_str)
        else:
            cumu_idx = 0

        # 9) slave_address
        slav_val = row["slave_address"].GetValue().strip()
        try:
            slav_int = int(slav_val)
        except ValueError:
            slav_int = 0

        # 10) function_code
        func_val = row["function_code"].GetValue().strip()
        try:
            func_int = int(func_val)
        except ValueError:
            func_int = 0

        # 11) op_type
        op_str = row["op_type"].GetValue()
        op_idx = 0
        if op_str in self.op_type_choices:
            op_idx = self.op_type_choices.index(op_str)

        # Build the line with hex address:
        line = (
            f"{pos_val},"  # pos
            f"{en_val},"  # enable
            f"{addr_hex},"  # e.g. "0x160"
            f"{dt_idx},"
            f"{nb_int},"
            f"{freq_int},"
            f"{ff_idx},"
            f"{cumu_idx},"
            f"{slav_int},"
            f"{func_int},"
            f"{op_idx}"
        )
        return line
