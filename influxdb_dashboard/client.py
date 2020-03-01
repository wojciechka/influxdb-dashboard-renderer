# wrapper around InfluxDBClient to handle dashboard and cells

from influxdb_client import InfluxDBClient, CellsService, DashboardsService
from influxdb_dashboard.cell import InfluxDBDashboardCellOutput

# TODO: open a PR against https://github.com/influxdata/influxdb-client-python/ to expose dashboards API

class InfluxDBDashboardCell:
  def __init__(self, client, org_id, dashboard_id, cell_info):
    self.client = client
    self.cell_info = cell_info
    self.org_id = org_id
    self.dashboard_id = dashboard_id
    self.cs = CellsService(self.client.api_client)
    self.init_cell()
    self.init_queries()
    self.init_axes()
    self.init_colors()

  def init_cell(self):
    self.id = self.cell_info.id
    self.x = self.cell_info.x
    self.y = self.cell_info.y
    self.w = self.cell_info.w
    self.h = self.cell_info.h
    self.yh = self.y + self.h
    self.info = self.cs.get_dashboards_id_cells_id_view(self.dashboard_id, self.id)
    self.type = self.info.properties.get('type', 'xy')
    self.name = self.info.name

  def init_queries(self):
    self.queries = map(lambda q: q['text'], self.info.properties['queries'])
    self.query_api = self.client.query_api()

  def init_axes(self):
    self.x_column = self.info.properties.get('xColumn', '_time')
    if self.x_column == '':
      self.x_column = '_time'
    self.y_column = self.info.properties.get('yColumn', '_value')
    if self.y_column == '':
      self.y_column = '_value'
    self.x_axis = self.info.properties.get('axes', {}).get('x', {})
    self.y_axis = self.info.properties.get('axes', {}).get('y', {})
    self.shade_below = self.info.properties.get('shadeBelow', False)
    decimal_places = self.info.properties.get('decimalPlaces', {'isEnforced': False})
    self.decimal_places = int(decimal_places['digits']) if decimal_places['isEnforced'] else None

  def init_colors(self):
    convert_color = lambda c: {**c, 'color': (int(c['hex'][1:3], 16), int(c['hex'][3:5], 16), int(c['hex'][5:7], 16))}
    text_colors = filter(lambda c: c['type'] == 'text', self.info.properties['colors'])
    scale_colors = filter(lambda c: c['type'] == 'scale', self.info.properties['colors'])
    self.text_colors = list(map(convert_color, text_colors))
    self.scale_colors = list(map(convert_color, scale_colors))

  def queries(self):
    return self.queries

  def results(self):
    return map(lambda q: self.query_api.query(q), self.queries)

  def flat_results(self):
    tables = []
    for result in self.results():
      tables += result
    return tables

  def cell_output(self):
    return InfluxDBDashboardCellOutput(self, self.flat_results())

class InfluxDBDashboardView:
  def __init__(self, client, org_id, dashboard_id):
    self.client = client
    self.org_id = org_id
    self.id = dashboard_id
    self.ds = DashboardsService(self.client.api_client)
    info = self.ds.get_dashboards_id(self.id)
    self.name = info.name
    self.description = info.description
    self.cells_info = info.cells

  def cells(self):
    return map(lambda cell_info: InfluxDBDashboardCell(self.client, self.org_id, self.id, cell_info), self.cells_info)

  @classmethod
  def find_by_label(cls, client, org_id, label_name):
    match_label = (lambda d: len([l for l in d.labels if l.name == label_name]) > 0)
    ds = DashboardsService(client.api_client)
    dashboards = ds.get_dashboards(org_id=org_id).dashboards
    matches = [d for d in dashboards if match_label(d)]
    if len(matches) == 0:
      return None
    else:
      return cls(client, org_id, matches[0].id)
