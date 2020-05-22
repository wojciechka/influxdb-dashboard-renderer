import matplotlib.pyplot as plt
import matplotlib
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

from influxdb_dashboard.output import InfluxDBDashboardBaseOutput

class InfluxDBDashboardMatplotlibOutput(InfluxDBDashboardBaseOutput):
  def draw(self):
    self.background_color = self.output.background_color()
    self.foreground_color = self.output.foreground_color()

    self.init_figure_and_axes()
    self.draw_figure(self.canvas, self.output)
    self.paste_figure()
    plt.close(self.fig)

  def draw_figure(self, canvas, output):
    None

  def init_figure_and_axes(self, figsize=None, show_axes=True, constrained_layout=True):
    if figsize == None:
      figsize = self.canvas.size

    figsize = (figsize[0] / self.output.dpi, figsize[1] / self.output.dpi)

    self.fig = plt.figure(
      figsize=figsize, dpi=self.output.dpi,
      facecolor=self.background_color, edgecolor=self.background_color,
      constrained_layout=constrained_layout
    )
    self.ax = self.fig.gca(facecolor=self.background_color)

    if show_axes:
      self.ax.tick_params(axis='x', colors=self.foreground_color)
      self.ax.tick_params(axis='y', colors=self.foreground_color)
      self.ax.xaxis.label.set_color(self.foreground_color)
      self.ax.yaxis.label.set_color(self.foreground_color)
      self.ax.xaxis.set_visible(False)

      for child in self.ax.get_children():
        if isinstance(child, matplotlib.spines.Spine):
          child.set_color(self.foreground_color)
    else:
      self.ax.set_axis_off()

  def paste_figure(self):
    bytes = BytesIO()
    self.fig.savefig(fname=bytes, format='png', facecolor=self.background_color, edgecolor=self.background_color)
    bytes.seek(0)
    with Image.open(bytes) as img:
      offset = (
        round((self.canvas.size[0] - img.size[0]) / 2),
        round((self.canvas.size[1] - img.size[1]) / 2)
      )
      self.canvas.paste(img, box=offset)
      img.close()
    bytes.close()
