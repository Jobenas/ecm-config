import os
import time
import logging
from pathlib import Path
from datetime import datetime

import serial
import serial.tools.list_ports

def setup_logger():
    """
    Set up and configure the logger with both file and console handlers.
    
    Returns:
        logging.Logger: Configured logger instance
    """
    # Use app data directory for logs
    if os.name == 'nt':  # Windows
        app_data = os.getenv('APPDATA')
        if not app_data:
            app_data = os.path.expanduser('~')  # Fallback to user home if APPDATA not set
        log_dir = Path(app_data) / 'ECM_Field_App' / 'logs'
    else:  # Unix/Linux/Mac
        log_dir = Path.home() / '.ecm_field_app' / 'logs'
    
    # Create logs directory if it doesn't exist
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        # If we can't create the log directory, fall back to a temporary directory
        import tempfile
        log_dir = Path(tempfile.gettempdir()) / 'ecm_field_app_logs'
        log_dir.mkdir(parents=True, exist_ok=True)
    
    # Create a timestamped log file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = log_dir / f'serial_controller_{timestamp}.log'
    
    # Create logger
    logger = logging.getLogger('SerialController')
    logger.setLevel(logging.DEBUG)
    
    # Create file handler which logs even debug messages
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    
    # Create console handler with a higher log level
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Initialize logger
logger = setup_logger()


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
		self.logger = setup_logger()
		self.logger.info(f"Initialized SerialController with port: {port}, baudrate: {baudrate}")

		try:
			self.create_serial()
			self.serial_created = True
			self.logger.info("Serial port created successfully")
		except serial.SerialException as e:
			error_msg = f"Serial port could not be opened: {e}"
			self.logger.error(error_msg, exc_info=True)
			self.serial = None

	def create_serial(self):
		self.logger.debug("=== Creating serial connection ===")
		self.logger.debug(f"Port: {self.port}")
		self.logger.debug(f"Baudrate: {self.baudrate}")
		self.logger.debug(f"Current serial object: {self.serial}")
		try:
			# Create the serial port without opening it
			self.serial = serial.Serial()
			self.serial.port = self.port
			self.serial.baudrate = self.baudrate
			self.serial.bytesize = self.byte_size
			self.serial.parity = self.parity
			self.serial.stopbits = self.stop_bits
			self.serial.timeout = self.timeout
			# Explicitly set flow control and other parameters
			self.serial.xonxoff = False     # Disable software flow control
			self.serial.rtscts = False      # Disable hardware (RTS/CTS) flow control
			self.serial.dsrdtr = False      # Disable hardware (DSR/DTR) flow control
			self.serial.write_timeout = 2.0  # Add write timeout
			self.serial.inter_byte_timeout = 0.1  # Timeout between bytes
			# Explicitly set port to not open on creation
			self.serial._port_handle = None
			self.serial.is_open = False
			self.logger.debug(f"Successfully created serial object (not opened yet): {self.serial}")
		except Exception as e:
			self.logger.error("Error creating serial object", exc_info=True)
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
		self.logger.debug("Attempting to close serial port")
		if self.serial is None:
			self.logger.debug("No serial port to close")
			return True
			
		try:
			if hasattr(self.serial, 'is_open') and self.serial.is_open:
				self.logger.debug(f"Closing serial port: {self.port}")
				self.serial.close()
			self.serial = None
			self.serial_created = False
			self.logger.info("Successfully closed serial port")
			return True
		except Exception as e:
			self.logger.error(f"Error closing serial port: {e}", exc_info=True)
			try:
				# Try to force close if normal close failed
				self.serial.__exit__(None, None, None)
				self.logger.warning("Force closed serial port")
			except Exception as force_close_error:
				self.logger.error(f"Error force closing serial port: {force_close_error}", exc_info=True)
			self.serial = None
			self.serial_created = False
			return False

	def update_port(self, port: str):
		"""
		Update the serial port. The port string can be in the format 'COMx' or 'COMx - Description'.
		Extracts just the COM port number before updating.
		"""
		self.logger.debug(f"=== update_port called with: {port} ===")
		self.logger.debug(f"Current port: {self.port}")
		self.logger.debug(f"Current serial_created: {self.serial_created}")
		self.logger.debug(f"Current serial object: {self.serial}")
		
		# Extract just the COM port if the string contains a dash (e.g., 'COM3 - USB Serial' -> 'COM3')
		if ' - ' in port:
			port = port.split(' - ')[0].strip()
		self.logger.info(f"Extracted port: {port}")
		
		try:
			# If the port hasn't changed and is already open, do nothing
			if port == self.port and self.serial_created and self.serial is not None:
				try:
					if self.serial.is_open:
						self.logger.info("Port is already open and matches, no action needed")
						return
				except Exception as e:
					self.logger.warning(f"Couldn't check if port is open, continuing: {e}")
					# If we can't check if it's open, assume it's not and continue
					pass
			
			self.logger.info(f"Setting new port to: {port}")
			self.port = port
			
			# Close existing connection if it exists
			self.logger.debug("Closing existing connection...")
			self.close_serial()
			
			# Create new connection
			self.logger.debug("Creating new connection...")
			try:
				self.create_serial()
				self.serial_created = True
				self.logger.debug("Attempting to open port...")
				try:
					self.serial.open()
					self.logger.info(f"Successfully opened port {port}")
				except serial.SerialException as e:
					self.logger.error(f"Failed to open port {port}", exc_info=True)
					# If open fails, make sure we clean up
					try:
						self.serial.close()
					except Exception as close_error:
						self.logger.error(f"Error closing port after open failed: {close_error}")
					self.serial = None
					self.serial_created = False
					raise
			except serial.SerialException as e:
					self.logger.error(f"Failed to create serial connection: {e}", exc_info=True)
					self.serial_created = False
					self.serial = None  # Ensure we don't keep a reference to a bad port
					raise
		except Exception as e:
			self.logger.error(f"Unexpected error in update_port: {e}", exc_info=True)
			raise
		except Exception as e:
			print(f"!!! Unexpected error in update_port: {e}")
			raise

	def open(self) -> bool:
		"""Open the serial port if it's not already open."""
		try:
			if not self.is_open():
				self.logger.debug("Port not open, attempting to open...")
				if self.serial is None:
					self.logger.debug("Creating new serial instance")
					self.create_serial()
				self.serial.open()
				self.serial_created = True
				self.logger.info(f"Successfully opened port {self.port}")
				return True
			self.logger.debug("Port is already open")
			return True
		except Exception as e:
			self.logger.error(f"Failed to open serial port: {e}", exc_info=True)
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

	def _read_response(self, timeout: float) -> bytes:
		"""Helper method to read response with timeout."""
		response = b''
		start_time = time.time()
		last_data_time = time.time()
		
		while time.time() - start_time < timeout:
			if self.serial.in_waiting > 0:
				chunk = self.serial.read(self.serial.in_waiting)
				if chunk:
					response += chunk
					last_data_time = time.time()
					self.logger.debug(f"Received chunk: {chunk!r}")
			elif response:  # If we got response but no new data for a while
				if time.time() - last_data_time > 0.1:
					break
				time.sleep(0.01)
			else:  # No response yet
				time.sleep(0.1)
				
		return response if response else None

	def send_command(self, command: str, return_str: bool = True, timeout: float = 5.0) -> str | bytes | None:
		"""
		Send a command to the serial port and wait for a response.
		
		Args:
			command: The command to send (without line endings)
			return_str: If True, return response as string, otherwise return bytes
			timeout: Time in seconds to wait for a response
			
		Returns:
			The response as string or bytes, or None if no response was received
		"""
		if not self.is_open():
			self.logger.error("Cannot send command: Serial port is not open")
			return None

		try:
			# Ensure proper line ending
			if not command.endswith('\r\n'):
				command = command.rstrip('\r\n') + '\r\n'
		
			self.logger.debug(f"Sending command: {command.strip()!r}")
			self.serial.reset_input_buffer()
			self.serial.reset_output_buffer()
		
			# Send the command multiple times with delays
			for attempt in range(3):
				try:
					self.serial.write(command.encode('utf-8'))
					self.serial.flush()
					self.logger.debug(f"Command sent (attempt {attempt + 1})")
					time.sleep(0.2)  # Small delay between attempts
				except Exception as e:
					self.logger.error(f"Error sending command (attempt {attempt + 1}): {e}")
					if attempt == 2:  # If this was the last attempt
						raise
					continue
			
				# Try to read response
				response = self._read_response(timeout)
				if response:
					break

			if not response:
				self.logger.warning(f"No response received after {timeout} seconds")
				return None

			self.logger.debug(f"Raw response: {response!r}")
			
			if return_str:
				try:
					decoded = response.decode('utf-8', errors='replace').strip()
					self.logger.debug(f"Decoded response: {decoded!r}")
					return decoded
				except UnicodeDecodeError:
					self.logger.warning(f"Could not decode response as UTF-8, returning raw bytes: {response}")
					return response
			
			return response
			
		except serial.SerialException as e:
			self.logger.error(f"Serial communication error: {e}", exc_info=True)
			try:
				self.flush_buffer()
			except Exception as flush_error:
				self.logger.error(f"Error flushing buffer: {flush_error}", exc_info=True)
			return None
		except Exception as e:
			self.logger.critical(f"Unexpected error in send_command: {e}", exc_info=True)
			return None

	def flush_buffer(self):
		self.serial.reset_input_buffer()
		self.serial.reset_output_buffer()
		self.serial.flush()



