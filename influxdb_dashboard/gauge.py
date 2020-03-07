import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Wedge, Polygon
import matplotlib
import math

from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

class InfluxDBDashboardGaugeOutput:
  def __init__(self, cell):
    self.cell = cell

  def draw(self, canvas, output, has_stat=False):
    self.init_degrees()

    background_color = output.background_color()
    foreground_color = output.foreground_color()

    figdim = [canvas.size[0] / output.dpi, canvas.size[1] / output.dpi]
    minfigdim = min(*figdim)
    base_width = minfigdim * 0.25

    figsize = (minfigdim, minfigdim)

    fig = plt.figure(figsize=figsize, dpi=output.dpi, facecolor=background_color, edgecolor=background_color)
    ax = self.init_axes(fig, background_color, foreground_color)

    for i in range(0, len(self.value_range) - 1):
      val0 = self.value_range[i + 0]
      val1 = self.value_range[i + 1]
      color = self.cell.to_gauge_color(output, val0, in_graph=True)
      ax.add_patch(Wedge((0.5, 0.4), 0.44, *self.fig_value_angles(val0, val1), facecolor=color, edgecolor=background_color, lw=base_width))
    ax.add_patch(Circle((0.5, 0.4), 0.36, facecolor=background_color))

    # draw 5 values
    for degree in range(0, 271, 54):
      value = self.value(degree)
      value_text = self.cell.to_string(value)
      polygon_coords = [
        self.angle_coords(degree, 0.44),
        self.angle_coords(degree, 0.45)
      ]
      ax.add_patch(Polygon(polygon_coords, color=foreground_color, lw=base_width))
      ax.text(
        *self.angle_coords(degree, 0.475),
        value_text,
        horizontalalignment='center', verticalalignment='center',
        fontsize=round(base_width * 5), fontweight='bold', color=foreground_color
      )

    if len(self.cell.tables) > 0:
      if len(self.cell.tables[-1].records) > 0:
        row = self.cell.tables[-1].records[-1]
        value = row[self.cell.cell.y_column]
        value_text = self.cell.to_string(value, row=row)

        ax.text(
          0.5, 0.1,
          value_text,
          horizontalalignment='center', verticalalignment='center',
          fontsize=round(base_width * 25), fontweight='bold', color=foreground_color
        )

        value_degree = self.degree(value)
        if value_degree < 0.0:
          value_degree = 0.0
        elif value_degree > 180.0:
          value_degree = 180.0

        polygon_coords = [
          self.angle_coords(value_degree - 90, 0.022),
          self.angle_coords(value_degree + 90, 0.022),
          self.angle_coords(value_degree, 0.4)
        ]
        ax.add_patch(Polygon(polygon_coords, facecolor=foreground_color, edgecolor=background_color, lw=base_width))
        ax.add_patch(Circle((0.5, 0.4), 0.02, facecolor=foreground_color))

    self.paste_figure(canvas, fig, background_color)

  def angle_coords(self, angle, size, basex=0.5, basey=0.4):
    ra = math.radians(-135 + angle)
    return (
      basex + math.sin(ra) * size,
      basey + math.cos(ra) * size
    )

  def fig_value_angles(self, val0, val1):
    vmin = self.degree(min([val0, val1]))
    vmax = self.degree(max([val0, val1]))
    return [-135-vmax, -135-vmin]

  def init_degrees(self):
    self.value_range = list(map(lambda c: c['value'], self.cell.cell.colors))
    if len(self.value_range) < 2:
      self.value_range = [0.0, max(*self.value_range)]
    self.value_base = min(*self.value_range)
    self.value_diff = max(*self.value_range) - self.value_base

  def value(self, degree):
    return(self.value_base + self.value_diff * (degree / 270))

  def degree(self, value):
    return(0 + 270 * (value - self.value_base) / self.value_diff)

  def paste_figure(self, canvas, fig, background_color):
    bytes = BytesIO()
    fig.savefig(fname=bytes, format='png', facecolor=background_color, edgecolor=background_color)
    bytes.seek(0)
    with Image.open(bytes) as img:
      offset = (
        round((canvas.size[0] - img.size[0]) / 2),
        round((canvas.size[1] - img.size[1]) / 2)
      )
      canvas.paste(img, box=offset)
      img.close()

  def init_axes(self, fig, background_color, foreground_color):
    ax = fig.gca(facecolor=background_color)
    ax.title.set_color(foreground_color)
    ax.set_title(self.cell.cell.name)
    ax.set_axis_off()
    return ax
