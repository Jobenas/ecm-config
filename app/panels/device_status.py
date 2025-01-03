import time

import wx


class DeviceStatusPanel(wx.ScrolledWindow):
	def __init__(self, parent, controller):
		super(DeviceStatusPanel, self).__init__(parent)

		self.controller = controller

		self.device_info = {
			"network_type": {"value": "", "text_ctrl": None},
			"device_id": {"value": "", "text_ctrl": None},
			"pulse_count1": {"value": "", "text_ctrl": None},
			"pulse_count2": {"value": "", "text_ctrl": None},
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
						"type": "multi-item",
						"items": [
							{"label": "Tipo de Red", "key": "network_type", "type": "single"},
							{"label": "ID de Dispositivo", "key": "device_id", "type": "single"},
						]
					},
				],
				"title": "Configuración de Red",
				"type": "multiple",
			},
			{
				"rows": [
					{
						"type": "multi-item",
						"items": [
							{"label": "Cuenta de Pulsos 1", "key": "pulse_count1", "type": "single"},
							{"label": "Cuenta de Pulsos 2", "key": "pulse_count2", "type": "single"},
						],
					},
				],
				"title": "Cuentas de Pulsos Actuales",
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
				"title": "Control de la entrada AC",
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
				"title": "Configuración de la Entrada Digital",
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
			self.controller.send_command("AT+PROGMODE=1\r\n", False)  # entering programming mode to stop the device
			time.sleep(1)
			self.controller.flush_buffer()
			# from sending data via Modbus
			dlg = wx.ProgressDialog(
				"Leyendo parámetros",
				"Por favor espere mientras se realiza la lectura",
				maximum=6,
				parent=self,
				style=wx.PD_APP_MODAL | wx.PD_AUTO_HIDE
			)
			network_type = self.controller.send_command("AT+NETWORK?\r\n")
			print(f"Raw network type value: {network_type}")
			network_type = network_type.split("\r\n")[0].split(": ")[1]
			print(f"Raw network type value: {network_type}")
			match network_type:
				case "0":
					network_type = "Sigfox"
				case "1":
					network_type = "LoRaWAN"
				case "2":
					network_type = "Celular"
				case _:
					network_type = "Desconocido"
			print(f"Network type: {network_type}")
			dlg.Update(0, "Leyendo la configuración de red...")

			device_id = self.controller.send_command("AT+DEVID?\r\n")
			device_id = device_id.split("\r\n")[0].split(": ")[1].lstrip('0')  # Remove any leading 0 characters
			print(f"Device ID: {device_id}")
			dlg.Update(1, "Leyendo el ID del dispositivo...")

			pulse_count_hex_str = self.controller.send_command("AT+PULSECOUNT1?\r\n")
			print(f"Current pulse count: {pulse_count_hex_str}")
			pulse_count_hex_str = pulse_count_hex_str.split("\r\n")[0]
			pulse_count1 = int(pulse_count_hex_str, 16)
			print(f"Integer pulse count: {pulse_count1}")
			dlg.Update(2, "Leyendo la cuenta de pulsos 1...")

			pulse_count_hex_str = self.controller.send_command("AT+PULSECOUNT2?\r\n")
			print(f"Current pulse count: {pulse_count_hex_str}")
			pulse_count_hex_str = pulse_count_hex_str.split("\r\n")[0]
			pulse_count2 = int(pulse_count_hex_str, 16)
			print(f"Integer pulse count: {pulse_count2}")
			dlg.Update(3, "Leyendo la cuenta de pulsos 2...")

			schedule_config = self.controller.send_command("AT+SCHEDULE?\r\n")
			schedule_config = schedule_config.split("\r\n")[0]
			print(f"Schedule config: {schedule_config}")
			dlg.Update(4, "Leyendo el control por horario...")

			ac_input_schedule = self.controller.send_command("AT+ACINPUT?\r\n")
			ac_input_schedule = ac_input_schedule.split("\r\n")[0]
			print(f"AC input schedule: {ac_input_schedule}")
			dlg.Update(5, "Leyendo la configuración de entrada AC...")

			dc_input = self.controller.send_command("AT+IN3MODE?\r\n")
			dc_input = dc_input.split("\r\n")[0]
			print(f"DC input: {dc_input}")
			dlg.Update(6, "Leyendo la configuración de entrada digital...")

			dlg.Destroy()

			self.controller.send_command("AT+PROGMODE=0\r\n", False)  # exiting programming mode to start the device

			schedule_config_list = schedule_config[:-2].split(",")
			schedule_on = f"{schedule_config_list[0]}:{schedule_config_list[1]}" if schedule_config_list[0] != "99" else "No configurado"
			schedule_off = f"{schedule_config_list[3]}:{schedule_config_list[4]}" if schedule_config_list[3] != "99" else "No configurado"
			contactor_on = ("Cerrado" if schedule_config_list[2] == "1" else "Abierto") if schedule_on != "No configurado" else "No configurado"
			contactor_off = ("Abierto" if schedule_config_list[2] == "1" else "Cerrado") if schedule_off != "No configurado" else "No configurado"

			ac_input_list = ac_input_schedule[:-2].split(",")
			ac_on_schedule = f"{ac_input_list[0]}:{ac_input_list[1]}" if ac_input_list[0] != "99" else "No configurado"
			ac_off_schedule = f"{ac_input_list[2]}:{ac_input_list[3]}" if ac_input_list[2] != "99" else "No configurado"

			self.device_info["network_type"]["text_ctrl"].SetValue(network_type)
			self.device_info["device_id"]["text_ctrl"].SetValue(device_id)
			self.device_info["pulse_count1"]["text_ctrl"].SetValue(str(pulse_count1))
			self.device_info["pulse_count2"]["text_ctrl"].SetValue(str(pulse_count2))
			self.device_info["on_schedule"]["text_ctrl"].SetValue(schedule_on)
			self.device_info["off_schedule"]["text_ctrl"].SetValue(schedule_off)
			self.device_info["on_contactor_state"]["text_ctrl"].SetValue(contactor_on)
			self.device_info["off_contactor_state"]["text_ctrl"].SetValue(contactor_off)
			self.device_info["start_schedule"]["text_ctrl"].SetValue(ac_on_schedule)
			self.device_info["end_schedule"]["text_ctrl"].SetValue(ac_off_schedule)
			self.device_info["dc_input_mode"]["text_ctrl"].SetValue("Solo alerta" if "OPENING_DETECTION" in dc_input else "Conmutación de relé")
		else:
			wx.MessageBox("No se pudo comunicar con el dispositivo")

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
