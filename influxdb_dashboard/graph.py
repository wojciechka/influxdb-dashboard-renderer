import matplotlib.pyplot as plt
import matplotlib
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

class InfluxDBDashboardGraphOutput:
  def __init__(self, cell):
    self.cell = cell

  def draw(self, canvas, output, has_stat=False):
    background_color = output.background_color()
    foreground_color = output.foreground_color()

    figsize = (canvas.size[0] / output.dpi, canvas.size[1] / output.dpi)
    fig = plt.figure(figsize=figsize, dpi=output.dpi, facecolor=background_color, edgecolor=background_color)
    ax = self.init_axes(fig, background_color, foreground_color)
    ax.xaxis.set_visible(False)

    ybounds = self.cell.cell.y_axis.get('bounds', ['', ''])

    idx = 0
    table_count = len(self.cell.tables)
    for table in self.cell.tables:
      xd = []
      yd = []
      for row in table.records:
        xv = row.values[self.cell.cell.x_column]
        yv = row.values[self.cell.cell.y_column]
        if xv != None:
          xd += [xv]
          yd += [yv if yv != None else 0.0]
      if len(yd) > 0:
        color = self.cell.to_scale_color(output, idx, table_count, in_graph=True)
        p = ax.plot(xd, yd, color=color)
        if self.cell.cell.shade_below:
          if ybounds[0] != '':
            fill_between = float('0')
          else:
            fill_between = min(*yd)
          color = self.cell.to_scale_color(output, idx, table_count, fill=True, in_graph=True)
          ax.fill_between(xd, yd, fill_between, color=color)
      idx += 1

    if ybounds[0] != '' and ybounds[1] != '':
      ax.set_ylim((float(ybounds[0]), float(ybounds[1])))

    self.paste_figure(canvas, fig, background_color)

  def paste_figure(self, canvas, fig, background_color):
    bytes = BytesIO()
    fig.savefig(fname=bytes, format='png', facecolor=background_color, edgecolor=background_color)
    bytes.seek(0)
    with Image.open(bytes) as img:
      canvas.paste(img)
      img.close()

  def init_axes(self, fig, background_color, foreground_color):
    ax = fig.gca(facecolor=background_color)
    ax.title.set_color(foreground_color)
    ax.set_title(self.cell.cell.name)

    ax.tick_params(axis='x', colors=foreground_color)
    ax.tick_params(axis='y', colors=foreground_color)
    ax.xaxis.label.set_color(foreground_color)
    ax.yaxis.label.set_color(foreground_color)

    for child in ax.get_children():
      if isinstance(child, matplotlib.spines.Spine):
        child.set_color(foreground_color)
    return ax
