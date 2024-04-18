from dummy_modules import spidev
import dummy_modules as GPIO

# Setup GPIO for Chip Select (CS)
cs_pin = 8  # Example CS pin
GPIO.setmode(GPIO.BOARD)
GPIO.setup(cs_pin, GPIO.OUT, initial=GPIO.HIGH)

# Initialize SPI
spi = spidev.SpiDev()
spi.open(0, 0)  # Open SPI bus 0, device 0
spi.max_speed_hz = 5000  # SPI speed
spi.mode = 0b01  # SPI mode as required by TDC7200

# Function to read a 24-bit register
def read_time1_register():
    register_address = 0x04  # Address for TIME1 register
    read_command = 0x80 | register_address  # Construct read command with auto-increment disabled
    
    GPIO.output(cs_pin, GPIO.LOW)  # Enable communication
    
    # Send read command and read 3 bytes
    spi.xfer([read_command])  # Send command
    time1_bytes = spi.xfer([0x00, 0x00, 0x00])  # Read 3 bytes for 24-bit TIME1 register
    
    GPIO.output(cs_pin, GPIO.HIGH)  # Disable communication
    
    # Combine the 3 bytes into one 24-bit value
    time1_value = (time1_bytes[0] << 16) | (time1_bytes[1] << 8) | time1_bytes[2]
    return time1_value

# Read TIME1 register and print value
time1_value = read_time1_register()
print(f"TIME1 Value: {time1_value}")

# Cleanup
spi.close()
GPIO.cleanup()
