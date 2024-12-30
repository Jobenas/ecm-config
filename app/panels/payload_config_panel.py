import wx
import wx.lib.scrolledpanel as scrolled

class PayloadConfigPanel(scrolled.ScrolledPanel):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # We'll store a list of rows, e.g.: {"position": 0, "assigned_value": "Pulse Counter 1"}
        self.msg_info = []

        # Mapping of numeric values to variable names
        self.VAR_TYPE_MAP = {
            0:  "Modbus Register 0",
            1:  "Modbus Register 1",
            2:  "Modbus Register 2",
            3:  "Modbus Register 3",
            4:  "Modbus Register 4",
            5:  "Modbus Register 5",
            6:  "Modbus Register 6",
            7:  "Modbus Register 7",
            8:  "Modbus Register 8",
            9:  "Modbus Register 9",
            10: "Pulse Counter 1",
            11: "Pulse Counter 2",
        }

        # Will store references to the widgets in each row
        self.row_controls = []

        # Flag that indicates whether we already placed a single combo box
        # for an unassigned row. We only allow one combo for the first unassigned.
        self.unassigned_combo_placed = False

        # Build the UI
        self.init_ui()

        # This call ensures we can scroll vertically (and/or horizontally).
        # By default, let’s allow Y scrolling, and disable X scrolling (scroll_x=False).
        self.SetupScrolling(scroll_x=False, scroll_y=True)

    def init_ui(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # ----- Title -----
        main_sizer.Add(
            self.create_title("Configuración de variables de mensaje"),
            flag=wx.EXPAND | wx.ALL,
            border=5
        )

        # Create one FlexGridSizer for the 2-column table (headers + data).
        self.table_sizer = wx.FlexGridSizer(rows=0, cols=2, hgap=10, vgap=5)
        self.table_sizer.SetFlexibleDirection(wx.HORIZONTAL)

        # ----- HEADERS -----
        header1 = wx.StaticText(self, label="Posición")
        header2 = wx.StaticText(self, label="Variable Asignada")

        self.table_sizer.Add(header1, flag=wx.ALL, border=5)
        self.table_sizer.Add(header2, flag=wx.ALL, border=5)

        main_sizer.Add(self.table_sizer, proportion=0, flag=wx.EXPAND | wx.ALL, border=5)

        # Divider line
        divider = wx.StaticLine(self)
        main_sizer.Add(divider, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=5)

        # ----- Buttons -----
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)

        update_button = wx.Button(self, label="Actualizar")
        update_button.Bind(wx.EVT_BUTTON, self.on_update)
        button_sizer.Add(update_button, flag=wx.ALL, border=5)

        reset_button = wx.Button(self, label="Reiniciar")
        reset_button.Bind(wx.EVT_BUTTON, self.on_reset)
        button_sizer.Add(reset_button, flag=wx.ALL, border=5)

        main_sizer.Add(button_sizer, flag=wx.ALIGN_CENTER | wx.ALL, border=10)

        # Tell the panel to use main_sizer for layout
        self.SetSizer(main_sizer)

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

    def on_enter(self):
        """
        Called when this panel becomes the selected tab in the notebook.
        We'll query the device for the MSGVAR values and populate them.
        Also shows a progress dialog while reading data.
        """
        print("Inside PayloadConfigPanel - reading from device...")

        if self.controller.is_open():
            # Show a small progress dialog
            dlg = wx.ProgressDialog(
                "Leyendo configuración",
                "Por favor espere mientras se lee la configuración...",
                maximum=1,
                parent=self,
                style=wx.PD_APP_MODAL | wx.PD_AUTO_HIDE
            )

            self.controller.send_command("AT+PROGMODE=1\r\n", False)
            cmd_response = self.controller.send_command("AT+MSGVAR?\r\n")
            self.controller.send_command("AT+PROGMODE=0\r\n", False)

            dlg.Update(1, "Lectura completada")
            dlg.Destroy()

            lines = cmd_response.split("\n")
            self.parse_msgvar_response(lines)
        else:
            # Fallback if device is not open
            self.msg_info = [
                {"position": i, "assigned_value": "unassigned"} for i in range(10)
            ]
            wx.MessageBox(
                "El puerto serial no está abierto.",
                "Error",
                wx.OK | wx.ICON_ERROR
            )

        self.clear_data_rows()
        self.populate_data_rows()

        # Recompute scrolling after data changes
        self.SetupScrolling(scroll_x=False, scroll_y=True)

    def parse_msgvar_response(self, lines):
        """
        Parse lines like '0 - 10' or '1 - unassigned'.
        """
        self.msg_info.clear()

        for line in lines:
            line = line.strip()
            if not line:
                continue
            if " - " not in line:
                continue

            parts = line.split(" - ")
            if len(parts) != 2:
                continue

            position_str, var_str = parts
            try:
                position = int(position_str)
            except ValueError:
                continue

            if var_str.lower() == "unassigned":
                assigned_value = "unassigned"
            else:
                try:
                    var_value = int(var_str)
                    assigned_value = self.VAR_TYPE_MAP.get(var_value, f"Desconocido ({var_value})")
                except ValueError:
                    assigned_value = f"Desconocido ({var_str})"

            self.msg_info.append({
                "position": position,
                "assigned_value": assigned_value
            })

        # Sort by position so they appear in ascending order
        self.msg_info.sort(key=lambda x: x["position"])

    def populate_data_rows(self):
        """
        Build the table rows.
        Only the FIRST unassigned row gets a ComboBox;
        all other unassigned rows remain 'unassigned' text.
        """
        # Reset the flag so each time we re-populate,
        # only one new combo can appear.
        self.unassigned_combo_placed = False

        # Build a reverse map: name -> code
        name_to_code = {v: k for k, v in self.VAR_TYPE_MAP.items()}

        # Figure out which codes are already assigned so we can remove them from the combo choices.
        assigned_codes = set()
        for item in self.msg_info:
            if item["assigned_value"] != "unassigned" and "Desconocido" not in item["assigned_value"]:
                code = name_to_code.get(item["assigned_value"], None)
                if code is not None:
                    assigned_codes.add(code)

        for row_data in self.msg_info:
            pos_str = str(row_data["position"])
            assigned_str = row_data["assigned_value"]

            # Column 1: Position
            pos_text = wx.StaticText(self, label=pos_str)
            self.table_sizer.Add(pos_text, flag=wx.ALL, border=5)

            # Column 2: either combo or static text
            if assigned_str == "unassigned":
                if not self.unassigned_combo_placed:
                    # Build a combo for the first unassigned row
                    combo_choices = []
                    for code, name in self.VAR_TYPE_MAP.items():
                        if code not in assigned_codes:
                            combo_choices.append(name)

                    assigned_ctrl = wx.ComboBox(
                        self,
                        choices=combo_choices,
                        style=wx.CB_READONLY
                    )
                    # Make it narrower
                    assigned_ctrl.SetMinSize((150, -1))

                    # Mark that we've placed our single combo
                    self.unassigned_combo_placed = True
                else:
                    # All other unassigned rows: show a static text "unassigned"
                    assigned_ctrl = wx.StaticText(self, label="unassigned")
            else:
                # It's assigned or "Desconocido(...)"
                assigned_ctrl = wx.StaticText(self, label=assigned_str)

            self.table_sizer.Add(assigned_ctrl, flag=wx.ALL, border=5)

            self.row_controls.append({
                "pos_text": pos_text,
                "assigned_ctrl": assigned_ctrl,  # could be a ComboBox or StaticText
            })

        # Force layout
        self.Layout()

        # Important: call SetupScrolling again after populating
        self.SetupScrolling(scroll_x=False, scroll_y=True)

    def clear_data_rows(self):
        """Remove existing data rows (not the header row) from the sizer."""
        for row_ctrls in self.row_controls:
            for widget in row_ctrls.values():
                self.table_sizer.Detach(widget)
                widget.Destroy()
        self.row_controls.clear()
        self.Layout()

    def on_update(self, event):
        """
        Refresh logic (similar to on_enter).
        But first, read the combo's selected value (if any),
        map it to the code, and show or store that code.
        """
        # 1) If we have a combo box (the first unassigned row),
        # read its value and find the code in VAR_TYPE_MAP
        name_to_code = {v: k for k, v in self.VAR_TYPE_MAP.items()}
        for row_ctrls in self.row_controls:
            assigned_ctrl = row_ctrls["assigned_ctrl"]
            if isinstance(assigned_ctrl, wx.ComboBox):
                chosen_name = assigned_ctrl.GetValue().strip()
                if chosen_name:
                    code = name_to_code.get(chosen_name)
                    print(f"Combo selection: '{chosen_name}' => code {code}")
                    self.controller.send_command("AT+PROGMODE=1\r\n", False)
                    res = self.controller.send_command(f"AT+MSGVAR={code}\r\n")
                    self.controller.send_command("AT+PROGMODE=0\r\n", False)
                else:
                    print("Combo selection is empty.")
                    # Show a dialog telling the user to select an option if needed.
                # There's only one combo box, so we can break after reading it.
                break

        # 2) Then do the normal refresh (which calls on_enter)
        self.on_enter()

    def on_reset(self, event):
        """Clear all assignments (make them 'unassigned')."""
        self.controller.send_command("AT+PROGMODE=1\r\n", False)
        self.controller.send_command("AT+MSGVAR=255\r\n")
        self.controller.send_command("AT+PROGMODE=0\r\n", False)

        wx.MessageBox(
            "Se ha reiniciado la configuración del payload.",
            "Info",
            wx.OK | wx.ICON_INFORMATION
        )

        self.on_enter()
