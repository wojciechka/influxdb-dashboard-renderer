from PIL import Image, ImageDraw, ImageFont
import math

def draw_text_on_canvas(canvas, font_name, box, text, color, border_color=None, border_width=0, max_size=1.0, offset=[0,0]):
  draw = ImageDraw.Draw(canvas)

  (font_size, text_offset) = font_size_and_offset(font_name, box, text, max_size)
  offset = (offset[0] + text_offset[0], offset[1] + text_offset[1])

  font = ImageFont.truetype(font_name, font_size)

  border_width = round(0.025 * border_width * font_size) if border_color != None and border_width != None else 0

  draw.text(offset, text, font=font, fill=color, stroke_width=border_width, stroke_fill=border_color)

def font_size_and_offset(font_name, box, text, max_size):
  font_size = box[1] * 2
  while True:
    font = ImageFont.truetype(font_name, font_size)
    text_offset = font.getoffset(text)
    text_size = font.getsize(text)
    overscale = max(text_size[0] / box[0], text_size[1] / box[1]) / max_size
    if overscale > 2.0:
      font_size = math.floor(font_size * 0.75)
    elif overscale > 1.2:
      font_size = math.floor(font_size * 0.9)
    elif overscale > 1.0:
      font_size = math.floor(font_size * 0.95)
    else:
      break
  offset = (
    math.floor((box[0] - text_size[0] - text_offset[0]) / 2),
    math.floor((box[1] - text_size[1] - text_offset[1]) / 2)
  )
  return (font_size, offset)
