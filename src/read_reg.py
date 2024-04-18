from dummy_modules import spidev
import dummy_modules as GPIO

# Setup GPIO for Chip Select (CS)
cs_pin = 8  
GPIO.setmode(GPIO.BOARD)
GPIO.setup(cs_pin, GPIO.OUT, initial=GPIO.HIGH)

# Initialize SPI
spi = spidev.SpiDev()
spi.open(0, 0)  # Open SPI bus 0, device 0
spi.max_speed_hz = 5000  # SPI speed
spi.mode = 0b00  # SPI mode as required by TDC7200

def read_register(register_address):

    read_command = 0x0 | (register_address & 0x3F)  # Read instruction bit set, auto-increment disabled
    GPIO.output(cs_pin, GPIO.LOW) 
    # The first byte sent is the command, the second byte (0x00) is a dummy to clock out the data
    response = spi.xfer2([read_command, 0x00])
    GPIO.output(cs_pin, GPIO.HIGH) 
    return response[1]



register_address = 0x00  # Replace with the actual register address you want to read
data = read_register(register_address)
print(f"Data read from register {register_address:02X}: {data:02X}")

register_address = 0x01  # Replace with the actual register address you want to read
data = read_register(register_address)
print(f"Data read from register {register_address:02X}: {data:02X}")


#for i in range(0x3F):

 #   register_address = i  # Replace with the actual register address you want to read
  #  data = read_register(register_address)
   # print(f"Data read from register {register_address:02X}: {data}")
    #time.sleep(0.01)

# Cleanup
spi.close()
GPIO.cleanup()

