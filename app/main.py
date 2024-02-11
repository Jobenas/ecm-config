import wx

from app.back_logic.config_manager import get_from_config
from app.back_logic.serial_controller import SerialController
from app.dir_paths import ASSETS_DIR
from app.main_screen import MainFrame


class App(wx.App):
	def OnInit(self):
		splash_image = wx.Image(f"{ASSETS_DIR}/logo-recortado.jpg", wx.BITMAP_TYPE_ANY).ConvertToBitmap()
		# Create a splash screen
		splash_screen = wx.adv.SplashScreen(
			splash_image,
			wx.adv.SPLASH_CENTRE_ON_SCREEN | wx.adv.SPLASH_TIMEOUT,
			500,
			None
		)

		self.setup_main_frame()

		return True

	def setup_main_frame(self):
		selected_port = get_from_config("serial_port")
		comms_controller = SerialController(selected_port)
		frame = MainFrame(None, "ECM Config", comms_controller)
		frame.Show(True)
		self.SetTopWindow(frame)


def main():
	app = App(False)

	app.MainLoop()


if __name__ == "__main__":
	main()
