from PIL import Image, ImageDraw, ImageFont
from influxdb_dashboard.graph import InfluxDBDashboardGraphOutput
from influxdb_dashboard.gauge import InfluxDBDashboardGaugeOutput
from influxdb_dashboard.single_stat import InfluxDBDashboardSingleStatOutput
from tzlocal import get_localzone
import pytz
import math
import colorsys

class InfluxDBDashboardCellOutput:
  def __init__(self, cell, tables):
    self.cell = cell
    self.tables = tables

  def draw(self, output):
    canvas = output.draw_canvas(cols=self.cell.w, rows=self.cell.h)
    if self.cell.type == 'xy':
      InfluxDBDashboardGraphOutput(self).draw(canvas, output)
    if self.cell.type == 'gauge':
      InfluxDBDashboardGaugeOutput(self).draw(canvas, output)
    elif self.cell.type == 'single-stat':
      if self.cell.name != '':
        title_height = int(round(18 * output.dpi / 100))
        InfluxDBDashboardSingleStatOutput(self).draw(
          canvas, output, box=(canvas.size[0], title_height),
          text=self.cell.name, foreground_color=output.foreground_color())
        InfluxDBDashboardSingleStatOutput(self).draw(canvas, output, box_offset=(0, title_height))
      else:
        InfluxDBDashboardSingleStatOutput(self).draw(canvas, output)
    if self.cell.type == 'line-plus-single-stat':
      InfluxDBDashboardGraphOutput(self).draw(canvas, output, has_stat=True)
      InfluxDBDashboardSingleStatOutput(self).draw(canvas, output, max_size=0.6, border=True)
    return canvas

  def to_string(self, value, row=None):
    if type(value).__name__ == 'float':
      n_digits = self.cell.decimal_places if self.cell.decimal_places != None else self.round_digits(value)
      return '%g' % (round(value, n_digits))
    elif row != None:
      if type(value).__name__ == 'datetime' and row.values.get('__dateformat', None) != None:
        if row.values.get('__localtz', False) == True:
          value = value.astimezone(get_localzone())
        return value.strftime(row['__dateformat'])
    return '%s' % (value)

  def round_digits(self, vmax, vmin=0):
    diff = vmax - vmin
    diffLog10 = math.log10(diff)
    return max(0, round(2 - diffLog10))

  def to_text_color(self, output, value=None, in_graph=False):
    colors = self.cell.color_map['text']
    if output.mode == 'bw':
      if output.dark:
        color = (255, 255, 255)
      else:
        color = (0, 0, 0)
    else:
      color = colors[0]['color']
      if value != None and len(colors) > 1:
        for c in colors:
          if value >= c['value']:
            color = c['color']
    return self.return_color(color, in_graph)

  def to_scale_color(self, output, index, total, fill=False, in_graph=False):
    colors = self.cell.color_map['scale']
    if output.mode == 'bw':
      if output.dark:
        color = (255, 255, 255)
      else:
        color = (0, 0, 0)

    elif len(colors) < 2 or total < 2:
      color = colors[0]['color']
    elif len(colors) > total:
      color = colors[index]['color']
    else:
      ci = (len(colors) - 1) * index / (total - 1)
      c0 = math.floor(ci)
      c1 = math.ceil(ci)
      if c0 == c1:
        color = colors[c0]['color']
      else:
        cd = ci - c0
        color0 = colorsys.rgb_to_hls(*colors[c0]['color'])
        color1 = colorsys.rgb_to_hls(*colors[c1]['color'])
        color = colorsys.hls_to_rgb(*self.merge_color(color0, color1, cd))

    if fill:
      if output.mode == 'bw':
        alpha = 85
      else:
        alpha = 100
      if len(color) > 3:
        color[3] = alpha
      else:
        color = list(color) + [alpha]

    return self.return_color(color, in_graph)

  def to_gauge_color(self, output, value, in_graph=False):
    if output.mode == 'bw':
      if output.dark:
        color = (255, 255, 255)
      else:
        color = (0, 0, 0)
    else:
      color = self.cell.colors[0]['color']
      for col in self.cell.colors[1:-1]:
        if value >= col['value']:
          color = col['color']
    return self.return_color(color, in_graph)


  def return_color(self, color, in_graph):
    if in_graph:
      return list(map(lambda c: c / 255.0, color))
    else:
      return '#' + ''.join(map(lambda c: '%02x' % (c), color))

  def merge_color(self, color0, color1, cd):
    merge_color_item = lambda i: color0[i] + (color1[i] - color0[i]) * cd
    return (merge_color_item(0), merge_color_item(1), merge_color_item(2))
