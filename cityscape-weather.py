import sys
import time

from PIL import Image, ImageDraw, ImageFont
import ST7789 as ST7789

try:
    from smbus2 import SMBus
except ImportError:
    from smbus import SMBus

from bme280 import BME280
from ltr559 import LTR559

def blend_colours(a, b, alpha):
    r1, g1, b1 = a
    r2, g2, b2 = b
    r_diff = r2 - r1
    g_diff = g2 - g1
    b_diff = b2 - b1
    r_new = int(r1 + (alpha * r_diff))
    g_new = int(g1 + (alpha * g_diff))
    b_new = int(b1 + (alpha * b_diff))
    return (r_new, g_new, b_new)

disp = ST7789.ST7789(
    port=0,
    cs=ST7789.BG_SPI_CS_FRONT,  # BG_SPI_CSB_BACK or BG_SPI_CS_FRONT
    dc=9,
    backlight=19,               # 18 for back BG slot, 19 for front BG slot.
    spi_speed_hz=80 * 1000 * 1000
)

WIDTH = disp.width
HEIGHT = disp.height

day_image = Image.open("cityscape-day.jpg").resize((WIDTH, HEIGHT))
night_image = Image.open("cityscape-night.jpg").resize((WIDTH, HEIGHT))

day_colour = (15, 58, 68)
night_colour = (58, 42, 73)

disp.begin()

bus = SMBus(1)

bme280 = BME280(i2c_dev=bus)
ltr559 = LTR559()

lux_vals = [100] * 10

while True:
    lux = lux = ltr559.get_lux()
    lux_vals = lux_vals[1:] + [lux]
    avg_lux = sum(lux_vals) / len(lux_vals)
    alpha = min((avg_lux / 100), 1.0)
    colour = blend_colours(night_colour, day_colour, alpha)
    image = Image.blend(night_image, day_image, alpha)
    draw = ImageDraw.Draw(image)

    font = ImageFont.truetype("fonts/Nunito-Bold.ttf", 32)

    temperature = bme280.get_temperature()
    message = f"Temp: {temperature:.2f}°C"
    draw.text((5, 196), message, font=font, fill=colour)

    disp.display(image)
#    time.sleep(0.25)
