import time

import wx


class ModbusConfigPanel(wx.ScrolledWindow):
    def __init__(self, parent, modbus_controller):
        super().__init__(parent)
        self.controller = modbus_controller

        # We'll start with an empty modbus_info; you can populate it later
        self.modbus_info = []

        self.data_type_choices = [
            "char", "int", "float",
            "unsigned char", "unsigned int",
            "long", "unsigned long"
        ]
        self.cumulative_choices = ["instantanea", "acumulado"]

        # This will hold references to all controls for enabling/disabling, etc.
        # Each element of row_controls is a dict representing one row's widgets.
        self.row_controls = []

        self.init_ui()
        self.SetScrollRate(5, 5)

    def init_ui(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Title
        main_sizer.Add(
            self.create_title("Configuración de registros Modbus"),
            flag=wx.EXPAND | wx.ALL,
            border=5
        )

        # Create a FlexGridSizer for both the header row and data rows.
        self.table_sizer = wx.FlexGridSizer(rows=0, cols=8, hgap=5, vgap=5)
        # Example: Let column #2 expand if needed
        self.table_sizer.AddGrowableCol(2)
        self.table_sizer.SetFlexibleDirection(wx.HORIZONTAL)

        # ----- 1) HEADERS ROW -----
        headers = [
            "Posición",
            "Habilitar",
            "Dir. Registro",
            "Tipo de Dato",
            "Número de Bytes",
            "Frec. Muestreo",
            "Posiciones Decimales",
            "Tipo Variable"
        ]
        for header in headers:
            header_text = wx.StaticText(self, label=header, style=wx.ALIGN_CENTER)
            self.table_sizer.Add(header_text, flag=wx.EXPAND | wx.ALL, border=5)

        main_sizer.Add(self.table_sizer, flag=wx.EXPAND | wx.ALL, border=5)

        # Divider (horizontal line)
        divider = wx.StaticLine(self)
        main_sizer.Add(divider, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=5)

        # ----- 2) DATA ROWS -----
        # If you already have data in self.modbus_info, you can populate now:
        self.populate_data_rows()

        # ----- 3) Buttons -----
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        # read_button = wx.Button(self, label="Leer valores")
        # read_button.Bind(wx.EVT_BUTTON, self.on_read)
        # button_sizer.Add(read_button, flag=wx.ALIGN_CENTER | wx.ALL, border=5)

        save_button = wx.Button(self, label="Actualizar")
        save_button.Bind(wx.EVT_BUTTON, self.on_save)
        button_sizer.Add(save_button, flag=wx.ALIGN_CENTER | wx.ALL, border=5)

        main_sizer.Add(button_sizer, flag=wx.ALIGN_CENTER | wx.ALL, border=10)

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

    def populate_data_rows(self):
        """
        Creates a row of widgets for each entry in self.modbus_info.
        Storing ALL widgets (including wx.StaticText for "Posición")
        in self.row_controls so that clear_data_rows() can remove them.
        """

        # If this is a refresh, remove old rows first:
        # self.clear_data_rows()

        for register in self.modbus_info:
            # 1) Position (StaticText)
            position_text = wx.StaticText(
                self,
                label=str(register["register_position"])
            )
            self.table_sizer.Add(position_text, flag=wx.EXPAND | wx.ALL, border=2)

            # 2) Enable Flag (checkbox)
            enable_checkbox = wx.CheckBox(self)
            enable_checkbox.SetValue(bool(register["enable_flag"]))
            enable_checkbox.Bind(
                wx.EVT_CHECKBOX,
                lambda evt, c=enable_checkbox: self.on_enable_flag_change(evt, c)
            )
            self.table_sizer.Add(enable_checkbox, flag=wx.EXPAND | wx.ALL, border=2)

            # 3) Modbus Address
            modbus_address = wx.TextCtrl(
                self,
                value=str(register["modbus_register_address"])
            )
            self.table_sizer.Add(modbus_address, flag=wx.EXPAND | wx.ALL, border=2)

            # 4) Data type
            data_type = wx.ComboBox(
                self,
                choices=self.data_type_choices,
                style=wx.CB_READONLY
            )
            # data_type index is register["data_type"] - 1
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
            sampling_frequency = wx.TextCtrl(
                self,
                value=str(register["sampling_frequency"])
            )
            self.table_sizer.Add(sampling_frequency, flag=wx.EXPAND | wx.ALL, border=2)

            # 7) Decimal positions
            decimal_positions = wx.TextCtrl(
                self,
                value=str(register["decimal_positions"])
            )
            self.table_sizer.Add(decimal_positions, flag=wx.EXPAND | wx.ALL, border=2)

            # 8) Cumulative flag (combo box)
            cumu_choice_idx = max(
                0,
                min(register["cumulative_flag"], len(self.cumulative_choices) - 1)
            )
            cumulative_flag = wx.ComboBox(
                self,
                choices=self.cumulative_choices,
                style=wx.CB_READONLY
            )
            cumulative_flag.SetSelection(cumu_choice_idx)
            self.table_sizer.Add(cumulative_flag, flag=wx.EXPAND | wx.ALL, border=2)

            # Store references to ALL widgets for this row,
            # including position_text
            controls_for_this_row = {
                "position_text": position_text,
                "enable_checkbox": enable_checkbox,
                "modbus_address": modbus_address,
                "data_type": data_type,
                "num_bytes": num_bytes,
                "sampling_frequency": sampling_frequency,
                "decimal_positions": decimal_positions,
                "cumulative_flag": cumulative_flag
            }
            self.row_controls.append(controls_for_this_row)

            # Update initial state
            self.update_controls_state(controls_for_this_row, bool(register["enable_flag"]))

        # Layout so everything is properly aligned
        self.Layout()

    def on_enter(self):
        """
        Called when this panel becomes the selected tab in the notebook.
        For instance, you can query the device for values, or if the device isn't open,
        populate with defaults, etc.
        """
        print("Inside the modbus config panel")
        self.modbus_info = list()   # Clear existing data

        if self.controller.is_open():
            self.controller.send_command("AT+PROGMODE=1\r\n", False)
            dlg = wx.ProgressDialog(
                "Leyendo parámetros",
                "Por favor espere mientras se realiza la lectura",
                maximum=1,
                parent=self,
                style=wx.PD_APP_MODAL | wx.PD_AUTO_HIDE
            )

            modbus_reg_data = self.controller.send_command("AT+MBREGCFG?\r\n")

            dlg.Update(1, "Leyendo la configuración Registros Modbus...")
            modbus_reg_data_array = modbus_reg_data.split("\r\n")
            print(f"Modbus Reg Data: {modbus_reg_data_array}")

            for modbus_reg_data_item in modbus_reg_data_array:
                if modbus_reg_data_item:
                    modbus_reg_data_item_array = modbus_reg_data_item.split(",")
                    self.modbus_info.append({
                        "register_position": int(modbus_reg_data_item_array[0]),
                        "enable_flag": int(modbus_reg_data_item_array[1]),
                        "modbus_register_address": modbus_reg_data_item_array[2],
                        "data_type": int(modbus_reg_data_item_array[3]),
                        "num_bytes": modbus_reg_data_item_array[4],
                        "sampling_frequency": modbus_reg_data_item_array[5],
                        "decimal_positions": modbus_reg_data_item_array[6],
                        "cumulative_flag": int(modbus_reg_data_item_array[7]),
                    })
            self.clear_data_rows()
            self.populate_data_rows()

            dlg.Destroy()
            self.controller.send_command("AT+PROGMODE=0\r\n", False)
        else:
            # For demonstration, append some new data
            for i in range(10):
                self.modbus_info.append({
                    "register_position": i,
                    "enable_flag": 0,
                    "modbus_register_address": 0,
                    "data_type": 1,
                    "num_bytes": 0,
                    "sampling_frequency": 0,
                    "decimal_positions": 0,
                    "cumulative_flag": 0
                })
            # Rebuild the UI rows
            self.clear_data_rows()
            self.populate_data_rows()

            wx.MessageBox(
                "No se puede leer la configuración de registros Modbus.\n"
                "El puerto serial no está abierto.",
                "Error",
                wx.OK | wx.ICON_ERROR
            )

    def update_controls_state(self, controls_dict, is_enabled):
        """
        Enable/disable the row controls based on is_enabled.
        Typically we keep the checkbox itself always enabled.
        """
        for key, ctrl in controls_dict.items():
            if key == "enable_checkbox":
                continue
            ctrl.Enable(is_enabled)

    def on_enable_flag_change(self, event, checkbox):
        is_enabled = event.IsChecked()
        for row in self.row_controls:
            if row["enable_checkbox"] is checkbox:
                self.update_controls_state(row, is_enabled)
                break

    def on_read(self, event):
        if self.controller.is_open():
            wx.MessageBox("Reading values from device (stub).")
            # Then clear and repopulate rows if new data is loaded.
        else:
            wx.MessageBox(
                "No se puede leer la configuración de registros Modbus.\n"
                "El puerto serial no está abierto.",
                "Error",
                wx.OK | wx.ICON_ERROR
            )

    def on_save(self, event):
        """
        Collect all row data using extract_data_from_row,
        then send each row's data with a progress dialog.
        Format: register_position,enable_flag,modbus_register_address,
                data_type,num_bytes,sampling_frequency,decimal_positions,cumulative_flag
        """
        if not self.controller.is_open():
            wx.MessageBox(
                "No se puede guardar la configuración.\n"
                "El puerto serial está cerrado.",
                "Error",
                wx.OK | wx.ICON_ERROR
            )
            return

        # 1) Gather rows
        rows_for_sending = []
        for row in self.row_controls:
            line = self.extract_data_from_row(row)
            rows_for_sending.append(line)

        if not rows_for_sending:
            wx.MessageBox("No hay filas para guardar.", "Info", wx.OK | wx.ICON_INFORMATION)
            return

        # 2) Create a progress dialog to show the user each row being sent
        total_rows = len(rows_for_sending)
        dialog = wx.ProgressDialog(
            "Guardando parámetros",
            "En proceso...",
            maximum=total_rows,
            parent=self,
            style=wx.PD_APP_MODAL | wx.PD_AUTO_HIDE | wx.PD_SMOOTH
        )
        self.controller.send_command("AT+PROGMODE=1\r\n", False)
        # 3) Send each line as an AT command, updating the progress bar
        for i, row_str in enumerate(rows_for_sending, start=1):
            # Optionally display which register is being processed
            register_position = row_str.split(",")[0]
            dialog_msg = f"Guardando parámetros para el registro {register_position}..."
            dialog.Update(i, dialog_msg)

            cmd = f"AT+MBREGCFG={row_str}\r\n"
            response = self.controller.send_command(cmd)
            print(f"Sent: {cmd.strip()}, Received: {response.strip()}")
            time.sleep(0.5)  # Optional delay between commands

            # If your device typically returns "OK", handle errors if response != "OK"
            if response.strip() != "OK":
                wx.MessageBox(
                    f"Error al guardar registro {register_position}.\n"
                    f"Respuesta del dispositivo: {response}",
                    "Error",
                    wx.OK | wx.ICON_ERROR
                )
                dialog.Destroy()
                return
        self.controller.send_command("AT+PROGMODE=0\r\n", False)
        # 4) Clean up and inform the user
        dialog.Destroy()
        wx.MessageBox(
            "Todos los parámetros han sido enviados correctamente.",
            "Info",
            wx.OK | wx.ICON_INFORMATION
        )

    def extract_data_from_row(self, row: list) -> str:
        """
        Extracts data from a row of widgets and returns a comma-separated string.
        :param row: list of widgets in a row
        :return: str containing the row data
        """
        # 1) register_position: from StaticText label
        register_position = int(row["position_text"].GetLabel())

        # 2) enable_flag: from checkbox
        enable_flag = 1 if row["enable_checkbox"].GetValue() else 0

        # 3) modbus_register_address: from TextCtrl
        #   Convert to int if you need numeric, or keep string if sending as is.
        modbus_register_address_str = row["modbus_address"].GetValue()
        # Example: convert to int, then back to string (if you want consistent formatting)
        # Otherwise, you can keep the raw string. We'll do int->str:
        try:
            modbus_register_address_int = int(modbus_register_address_str)
        except ValueError:
            modbus_register_address_int = 0  # fallback
        modbus_register_address = str(modbus_register_address_int)

        # 4) data_type: from combo box (which stores a string, like "char")
        #   We want the *index+1* in self.data_type_choices to match your device command format.
        data_type_str = row["data_type"].GetValue()
        # Find which index in data_type_choices
        if data_type_str in self.data_type_choices:
            data_type_index = self.data_type_choices.index(data_type_str) + 1
        else:
            data_type_index = 0  # fallback

        # 5) num_bytes: from TextCtrl
        num_bytes_str = row["num_bytes"].GetValue()
        try:
            num_bytes_int = int(num_bytes_str)
        except ValueError:
            num_bytes_int = 0
        num_bytes = str(num_bytes_int)

        # 6) sampling_frequency
        sampling_frequency_str = row["sampling_frequency"].GetValue()
        try:
            sampling_frequency_int = int(sampling_frequency_str)
        except ValueError:
            sampling_frequency_int = 0
        sampling_frequency = str(sampling_frequency_int)

        # 7) decimal_positions
        decimal_positions_str = row["decimal_positions"].GetValue()
        try:
            decimal_positions_int = int(decimal_positions_str)
        except ValueError:
            decimal_positions_int = 0
        decimal_positions = str(decimal_positions_int)

        # 8) cumulative_flag: from combo box
        cumulative_str = row["cumulative_flag"].GetValue()
        if cumulative_str in self.cumulative_choices:
            cumulative_flag_index = self.cumulative_choices.index(cumulative_str)
        else:
            cumulative_flag_index = 0

        # Build the single comma‐separated line
        line = f"{register_position}," \
               f"{enable_flag}," \
               f"{modbus_register_address}," \
               f"{data_type_index}," \
               f"{num_bytes}," \
               f"{sampling_frequency}," \
               f"{decimal_positions}," \
               f"{cumulative_flag_index}"

        return line

    def clear_data_rows(self):
        """
        Remove existing "data row" widgets from table_sizer, destroy them,
        and clear self.row_controls so we can repopulate fresh data.
        """
        for row_ctrls in self.row_controls:
            # Detach and destroy *every* widget in the row, including position_text
            for widget in row_ctrls.values():
                self.table_sizer.Detach(widget)
                widget.Destroy()

        self.row_controls.clear()
        self.Layout()
