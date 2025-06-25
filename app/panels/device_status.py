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
        if not self.controller.is_open():
            wx.MessageBox("Error: No hay conexión con el dispositivo. Por favor, verifique la conexión.", 
                      "Error de conexión", wx.ICON_ERROR)
            return

        dlg = None
        try:
            self.controller.send_command("AT+PROGMODE=1\r\n", False)  # entering programming mode to stop the device
            time.sleep(1)
            self.controller.flush_buffer()
            
            dlg = wx.ProgressDialog(
                "Leyendo parámetros",
                "Por favor espere mientras se realiza la lectura",
                maximum=6,
                parent=self,
                style=wx.PD_APP_MODAL | wx.PD_AUTO_HIDE
            )

            network_type = ""
            device_id = ""
            pulse_count1 = 0
            pulse_count2 = 0
            schedule_config = ""
            ac_input_schedule = ""
            dc_input = ""

            # Read network type
            dlg.Update(0, "Leyendo la configuración de red...")
            network_response = self.controller.send_command("AT+NETWORK?\r\n")
            
            if network_response is None:
                raise Exception("No se recibió respuesta del dispositivo")
                
            print(f"Raw network response: {network_response}")
            
            try:
                network_type_parts = network_response.split("\r\n")[0].split(": ")
                if len(network_type_parts) > 1:
                    network_code = network_type_parts[1].strip()
                    print(f"Network code: {network_code}")
                    
                    # Map network code to human-readable name
                    network_types = {
                        "0": "Sigfox",
                        "1": "LoRaWAN",
                        "2": "Celular"
                    }
                    network_type = network_types.get(network_code, "Desconocido")
                else:
                    network_type = "Formato de respuesta no válido"
            except (IndexError, AttributeError) as e:
                print(f"Error parsing network response: {e}")
                network_type = "Error al leer"
            print(f"Network type: {network_type}")
            
            # Continue with reading other parameters
            dlg.Update(1, "Leyendo ID del dispositivo...")
            device_id_response = self.controller.send_command("AT+DEVID?\r\n")
            if device_id_response is None:
                raise Exception("No se pudo leer el ID del dispositivo")
            
            try:
                device_id = device_id_response.split("\r\n")[0].split(": ")[1].lstrip('0')  # Remove any leading 0 characters
            except (IndexError, AttributeError) as e:
                print(f"Error parsing device ID: {e}")
                raise Exception("Formato de ID de dispositivo no válido")
            
            dlg.Update(2, "Leyendo la cuenta de pulsos 1...")
            pulse_count_hex_str = self.controller.send_command("AT+PULSECOUNT1?\r\n")
            if pulse_count_hex_str is None:
                raise Exception("No se pudo leer la cuenta de pulsos 1")
            
            try:
                pulse_count_hex_str = pulse_count_hex_str.split("\r\n")[0]
                pulse_count1 = int(pulse_count_hex_str, 16)
            except (ValueError, IndexError) as e:
                print(f"Error parsing pulse count 1: {e}")
                pulse_count1 = 0
            
            dlg.Update(3, "Leyendo la cuenta de pulsos 2...")
            pulse_count_hex_str = self.controller.send_command("AT+PULSECOUNT2?\r\n")
            if pulse_count_hex_str is not None:
                try:
                    pulse_count_hex_str = pulse_count_hex_str.split("\r\n")[0]
                    pulse_count2 = int(pulse_count_hex_str, 16)
                except (ValueError, IndexError) as e:
                    print(f"Error parsing pulse count 2: {e}")
                    pulse_count2 = 0
            
            # Read schedule configuration
            dlg.Update(4, "Leyendo el control por horario...")
            try:
                schedule_config = self.controller.send_command("AT+SCHEDULE?\r\n")
                if schedule_config is not None:
                    schedule_config = schedule_config.split("\r\n")[0]
                    print(f"Schedule config: {schedule_config}")
                else:
                    schedule_config = ""
                    print("Warning: No se pudo leer la configuración de horario")
            except Exception as e:
                print(f"Error reading schedule config: {e}")
                schedule_config = ""

            # Read AC input schedule
            dlg.Update(5, "Leyendo la configuración de entrada AC...")
            try:
                ac_input_schedule = self.controller.send_command("AT+ACINPUT?\r\n")
                if ac_input_schedule is not None:
                    ac_input_schedule = ac_input_schedule.split("\r\n")[0]
                    print(f"AC input schedule: {ac_input_schedule}")
                else:
                    ac_input_schedule = ""
                    print("Warning: No se pudo leer la configuración de entrada AC")
            except Exception as e:
                print(f"Error reading AC input schedule: {e}")
                ac_input_schedule = ""

            # Read DC input mode
            dlg.Update(6, "Leyendo la configuración de entrada digital...")
            try:
                dc_input = self.controller.send_command("AT+IN3MODE?\r\n")
                if dc_input is not None:
                    dc_input = dc_input.split("\r\n")[0]
                    print(f"DC input: {dc_input}")
                else:
                    dc_input = ""
                    print("Warning: No se pudo leer la configuración de entrada digital")
            except Exception as e:
                print(f"Error reading DC input mode: {e}")
                dc_input = ""

            # Update UI with the collected data
            try:
                schedule_on = "No configurado"
                schedule_off = "No configurado"
                contactor_on = "No configurado"
                contactor_off = "No configurado"
                ac_on_schedule = "No configurado"
                ac_off_schedule = "No configurado"
                
                if schedule_config:
                    try:
                        schedule_config_list = schedule_config.split(',')
                        if len(schedule_config_list) >= 5:
                            schedule_on = f"{schedule_config_list[0]}:{schedule_config_list[1]}" if schedule_config_list[0] != "99" else "No configurado"
                            schedule_off = f"{schedule_config_list[3]}:{schedule_config_list[4]}" if schedule_config_list[3] != "99" else "No configurado"
                            contactor_on = ("Cerrado" if schedule_config_list[2] == "1" else "Abierto") if schedule_on != "No configurado" else "No configurado"
                            contactor_off = ("Abierto" if schedule_config_list[2] == "1" else "Cerrado") if schedule_off != "No configurado" else "No configurado"
                    except Exception as e:
                        print(f"Error parsing schedule config: {e}")
                
                if ac_input_schedule:
                    try:
                        ac_input_list = ac_input_schedule.split(',')
                        if len(ac_input_list) >= 4:
                            ac_on_schedule = f"{ac_input_list[0]}:{ac_input_list[1]}" if ac_input_list[0] != "99" else "No configurado"
                            ac_off_schedule = f"{ac_input_list[2]}:{ac_input_list[3]}" if ac_input_list[2] != "99" else "No configurado"
                    except Exception as e:
                        print(f"Error parsing AC input schedule: {e}")
                
                # Update all UI elements
                wx.CallAfter(self.device_info["network_type"]["text_ctrl"].SetValue, network_type)
                wx.CallAfter(self.device_info["device_id"]["text_ctrl"].SetValue, device_id)
                wx.CallAfter(self.device_info["pulse_count1"]["text_ctrl"].SetValue, str(pulse_count1))
                wx.CallAfter(self.device_info["pulse_count2"]["text_ctrl"].SetValue, str(pulse_count2))
                wx.CallAfter(self.device_info["on_schedule"]["text_ctrl"].SetValue, schedule_on)
                wx.CallAfter(self.device_info["off_schedule"]["text_ctrl"].SetValue, schedule_off)
                wx.CallAfter(self.device_info["on_contactor_state"]["text_ctrl"].SetValue, contactor_on)
                wx.CallAfter(self.device_info["off_contactor_state"]["text_ctrl"].SetValue, contactor_off)
                wx.CallAfter(self.device_info["start_schedule"]["text_ctrl"].SetValue, ac_on_schedule)
                wx.CallAfter(self.device_info["end_schedule"]["text_ctrl"].SetValue, ac_off_schedule)
                wx.CallAfter(self.device_info["dc_input_mode"]["text_ctrl"].SetValue, 
                           "Solo alerta" if dc_input and "OPENING_DETECTION" in dc_input else "Conmutación de relé")
            except Exception as e:
                print(f"Error updating UI: {e}")
                wx.CallAfter(wx.MessageBox, f"Error al actualizar la interfaz de usuario: {str(e)}", "Error", wx.ICON_ERROR)

        except Exception as e:
            print(f"Error in on_read: {e}")
            wx.CallAfter(wx.MessageBox, f"Error al leer del dispositivo: {str(e)}", "Error de comunicación", wx.ICON_ERROR)
        finally:
            try:
                # Exit programming mode
                self.controller.send_command("AT+PROGMODE=0\r\n", False)
                # Ensure progress dialog is destroyed
                if dlg:
                    dlg.Destroy()
            except Exception as e:
                print(f"Error during cleanup: {e}")

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
