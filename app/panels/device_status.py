import wx


class DeviceStatusPanel(wx.Panel):
	def __init__(self, parent, controller):
		super(DeviceStatusPanel, self).__init__(parent)

		self.controller = controller

		self.device_info = {
			"pulse_count": {"value": "", "text_ctrl": None},
			"schedule_control": {"value": "", "text_ctrl": None},
			"ac_input_enabled": {"value": "", "text_ctrl": None},
			"dc_input_mode": {"value": "", "text_ctrl": None},
		}

		self.init_ui()

	def init_ui(self):
		sizer = wx.BoxSizer(wx.VERTICAL)

		rows = [
			{"label": "Cuenta de Pulsos Actual", "key": "pulse_count"},
			{"label": "Control por horario", "key": "schedule_control"},
			{"label": "Entrada AC", "key": "ac_input_enabled"},
			{"label": "Entrada Digital", "key": "dc_input_mode"},
		]

		for row in rows:
			sizer.Add(self.create_card(row['label'], [row]))

		button = wx.Button(self, label="Leer valores")
		button.Bind(wx.EVT_BUTTON, self.on_read)

		sizer.Add(button, flag=wx.ALL, border=20)

		self.SetSizer(sizer)

	def on_read(self, event):
		if self.controller.is_open():
			pulse_count_hex_str = self.controller.send_command("AT+ACTIVEPULSES?$\r\n")
			print(f"Current pulse count: {pulse_count_hex_str}")
			pulse_count = int(pulse_count_hex_str, 16)
			print(f"Integer pulse count: {pulse_count}")
			self.device_info["pulse_count"]["text_ctrl"].SetValue(str(pulse_count))

			schedule_config = self.controller.send_command("AT+SCHEDULE?\r\n")
			print(f"Schedule config: {schedule_config}")
			self.device_info["schedule_control"]["text_ctrl"].SetValue(schedule_config)

			ac_input_schedule = self.controller.send_command("AT+ACINPUT?\r\n")
			print(f"AC input schedule: {ac_input_schedule}")
			self.device_info["ac_input_enabled"]["text_ctrl"].SetValue(ac_input_schedule)

			dc_input = self.controller.send_command("AT+IN3MODE?\r\n")
			print(f"DC input: {dc_input}")
			self.device_info["dc_input_mode"]["text_ctrl"].SetValue(dc_input)
		else:
			wx.MessageBox("No se pudo comunicar con el dispositivo")

	def create_card(self, title, rows):
		box = wx.StaticBox(self, label=title)
		sizer = wx.StaticBoxSizer(box, wx.VERTICAL)

		for row in rows:
			key = row['key']
			text_ctrl = wx.TextCtrl(self, value=str(self.device_info[key]["value"]), style=wx.TE_READONLY,
									size=(200, -1))
			self.device_info[key]["text_ctrl"] = text_ctrl

			label = wx.StaticText(self, label=f"{row['label']}:")
			label.SetFont(wx.Font(wx.FontInfo(12).Bold()))

			sizer.Add(label, flag=wx.ALL, border=5)
			sizer.Add(text_ctrl, flag=wx.EXPAND | wx.ALL, border=5)

		h_sizer = wx.BoxSizer(wx.HORIZONTAL)
		h_sizer.Add((20, 0))
		h_sizer.Add(sizer, 1, flag=wx.EXPAND)

		v_sizer = wx.BoxSizer(wx.VERTICAL)
		v_sizer.Add((0, 20))
		v_sizer.Add(h_sizer, 1, flag=wx.EXPAND)

		return v_sizer
