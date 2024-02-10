import wx


class ScheduleConfigPanel(wx.ScrolledWindow):
    def __init__(self, parent, serial_comms_controller):
        super(ScheduleConfigPanel, self).__init__(parent)

        self.serial_comms_controller = serial_comms_controller

        self.schedule_info = {
            "on_schedule": {"value": "", "text_ctrl": None},
            "off_schedule": {"value": "", "text_ctrl": None},
            "on_contactor_state": {"value": "", "text_ctrl": None},
            "off_contactor_state": {"value": "", "text_ctrl": None},
        }

        self.current_open_hour = 0
        self.current_open_minute = 0
        self.current_open_contact = "NA"

        self.current_close_hour = 0
        self.current_close_minute = 0
        self.current_close_contact = "NC"

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
                            {"label": "Horario de encendido", "key": "on_schedule", "type": "single"},
                            {"label": "Estado de contactor (encendido)", "key": "on_contactor_state", "type": "single"}
                        ],
                    },
                    {
                        "type": "multi-item",
                        "items": [
                            {"label": "Horario de apagado", "key": "off_schedule", "type": "single"},
                            {"label": "Estado de contactor (apagado)", "key": "off_contactor_state", "type": "single"}
                        ],
                    }
                ],
                "title": "Control por Horario",
                "type": "multiple"
            },
        ]

        sizer.Add(self.create_title("Configuración Actual"))
        for row in rows:
            sizer.Add(self.create_card(row['title'], row["rows"]))

        sizer.AddSpacer(20)

        read_button = wx.Button(self, label="Leer valores")
        read_button.Bind(wx.EVT_BUTTON, self.on_read)
        sizer.Add(read_button, flag=wx.ALIGN_CENTER, border=20)

        sizer.Add(wx.StaticLine(self), flag=wx.EXPAND | wx.ALL, border=10)

        sizer.Add(self.create_title("Nuevos valores a cargar"))
        sizer.Add(self.create_edit_card("Configurar encendido", "open"))
        sizer.Add(self.create_edit_card("Configurar apagado", "close"))

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
            schedule_config = self.serial_comms_controller.send_command("AT+SCHEDULE?\r\n")
            print(f"Schedule config: {schedule_config}")
            dlg.Update(1, "Leyendo el control por horario...")

            dlg.Destroy()

            schedule_config_list = schedule_config[:-2].split(",")
            schedule_on = f"{schedule_config_list[0]}:{schedule_config_list[1]}" if schedule_config_list[
                                                                                        0] != "99" else "No configurado"
            schedule_off = f"{schedule_config_list[3]}:{schedule_config_list[4]}" if schedule_config_list[
                                                                                         3] != "99" else "No configurado"
            contactor_on = ("Cerrado" if schedule_config_list[
                                             2] == "1" else "Abierto") if schedule_on != "No configurado" else "No configurado"
            contactor_off = ("Abierto" if schedule_config_list[
                                              2] == "1" else "Cerrado") if schedule_off != "No configurado" else "No configurado"

            self.schedule_info["on_schedule"]["text_ctrl"].SetValue(schedule_on)
            self.schedule_info["off_schedule"]["text_ctrl"].SetValue(schedule_off)
            self.schedule_info["on_contactor_state"]["text_ctrl"].SetValue(contactor_on)
            self.schedule_info["off_contactor_state"]["text_ctrl"].SetValue(contactor_off)

        else:
            wx.MessageBox(
                "No se puede leer la configuración de horario, el puerto serial está cerrado",
                "Error",
                wx.OK | wx.ICON_ERROR
            )

    def create_title(self, title):
        title_text = wx.StaticText(self, label=title)
        title_text.SetFont(wx.Font(wx.FontInfo(12).Bold()))

        # Create a horizontal box sizer
        h_sizer = wx.BoxSizer(wx.HORIZONTAL)
        # Add a spacer to the left of the sizer
        h_sizer.Add((20, 0))  # 20 is the width of the spacer, adjust as needed
        # Add the title_text to the horizontal sizer
        h_sizer.Add(title_text, 1, flag=wx.EXPAND)

        # Create a vertical box sizer
        v_sizer = wx.BoxSizer(wx.VERTICAL)
        # Add a spacer to the top of the sizer
        v_sizer.Add((0, 20))  # 20 is the height of the spacer, adjust as needed
        # Add the horizontal sizer to the vertical sizer
        v_sizer.Add(h_sizer, 1, flag=wx.EXPAND)

        return v_sizer

    def create_card(self, title, rows):
        box = wx.StaticBox(self, label=title, size=(300, -1))  # Set a fixed width for the box
        font = wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        box.SetFont(font)
        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)

        for row in rows:
            items = row["items"]

            grid_sizer = wx.GridSizer(rows=len(items), cols=2, vgap=5,
                                      hgap=5)  # Adjust the number of rows in the GridSizer

            for item in items:
                key = item['key']
                label = wx.StaticText(self, label=item["label"])
                grid_sizer.Add(label, flag=wx.ALL, border=5)
                text_ctrl = wx.TextCtrl(self, value=str(self.schedule_info[key]['value']),
                                        style=wx.TE_READONLY, size=(50, -1))
                self.schedule_info[key]["text_ctrl"] = text_ctrl
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

        # start_label = wx.StaticText(self, label=f"{title}:")
        # start_label.SetFont(wx.Font(wx.FontInfo(12).Bold()))

        hour_choices = [str(value) for value in range(24)]
        minute_choices = [str(value) for value in range(60)]
        contact_choices = ["NA", "NC"]

        start_hour_combo = wx.ComboBox(self, choices=hour_choices, style=wx.CB_READONLY, size=(200, -1))
        start_hour_combo.SetValue(str(self.get_current_hour(identifier)))

        start_minute_combo = wx.ComboBox(self, choices=minute_choices, style=wx.CB_READONLY, size=(200, -1))
        start_minute_combo.SetValue(str(self.get_current_minute(identifier)))

        contact_combo = wx.ComboBox(self, choices=contact_choices, style=wx.CB_READONLY, size=(200, -1))
        contact_combo.SetValue(self.get_current_contact(identifier))

        def on_hour_change(event):
            self.set_current_hour(identifier, int(start_hour_combo.GetValue()))

        def on_minute_change(event):
            self.set_current_minute(identifier, int(start_minute_combo.GetValue()))

        def on_contact_change(event):
            self.set_current_contact(identifier, contact_combo.GetValue())

        start_hour_combo.Bind(wx.EVT_COMBOBOX, on_hour_change)
        start_minute_combo.Bind(wx.EVT_COMBOBOX, on_minute_change)
        contact_combo.Bind(wx.EVT_COMBOBOX, on_contact_change)

        time_sizer = wx.BoxSizer(wx.HORIZONTAL)
        time_sizer.Add(wx.StaticText(self, label="Hora: "), flag=wx.ALL, border=5)
        time_sizer.Add(start_hour_combo, flag=wx.ALL, border=5)
        time_sizer.Add(wx.StaticText(self, label="Minutos: "), flag=wx.ALL, border=5)
        time_sizer.Add(start_minute_combo, flag=wx.ALL, border=5)

        # sizer.Add(start_label, flag=wx.ALL, border=5)
        sizer.Add(time_sizer, flag=wx.ALL, border=5)
        sizer.Add(wx.StaticText(self, label="Contacto: "), flag=wx.ALL, border=5)
        sizer.Add(contact_combo, flag=wx.ALL, border=5)

        # Create a horizontal box sizer
        h_sizer = wx.BoxSizer(wx.HORIZONTAL)
        # Add a spacer to the left of the sizer
        h_sizer.Add((20, 0))  # 20 is the width of the spacer, adjust as needed
        # Add the original sizer to the horizontal sizer
        h_sizer.Add(sizer, 1, flag=wx.EXPAND)

        # Create a vertical box sizer
        v_sizer = wx.BoxSizer(wx.VERTICAL)
        # Add a spacer to the top of the sizer
        v_sizer.Add((0, 20))  # 20 is the height of the spacer, adjust as needed
        # Add the horizontal sizer to the vertical sizer
        v_sizer.Add(h_sizer, 1, flag=wx.EXPAND)

        return v_sizer

    def on_save(self, event):
        if self.serial_comms_controller.is_open():
            open_hour = str(self.current_open_hour).zfill(2)
            open_minute = str(self.current_open_minute).zfill(2)
            open_relay_status = "1" if self.current_open_contact == "NA" else "0"
            close_hour = str(self.current_close_hour).zfill(2)
            close_minute = str(self.current_close_minute).zfill(2)
            close_relay_status = "1" if self.current_close_contact == "NA" else "0"

            self.schedule_info["on_schedule"]["value"] = f"{open_hour}:{open_minute}"
            self.schedule_info["off_schedule"]["value"] = f"{close_hour}:{close_minute}"
            self.schedule_info["on_contactor_state"]["value"] = open_relay_status
            self.schedule_info["off_contactor_state"]["value"] = close_relay_status

            dlg = wx.ProgressDialog(
                "Cargando parámetros",
                "Por favor espere mientras se realiza la carga",
                maximum=1,
                parent=self,
                style=wx.PD_APP_MODAL | wx.PD_AUTO_HIDE
            )

            # Add logic to save to serial controller or perform other actions
            schedule_config_msg = f"AT+SCHEDULE={open_hour},{open_minute},{open_relay_status},{close_hour},{close_minute},{close_relay_status}\r\n"
            print(f"Schedule config message: {schedule_config_msg}")
            response = self.serial_comms_controller.send_command(schedule_config_msg)
            dlg.Update(1, "Cargando el control por horario...")

            dlg.Destroy()

            if response == "OK\r\n":
                wx.MessageBox("Valores cargados correctamente", "Info", wx.OK | wx.ICON_INFORMATION)
            else:
                wx.MessageBox(
                    f"No se pudieron guardar los valores",
                    "Error",
                    wx.OK | wx.ICON_ERROR,
                )
        else:
            wx.MessageBox(
                "No se puede guardar la configuración de horario, el puerto serial está cerrado",
                "Error",
                wx.OK | wx.ICON_ERROR
            )

    def get_schedule_text(self, hour_key, minute_key, relay_status_key):
        return (
            f"Hora: {self.schedule_info[hour_key]}:{self.schedule_info[minute_key]}, "
            f"tipo de contacto: {self.get_relay_status_text(relay_status_key)}"
        )

    def get_relay_status_text(self, relay_status_key):
        return (
            "Normalmente Abierto"
            if self.schedule_info[relay_status_key] == "NA"
            else "Normalmente Cerrado"
        )

    def get_current_hour(self, identifier):
        return (
            self.current_open_hour if identifier == "open" else self.current_close_hour
        )

    def get_current_minute(self, identifier):
        return (
            self.current_open_minute
            if identifier == "open"
            else self.current_close_minute
        )

    def get_current_contact(self, identifier):
        return (
            self.current_open_contact
            if identifier == "open"
            else self.current_close_contact
        )

    def set_current_hour(self, identifier, value):
        if identifier == "open":
            self.current_open_hour = value
        else:
            self.current_close_hour = value

    def set_current_minute(self, identifier, value):
        if identifier == "open":
            self.current_open_minute = value
        else:
            self.current_close_minute = value

    def set_current_contact(self, identifier, value):
        if identifier == "open":
            self.current_open_contact = value
        else:
            self.current_close_contact = value
