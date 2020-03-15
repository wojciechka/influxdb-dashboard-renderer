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

    for item_to_draw in self.items_to_draw(canvas, output):
      item_to_draw.draw()
    return canvas

  def items_to_draw(self, canvas, output):
    items_to_draw = []
    if self.cell.type == 'xy':
      items_to_draw.append(
        InfluxDBDashboardGraphOutput(cell=self, canvas=canvas, output=output)
      )
    if self.cell.type == 'gauge':
      items_to_draw.append(
        InfluxDBDashboardGaugeOutput(cell=self, canvas=canvas, output=output)
      )
    elif self.cell.type == 'single-stat':
      items_to_draw.append(
        InfluxDBDashboardSingleStatOutput(cell=self, canvas=canvas, output=output)
      )
    if self.cell.type == 'line-plus-single-stat':
      items_to_draw.append(
        InfluxDBDashboardGraphOutput(cell=self, canvas=canvas, output=output)
      )
      items_to_draw.append(
        InfluxDBDashboardSingleStatOutput(cell=self, canvas=canvas, output=output, max_size=0.6, border=True)
      )
    return items_to_draw

  def to_string(self, value, row=None):
    if type(value).__name__ == 'float':
      n_digits = self.cell.decimal_places if self.cell.decimal_places != None else self.round_digits(value)
      text = '%g' % (round(value, n_digits))
    elif row != None:
      if type(value).__name__ == 'datetime' and row.values.get('__dateformat', None) != None:
        if row.values.get('__localtz', False) == True:
          value = value.astimezone(get_localzone())
        text = value.strftime(row['__dateformat'])
    else:
      text = '%s' % (value)
    return '%s%s%s' % (self.cell.value_prefix, text, self.cell.value_suffix)

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
    elif output.mode == 'bw4':
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
    if output.mode == 'bw4':
      if output.dark:
        color = (170, 170, 170)
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
        color = self.merge_color(colors[c0], colors[c1], cd)

    if fill:
      if output.mode == 'bw':
        alpha = 85
      if output.mode == 'bw4':
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
    elif len(self.cell.colors) == 2:
      # for 2-color gauges, calculate transient colors
      (color0, color1) = self.cell.colors
      min_value = color0['value']
      max_value = self.cell.colors[1]['value']
      cd = (value - color0['value']) / (color1['value'] - color0['value'])
      color = self.merge_color(color0, color1, cd)
    else:
      # for gauges not using 2 colors, render regular ranges
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
    cd = 1.0 if cd > 1.0 else cd
    cd = 0.0 if cd < 0.0 else cd
    hls_color0 = colorsys.rgb_to_hls(*color0['color'])
    hls_color1 = colorsys.rgb_to_hls(*color1['color'])
    merge_color_item = lambda i: hls_color0[i] + (hls_color1[i] - hls_color0[i]) * cd
    return colorsys.hls_to_rgb(merge_color_item(0), merge_color_item(1), merge_color_item(2))
