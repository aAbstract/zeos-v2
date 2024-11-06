import machine  # type: ignore
import gc9a01 # type: ignore
import vga2_bold_16x32 # type: ignore


_sck = machine.Pin(6)
_mosi = machine.Pin(7)
_spi = machine.SPI(1, baudrate=60000000, sck=_sck, mosi=_mosi)

_dc = machine.Pin(2, machine.Pin.OUT)
_cs = machine.Pin(10, machine.Pin.OUT)
_bklt = machine.Pin(3, machine.Pin.OUT)
_tft = gc9a01.GC9A01(_spi, dc=_dc, cs=_cs, backlight=_bklt)

_tft.fill(gc9a01.BLACK)
_tft.text(vga2_bold_16x32, "ZEOS", 100, 100, gc9a01.WHITE, gc9a01.BLACK)
