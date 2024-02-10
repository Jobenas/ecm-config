import wx


class DigitalInputPanel(wx.ScrolledWindow):
    def __init__(self, parent, serial_comms_controller):
        super(DigitalInputPanel, self).__init__(parent)

        self.serial_comms_controller = serial_comms_controller

        self.dc_input_info = {
            "dc_input_mode": {"value": "", "text_ctrl": None},
        }

        self.digital_input_modes = ["Solo alerta", "Conmutación de relé"]

        self.configured_digital_input_mode = ""
        self.current_digital_input_mode = "Solo alerta"

        self.init_ui()
        self.SetScrollRate(5, 5)

    def init_ui(self):
        sizer = wx.BoxSizer(wx.VERTICAL)

        rows = [
            {
                "rows": [
                    {
                        "type": "single-item",
                        "items": [
                            {"label": "Entrada Digital", "key": "dc_input_mode", "type": "single"},
                        ],
                    },
                ],
                "title": "Cuenta de Pulsos Actual",
                "type": "multiple"
            },
        ]

        sizer.Add(self.create_title("Configuración actual de la entrada digital"))
        sizer.AddSpacer(15)
        for row in rows:
            sizer.Add(self.create_card(row['title'], row["rows"]))
        sizer.AddSpacer(20)
        read_button = wx.Button(self, label="Leer valores")
        read_button.Bind(wx.EVT_BUTTON, self.on_read)
        sizer.Add(read_button, flag=wx.ALIGN_CENTER, border=20)

        sizer.Add(wx.StaticLine(self), flag=wx.EXPAND | wx.ALL, border=10)

        sizer.Add(self.create_title("Nuevos valores de la entrada digital"))
        sizer.AddSpacer(10)
        sizer.Add(self.create_action_card("Acción de la entrada digital"))

        sizer.AddSpacer(20)

        save_button = wx.Button(self, label="Guardar")
        save_button.Bind(wx.EVT_BUTTON, self.on_save)
        sizer.Add(save_button, flag=wx.ALIGN_CENTER)

        self.SetSizer(sizer)

    def on_read(self, event):
        if self.serial_comms_controller.is_open():
            dlg = wx.ProgressDialog(
                "Leyendo parámetros",
                "Por favor espere mientras se realiza la lectura",
                maximum=1,
                parent=self,
                style=wx.PD_APP_MODAL | wx.PD_AUTO_HIDE
            )

            dc_input = self.serial_comms_controller.send_command("AT+IN3MODE?\r\n")
            print(f"DC input: {dc_input}")
            dlg.Update(1, "Leyendo la configuración de entrada digital...")

            dlg.Destroy()

            self.dc_input_info["dc_input_mode"]["text_ctrl"].SetValue(dc_input)
        else:
            wx.MessageBox(
                "No se puede leer la configuración de entrada Digital, el puerto serial no está abierto",
                "Error",
                wx.OK | wx.ICON_ERROR,
            )

    def create_title(self, title):
        title_text = wx.StaticText(self, label=title)
        title_text.SetFont(wx.Font(wx.FontInfo(12).Bold()))

        h_sizer = wx.BoxSizer(wx.HORIZONTAL)
        h_sizer.Add((20, 0))  # Add left padding
        h_sizer.Add(title_text)

        v_sizer = wx.BoxSizer(wx.VERTICAL)
        v_sizer.Add((0, 20))  # Add top padding
        v_sizer.Add(h_sizer)

        return v_sizer

    def create_card(self, title, rows):
        box = wx.StaticBox(self, label=title, size=(300, -1))  # Set a fixed width for the box
        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)

        label = wx.StaticText(self, label=f"{title}:")
        label.SetFont(wx.Font(wx.FontInfo(12).Bold()))

        sizer.Add(label, flag=wx.ALL, border=5)

        for row in rows:
            items = row["items"]

            grid_sizer = wx.GridSizer(rows=len(items), cols=2, vgap=5,
                                      hgap=5)  # Adjust the number of rows in the GridSizer

            for item in items:
                key = item['key']
                label = wx.StaticText(self, label=item["label"])
                grid_sizer.Add(label, flag=wx.ALL, border=5)
                text_ctrl = wx.TextCtrl(self, value=str(self.dc_input_info[key]['value']),
                                        style=wx.TE_READONLY, size=(50, -1))
                self.dc_input_info[key]["text_ctrl"] = text_ctrl
                grid_sizer.Add(text_ctrl, flag=wx.EXPAND | wx.ALL, border=5)

            sizer.Add(grid_sizer, flag=wx.EXPAND)

        h_sizer = wx.BoxSizer(wx.HORIZONTAL)
        h_sizer.Add((20, 0))
        h_sizer.Add(sizer, 1, flag=wx.EXPAND)

        v_sizer = wx.BoxSizer(wx.VERTICAL)
        v_sizer.Add((0, 20))
        v_sizer.Add(h_sizer, 1, flag=wx.EXPAND)

        return v_sizer

    def create_action_card(self, title):
        box = wx.StaticBox(self, label=title)
        box.SetFont(wx.Font(wx.FontInfo(9).Bold()))
        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)

        # action_label = wx.StaticText(self, label=f"{title}:")
        # action_label.SetFont(wx.Font(wx.FontInfo(12).Bold()))

        action_choices = self.digital_input_modes

        action_combo = wx.ComboBox(self, choices=action_choices, style=wx.CB_READONLY, size=(200, -1))
        action_combo.SetValue(self.current_digital_input_mode)

        # sizer.Add(action_label, flag=wx.ALL, border=5)
        sizer.Add(wx.StaticText(self, label="Acción: "), flag=wx.ALL, border=5)
        sizer.Add(action_combo, flag=wx.ALL, border=5)

        def on_action_change(event):
            self.current_digital_input_mode = action_combo.GetValue()

        action_combo.Bind(wx.EVT_COMBOBOX, on_action_change)

        h_sizer = wx.BoxSizer(wx.HORIZONTAL)
        h_sizer.Add((20, 0))  # Add left padding
        h_sizer.Add(sizer, 1, flag=wx.EXPAND)

        v_sizer = wx.BoxSizer(wx.VERTICAL)
        v_sizer.Add((0, 20))  # Add top padding
        v_sizer.Add(h_sizer, 1, flag=wx.EXPAND)

        return v_sizer

    def on_save(self, event):
        digital_input_mode = (
            1 if self.current_digital_input_mode == "Solo alerta" else 0
        )

        print(f"Digital input mode: {digital_input_mode}")

        self.dc_input_info["dc_input_mode"]["text_ctrl"].SetValue("TOGGLE_RELAY" if digital_input_mode == 0 else "ALERT_ONLY")

        dc_config_msg = f"AT+CONFIG={digital_input_mode}0,00\r\n"
        print(f"DC config msg: {dc_config_msg}")
        response = self.serial_comms_controller.send_command(dc_config_msg)

        if response == "OK\r\n":
            wx.MessageBox(
                f"Valores guardados correctamente!",
                "Info",
                wx.OK | wx.ICON_INFORMATION,
            )
        else:
            wx.MessageBox(
                f"No se pudieron guardar los valores",
                "Error",
                wx.OK | wx.ICON_ERROR,
            )

    def get_status_text(self):
        return (
            f"Solo envio Alertas"
            if self.configured_digital_input_mode == "1"
            else f"Conmutación de relé"
        )
