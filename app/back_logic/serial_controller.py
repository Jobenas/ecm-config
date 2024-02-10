import time

import serial
import serial.tools.list_ports


def list_available_serial_ports():
	ports = serial.tools.list_ports.comports()

	if not ports:
		print("No serial ports found.")
		return

	listed_ports = list()
	for port in ports:
		listed_ports.append(f"{port.device}")

	return listed_ports


class SerialController:
	def __init__(
			self,
			port: str,
			baudrate: int = 9600,
			byte_size: int = serial.EIGHTBITS,
			parity: str = serial.PARITY_NONE,
			stop_bits: int = serial.STOPBITS_ONE,
			timeout: float = 5.0,
	):
		self.port = port
		self.baudrate = baudrate
		self.byte_size = byte_size
		self.parity = parity
		self.stop_bits = stop_bits
		self.timeout = timeout

		self.serial_connection = None
		self.serial_created = False

		try:
			self.create_serial()
			self.serial_created = True
		except serial.SerialException:
			print("Serial port could not be opened.")
			self.serial = None

	def create_serial(self):
		self.serial = serial.Serial(
			port=self.port,
			baudrate=self.baudrate,
			bytesize=self.byte_size,
			parity=self.parity,
			stopbits=self.stop_bits,
			timeout=self.timeout,
		)

	def update_port(self, port: str):
		if self.serial is None:
			self.create_serial()
			self.serial_created = True
		self.port = port
		self.serial.port = port

	def open(self) -> bool:
		if not self.is_open():
			try:
				self.serial.open()
				self.serial_created = True
				return True
			except serial.serialutil.SerialException:
				print("Serial port could not be opened.")
				return False

	def close(self):
		self.serial.close()

	def is_open(self) -> bool:
		try:
			return self.serial.is_open
		except AttributeError:
			return False

	def send_command(self, command: str) -> str:
		self.serial.write(command.encode("utf-8"))
		time.sleep(1)
		try:
			data = self.serial.read_all()
		except serial.Timeout:
			data = ""

		return data.decode("utf-8")



