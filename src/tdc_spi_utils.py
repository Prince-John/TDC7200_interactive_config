DEV_ENV = True
if DEV_ENV:
    from dummy_modules import spidev
    from dummy_modules import RPi as GPIO
else:
    import RPi.GPIO as GPIO
    import spidev


class TDC:
    def __init__(self):
        self.spi = spidev.SpiDev()
        self.CONFIG1 = 0b00000000
        self.CONFIG2 = 0b00000001
        self.configuration = {}

    def initialize(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(CS_PIN, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(EN_PIN, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(INT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self.spi.open(SPI_BUS, SPI_DEVICE)
        self.spi.max_speed_hz = int(SPI_SPEED_HZ)
        self.spi.mode = SPI_MODE

    def read_register(self, register_address, num_bytes=1):
        command = 0x0 | (register_address & 0x3F)
        GPIO.output(CS_PIN, GPIO.LOW)
        response = self.spi.xfer2([command] + [0x00] * num_bytes)
        GPIO.output(CS_PIN, GPIO.HIGH)
        return response[1:]

    def write_register(self, register_address, value):
        command_byte = 0x40 | (register_address & 0x3F)
        GPIO.output(CS_PIN, GPIO.LOW)
        self.spi.xfer2([command_byte, value])
        GPIO.output(CS_PIN, GPIO.HIGH)

    def reset_board(self):
        print("TDC7200 EN Pulsed to reset state")
        GPIO.output(EN_PIN, GPIO.LOW)
        sleep(0.01)
        GPIO.output(EN_PIN, GPIO.HIGH)

    def cleanup(self):
        self.spi.close()
        GPIO.cleanup()

    def blocking_wait(self):
        GPIO.wait_for_edge(INT_PIN, GPIO.FALLING)
        return
