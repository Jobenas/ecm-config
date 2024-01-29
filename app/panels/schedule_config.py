import wx


class ScheduleConfigPanel(wx.ScrolledWindow):
    def __init__(self, parent, serial_comms_controller):
        super(ScheduleConfigPanel, self).__init__(parent)

        self.serial_comms_controller = serial_comms_controller

        self.schedule_info = {
            "open_hour": "",
            "open_minute": "",
            "open_relay_status": "",
            "close_hour": "",
            "close_minute": "",
            "close_relay_status": "",
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

        sizer.Add(self.create_title("Configuración Actual"))
        sizer.Add(
            self.create_card(
                "Horario de encendido", "open_hour", "open_minute", "open_relay_status"
            )
        )
        sizer.Add(
            self.create_card(
                "Horario de apagado", "close_hour", "close_minute", "close_relay_status"
            )
        )

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
        print("This is where we read the schedule config")

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

    def create_card(self, title, hour_key, minute_key, relay_status_key):
        box = wx.StaticBox(self, label=title)
        font = wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        box.SetFont(font)
        sizer = wx.StaticBoxSizer(box, wx.HORIZONTAL)  # Change to horizontal sizer

        # label = wx.StaticText(self, label=f"{title}:")
        # label.SetFont(wx.Font(wx.FontInfo(12).Bold()))
        hour_label = wx.StaticText(
            self,
            label=f"Hora: {self.schedule_info[hour_key]}:{self.schedule_info[minute_key]}",
        )
        relay_status_label = wx.StaticText(
            self,
            label=f"Tipo de contacto: {self.get_relay_status_text(relay_status_key)}",
        )

        # sizer.Add(label, flag=wx.ALL, border=5)
        sizer.Add(hour_label, flag=wx.EXPAND | wx.ALL, border=5)
        sizer.Add(relay_status_label, flag=wx.EXPAND | wx.ALL, border=5)

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
        open_hour = str(self.current_open_hour).zfill(2)
        open_minute = str(self.current_open_minute).zfill(2)
        open_relay_status = "1" if self.current_open_contact == "NA" else "0"
        close_hour = str(self.current_close_hour).zfill(2)
        close_minute = str(self.current_close_minute).zfill(2)
        close_relay_status = "1" if self.current_close_contact == "NA" else "0"

        schedule_info = {
            "open_hour": open_hour,
            "open_minute": open_minute,
            "open_relay_status": open_relay_status,
            "close_hour": close_hour,
            "close_minute": close_minute,
            "close_relay_status": close_relay_status,
        }

        self.schedule_info = schedule_info
        # Add logic to save to serial controller or perform other actions

        wx.MessageBox("Values saved!", "Info", wx.OK | wx.ICON_INFORMATION)

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
