from ctypes import windll

import serial
import win32con
import wx
import wx.adv
import wx.lib.agw.aui as aui

from app.panels.ac_input import AcInputPanel
from app.panels.device_status import DeviceStatusPanel
from app.panels.digital_input import DigitalInputPanel
from app.panels.schedule_config import ScheduleConfigPanel
from app.dialogs.settings import SettingsDialog, EVT_PORT_CHANGED


def set_taskbar_icon(frame, icon_path):
	icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
	icon_handle = windll.user32.LoadImageW(0, icon_path, win32con.IMAGE_ICON, 0, 0, icon_flags)

	if icon_handle == 0:
		print("Failed to load icon")
		return

	windll.user32.SendMessageW(frame.GetHandle(), win32con.WM_SETICON, win32con.ICON_SMALL, icon_handle)


class MainFrame(wx.Frame):
	def __init__(self, parent, title, serial_controller):
		super(MainFrame, self).__init__(parent, title=title, size=(800, 600))

		self.serial_controller = serial_controller

		icon_path = "./assets/logo.ico"
		icon = wx.Icon(icon_path, wx.BITMAP_TYPE_ICO)
		self.SetIcon(icon)

		set_taskbar_icon(self, icon_path)

		self.Bind(wx.EVT_CLOSE, self.on_close)

		self.page_controller = aui.AuiNotebook(self)

		self.setup_menu_bar()

		self.toolbar = self.CreateToolBar()
		self.toolbar.SetToolBitmapSize((16, 16))
		self.setup_toolbar()

		self.toolbar.AddStretchableSpace()

		self.port_status_label = wx.StaticText(self.toolbar, label="Estado del puerto: ")
		self.toolbar.AddControl(self.port_status_label)

		self.port_status = wx.StaticText(self.toolbar, label="")
		self.toolbar.AddControl(self.port_status)

		self.toolbar.Realize()
		self.update_port_status()

		self.setup_tabs()

		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self.page_controller, 1, wx.EXPAND)

		self.Bind(EVT_PORT_CHANGED, self.on_port_changed)

		self.SetSizer(sizer)
		self.Layout()

	def on_close(self, event):
		self.Destroy()

	def setup_tabs(self):
		tabs = [
			("Estado del Dispositivo", DeviceStatusPanel),
			("Configuración de horarios", ScheduleConfigPanel),
			("Configuración de entrada de AC", AcInputPanel),
			("Configuración de entrada Digital", DigitalInputPanel),
			# ("Ajustes", SettingsView),
		]

		for tab_name, tab_class in tabs:
			page = tab_class(self, self.serial_controller)
			self.page_controller.AddPage(page, tab_name)

	def setup_menu_bar(self):
		# Create a menu bar
		menu_bar = wx.MenuBar()

		# Create a menu
		file_menu = wx.Menu()

		#create settings item
		settings_item = wx.MenuItem(file_menu, wx.ID_ANY, "&Ajustes")
		file_menu.Append(settings_item)

		self.Bind(wx.EVT_MENU, self.on_ajustes, id=settings_item.GetId())

		file_menu.AppendSeparator()
		
		# Create a menu item
		exit_item = wx.MenuItem(file_menu, wx.ID_EXIT, "&Exit\tAlt+F4")
		file_menu.Append(exit_item)

		# Bind the menu item to a method
		self.Bind(wx.EVT_MENU, self.on_close, id=wx.ID_EXIT)

		help_menu = wx.Menu()

		about_item = wx.MenuItem(help_menu, wx.ID_ANY, "&Acerca de")
		help_menu.Append(about_item)

		self.Bind(wx.EVT_MENU, self.on_about, id=about_item.GetId())

		# Add the menu to the menu bar
		menu_bar.Append(file_menu, "&Archivo")
		menu_bar.Append(help_menu, "&Ayuda")

		# Set the menu bar for the frame
		self.SetMenuBar(menu_bar)

	def setup_toolbar(self):
		open_port_id = wx.NewIdRef()
		close_port_id = wx.NewIdRef()
		ajustes_id = wx.NewIdRef()
		self.toolbar.AddTool(open_port_id, "Abrir Puerto", wx.Bitmap("./assets/connect.ico"))
		self.toolbar.AddTool(close_port_id, "Cerrar Puerto", wx.Bitmap("./assets/disconnect.ico"))
		self.toolbar.AddTool(ajustes_id, "Ajustes", wx.Bitmap("./assets/settings_icon.png"))

		self.toolbar.Realize()

		self.Bind(wx.EVT_TOOL, self.on_open_port, id=open_port_id)
		self.Bind(wx.EVT_TOOL, self.on_close_port, id=close_port_id)
		self.Bind(wx.EVT_TOOL, self.on_ajustes, id=ajustes_id)

		self.Bind(wx.EVT_TOOL, self.on_open_port, id=open_port_id)
		self.Bind(wx.EVT_TOOL, self.on_close_port, id=close_port_id)

	def on_ajustes(self, event):
		dialog = SettingsDialog(self, "Settings", self.serial_controller)
		dialog.ShowModal()
		dialog.Destroy()

	def on_about(self, event):
		wx.MessageBox(
			"ECM Config v1.0.0\n\n"
			"Desarrollado por:\n\n"
			"- Jorge Benavides Aspiazu\n\n\n"
			"\t2024 Energy Automation Technologies, todos los derechos reservados."
		)

	def on_open_port(self, event):
		if self.serial_controller.serial_created:
			self.serial_controller.open()
			print(f"Status of serial port {self.serial_controller.port} is "
				  f"{'open' if self.serial_controller.is_open() else 'closed'}")
		else:
			try:
				self.serial_controller.create_serial()
				self.serial_controller.serial_created = True
			except serial.SerialException:
				wx.MessageBox("Puerto Serial no disponible, seleccione otro")
		self.update_port_status()

	def on_close_port(self, event):
		if self.serial_controller.serial_created:
			self.serial_controller.close()
			print(f"Status of serial port {self.serial_controller.port} is "
				  f"{'open' if self.serial_controller.is_open() else 'closed'}")
		else:
			wx.MessageBox("Puerto Serial no disponible, seleccione otro")
		self.update_port_status()

	def update_port_status(self):
		try:
			if self.serial_controller.is_open():
				self.port_status.SetLabel("ABIERTO")
				self.port_status.SetForegroundColour(wx.GREEN)
			else:
				self.port_status.SetLabel("CERRADO")
				self.port_status.SetForegroundColour(wx.RED)
		except serial.SerialException:
			self.port_status.SetLabel("NO DISPONIBLE")
			self.port_status.SetForegroundColour(wx.RED)
		self.toolbar.Realize()

	def on_port_changed(self, event):
		new_port = event.get_port()
		self.serial_controller.update_port(new_port)

		if not self.serial_controller.open():
			wx.MessageBox("No se pudo abrir el puerto serial")
			self.serial_controller.serial_created = False
		else:
			self.serial_controller.close()
