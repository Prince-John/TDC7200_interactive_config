import tdc_spi_utils
from config_utils import *

address_map = {"CONFIG1": 0x00,
               "CONFIG2": 0x01,
               "INT_STATUS": 0x02,
               "INT_MASK": 0x03,
               "COARSE_CNTR_OVF_H": 0x04,
               "COARSE_CNTR_OVF_L": 0x05,
               "CLOCK_CNTR_OVF_H": 0x06,
               "CLOCK_CNTR_OVF_L": 0x07,
               "CLOCK_CNTR_STOP_MASK_H": 0x08,
               "CLOCK_CNTR_STOP_MASK_L": 0x09,
               "TIME1": 0x10,
               "CLOCK_COUNT1": 0x11,
               "TIME2": 0x12,
               "CLOCK_COUNT2": 0x13,
               "TIME3": 0x14,
               "CLOCK_COUNT3": 0x15,
               "TIME4": 0x16,
               "CLOCK_COUNT4": 0x17,
               "TIME5": 0x18,
               "CLOCK_COUNT5": 0x19,
               "TIME6": 0x1A,
               "CALIBRATION1": 0x1B,
               "CALIBRATION2": 0x1C,
               }

def configure_chip(chip: tdc_spi_utils.TDC):

    chip.write_register(address_map["CONFIG2"], chip.CONFIG2)
    chip.write_register(address_map["CONFIG1"], chip.CONFIG1 & 0xFE)
    print("Chip Configured with :")
    display_configuration(chip.CONFIG1, "CONFIG1")
    display_configuration(chip.CONFIG2, "CONFIG2")


def take_measurement(chip):

    chip.write_register(address_map["CONFIG1"], chip.CONFIG1 | 0x01)
    chip.blocking_wait()
    print("Measurement complete")



]if __name__ == "__main__":
    pass
