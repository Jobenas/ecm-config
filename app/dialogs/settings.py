import wx

from app.back_logic.config_manager import save_to_config, get_from_config
from app.back_logic.serial_controller import list_available_serial_ports

my_EVT_PORT_CHANGED = wx.NewEventType()
EVT_PORT_CHANGED = wx.PyEventBinder(my_EVT_PORT_CHANGED, 1)


class PortChangedEvent(wx.PyCommandEvent):
    def __init__(self, etype, eid, port):
        super(PortChangedEvent, self).__init__(etype, eid)
        self.port = port

    def get_port(self):
        return self.port


class SettingsDialog(wx.Dialog):
    def __init__(self, parent, title, controller):
        super(SettingsDialog, self).__init__(parent, title=title, size=(400, 200))

        self.controller = controller
        self.init_ui()

    def init_ui(self):
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        # Port selection row
        port_box = wx.StaticBox(panel, label="Configuración de Puerto Serial")
        port_box_sizer = wx.StaticBoxSizer(port_box, wx.VERTICAL)
        
        port_hbox = wx.BoxSizer(wx.HORIZONTAL)
        port_label = wx.StaticText(panel, label="Puerto:")
        
        # Add refresh button
        refresh_btn = wx.Button(panel, label="Actualizar", size=(80, -1))
        refresh_btn.Bind(wx.EVT_BUTTON, self.on_refresh_ports)
        
        # Get saved port (just the COMx part)
        saved_port = get_from_config("serial_port")
        
        # Get available ports and populate dropdown
        self.available_ports = list_available_serial_ports()
        self.port_dropdown = wx.Choice(panel, choices=self.available_ports, size=(250, -1))
        
        # Try to select the saved port if it exists
        if saved_port:
            # Find the full port string that starts with the saved port
            for i, port in enumerate(self.available_ports):
                if port.startswith(saved_port):
                    self.port_dropdown.SetSelection(i)
                    break
        
        port_hbox.Add(port_label, flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=5)
        port_hbox.Add(self.port_dropdown, proportion=1, flag=wx.EXPAND | wx.RIGHT, border=5)
        port_hbox.Add(refresh_btn, flag=wx.LEFT, border=5)
        
        port_box_sizer.Add(port_hbox, flag=wx.EXPAND | wx.ALL, border=10)
        
        # Baud rate selection
        baud_hbox = wx.BoxSizer(wx.HORIZONTAL)
        baud_label = wx.StaticText(panel, label="Baud Rate:")
        
        selected_baud_rate = get_from_config("baud_rate")
        baud_rate_choices = ["9600", "14400", "19200", "38400", "57600", "115200"]
        self.baud_rate_dropdown = wx.Choice(panel, choices=baud_rate_choices)
        self.baud_rate_dropdown.SetStringSelection(selected_baud_rate if selected_baud_rate else "9600")
        
        baud_hbox.Add(baud_label, flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=5)
        baud_hbox.Add(self.baud_rate_dropdown, flag=wx.EXPAND | wx.RIGHT, border=5)
        
        port_box_sizer.Add(baud_hbox, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=10)
        
        # Add port configuration to main sizer
        vbox.Add(port_box_sizer, flag=wx.EXPAND | wx.ALL, border=10)

        hbox_btn = wx.BoxSizer(wx.HORIZONTAL)
        save_btn = wx.Button(panel, label="Guardar", size=(70, 30))
        cancel_btn = wx.Button(panel, label="Cancelar", size=(70, 30))
        hbox_btn.Add(save_btn, flag=wx.LEFT, border=10)
        hbox_btn.Add(cancel_btn, flag=wx.LEFT, border=5)

        vbox.Add(hbox_btn, flag=wx.EXPAND | wx.ALL, border=10)

        panel.SetSizer(vbox)

        self.Bind(wx.EVT_BUTTON, self.on_save, save_btn)
        self.Bind(wx.EVT_BUTTON, self.on_cancel, cancel_btn)

    def on_refresh_ports(self, event):
        """Refresh the list of available serial ports"""
        current_selection = self.port_dropdown.GetStringSelection()
        self.available_ports = list_available_serial_ports()
        self.port_dropdown.SetItems(self.available_ports)
        
        # Try to restore the previous selection if it still exists
        if current_selection in self.available_ports:
            self.port_dropdown.SetStringSelection(current_selection)
        elif self.available_ports:
            self.port_dropdown.SetSelection(0)
    
    def on_save(self, event):
        """
        Called when the user clicks "Guardar". We save the selected port + baud rate,
        update the controller's baud rate, and fire our custom event to notify the parent.
        """
        selected_port = self.port_dropdown.GetStringSelection()
        selected_baud_rate = self.baud_rate_dropdown.GetStringSelection()
        
        # Extract just the COM port part if it's in the new format
        port_to_save = selected_port.split(' - ')[0].strip() if ' - ' in selected_port else selected_port

        # Save to config first in case something goes wrong
        previous_port = get_from_config("serial_port")
        save_to_config("serial_port", port_to_save)
        save_to_config("baud_rate", selected_baud_rate)

        # Update the controller's baud rate
        self.controller.update_baud_rate(int(selected_baud_rate))
        
        try:
            # Try to update the port
            self.controller.update_port(port_to_save)
            
            # If we get here, the port was changed successfully
            # Fire our custom event so MainFrame can update its UI
            evt = PortChangedEvent(my_EVT_PORT_CHANGED, -1, port_to_save)
            wx.PostEvent(self.GetParent(), evt)
            self.Close()
            
        except Exception as e:
            # If port change failed, revert to previous port in config
            save_to_config("serial_port", previous_port)
            wx.MessageBox(
                f"No se pudo cambiar al puerto {port_to_save}. Error: {str(e)}\n\n"
                f"Se ha restaurado la configuración anterior.",
                "Error al cambiar el puerto",
                wx.OK | wx.ICON_ERROR
            )
            # Update the dropdown to show the previous port
            for i, port in enumerate(self.available_ports):
                if port.startswith(previous_port):
                    self.port_dropdown.SetSelection(i)
                    break

    def on_cancel(self, event):
        self.Close()
