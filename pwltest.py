import pywizlight as pwl
import asyncio
import time
from webcolors import CSS3_NAMES_TO_HEX

css_colors = CSS3_NAMES_TO_HEX
css_options = list(CSS3_NAMES_TO_HEX.keys())
color = 'indigo'
hex = css_colors[str(color)].lstrip('#')
rgb = tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))
print(hex)
print(rgb)