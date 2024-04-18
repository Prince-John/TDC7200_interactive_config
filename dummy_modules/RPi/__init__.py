BCM = 'BCM'
BOARD = 'BOARD'
OUT = 'OUT'
IN = 'IN'
HIGH = 'HIGH'
LOW = 'LOW'
PUD_UP = 'PUD_UP'


def setmode(mode, **kwargs):
    print(f"Dummy GPIO: Setting mode {mode}")
    for key, value in kwargs.items():
        print(f"  With additional argument {key}: {value}")


def setup(channel, mode, **kwargs):
    print(f"Dummy GPIO: Setting up channel {channel} to mode {mode}")
    for key, value in kwargs.items():
        print(f"  With additional argument {key}: {value}")


def output(channel, state, **kwargs):
    print(f"Dummy GPIO: Setting channel {channel} to state {state}")
    for key, value in kwargs.items():
        print(f"  With additional argument {key}: {value}")


def input(channel, **kwargs):
    print(f"Dummy GPIO: Reading from channel {channel}")
    for key, value in kwargs.items():
        print(f"  With additional argument {key}: {value}")
    return False  # Return False for simplicity


def cleanup(**kwargs):
    print("Dummy GPIO: Cleaning up")
    for key, value in kwargs.items():
        print(f"  With additional argument {key}: {value}")


def FALLING():
    return None


def wait_for_edge(INT_PIN, FALLING):
    print(f"Dummy GPIO: Wait for {FALLING} edge on pin {INT_PIN}")
    return None