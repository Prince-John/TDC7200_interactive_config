def toggle_bit(configuration, bit_position):
    """Toggle the bit at the specified position in the configuration byte."""
    return configuration ^ (1 << bit_position)


def display_configuration(configuration, address):
    """Display the current configuration in binary format."""
    print(f"{address}\tCurrent configuration: {configuration:08b} (binary) | {configuration} (decimal)")
