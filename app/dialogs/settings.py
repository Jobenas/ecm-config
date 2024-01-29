import wx

from app.back_logic.config_manager import save_to_config, get_from_config
from app.back_logic.serial_controller import list_available_serial_ports


class SettingsDialog(wx.Dialog):
    def __init__(self, parent, title, controller):
        super(SettingsDialog, self).__init__(parent, title=title, size=(400, 200))

        self.controller = controller

        self.init_ui()

    def init_ui(self):
        panel = wx.Panel(self)

        vbox = wx.BoxSizer(wx.VERTICAL)
        port_label = wx.StaticText(panel, label="Serial Port:")
        # self.port_dropdown = wx.Choice(panel, choices=self.controller.ports)

        selected_port = get_from_config("serial_port")

        available_ports = list_available_serial_ports()
        self.port_dropdown = wx.Choice(panel, choices=available_ports)
        self.port_dropdown.SetStringSelection(selected_port if selected_port is not None else "")

        vbox.Add(port_label, flag=wx.EXPAND | wx.LEFT | wx.TOP, border=10)
        vbox.Add(self.port_dropdown, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        hbox_btn = wx.BoxSizer(wx.HORIZONTAL)
        save_btn = wx.Button(panel, label="Save", size=(70, 30))
        cancel_btn = wx.Button(panel, label="Cancel", size=(70, 30))
        hbox_btn.Add(save_btn, flag=wx.LEFT, border=10)
        hbox_btn.Add(cancel_btn, flag=wx.LEFT, border=5)

        vbox.Add(hbox_btn, flag=wx.EXPAND | wx.ALL, border=10)

        panel.SetSizer(vbox)

        self.Bind(wx.EVT_BUTTON, self.on_save, save_btn)
        self.Bind(wx.EVT_BUTTON, self.on_cancel, cancel_btn)

    def on_save(self, event):
        selected_port = self.port_dropdown.GetStringSelection()
        print(selected_port)
        # self.controller.update_selected_port(selected_port)
        save_to_config("serial_port", selected_port)
        self.Close()

    def on_cancel(self, event):
        self.Close()
