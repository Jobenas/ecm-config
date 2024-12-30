import wx


class DisplayConfigDialog(wx.Dialog):
    def __init__(self, parent, title, controller):
        super(DisplayConfigDialog, self).__init__(parent, title=title)
        self.controller = controller

        self.SetSize(500, 500)  # Set the size of the dialog

        self.display_config_info = {
            "offset": {"value": "", "text_ctrl": None},
            "pulse_factor": {"value": "", "text_ctrl": None},
        }

        self.Bind(wx.EVT_BUTTON, self.on_close, id=wx.ID_CLOSE)

        self.init_ui()

    def init_ui(self):
        panel = wx.Panel(self)

        sizer = wx.BoxSizer(wx.VERTICAL)

        rows = [
            {
                "rows": [
                    {
                        "type": "multi-item",
                        "items": [
                            {"label": "Offset:", "key": "offset", "type": "single"},
                        ],
                    },
                    {
                        "type": "multi-item",
                        "items": [
                            {"label": "Factor de pulso:", "key": "pulse_factor", "type": "single"},
                        ],
                    },
                ],
                "title": "Valores actuales",
                "type": "multiple"
            },
        ]

        sizer.Add(self.create_title(panel, "Configuracion de Display"))

        for row in rows:
            sizer.Add(self.create_card(panel, row['title'], row["rows"]))

        sizer.AddSpacer(10)

        read_button = wx.Button(panel, label="Leer")
        sizer.Add(read_button, flag=wx.ALIGN_CENTER, border=20)
        read_button.Bind(wx.EVT_BUTTON, self.on_read)

        sizer.Add(wx.StaticLine(panel), flag=wx.EXPAND | wx.ALL, border=10)

        sizer.AddSpacer(10)

        sizer.Add(self.create_edit_card(panel, "Editar valores", "display_config"))

        sizer.AddSpacer(10)

        write_button = wx.Button(panel, label="Guardar")
        sizer.Add(write_button, flag=wx.ALIGN_CENTER, border=20)
        write_button.Bind(wx.EVT_BUTTON, self.on_write)

        sizer.AddSpacer(10)
        sizer.Add(wx.StaticLine(panel), flag=wx.EXPAND | wx.ALL, border=10)
        sizer.AddSpacer(10)

        close_button = wx.Button(panel, label="Cerrar")
        close_button.Bind(wx.EVT_BUTTON, self.on_close)
        sizer.AddSpacer(5)  # Add spacer for padding
        sizer.Add(close_button, flag=wx.ALIGN_CENTER)

        panel.SetSizer(sizer)

    def create_title(self, parent, title):
        title_text = wx.StaticText(parent, label=title)
        title_text.SetFont(wx.Font(wx.FontInfo(12).Bold()))

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add((20, 0))  # left padding
        sizer.Add(title_text)

        v_sizer = wx.BoxSizer(wx.VERTICAL)
        v_sizer.Add((0, 20))  # top padding
        v_sizer.Add(sizer)

        return v_sizer

    def create_card(self, parent, title, rows):
        box = wx.StaticBox(parent, label=title, size=(300, -1))  # Set a fixed width for the box

        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)

        for row in rows:
            items = row["items"]
            font = wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD)
            box.SetFont(font)
            grid_sizer = wx.FlexGridSizer(len(items), 2, 5, 5)  # Adjust the number of rows in the FlexGridSizer

            for item in items:
                label = wx.StaticText(parent, label=item["label"])
                grid_sizer.Add(label, flag=wx.ALL, border=5)
                if "info_type" in item and item["info_type"] == "choice":
                    text_ctrl = wx.Choice(parent, choices=["COM1", "COM2", "COM3", "COM4"])
                    text_ctrl.SetStringSelection("COM1")
                else:
                    text_ctrl = wx.TextCtrl(parent, value="", style=wx.TE_READONLY, size=(50, -1))
                grid_sizer.Add(text_ctrl, flag=wx.EXPAND | wx.ALL, border=5)
                self.display_config_info[item["key"]][
                    "text_ctrl"] = text_ctrl  # Assign the wx.TextCtrl object to the text_ctrl attribute

            sizer.Add(grid_sizer, flag=wx.EXPAND)

        h_sizer = wx.BoxSizer(wx.HORIZONTAL)
        h_sizer.Add((20, 0))
        h_sizer.Add(sizer, 1, flag=wx.EXPAND)

        v_sizer = wx.BoxSizer(wx.VERTICAL)
        v_sizer.Add((0, 20))
        v_sizer.Add(h_sizer, 1, flag=wx.EXPAND)

        return v_sizer

    def create_edit_card(self, parent, title, identifier):
        box = wx.StaticBox(parent, label=title)
        font = wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        box.SetFont(font)
        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)

        # Create a FlexGridSizer with 2 columns
        grid_sizer = wx.FlexGridSizer(2, 2, 5, 5)

        # Add the label and text control for "Offset"
        grid_sizer.Add(wx.StaticText(parent, label="Offset: "), flag=wx.ALL, border=5)
        self.offset_input = wx.TextCtrl(parent, size=(200, -1))  # Store as instance variable
        grid_sizer.Add(self.offset_input, flag=wx.ALL, border=5)

        # Add the label and text control for "Factor de pulsos"
        grid_sizer.Add(wx.StaticText(parent, label="Factor de pulsos: "), flag=wx.ALL, border=5)
        self.pulse_factor_input = wx.TextCtrl(parent, size=(200, -1))  # Store as instance variable
        grid_sizer.Add(self.pulse_factor_input, flag=wx.ALL, border=5)

        # Add the grid sizer to the main sizer
        sizer.Add(grid_sizer, flag=wx.ALL, border=5)

        h_sizer = wx.BoxSizer(wx.HORIZONTAL)
        h_sizer.Add((20, 0))  # 20 is the width of the spacer, adjust as needed
        h_sizer.Add(sizer, 1, flag=wx.EXPAND)

        v_sizer = wx.BoxSizer(wx.VERTICAL)
        v_sizer.Add((0, 20))  # 20 is the height of the spacer, adjust as needed
        v_sizer.Add(h_sizer, 1, flag=wx.EXPAND)

        return v_sizer

    def on_close(self, event):
        # Add your save logic here
        self.Close()

    def on_read(self, event):
        if self.controller.is_open():
            dlg = wx.ProgressDialog(
                "Leyendo parámetros",
                "Por favor espere mientras se realiza la lectura",
                maximum=2,
                parent=self,
                style=wx.PD_APP_MODAL | wx.PD_AUTO_HIDE
            )
            offset_value = self.controller.send_command("AT+OFFSET?\r\n")
            print(f"offset: {offset_value}")
            offset_value = offset_value.split(" ")[-1]
            dlg.Update(1, "Leyendo valor de offset...")

            pulse_factor_value = self.controller.send_command("AT+FPULSE?\r\n")
            print(f"Pulse factor: {pulse_factor_value}")
            pulse_factor_value = pulse_factor_value.split(" ")[-1]
            dlg.Update(2, "Leyendo valor de factor de pulsos...")

            dlg.Destroy()

            self.display_config_info["offset"]["text_ctrl"].SetValue(offset_value)
            self.display_config_info["pulse_factor"]["text_ctrl"].SetValue(pulse_factor_value)
        else:
            wx.MessageBox("No se puede leer la configuración de display, el puerto serial no está abierto",
                          "Error", wx.OK | wx.ICON_ERROR)

    def on_write(self, event):
        if self.controller.is_open():
            dlg = wx.ProgressDialog(
                "Cargando parámetros",
                "Por favor espere mientras se realiza la carga",
                maximum=2,
                parent=self,
                style=wx.PD_APP_MODAL | wx.PD_AUTO_HIDE
            )
            # Retrieve the values from the text controls
            offset_value = self.offset_input.GetValue()
            pulse_factor_value = self.pulse_factor_input.GetValue()

            # Format the values into the appropriate command strings
            offset_command = f"AT+OFFSET={offset_value}\r\n"
            self.controller.send_command(offset_command)
            dlg.Update(1, "Cargando configuración de offset...")

            pulse_factor_command = f"AT+FPULSE={pulse_factor_value}\r\n"
            reply = self.controller.send_command(pulse_factor_command)
            dlg.Update(2, "Cargando configuración de factor de pulsos...")

            dlg.Destroy()

            wx.MessageBox("Valores cargados correctamente", "Info", wx.OK | wx.ICON_INFORMATION)
        else:
            wx.MessageBox("No se puede escribir la configuración de display, el puerto serial no está abierto",
                          "Error", wx.OK | wx.ICON_ERROR)
