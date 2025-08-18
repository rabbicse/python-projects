import os

import arabic_reshaper

FONT_ARABIC_PATH = os.path.join(os.path.dirname(__file__), "fonts/NotoSansArabic-Regular.ttf") #"fonts/NotoSansArabic-Regular.ttf"

text_to_be_reshaped = 'اللغة العربية رائعة'
# reshaped_text = arabic_reshaper.reshape(text_to_be_reshaped)

reshaper = arabic_reshaper.ArabicReshaper(
    arabic_reshaper.config_for_true_type_font(
        FONT_ARABIC_PATH,
        arabic_reshaper.ENABLE_ALL_LIGATURES
    )
)

reshaped_text = reshaper.reshape(text_to_be_reshaped)

# At this stage the text is reshaped, all letters are in their correct form
# based on their surroundings, but if you are going to print the text in a
# left-to-right context, which usually happens in libraries/apps that do not
# support Arabic and/or right-to-left text rendering, then you need to use
# get_display from python-bidi.
# Note that this is optional and depends on your usage of the reshaped text.

from bidi.algorithm import get_display
bidi_text = get_display(reshaped_text)

# At this stage the text in bidi_text can be easily rendered in any library
# that doesn't support Arabic and/or right-to-left, so use it as you'd use
# any other string. For example if you're using PIL.ImageDraw.text to draw
# text over an image you'd just use it like this...

from PIL import Image, ImageDraw, ImageFont

# We load Arial since it's a well known font that supports Arabic Unicode
font = ImageFont.truetype(FONT_ARABIC_PATH, 40)

image = Image.new('RGBA', (800, 600), (255,255,255,0))
image_draw = ImageDraw.Draw(image)
image_draw.text((10,10), bidi_text, fill=(255,255,255,128), font=font)

# Now the text is rendered properly on the image, you can save it to a file or just call `show` to see it working
image.show()

# For more details on PIL.Image and PIL.ImageDraw check the documentation
# See http://pillow.readthedocs.io/en/5.1.x/reference/ImageDraw.html?#PIL.ImageDraw.PIL.ImageDraw.Draw.text
