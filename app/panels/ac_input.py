import wx


class AcInputPanel(wx.ScrolledWindow):
    def __init__(self, parent, serial_comms_controller):
        super(AcInputPanel, self).__init__(parent)

        self.serial_comms_controller = serial_comms_controller

        self.ac_schedule_info = {
            "start_schedule": {"value": "", "text_ctrl": None},
            "end_schedule": {"value": "", "text_ctrl": None},
        }

        self.current_start_hour = 0
        self.current_start_minute = 0
        self.current_end_hour = 0
        self.current_end_minute = 0

        self.init_ui()
        self.SetScrollRate(5, 5)

    def init_ui(self):
        sizer = wx.BoxSizer(wx.VERTICAL)

        rows = [
            {
                "rows": [
                    {
                        "type": "multi-item",
                        "items": [
                            {"label": "Horario de Inicio", "key": "start_schedule", "type": "single"},
                        ],
                    },
                    {
                        "type": "multi-item",
                        "items": [
                            {"label": "Horario de Fin", "key": "end_schedule", "type": "single"},
                        ],
                    }
                ],
                "title": "Control por Horario",
                "type": "multiple"
            },
        ]

        sizer.Add(self.create_title("Configuracion de entrada AC"))

        for row in rows:
            sizer.Add(self.create_card(row['title'], row["rows"]))

        sizer.AddSpacer(20)

        read_button = wx.Button(self, label="Leer valores")
        read_button.Bind(wx.EVT_BUTTON, self.on_read)
        sizer.Add(read_button, flag=wx.ALIGN_CENTER, border=20)

        sizer.Add(wx.StaticLine(self), flag=wx.EXPAND | wx.ALL, border=10)

        sizer.Add(self.create_title("Nuevos valores a cargar"))
        sizer.Add(self.create_edit_card("Configurar encendido", "start"))
        sizer.Add(self.create_edit_card("Configurar apagado", "end"))

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
            ac_input_schedule = self.serial_comms_controller.send_command("AT+ACINPUT?\r\n")
            print(f"AC input schedule: {ac_input_schedule}")
            dlg.Update(1, "Leyendo la configuración de entrada AC...")

            dlg.Destroy()

            ac_input_list = ac_input_schedule[:-2].split(",")
            ac_on_schedule = f"{ac_input_list[0]}:{ac_input_list[1]}" if ac_input_list[0] != "99" else "No configurado"
            ac_off_schedule = f"{ac_input_list[2]}:{ac_input_list[3]}" if ac_input_list[2] != "99" else "No configurado"

            self.ac_schedule_info["start_schedule"]["text_ctrl"].SetValue(ac_on_schedule)
            self.ac_schedule_info["end_schedule"]["text_ctrl"].SetValue(ac_off_schedule)
        else:
            wx.MessageBox("No se puede leer la configuración de entrada AC, el puerto serial no está abierto",
                          "Error", wx.OK | wx.ICON_ERROR)

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
                text_ctrl = wx.TextCtrl(self, value=str(self.ac_schedule_info[key]['value']),
                                        style=wx.TE_READONLY, size=(50, -1))
                self.ac_schedule_info[key]["text_ctrl"] = text_ctrl
                grid_sizer.Add(text_ctrl, flag=wx.EXPAND | wx.ALL, border=5)

            sizer.Add(grid_sizer, flag=wx.EXPAND)

        h_sizer = wx.BoxSizer(wx.HORIZONTAL)
        h_sizer.Add((20, 0))
        h_sizer.Add(sizer, 1, flag=wx.EXPAND)

        v_sizer = wx.BoxSizer(wx.VERTICAL)
        v_sizer.Add((0, 20))
        v_sizer.Add(h_sizer, 1, flag=wx.EXPAND)

        return v_sizer

    def create_edit_card(self, title, identifier):
        box = wx.StaticBox(self, label=title)
        font = wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        box.SetFont(font)
        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)

        hour_choices = [str(value) for value in range(24)]
        minute_choices = [str(value) for value in range(60)]

        if identifier == "start":
            current_hour = self.current_start_hour
            current_minute = self.current_start_minute
        else:  # identifier == "end"
            current_hour = self.current_end_hour
            current_minute = self.current_end_minute

        hour_combo = wx.ComboBox(self, choices=hour_choices, style=wx.CB_READONLY, size=(200, -1))
        hour_combo.SetValue(str(current_hour))

        minute_combo = wx.ComboBox(self, choices=minute_choices, style=wx.CB_READONLY, size=(200, -1))
        minute_combo.SetValue(str(current_minute))

        dropdown_sizer = wx.BoxSizer(wx.HORIZONTAL)
        dropdown_sizer.Add(wx.StaticText(self, label="Hora: "), flag=wx.ALL, border=5)
        dropdown_sizer.Add(hour_combo, flag=wx.ALL, border=5)
        dropdown_sizer.Add(wx.StaticText(self, label="Minutos: "), flag=wx.ALL, border=5)
        dropdown_sizer.Add(minute_combo, flag=wx.ALL, border=5)

        sizer.Add(dropdown_sizer, flag=wx.ALL, border=5)

        h_sizer = wx.BoxSizer(wx.HORIZONTAL)
        h_sizer.Add((20, 0))  # 20 is the width of the spacer, adjust as needed
        h_sizer.Add(sizer, 1, flag=wx.EXPAND)

        v_sizer = wx.BoxSizer(wx.VERTICAL)
        v_sizer.Add((0, 20))  # 20 is the height of the spacer, adjust as needed
        v_sizer.Add(h_sizer, 1, flag=wx.EXPAND)

        def on_hour_change(event):
            if identifier == "start":
                self.current_start_hour = int(hour_combo.GetValue())
            else:  # identifier == "end"
                self.current_end_hour = int(hour_combo.GetValue())

        def on_minute_change(event):
            if identifier == "start":
                self.current_start_minute = int(minute_combo.GetValue())
            else:  # identifier == "end"
                self.current_end_minute = int(minute_combo.GetValue())

        hour_combo.Bind(wx.EVT_COMBOBOX, on_hour_change)
        minute_combo.Bind(wx.EVT_COMBOBOX, on_minute_change)

        return v_sizer

    def on_save(self, event):
        start_hour = str(self.current_start_hour).zfill(2)
        start_minute = str(self.current_start_minute).zfill(2)
        end_hour = str(self.current_end_hour).zfill(2)
        end_minute = str(self.current_end_minute).zfill(2)

        self.ac_schedule_info["start_schedule"]["text_ctrl"].SetValue(f"{start_hour}:{start_minute}")
        self.ac_schedule_info["end_schedule"]["text_ctrl"].SetValue(f"{end_hour}:{end_minute}")

        # Add logic to save to serial controller or perform other actions
        ac_config_msg = f"AT+ACINPUT={start_hour},{start_minute},{end_hour},{end_minute}\r\n"
        print(f"Schedule config message: {ac_config_msg}")
        response = self.serial_comms_controller.send_command(ac_config_msg)

        if response == "OK\r\n":
            wx.MessageBox("Valores cargados correctamente", "Info", wx.OK | wx.ICON_INFORMATION)
