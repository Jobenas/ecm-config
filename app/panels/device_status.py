import wx


class DeviceStatusPanel(wx.ScrolledWindow):
	def __init__(self, parent, controller):
		super(DeviceStatusPanel, self).__init__(parent)

		self.controller = controller

		self.device_info = {
			"pulse_count": {"value": "", "text_ctrl": None},
			"dc_input_mode": {"value": "", "text_ctrl": None},
			"on_schedule": {"value": "", "text_ctrl": None},
			"off_schedule": {"value": "", "text_ctrl": None},
			"on_contactor_state": {"value": "", "text_ctrl": None},
			"off_contactor_state": {"value": "", "text_ctrl": None},
			"start_schedule": {"value": "", "text_ctrl": None},
			"end_schedule": {"value": "", "text_ctrl": None},
		}

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
							{"label": "Cuenta de Pulsos Actual", "key": "pulse_count", "type": "single"},
						],
					},
				],
				"title": "Cuenta de Pulsos Actual",
				"type": "multiple"
			},
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

		for row in rows:
			sizer.Add(self.create_card(row['title'], row["rows"]))

		button = wx.Button(self, label="Leer valores")
		button.Bind(wx.EVT_BUTTON, self.on_read)

		sizer.Add(button, flag=wx.ALL, border=20)

		self.SetSizer(sizer)

	def on_read(self, event):
		if self.controller.is_open():
			dlg = wx.ProgressDialog(
				"Leyendo parámetros",
				"Por favor espere mientras se realiza la lectura",
				maximum=4,
				parent=self,
				style=wx.PD_APP_MODAL | wx.PD_AUTO_HIDE
			)
			pulse_count_hex_str = self.controller.send_command("AT+ACTIVEPULSES?\r\n")
			print(f"Current pulse count: {pulse_count_hex_str}")
			pulse_count = int(pulse_count_hex_str, 16)
			print(f"Integer pulse count: {pulse_count}")
			dlg.Update(1, "Leyendo la cuenta de pulsos...")

			schedule_config = self.controller.send_command("AT+SCHEDULE?\r\n")
			print(f"Schedule config: {schedule_config}")
			dlg.Update(2, "Leyendo el control por horario...")

			ac_input_schedule = self.controller.send_command("AT+ACINPUT?\r\n")
			print(f"AC input schedule: {ac_input_schedule}")
			dlg.Update(3, "Leyendo la configuración de entrada AC...")

			dc_input = self.controller.send_command("AT+IN3MODE?\r\n")
			print(f"DC input: {dc_input}")
			dlg.Update(4, "Leyendo la configuración de entrada digital...")

			dlg.Destroy()

			schedule_config_list = schedule_config[:-2].split(",")
			schedule_on = f"{schedule_config_list[0]}:{schedule_config_list[1]}" if schedule_config_list[0] != "99" else "No configurado"
			schedule_off = f"{schedule_config_list[3]}:{schedule_config_list[4]}" if schedule_config_list[3] != "99" else "No configurado"
			contactor_on = ("Cerrado" if schedule_config_list[2] == "1" else "Abierto") if schedule_on != "No configurado" else "No configurado"
			contactor_off = ("Abierto" if schedule_config_list[2] == "1" else "Cerrado") if schedule_off != "No configurado" else "No configurado"

			ac_input_list = ac_input_schedule[:-2].split(",")
			ac_on_schedule = f"{ac_input_list[0]}:{ac_input_list[1]}" if ac_input_list[0] != "99" else "No configurado"
			ac_off_schedule = f"{ac_input_list[2]}:{ac_input_list[3]}" if ac_input_list[2] != "99" else "No configurado"

			self.device_info["pulse_count"]["text_ctrl"].SetValue(str(pulse_count))
			self.device_info["on_schedule"]["text_ctrl"].SetValue(schedule_on)
			self.device_info["off_schedule"]["text_ctrl"].SetValue(schedule_off)
			self.device_info["on_contactor_state"]["text_ctrl"].SetValue(contactor_on)
			self.device_info["off_contactor_state"]["text_ctrl"].SetValue(contactor_off)
			self.device_info["start_schedule"]["text_ctrl"].SetValue(ac_on_schedule)
			self.device_info["end_schedule"]["text_ctrl"].SetValue(ac_off_schedule)
			self.device_info["dc_input_mode"]["text_ctrl"].SetValue(dc_input)
		else:
			wx.MessageBox("No se pudo comunicar con el dispositivo")

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
				text_ctrl = wx.TextCtrl(self, value=str(self.device_info[key]['value']),
										style=wx.TE_READONLY, size=(50, -1))
				self.device_info[key]["text_ctrl"] = text_ctrl
				grid_sizer.Add(text_ctrl, flag=wx.EXPAND | wx.ALL, border=5)

			sizer.Add(grid_sizer, flag=wx.EXPAND)

		h_sizer = wx.BoxSizer(wx.HORIZONTAL)
		h_sizer.Add((20, 0))
		h_sizer.Add(sizer, 1, flag=wx.EXPAND)

		v_sizer = wx.BoxSizer(wx.VERTICAL)
		v_sizer.Add((0, 20))
		v_sizer.Add(h_sizer, 1, flag=wx.EXPAND)

		return v_sizer
