import wx
import wx.adv
import wx.lib.agw.aui as aui
import serial
import win32con
from ctypes import windll

from app.dialogs.display_config import DisplayConfigDialog
from app.dir_paths import ASSETS_DIR
from app.panels.ac_input import AcInputPanel
from app.panels.device_status import DeviceStatusPanel
from app.panels.digital_input import DigitalInputPanel
from app.panels.schedule_config import ScheduleConfigPanel
from app.panels.modbus_config import ModbusConfigPanel
from app.panels.payload_config_panel import PayloadConfigPanel

from app.back_logic.config_manager import get_from_config
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
		super(MainFrame, self).__init__(parent, title=title, size=(1200, 700))

		self.serial_controller = serial_controller

		icon_path = f"{ASSETS_DIR}/logo.ico"
		icon = wx.Icon(icon_path, wx.BITMAP_TYPE_ICO)
		self.SetIcon(icon)
		set_taskbar_icon(self, icon_path)

		self.Bind(wx.EVT_CLOSE, self.on_close)

		self.page_controller = aui.AuiNotebook(self)
		self.page_controller.Bind(aui.EVT_AUINOTEBOOK_PAGE_CHANGED, self.on_tab_changed)

		self.setup_menu_bar()

		self.toolbar = self.CreateToolBar()
		self.toolbar.SetToolBitmapSize((16, 16))
		self.setup_toolbar()

		self.toolbar.AddStretchableSpace()

		self.selected_port = wx.StaticText(self.toolbar, label=f"Puerto: {self.serial_controller.port}")
		self.toolbar.AddControl(self.selected_port)

		self.vertical_spacer = wx.StaticText(self.toolbar, label="\t\t")
		self.toolbar.AddControl(self.vertical_spacer)

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

		self.page_controller.Bind(aui.EVT_AUINOTEBOOK_PAGE_CLOSE, self.on_page_close)

	def on_tab_changed(self, event):
		new_selection = event.GetSelection()
		page = self.page_controller.GetPage(new_selection)

		# If the tab is ModbusConfigPanel or PayloadConfigPanel, call on_enter
		if isinstance(page, ModbusConfigPanel):
			page.on_enter()
		elif isinstance(page, PayloadConfigPanel):
			page.on_enter()

		event.Skip()

	def on_page_close(self, event):
		# Prevent the tab from closing
		event.Veto()

	def on_close(self, event):
		if self.serial_controller.is_open():
			self.serial_controller.close()
		self.Destroy()

	def setup_tabs(self):
		tabs = [
			("Estado del Dispositivo", DeviceStatusPanel),
			("Configuración de horarios", ScheduleConfigPanel),
			("Configuración de entrada de AC", AcInputPanel),
			("Configuración de entrada Digital", DigitalInputPanel),
			("Configuración de lectura Modbus", ModbusConfigPanel),
			("Configuración de Mensaje", PayloadConfigPanel),
		]
		for tab_name, tab_class in tabs:
			page = tab_class(self, self.serial_controller)
			self.page_controller.AddPage(page, tab_name)

	def setup_menu_bar(self):
		menu_bar = wx.MenuBar()
		file_menu = wx.Menu()

		settings_item = wx.MenuItem(file_menu, wx.ID_ANY, "&Ajustes")
		file_menu.Append(settings_item)
		self.Bind(wx.EVT_MENU, self.on_ajustes, id=settings_item.GetId())

		file_menu.AppendSeparator()

		exit_item = wx.MenuItem(file_menu, wx.ID_EXIT, "&Exit\tAlt+F4")
		file_menu.Append(exit_item)
		self.Bind(wx.EVT_MENU, self.on_close, id=wx.ID_EXIT)

		help_menu = wx.Menu()
		about_item = wx.MenuItem(help_menu, wx.ID_ANY, "&Acerca de")
		help_menu.Append(about_item)
		self.Bind(wx.EVT_MENU, self.on_about, id=about_item.GetId())

		menu_bar.Append(file_menu, "&Archivo")
		menu_bar.Append(help_menu, "&Ayuda")
		self.SetMenuBar(menu_bar)

	def setup_toolbar(self):
		open_port_id = wx.NewIdRef()
		close_port_id = wx.NewIdRef()
		display_config_id = wx.NewIdRef()
		ajustes_id = wx.NewIdRef()

		self.toolbar.AddTool(open_port_id, "Abrir Puerto", wx.Bitmap(f"{ASSETS_DIR}/connect.ico"))
		self.toolbar.AddTool(close_port_id, "Cerrar Puerto", wx.Bitmap(f"{ASSETS_DIR}/disconnect.ico"))
		self.toolbar.AddTool(display_config_id, "Configurar Display externo", wx.Bitmap(f"{ASSETS_DIR}/display.ico"))
		self.toolbar.AddTool(ajustes_id, "Ajustes", wx.Bitmap(f"{ASSETS_DIR}/settings_icon.png"))

		self.toolbar.Realize()

		self.Bind(wx.EVT_TOOL, self.on_open_port, id=open_port_id)
		self.Bind(wx.EVT_TOOL, self.on_close_port, id=close_port_id)
		self.Bind(wx.EVT_TOOL, self.on_display_config, id=display_config_id)
		self.Bind(wx.EVT_TOOL, self.on_ajustes, id=ajustes_id)

	def on_ajustes(self, event):
		dialog = SettingsDialog(self, "Settings", self.serial_controller)
		dialog.ShowModal()
		dialog.Destroy()

	def on_display_config(self, event):
		dialog = DisplayConfigDialog(self, "Configurar display", self.serial_controller)
		dialog.ShowModal()
		dialog.Destroy()

	def on_about(self, event):
		wx.MessageBox(
			"ECM Config v1.1.2\n\n"
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
		"""
		Updates the toolbar text to reflect whether the port is open or closed,
		and which port is selected.
		"""
		# Update the "Puerto: XXX" label
		self.selected_port.SetLabel(f"Puerto: {self.serial_controller.port}")

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
		"""
		Called when the SettingsDialog is closed and the user saved changes to
		port or baud rate. We'll use the new port, re-open it immediately (if possible),
		and refresh the toolbar text.
		"""
		new_port = event.get_port()

		# The user might also have changed baud rate, so re-check config:
		new_baud_rate = get_from_config("baud_rate")
		if new_baud_rate is not None:
			self.serial_controller.update_baud_rate(int(new_baud_rate))

		# Update the port in the controller
		self.serial_controller.update_port(new_port)

		# Attempt to open the port immediately with the new settings
		if not self.serial_controller.is_open():
			if not self.serial_controller.open():
				wx.MessageBox("No se pudo abrir el puerto serial con la nueva configuración.")
				self.serial_controller.serial_created = False
		else:
			# If it was already open with an old port, close and re-open
			self.serial_controller.close()
			self.serial_controller.open()

		# Now reflect the changes on the toolbar
		self.update_port_status()
