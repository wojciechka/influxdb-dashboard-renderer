import matplotlib.pyplot as plt
import matplotlib

from influxdb_dashboard.matplotlib_output import InfluxDBDashboardMatplotlibOutput

class InfluxDBDashboardGraphOutput(InfluxDBDashboardMatplotlibOutput):
  def draw_figure(self, canvas, output):
    self.init_figure_and_axes(show_axes=True)

    self.ybounds = self.cell.cell.y_axis.get('bounds', ['', ''])

    idx = 0
    self.table_count = len(self.cell.tables)
    for table in self.cell.tables:
      self.draw_table(table, output, idx)
      idx += 1

    if self.ybounds[0] != '' and self.ybounds[1] != '':
      self.ax.set_ylim((float(self.ybounds[0]), float(self.ybounds[1])))

  def draw_table(self, table, output, idx):
    plot_color = self.cell.to_scale_color(output, idx, self.table_count, in_graph=True)
    fill_color = self.cell.to_scale_color(output, idx, self.table_count, fill=True, in_graph=True)

    xd = []
    yd = []
    for row in table.records:
      xv = row.values[self.cell.cell.x_column]
      yv = row.values[self.cell.cell.y_column]
      if xv != None:
        xd += [xv]
        yd += [yv if yv != None else 0.0]
    if len(yd) > 0:
      p = self.ax.plot(xd, yd, color=plot_color)
      if self.cell.cell.shade_below:
        if self.ybounds[0] != '':
          fill_between = float(self.ybounds[0])
        else:
          fill_between = min(*yd)
        self.ax.fill_between(xd, yd, fill_between, color=fill_color)
