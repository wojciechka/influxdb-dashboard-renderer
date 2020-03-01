from PIL import Image, ImageDraw, ImageFont
from influxdb_dashboard.text import InfluxDBDashboardTextBase
import math

class InfluxDBDashboardSingleStatOutput(InfluxDBDashboardTextBase):
  def __init__(self, cell):
    self.cell = cell

  def draw(self, canvas, output, text=None, box_offset=(0, 0), box=None, max_size=0.95, foreground_color=None, border=False):
    draw = ImageDraw.Draw(canvas)

    if text == None or foreground_color == None:
      row = self.cell.tables[-1].records[-1]
      value = row[self.cell.cell.y_column]

    if text == None:
      text = self.cell.to_string(value, row=row)

    box = box if box != None else (canvas.size[0] - box_offset[0], canvas.size[1] - box_offset[1])

    font_name = 'arialnb.ttf'
    (font_size, offset) = self.font_size_and_offset(font_name, box, text, max_size)
    offset = (offset[0] + box_offset[0], offset[1] + box_offset[1])

    font = ImageFont.truetype(font_name, font_size)
    background_color = output.background_color()
    foreground_color = foreground_color if foreground_color != None else self.cell.to_text_color(output, value=value)

    if border:
      border_width = math.floor(min(math.floor(min(*canvas.size) * 0.02), font_size * 0.02))
      # manual border drawing is workaround for black and white images and stroke issue with draw.text
      draw.text((offset[0] - border_width, offset[1] - border_width), text, font=font, fill=background_color)
      draw.text((offset[0] + border_width, offset[1] - border_width), text, font=font, fill=background_color)
      draw.text((offset[0] - border_width, offset[1] + border_width), text, font=font, fill=background_color)
      draw.text((offset[0] + border_width, offset[1] + border_width), text, font=font, fill=background_color)

    draw.text(offset, text, font=font, fill=foreground_color)
