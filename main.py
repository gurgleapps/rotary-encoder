import utime
from machine import Pin

from RotaryEncoder import RotaryEncoder

val: int = 0


def rotary_change(event_type) -> None:  # Handler for RotaryEncoder.
    global val
    if event_type == RotaryEncoder.ROT_CW:
        val += 1
        print(f'COUNT: {val}')
    elif event_type == RotaryEncoder.ROT_CCW:
        val -= 1
        print(f'COUNT: {val}')
    elif event_type == RotaryEncoder.SW_PRESS:
        print('Switch pressed!')
    elif event_type == RotaryEncoder.SW_RELEASED:
        print('Switch released!')


def main():
    # Define pins for the rotary encoder
    dt_pin = Pin(0, Pin.IN, Pin.PULL_UP)
    clk_pin = Pin(1, Pin.IN, Pin.PULL_UP)
    sw_pin = Pin(2, Pin.IN, Pin.PULL_UP)

    # Create a RotaryEncoder object
    encoder = RotaryEncoder(dt_pin, clk_pin, sw_pin)

    # Add event handlers
    encoder.add_handler(rotary_change)

    # Your main code logic here (e.g., running other tasks or loops)
    while True:
        utime.sleep(0.1)


if __name__ == "__main__":
    main()
