import wx


class DigitalInputPanel(wx.ScrolledWindow):
    def __init__(self, parent, serial_comms_controller):
        super(DigitalInputPanel, self).__init__(parent)

        self.serial_comms_controller = serial_comms_controller

        self.digital_input_modes = ["Solo alerta", "Conmutación de relé"]

        self.configured_digital_input_mode = ""
        self.current_digital_input_mode = "Solo alerta"

        self.init_ui()
        self.SetScrollRate(5, 5)

    def init_ui(self):
        sizer = wx.BoxSizer(wx.VERTICAL)

        sizer.Add(self.create_title("Configuración actual de la entrada digital"))
        sizer.AddSpacer(15)
        sizer.Add(self.create_status_card("Estado de la entrada digital"))
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
        print("This is where we read the digital input config")

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

    def create_status_card(self, title):
        box = wx.StaticBox(self, label=title)
        box.SetFont(wx.Font(wx.FontInfo(9).Bold()))
        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)

        text_ctrl = wx.TextCtrl(
            self, value=self.get_status_text(), style=wx.TE_READONLY, size=(200, -1)
        )
        label = wx.StaticText(self, label=f"Estado:")
        label.SetFont(wx.Font(wx.FontInfo(8)))

        sizer.Add(label, flag=wx.ALL, border=5)
        sizer.Add(text_ctrl, flag=wx.EXPAND | wx.ALL, border=5)

        h_sizer = wx.BoxSizer(wx.HORIZONTAL)
        h_sizer.Add((20, 0))  # Add left padding
        h_sizer.Add(sizer, 1, flag=wx.EXPAND)

        v_sizer = wx.BoxSizer(wx.VERTICAL)
        v_sizer.Add((0, 20))  # Add top padding
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

        wx.MessageBox(
            f"Values saved! Digital Input Mode: {digital_input_mode}",
            "Info",
            wx.OK | wx.ICON_INFORMATION,
        )

        # Add logic to save to serial controller or perform other actions

    def get_status_text(self):
        return (
            f"Solo envio Alertas"
            if self.configured_digital_input_mode == "1"
            else f"Conmutación de relé"
        )
