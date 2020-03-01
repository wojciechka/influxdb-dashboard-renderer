import math
from PIL import Image, ImageDraw, ImageFont

class InfluxDBDashboardOutput:
  def __init__(self, width=1920, height=1080, cols=12, rows=8, dpi=100, mode='color', dark=True):
    self.x = self.axis_data(width, cols, dpi)
    self.y = self.axis_data(height, rows, dpi)
    self.dpi = dpi
    self.mode = mode
    self.dark = dark

  def axis_data(self, size, items, dpi):
    item_size = math.floor(size / items)
    item_offset = math.floor((size - item_size * items) / 2)
    offset_table = []
    for i in range(items):
      offset_table += [item_offset + item_size * i]
    return {
      'size': size,
      'item_size': item_size,
      'item_offset': item_offset,
      'dpi': dpi,
      'offset_table': offset_table
    }

  def draw_canvas(self, cols=None, rows=None, color=None):
    image_mode = 'RGB'
    if self.mode == 'color':
      image_mode = 'RGB'
    elif self.mode == 'greyscale':
      image_mode = 'L'
    elif self.mode == 'bw':
      image_mode = '1'
    else:
      raise Exception('Unknown output mode: %s' % (self.mode))
    if cols != None:
      width = self.x['item_size'] * cols
    else:
      width = self.x['size']
    if rows != None:
      height = self.y['item_size'] * rows
    else:
      height = self.y['size']
    if color == None:
      color = self.background_color()
    return Image.new(image_mode, (width, height), color=color)

  def draw(self, dashboard):
    canvas = self.draw_canvas()
    for cell in dashboard.cells():
      img = cell.cell_output().draw(self)
      box = (self.x['offset_table'][cell.x], self.y['offset_table'][cell.y])
      canvas.paste(img, box=box)
    return canvas

  def background_color(self):
    if self.dark: 
      return '#000000'
    else:
      return '#ffffff'

  def foreground_color(self):
    if self.dark: 
      return '#ffffff'
    else:
      return '#000000'
