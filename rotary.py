import micropython
from machine import Pin

micropython.alloc_emergency_exception_buf(100)


class RotaryEncoder:
    ROT_CW: int = micropython.const(0x01)
    ROT_CCW: int = micropython.const(0x02)
    SW_PRESS: int = micropython.const(0x04)
    SW_RELEASED: int = micropython.const(0x08)

    def __init__(self, dt_pin: Pin = None, clk_pin: Pin = None, sw_pin: Pin = None) -> None:
        if dt_pin is None or clk_pin is None or sw_pin is None:
            raise ValueError("All pins (dt_pin, clk_pin, sw_pin) must be provided.")

        self.__DT_PIN: Pin = dt_pin  # RotaryEncoder DT.
        self.__CLK_PIN: Pin = clk_pin  # RotaryEncoder CLK.
        self.__SW_PIN: Pin = sw_pin  # RotaryEncoder SW.

        self.__DT_PIN.irq(handler=self.__rotary_change, trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING)
        self.__CLK_PIN.irq(handler=self.__rotary_change, trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING)
        self.__SW_PIN.irq(handler=self.__switch_detect, trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING)

        self.__last_status: int = (self.__DT_PIN.value() << 1) | self.__CLK_PIN.value()
        self.__last_switch_status: int = self.__SW_PIN.value()
        self.__handlers: list = []

    def __rotary_change(self, pin) -> None:  # The handler for RotaryEncoder.
        new_status: int = (self.__DT_PIN.value() << 1) | self.__CLK_PIN.value()
        if new_status == self.__last_status:
            return
        transition: int = (self.__last_status << 2) | new_status
        if transition == 0x0E:  # In binary: 0b1110
            micropython.schedule(self.__call_handlers, RotaryEncoder.ROT_CW)
        elif transition == 0x0D:  # In binary: 0b1101
            micropython.schedule(self.__call_handlers, RotaryEncoder.ROT_CCW)

        self.__last_status = new_status  # Store last status into new status.

    def __switch_detect(self, pin) -> None:  # The handler for RotaryEncoder builtin SW.
        if self.__last_switch_status == self.__SW_PIN.value():
            return
        self.__last_switch_status = self.__SW_PIN.value()
        if self.__SW_PIN.value():
            micropython.schedule(self.__call_handlers, RotaryEncoder.SW_RELEASED)
        else:
            micropython.schedule(self.__call_handlers, RotaryEncoder.SW_PRESS)

    def add_handler(self, handler) -> None:
        self.__handlers.append(handler)

    def __call_handlers(self, event_type) -> None:
        for handler in self.__handlers:
            handler(event_type)
