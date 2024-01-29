import wx


class AcInputPanel(wx.ScrolledWindow):
    def __init__(self, parent, serial_comms_controller):
        super(AcInputPanel, self).__init__(parent)

        self.serial_comms_controller = serial_comms_controller

        self.ac_schedule_info = {
            "start_hour": "",
            "start_minute": "",
            "end_hour": "",
            "end_minute": "",
        }

        self.current_start_hour = 0
        self.current_start_minute = 0
        self.current_end_hour = 0
        self.current_end_minute = 0

        self.init_ui()
        self.SetScrollRate(5, 5)

    def init_ui(self):
        sizer = wx.BoxSizer(wx.VERTICAL)

        sizer.Add(self.create_title("Configuracion de entrada AC"))
        sizer.Add(self.create_card("Hora de inicio", "start_hour", "start_minute"))
        sizer.Add(self.create_card("Horario de fin", "end_hour", "end_minute"))

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
        print("This is where we reada the AC Input data")

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

    def create_card(self, title, hour_key, minute_key):
        box = wx.StaticBox(self, label=title)
        font = wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        box.SetFont(font)
        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)

        text_ctrl = wx.TextCtrl(self, value=f"{self.ac_schedule_info[hour_key]}:{self.ac_schedule_info[minute_key]}",
                                style=wx.TE_READONLY, size=(200, -1))
        # label = wx.StaticText(self, label=f"{title}:")
        # label.SetFont(wx.Font(wx.FontInfo(12).Bold()))

        # sizer.Add(label, flag=wx.ALL, border=5)
        sizer.Add(text_ctrl, flag=wx.EXPAND | wx.ALL, border=5)

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

        start_hour_combo = wx.ComboBox(self, choices=hour_choices, style=wx.CB_READONLY, size=(200, -1))
        start_hour_combo.SetValue(str(self.current_start_hour))

        start_minute_combo = wx.ComboBox(self, choices=minute_choices, style=wx.CB_READONLY, size=(200, -1))
        start_minute_combo.SetValue(str(self.current_start_minute))

        # Create a horizontal box sizer for the dropdown menus
        dropdown_sizer = wx.BoxSizer(wx.HORIZONTAL)
        dropdown_sizer.Add(wx.StaticText(self, label="Hora: "), flag=wx.ALL, border=5)
        dropdown_sizer.Add(start_hour_combo, flag=wx.ALL, border=5)
        dropdown_sizer.Add(wx.StaticText(self, label="Minutos: "), flag=wx.ALL, border=5)
        dropdown_sizer.Add(start_minute_combo, flag=wx.ALL, border=5)

        # Replace the separate sizer.Add calls for the dropdown menus with a single call
        # sizer.Add(start_label, flag=wx.ALL, border=5)
        sizer.Add(dropdown_sizer, flag=wx.ALL, border=5)

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

        def on_hour_change(event):
            self.current_start_hour = int(start_hour_combo.GetValue())

        def on_minute_change(event):
            self.current_start_minute = int(start_minute_combo.GetValue())

        start_hour_combo.Bind(wx.EVT_COMBOBOX, on_hour_change)
        start_minute_combo.Bind(wx.EVT_COMBOBOX, on_minute_change)

        return v_sizer

    def on_save(self, event):
        start_hour = str(self.current_start_hour).zfill(2)
        start_minute = str(self.current_start_minute).zfill(2)
        end_hour = str(self.current_end_hour).zfill(2)
        end_minute = str(self.current_end_minute).zfill(2)

        ac_schedule_info = {
            "start_hour": start_hour,
            "start_minute": start_minute,
            "end_hour": end_hour,
            "end_minute": end_minute,
        }

        self.ac_schedule_info = ac_schedule_info
        # Add logic to save to serial controller or perform other actions

        wx.MessageBox("Values saved!", "Info", wx.OK | wx.ICON_INFORMATION)
