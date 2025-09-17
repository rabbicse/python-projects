from arabic_animations.core.scene import Scene
from arabic_animations.core.text import Text
from arabic_animations.core.position import Position

# Create scene
scene = Scene(width=1920, height=1080)

# Create and add text
text = Text(
    "بسم الله الرحمن الرحيم",
    position=Position.CENTER,
    font_name="DecoType Thuluth II",
    font_size=128,
    write_duration=2.0
)

scene.add(text)
