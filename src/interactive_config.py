from time import sleep
import csv

DEV_ENV = False
if DEV_ENV:
    from dummy_modules import spidev
    from dummy_modules import RPi as GPIO
else:
    import RPi.GPIO as GPIO
    import spidev

# Setup GPIO for Chip Select (CS)
cs_pin = 8
en_pin = 10
int_pin = 12

# GPIO Setup
GPIO.setmode(GPIO.BOARD)
GPIO.setup(cs_pin, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(en_pin, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(int_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Initialize SPI
spi = spidev.SpiDev()
spi.open(0, 0)  # Open SPI bus 0, device 0
spi.max_speed_hz = 50000  # SPI speed
spi.mode = 0b00  # SPI mode as required by TDC7200

######## CONFIG SETTINGS #########

CONFIG1 = 0b00000000
CONFIG2 = 0b00000001

config = {"calib_cycles": 2,
          "num_stops": 2,
          "ext_clock_freq": 9.95e6,
          "avg_cycles": 0,
          "mode": 1}

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


def apply_number(configuration, number, start_bit, length):
    """Set `length` bits starting from `start_bit` to represent `number`."""
    mask = (1 << length) - 1  # Create a mask of `length` bits
    number &= mask  # Ensure `number` fits in the specified length
    configuration &= ~(mask << start_bit)  # Clear the target bits
    configuration |= (number << start_bit)  # Set the target bits to `number`
    return configuration


def toggle_bit(configuration, bit_position):
    """Toggle the bit at the specified position in the configuration byte."""
    return configuration ^ (1 << bit_position)


def display_configuration(configuration, address):
    """Display the current configuration in binary format."""
    print(f"{address}\tCurrent configuration: {configuration:08b} (binary) | {configuration} (decimal)")


def reset_board():
    print("TDC7200 EN Pulsed to reset state")
    GPIO.output(en_pin, GPIO.LOW)
    sleep(0.01)
    GPIO.output(en_pin, GPIO.HIGH)


def read_register(register_address, num_bytes):
    read_command = 0x0 | (register_address & 0x3F)  # Read instruction bit set, auto-increment disabled
    GPIO.output(cs_pin, GPIO.LOW)
    read_cycles = [0x00] * num_bytes
    # The first byte sent is the command, the second byte (0x00) is a dummy to clock out the data
    response = spi.xfer2([read_command] + read_cycles)
    GPIO.output(cs_pin, GPIO.HIGH)
    return response[1:]


def write_register(register_address, value):
    command_byte = 0x40 | (0x3F & register_address)
    command = [command_byte, value]

    GPIO.output(cs_pin, GPIO.LOW)  # Enable communication
    spi.xfer2(command)  # Send the command and value
    GPIO.output(cs_pin, GPIO.HIGH)  # Disable communication


def show_edge_menu():
    """Display the menu and get user choice."""
    menu = """
***********************************************************
Edge MENU
***********************************************************
    1. Trigger Edge
    2. Start Edge
    3. Stop Edge
    4. go back 

Enter your choice (1-4): """
    return input(menu)


def show_config_menu():
    """Display the menu and get user choice."""
    global CONFIG1
    global CONFIG2
    menu = """
***********************************************************
CONFIG MENU
***********************************************************
    1. Calibration Period
    2. Edge Sensitivity
    3. Average Cycles
    4. Number of Stops 
    5. Write config to chip
    6. Go back

Enter your choice (1-4): """
    current_config = f"\nCONFIG 1 = {CONFIG1:08b}\nCONFIG 2 = {CONFIG2:08b}"
    return input(current_config + menu)


def show_menu():
    """Display the config menu and get user choice."""
    menu = """
-----------------------------------------------------------
CHIP INTERFACE MENU
-----------------------------------------------------------
    1. Read from chip
    2. Write to chip
    3. Configure chip
    4. Take measurement - sets start measurement bit to 1.
    5. Read all registers
    6. Reset

Enter your choice (1-6): """

    return input(menu)


def read_from_chip():
    pass


def write_to_chip():
    write_register(address_map["CONFIG2"], CONFIG2)
    write_register(address_map["CONFIG1"], CONFIG1 & 0xFE)
    display_configuration(CONFIG1, "CONFIG1")
    display_configuration(CONFIG2, "CONFIG2")


def config_num_stops():
    global CONFIG2
    stops = get_integer_input("Enter required stops from 1 - 5, default 2")
    if stops > 5 or stops < 1:
        print("invalid choice choose between 1 - 5 stops")
        config_num_stops()
    CONFIG2 = apply_number(CONFIG2, stops - 1, 0, 3)
    config["num_stops"] = stops


def config_cycles():
    global CONFIG2
    cycles = get_integer_input("Enter the power n for cycles = 2^n, max n = 7\n")

    if cycles > 7 or cycles < 0:
        print("invalid choice choose between 0 - 7 n")
        config_cycles()
    CONFIG2 = apply_number(CONFIG2, cycles, 3, 3)
    config["avg_cycles"] = 2 ^ cycles
    return


def config_calibration():
    global CONFIG2
    calib_map = {0: 2, 1: 10, 2: 20, 3: 40}
    calibration_text = """
    0: Calibration 2 - measuring 2 CLOCK periods
    1: Calibration 2 - measuring 10 CLOCK periods
    2: Calibration 2 - measuring 20 CLOCK periods
    3: Calibration 2 - measuring 40 CLOCK periods

    Enter Calibration choice from 0 - 3, default 10\n
    """

    calibration_length = get_integer_input(calibration_text)

    if calibration_length > 3 or calibration_length < 0:
        print("invalid choice choose between 0 - 3")
        config_calibration()
    CONFIG2 = apply_number(CONFIG2, calibration_length, 6, 2)
    config["calib_cycles"] = int(calib_map[calibration_length])
    return


def config_trig_edge():
    global CONFIG1
    edge_text = """
        0: TRIGG is output as a Rising edge signal
        1: TRIGG is output as a Falling edge signal

        Enter Calibration choice from 0 - 1, default 0\n
        """
    edge = get_integer_input(edge_text)

    if edge > 1 or edge < 0:
        print("invalid choice choose between 0 - 1")
        config_start_edge()
    CONFIG1 = apply_number(CONFIG1, edge, 5, 1)
    return


def config_stop_edge():
    global CONFIG1
    edge_text = """
        0: Measurement is stopped on Rising edge of STOP signal
        1: Measurement is stopped on Falling edge of STOP signal

        Enter Calibration choice from 0 - 1, default 0\n
        """

    edge = get_integer_input(edge_text)

    if edge > 1 or edge < 0:
        print("invalid choice choose between 0 - 1")
        config_start_edge()
    CONFIG1 = apply_number(CONFIG1, edge, 4, 1)
    return


def config_start_edge():
    global CONFIG1
    edge_text = """
        0: Measurement is started on Rising edge of START signal
        1: Measurement is started on Falling edge of START signal

        Enter Calibration choice from 0 - 1, default 0\n
        """

    edge = get_integer_input(edge_text)

    if edge > 1 or edge < 0:
        print("invalid choice choose between 0 - 1")
        config_start_edge()
    CONFIG1 = apply_number(CONFIG1, edge, 3, 1)
    return


def format_time(time_s):
    """Formats time based on its magnitude for readability."""
    if time_s < 1e-6:  # Less than micro nanoseconds
        return f"{time_s * 1e9:.4f} ns"
    elif time_s < 1e-3:
        return f"{time_s * 1e6:.2f} µs"  # microseconds
    elif time_s < 1:
        return f"{time_s * 1e3:.2f} ms"  # milliseconds
    else:
        return f"{time_s:.2f} s"  # seconds


def print_tof_pretty(timing_data, computed_times):
    """
    Prints computed times alongside raw 24-bit register values for times,
    dynamically choosing the unit (ns, µs, ms) based on the magnitude of the computed time.
    Also prints the raw 24-bit register values for calibration.
    """
    # Print calibration data
    print(f"Calibration 1 (raw): {timing_data['CALIBRATION1']:06X}")
    print(f"Calibration 2 (raw): {timing_data['CALIBRATION2']:06X}")

    print("\nTimes:")
    # Check to ensure we have matching lengths of raw times and computed times
    if len(timing_data['TIMES']) != len(computed_times):
        print("Error: The number of raw times and calculated times does not match.")
        return

    # Print each raw time with its corresponding calculated time in a dynamically chosen unit
    for i, (raw_time, comp_time) in enumerate(zip(timing_data['TIMES'], computed_times)):
        formatted_time = format_time(comp_time)
        print(f"Time {i + 1}: {formatted_time} (raw: {raw_time:06X})")


def start_measurement(DEBUG=False):
    print("Starting Measurement, at a blocking call getting preempted now.")
    global CONFIG1
    write_register(0x00, CONFIG1 | 0b00000001)
    GPIO.wait_for_edge(int_pin, GPIO.FALLING, timeout=10000)
    sleep(0.1)
    print("Measurement Complete")

    if DEBUG:
        read_all_registers()

    timing_data = get_timing_data()

    if DEBUG:
        print(timing_data)
    tof = tof_calculation_mode0(timing_data["CALIBRATION1"],
                                timing_data["CALIBRATION2"],
                                config["calib_cycles"],
                                times=timing_data["TIMES"],
                                ext_clk_freq=config["ext_clock_freq"])

    print_tof_pretty(timing_data, tof)

    if DEBUG: read_all_registers()


def read_all_registers():
    for i in range(0x1C + 1):
        num_bytes = 1 if i < 10 else 3
        register_address = i  # Replace with the actual register address you want to read
        data = read_register(register_address, num_bytes)
        data_hex = ' '.join(f'{byte:02X}' for byte in data)
        print(f"Data read from register {register_address:02X}: {data_hex}")
        sleep(0.0001)


def get_timing_data() -> dict:
    timing_data = {"TIMES": [], "CALIBRATION1": 0, "CALIBRATION2": 0}

    timing_data["CALIBRATION1"] = combined_byte_value(read_register(address_map["CALIBRATION1"], 3))
    timing_data["CALIBRATION2"] = combined_byte_value(read_register(address_map["CALIBRATION2"], 3))
    timing_data["TIMES"] = [combined_byte_value(read_register(address_map[f"TIME{time}"], 3)) for time in
                            range(1, config["num_stops"] + 1)]

    return timing_data


def combined_byte_value(bytes_list) -> int:
    combined_number = (bytes_list[0] << 16) | (bytes_list[1] << 8) | bytes_list[2]
    return combined_number


def get_integer_input(prompt="Enter a number: "):
    while True:
        user_input = input(prompt)
        try:
            # Attempt to convert the user input to an integer
            user_input_int = int(user_input)

            return user_input_int
        except ValueError:
            # If conversion fails, inform the user and prompt again
            print("Invalid input. Please enter a valid integer.")


def configure_chip():
    try:
        while True:
            choice = show_config_menu()
            if choice == '1':
                config_calibration()

            elif choice == '2':
                config_edge()

            elif choice == '3':
                config_cycles()

            elif choice == '4':
                config_num_stops()

            elif choice == '5':
                write_to_chip()

            elif choice == '6':
                break

            else:
                print("Invalid choice. Please select an option between 1 and 4.")
    except KeyboardInterrupt:
        print("\nExiting Config")
        return


def config_edge():
    try:
        while True:
            choice = show_edge_menu()
            if choice == '1':
                config_trig_edge()

            elif choice == '2':
                config_stop_edge()

            elif choice == '3':
                config_start_edge()

            elif choice == '4':
                break

            else:
                print("Invalid choice. Please select an option between 1 and 4.")
    except KeyboardInterrupt:
        print("\nExiting Config")
        return


def tof_calculation_mode0(calib1, calib2, calib2_periods, times: list, ext_clk_freq=8e6):
    cal_count = (calib2 - calib1) / (calib2_periods - 1)
    if cal_count == 0:
        print(cal_count)
        cal_count += 1
    norm_lsb = (1 / ext_clk_freq) / cal_count
    tof = [time * norm_lsb for time in times]
    print(
        f"****************************************\nDEBUG\n************************************************\n NormLSB = {norm_lsb} seconds/count, ext_freq = {ext_clk_freq} Hz, Avg Counts per clock = {cal_count} ")
    return tof


def main():
    try:
        while True:

            choice = show_menu()

            if choice == '1':
                read_from_chip()

            elif choice == '2':
                data = int(input("Enter data to write in hex    "), base=0)
                add = int(input("Enter register address     "), base=0)
                write_register(add, data)

            elif choice == '3':
                configure_chip()

            elif choice == '4':
                start_measurement()

            elif choice == '5':
                read_all_registers()

            elif choice == '6':
                reset_board()

            elif choice == '7':
                print("Exiting!")
                break

            else:
                print("Invalid choice. Please select an option between 1 and 5.")

    except KeyboardInterrupt:
        print("\nExiting due to user interruption.")
    finally:
        spi.close()  # Clean up and close the SPI connection
        GPIO.cleanup()


if __name__ == "__main__":
    main()
