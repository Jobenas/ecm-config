import wx

from app.back_logic.config_manager import get_from_config
from app.back_logic.serial_controller import SerialController
from app.dir_paths import ASSETS_DIR
from app.main_screen import MainFrame


class App(wx.App):
	def OnInit(self):
		# Load the splash screen image from assets (using logo-recortado.jpg)
		splash_image_path = f"{ASSETS_DIR}/logo-recortado.jpg"
		splash_image = wx.Image(splash_image_path, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
		splash_screen = wx.adv.SplashScreen(
			splash_image,
			wx.adv.SPLASH_CENTRE_ON_SCREEN | wx.adv.SPLASH_TIMEOUT,
			500,
			None,
		)

		self.setup_main_frame()
		return True

	def setup_main_frame(self):
		selected_port = get_from_config("serial_port")
		baudrate = get_from_config("baud_rate")
		comms_controller = SerialController(selected_port, baudrate=baudrate)

		# Create the main frame
		frame = MainFrame(None, "ECM Config", comms_controller)

		# Set the custom icon for the frame so that it shows on the taskbar and title bar.
		# Make sure 'logo.ico' is in the ASSETS_DIR.
		icon_path = f"{ASSETS_DIR}/logo.ico"
		frame.SetIcon(wx.Icon(icon_path, wx.BITMAP_TYPE_ICO))

		frame.Show(True)
		self.SetTopWindow(frame)


def main():
	app = App(False)
	app.MainLoop()


if __name__ == "__main__":
	main()
