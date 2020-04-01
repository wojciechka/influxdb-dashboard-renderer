import math
from PIL import Image, ImageDraw, ImageFont
from influxdb_dashboard.text import draw_text_on_canvas

class InfluxDBDashboardBaseOutput:
  def __init__(self, cell=None, canvas=None, output=None):
    self.cell = cell
    self.canvas = canvas
    self.output = output

  def draw(self):
    self.background_color = self.output.background_color()
    self.foreground_color = self.output.foreground_color()
    self.draw_figure(self.canvas, self.output)

  def latest_row_and_value(self):
    if len(self.cell.tables) > 0 and len(self.cell.tables[-1].records) > 0:
      row = self.cell.tables[-1].records[-1]
      value = row[self.cell.cell.y_column]
      return (row, value)
    else:
      return [None, None]



class InfluxDBDashboardOutput:
  def __init__(self, width=1920, height=1080, cols=12, rows=8, dpi=100, mode='color', dark=True, font_name='arialnb.ttf', show_titles=True):
    self.x = self.axis_data(width, cols, dpi)
    self.y = self.axis_data(height, rows, dpi)
    self.title_height = title_height = int(round(22 * dpi / 100)) if show_titles else 0
    self.font_name = font_name
    self.dpi = dpi
    self.mode = mode
    self.dark = dark

  def draw(self, dashboard):
    canvas = self.draw_canvas(output_canvas=True)
    for cell in dashboard.cells():
      cell_output = cell.cell_output()
      self.draw_title(canvas, cell, cell_output)
      img = cell_output.draw(self)
      box = (self.x['offset_table'][cell.x], self.y['offset_table'][cell.y] + self.title_height)
      canvas.paste(img, box=box)
    return self.output_canvas(canvas)

  def draw_title(self, canvas, cell, cell_output):
    if self.title_height > 0 and cell.name != None:
      size = (self.x['item_size'] * cell.w, self.title_height)
      box = (self.x['offset_table'][cell.x], self.y['offset_table'][cell.y])
      draw_text_on_canvas(
        canvas, self.font_name, size, cell.name,
        self.foreground_color(),
        offset=box,
        max_size=0.9
      )

  def output_canvas(self, canvas):
    if self.mode == 'bw':
      # workaround for font border not being drawn correctly unless the image is converted to 3 colors
      temp = Image.eval(canvas, lambda a: [0, 128, 255][round(2 * a / 255.0)])
      canvas = Image.new('1', temp.size)
      canvas.paste(temp)
    elif self.mode == 'bw4':
      # draw image in 4 colors
      canvas = Image.eval(canvas, lambda a: [0, 85, 170, 255][round(3 * a / 255.0)])
    return canvas

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

  def draw_canvas(self, cols=None, rows=None, color=None, output_canvas=False):
    image_mode = 'RGB'
    if self.mode == 'color':
      image_mode = 'RGB'
    elif self.mode == 'greyscale':
      image_mode = 'L'
    elif self.mode == 'bw':
      image_mode = 'L'
    elif self.mode == 'bw4':
      image_mode = 'L'
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
    # add placeholder for title
    if not output_canvas:
      height = height - self.title_height
    return Image.new(image_mode, (width, height), color=color)

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
