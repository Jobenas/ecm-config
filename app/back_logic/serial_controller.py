import time

import serial
import serial.tools.list_ports


def list_available_serial_ports():
    """
    Returns a list of available serial ports with their descriptions.
    Each port is formatted as: 'COM1 - USB Serial Device (COM1)'
    """
    ports = serial.tools.list_ports.comports()
    
    if not ports:
        print("No serial ports found.")
        return ["No ports available"]
    
    listed_ports = []
    for port in sorted(ports):
        description = port.description if port.description else 'Unknown Device'
        listed_ports.append(f"{port.device} - {description}")
    
    return listed_ports


class SerialController:
	def __init__(
			self,
			port: str,
			baudrate: int = 9600,
			byte_size: int = serial.EIGHTBITS,
			parity: str = serial.PARITY_NONE,
			stop_bits: int = serial.STOPBITS_ONE,
			timeout: float = 10.0,
	):
		self.port = port
		self.baudrate = baudrate if baudrate is not None else 9600  # set default baud rate to 9600
		self.byte_size = byte_size
		self.parity = parity
		self.stop_bits = stop_bits
		self.timeout = timeout

		self.serial = None
		self.serial_created = False

		try:
			self.create_serial()
			self.serial_created = True
		except serial.SerialException as e:
			print(f"Serial port could not be opened: {e}")
			self.serial = None

	def create_serial(self):
		print(f"\n=== Creating serial connection ===")
		print(f"Port: {self.port}")
		print(f"Baudrate: {self.baudrate}")
		print(f"Current serial object: {self.serial}")
		try:
			# Create the serial port without opening it
			self.serial = serial.Serial()
			self.serial.port = self.port
			self.serial.baudrate = self.baudrate
			self.serial.bytesize = self.byte_size
			self.serial.parity = self.parity
			self.serial.stopbits = self.stop_bits
			self.serial.timeout = self.timeout
			# Explicitly set port to not open on creation
			self.serial._port_handle = None
			self.serial.is_open = False
			print(f"Successfully created serial object (not opened yet): {self.serial}")
		except Exception as e:
			print(f"!!! Error creating serial object: {e}")
			raise

	def update_baud_rate(self, baud_rate):
		self.baudrate = baud_rate
		if self.serial_created:
			self.serial.baudrate = baud_rate

	def close_serial(self):
		"""
		Safely close the serial connection if it exists and is open.
		Returns True if the port was successfully closed, False otherwise.
		"""
		if self.serial is None:
			return True
			
		try:
			if hasattr(self.serial, 'is_open') and self.serial.is_open:
				self.serial.close()
			self.serial = None
			self.serial_created = False
			return True
		except Exception as e:
			print(f"Error closing serial port: {e}")
			try:
				# Try to force close if normal close failed
				self.serial.__exit__(None, None, None)
			except:
				pass
			self.serial = None
			self.serial_created = False
			return False

	def update_port(self, port: str):
		"""
		Update the serial port. The port string can be in the format 'COMx' or 'COMx - Description'.
		Extracts just the COM port number before updating.
		"""
		print(f"\n=== update_port called with: {port} ===")
		print(f"Current port: {self.port}")
		print(f"Current serial_created: {self.serial_created}")
		print(f"Current serial object: {self.serial}")
		
		try:
			# Extract just the COM port if the string contains a dash (e.g., 'COM3 - USB Serial' -> 'COM3')
			if ' - ' in port:
				port = port.split(' - ')[0].strip()
			print(f"Extracted port: {port}")
			
			# If the port hasn't changed and is already open, do nothing
			if port == self.port and self.serial_created and self.serial is not None:
				try:
					if self.serial.is_open:
						print("Port is already open and matches, no action needed")
						return
				except Exception as e:
					print(f"Couldn't check if port is open, continuing: {e}")
					# If we can't check if it's open, assume it's not and continue
					pass
			
			print(f"Setting new port to: {port}")
			self.port = port
			
			# Close existing connection if it exists
			print("Closing existing connection...")
			self.close_serial()
			
			# Create new connection
			print("Creating new connection...")
			try:
				self.create_serial()
				self.serial_created = True
				print("Attempting to open port...")
				try:
					self.serial.open()
					print(f"Successfully opened port {port}")
				except serial.SerialException as e:
					# If open fails, make sure we clean up
					self.serial.close()
					self.serial = None
					self.serial_created = False
					print(f"!!! Failed to open port {port}: {e}")
					raise
			except serial.SerialException as e:
				print(f"!!! Failed to open port {port}: {e}")
				self.serial_created = False
				self.serial = None  # Ensure we don't keep a reference to a bad port
				raise
		except Exception as e:
			print(f"!!! Unexpected error in update_port: {e}")
			raise

	def open(self) -> bool:
		"""Open the serial port if it's not already open."""
		try:
			if not self.is_open():
				if self.serial is None:
					self.create_serial()
				self.serial.open()
				self.serial_created = True
				return True
			return True
		except Exception as e:
			print(f"Failed to open serial port: {e}")
			self.serial_created = False
			self.serial = None
			return False

	def close(self):
		"""Close the serial port if it's open."""
		return self.close_serial()

	def is_open(self) -> bool:
		try:
			return self.serial.is_open
		except AttributeError:
			return False

	def send_command(self, command: str, return_str: bool = True) -> str | bytes:
		print(f"sending command: {command}")
		self.serial.write(command.encode("utf-8"))
		time.sleep(1)
		try:
			data = self.serial.read_all()
		except serial.Timeout:
			data = ""

		print(f"received data: {data}")

		try:
			final_data = data.decode("utf-8") if return_str else data
		except UnicodeDecodeError:
			final_data = data

		return final_data

	def flush_buffer(self):
		self.serial.reset_input_buffer()
		self.serial.reset_output_buffer()
		self.serial.flush()



