import matplotlib.pyplot as plt
from matplotlib import patches
import math

from influxdb_dashboard.matplotlib_output import InfluxDBDashboardMatplotlibOutput

class InfluxDBDashboardGaugeOutput(InfluxDBDashboardMatplotlibOutput):
  def draw_figure(self, canvas, output):
    self.init_degrees()
    # TODO: move to helper
    minfigdim = min(*canvas.size)
    figsize = (minfigdim, minfigdim)
    self.base_width = minfigdim * 0.25 / output.dpi

    figsize = (minfigdim, minfigdim)
    self.init_figure_and_axes(figsize=figsize, show_axes=False)

    # draw all value ranges
    self.draw_ranges(output)

    # draw lines for 5 values and add labels next to tken

    # show current value if specified
    if len(self.cell.tables) > 0 and len(self.cell.tables[-1].records) > 0:
      row = self.cell.tables[-1].records[-1]
      value = row[self.cell.cell.y_column]
      self.draw_value_text(output, value, row)
      self.draw_value_indicator(output, value)

  def draw_ranges(self, output):
    # TODO: draw as transition when 2 colors specified
    for i in range(0, len(self.value_range) - 1):
      val0 = self.value_range[i + 0]
      val1 = self.value_range[i + 1]
      color = self.cell.to_gauge_color(output, val0, in_graph=True)
      self.ax.add_patch(
        patches.Wedge(
          (0.5, 0.4), 0.44, *self.fig_value_angles(val0, val1),
          facecolor=color, edgecolor=self.background_color,
          lw=self.base_width
        )
      )

    self.ax.add_patch(
      patches.Circle(
        (0.5, 0.4), 0.36,
        facecolor=self.background_color
      )
    )

  def draw_value_labels(self, output):
    for degree in range(0, 271, 54):
      value = self.value(degree)
      value_text = self.cell.to_string(value)
      polygon_coords = [
        self.angle_coords(degree, 0.44),
        self.angle_coords(degree, 0.45)
      ]
      self.ax.add_patch(
        patches.Polygon(
          polygon_coords, color=self.foreground_color, lw=self.base_width
        )
      )
      self.ax.text(
        *self.angle_coords(degree, 0.475),
        value_text,
        horizontalalignment='center', verticalalignment='center',
        fontsize=round(self.base_width * 5), fontweight='bold', color=self.foreground_color
      )

  def draw_value_indicator(self, output, value):
    value_degree = self.degree(value)
    if value_degree < 0.0:
      value_degree = 0.0
    elif value_degree > 280.0:
      value_degree = 280.0

    polygon_coords = [
      self.angle_coords(value_degree - 90, 0.022),
      self.angle_coords(value_degree + 90, 0.022),
      self.angle_coords(value_degree, 0.4)
    ]
    self.ax.add_patch(
      patches.Polygon(
        polygon_coords,
        facecolor=self.foreground_color, edgecolor=self.background_color, lw=self.base_width
      )
    )
    self.ax.add_patch(
      patches.Circle(
        (0.5, 0.4), 0.02,
        facecolor=self.foreground_color
      )
    )
    
  def draw_value_text(self, output, value, row):
    value_text = self.cell.to_string(value, row=row)

    self.ax.text(
      0.5, 0.1,
      value_text,
      horizontalalignment='center', verticalalignment='center',
      fontsize=round(self.base_width * 25), fontweight='bold', color=self.foreground_color
    )


  # helper methods for coordinates

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
