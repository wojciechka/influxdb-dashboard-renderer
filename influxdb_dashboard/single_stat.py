from PIL import Image, ImageDraw, ImageFont
from influxdb_dashboard.text import draw_text_on_canvas
import math

from influxdb_dashboard.output import InfluxDBDashboardBaseOutput

class InfluxDBDashboardSingleStatOutput(InfluxDBDashboardBaseOutput):
  def __init__(self, border=False, max_size=0.9, **kwargs):
    self.border = border
    self.max_size = max_size
    super().__init__(**kwargs)

  def draw_figure(self, canvas, output, text=None, box_offset=(0, 0), box=None):
    if text == None or foreground_color == None:
      if len(self.cell.tables) > 0 and len(self.cell.tables[-1].records) > 0:
        row = self.cell.tables[-1].records[-1]
        value = row[self.cell.cell.y_column]
      else:
        value = ""
        row = None

    if text == None:
      text = self.cell.to_string(value, row=row)

    border_width = 1

    (foreground_color, background_color) = self.cell.to_text_and_background_color(output, value=value)

    box = box if box != None else (canvas.size[0] - box_offset[0], canvas.size[1] - box_offset[1])

    draw_text_on_canvas(
      canvas, output.font_name, box, text,
      foreground_color,
      border_color=background_color,
      border_width=border_width,
      max_size=self.max_size,
      offset=box_offset
    )
