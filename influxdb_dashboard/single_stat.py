from PIL import Image, ImageDraw, ImageFont
from influxdb_dashboard.text import draw_text_on_canvas
from influxdb_dashboard import cell
import math

from influxdb_dashboard.output import InfluxDBDashboardBaseOutput

# TODO: move to another file
ALERT_COLORS_WARN = [
  '#f48d38', # tiger
  '#f95f53', # curacao
]
ALERT_COLORS_CRIT = [
  '#bf3d5e', # ruby
  '#dc4e58', # fire
]

class InfluxDBDashboardSingleStatOutput(InfluxDBDashboardBaseOutput):
  def __init__(self, border=False, max_size=0.9, **kwargs):
    self.border = border
    self.max_size = max_size
    super().__init__(**kwargs)

  def alert_state(self):
    (row, value) = self.latest_row_and_value()
    if value == None:
      return cell.ALERT_STATE_OK

    (foreground_color, background_color) = self.cell.to_text_and_background_color(None, value=value)
    if (foreground_color in ALERT_COLORS_CRIT) or (background_color in ALERT_COLORS_CRIT):
      return cell.ALERT_STATE_CRIT
    if (foreground_color in ALERT_COLORS_WARN) or (background_color in ALERT_COLORS_WARN):
      return cell.ALERT_STATE_WARN
    else:
      return cell.ALERT_STATE_OK

  def draw_figure(self, canvas, output, text=None, box_offset=(0, 0), box=None):
    if text == None or foreground_color == None:
      (row, value) = self.latest_row_and_value()

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
