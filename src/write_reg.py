from dummy_modules import spidev
import dummy_modules as GPIO
from time import sleep


# Setup GPIO for Chip Select (CS) and EN
cs_pin = 8
en_pin = 10

GPIO.setmode(GPIO.BOARD)
GPIO.setup(cs_pin, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(en_pin, GPIO.OUT, initial=GPIO.LOW)

# Initialize SPI
spi = spidev.SpiDev()
spi.open(0, 0)  # Open SPI bus 0, device 0
spi.max_speed_hz = 5000  # SPI speed
spi.mode = 0b00  # SPI mode as required by TDC7200


# Pulse EN pin
def reset_board():
    print("TDC7200 EN Pulsed to reset state") 
    GPIO.output(en_pin, GPIO.LOW)   
    sleep(0.01) 
    GPIO.output(en_pin, GPIO.HIGH)


def write_register(register_address, value):
  
    command_byte = 0x40 | (0x3F & register_address)
    command = [command_byte, value]
    
    GPIO.output(cs_pin, GPIO.LOW)  # Enable communication
    spi.xfer2(command)  # Send the command and value
    GPIO.output(cs_pin, GPIO.HIGH)  # Disable communication

reset_board()
sleep(0.01)


# Write values to CONFIG1 and CONFIG2 registers
write_register(0x01, 0b00000010)
write_register(0x00, 0b01000001)  


# Cleanup
spi.close()
GPIO.cleanup()
