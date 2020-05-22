# wrapper around InfluxDBClient to handle dashboard and cells

from influxdb_client import InfluxDBClient, CellsService, DashboardsService, Dialect, QueryService, Query
from influxdb_client.client.flux_csv_parser import FluxCsvParser, FluxSerializationMode
from influxdb_dashboard.cell import InfluxDBDashboardCellOutput

# TODO: open a PR against https://github.com/influxdata/influxdb-client-python/ to expose dashboards API
# TODO: open a PR against https://github.com/influxdata/influxdb-client-python/ to allow passing extern

class InfluxDBDashboardExtern:
  def __init__(self, variable='v'):
    self.variable = variable
    self.properties = []

  def remove_property(self, name):
    self.properties = list(filter(lambda property: property['key']['name'] != name, self.properties))

  def add_string_literal(self, name, value):
    self.remove_property(name)
    self.properties += [
      {
        'type': 'Property',
        'key': { 'type': 'Identifier', 'name': name },
        'value': {
          'type': 'StringLiteral',
          'value': value,
        }
      }
    ]

  def add_time_offset_variable(self, name, offset, offset_unit='h'):
    self.remove_property(name)
    self.properties += [
      {
        'type': 'Property',
        'key': { 'type': 'Identifier', 'name': name },
        'value': {
          'type': 'UnaryExpression',
          'operator': '-',
          'argument': { 'type': 'DurationLiteral', 'values': [{ 'magnitude': -(offset), 'unit': offset_unit }] }
        }
      }
    ]

  def add_now(self, name):
    self.remove_property(name)
    self.properties += [
      {
        'type': 'Property',
        'key': { 'type': 'Identifier', 'name': name },
        'value': {
          'type': 'CallExpression',
          'callee': { 'type': 'Identifier', 'name': 'now' }
        }
      }
    ]

  def add_duration_variable(self, name, offset, offset_unit='h'):
    self.remove_property(name)
    self.properties += [
      {
        'type': 'Property',
        'key': { 'type': 'Identifier', 'name': name },
        'value': {
          'type': 'DurationLiteral',
          'values': [{ 'magnitude': (offset), 'unit': offset_unit }]
        }
      }
    ]

  def serialize(self):
    return {
      'type': 'File', 'package': None, 'imports': None,
      'body': [
          {
          'type': 'OptionStatement', 'assignment': {
            'type': 'VariableAssignment',
            'id': {'type':'Identifier', 'name': self.variable },
            'init': {
              'type': 'ObjectExpression',
              'properties': self.properties
            }
          }
        }
      ]
    }


class InfluxDBDashboardCell:
  def __init__(self, client, org_id, dashboard_id, cell_info):
    self._results = None
    self.client = client
    self.cell_info = cell_info
    self.org_id = org_id
    self.dashboard_id = dashboard_id
    self.cs = CellsService(self.client.api_client)
    self.init_cell()
    self.init_queries()
    self.init_axes()
    self.init_colors()
    self.init_params()

  def init_cell(self):
    self.id = self.cell_info.id
    self.x = self.cell_info.x
    self.y = self.cell_info.y
    self.w = self.cell_info.w
    self.h = self.cell_info.h
    self.yh = self.y + self.h
    self.info = self.cs.get_dashboards_id_cells_id_view(self.dashboard_id, self.id)
    self.type = self.info.properties.get('type', 'xy')
    self.value_prefix = self.info.properties.get('prefix', '')
    self.value_suffix = self.info.properties.get('suffix', '')
    self.name = self.info.name

  def init_queries(self):
    self.queries = map(lambda q: q['text'], self.info.properties.get('queries', []))
    self.query_api = self.client.query_api()
    self.query_service = QueryService(self.client.api_client)

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
    self.colors = list(map(convert_color, self.info.properties.get('colors', [])))
    self.color_map = {}
    for c in self.colors:
      t = c['type']
      if not t in self.color_map:
        self.color_map[t] = []
      self.color_map[t] += [c]

  def init_params(self):
    self._extern_obj = InfluxDBDashboardExtern('v')
    self.set_time_range()

  def set_time_range(self, start_offset=-(7*24*60), end_offset=0, window_period=15, offset_unit='m'):
    self._extern_obj.add_time_offset_variable('timeRangeStart', start_offset, offset_unit=offset_unit)
    self._extern_obj.add_time_offset_variable('timeRangeStop', end_offset, offset_unit=offset_unit)
    self._extern_obj.add_duration_variable('windowPeriod', window_period, offset_unit=offset_unit)
    self._extern = self._extern_obj.serialize()
    # invalidate any previously stored results
    self._results = None

  def set_string_literval_variable(self, name, value):
    # TODO: handle duplicated values
    self._extern_obj.add_string_literal(name, value)
    self._extern = self._extern_obj.serialize()
    # invalidate any previously stored results
    self._results = None

  def queries(self):
    return self.queries

  def retrieve_result(self, query_string):
    # TODO: this method is hopefully temporary until InfluxDB /api/v2/query API simplifies passing

    # mimic default dialect
    dialect = Dialect(
      header=True, delimiter=",", comment_prefix="#",
      annotations=["datatype", "group", "default"], date_time_format="RFC3339"
    )

    query = Query(query=query_string, dialect=dialect, extern=self._extern)
    response = self.query_service.post_query(
      org=self.client.org,
      query=query,
      async_req=False, _preload_content=False, _return_http_data_only=False
    )
    _parser = FluxCsvParser(response=response, serialization_mode=FluxSerializationMode.tables)
    list(_parser.generator())
    return _parser.tables

  def results(self):
    if self._results == None:
      self._results = list(map(self.retrieve_result, self.queries))
    return self._results

  def flat_results(self):
    tables = []
    for result in self.results():
      tables += result
    return tables

  def cell_output(self):
    return InfluxDBDashboardCellOutput(self, self.flat_results())

class InfluxDBDashboardView:
  def __init__(self, client, dashboard_id, org_id=None):
    if org_id == None:
      org_id = client.org
    self.client = client
    self.org_id = org_id
    self.id = dashboard_id
    self.ds = DashboardsService(self.client.api_client)
    info = self.ds.get_dashboards_id(self.id)
    self.name = info.name
    self.description = info.description
    self.cells_info = info.cells
    self.init_height()
    self._cells = None

  def init_height(self):
    items = [1] + list(map(lambda c: 0 + c.y + c.h, self.cells_info))
    self.height = max(*items)

  def cells(self):
    if self._cells == None:
      self._cells = list(map(lambda cell_info: InfluxDBDashboardCell(self.client, self.org_id, self.id, cell_info), self.cells_info))
    return self._cells

  def set_time_range(self, start_offset=-(7*24*60), end_offset=0, window_period=15, offset_unit='m'):
    for cell in self.cells():
      cell.set_time_range(start_offset=start_offset, end_offset=end_offset, window_period=window_period, offset_unit=offset_unit)

  def set_string_literval_variable(self, name, value):
    for cell in self.cells():
      cell.set_string_literval_variable(name, value)

  # TODO: improve

  @classmethod
  def find_by_label(cls, client, label_name, org_id=None):
    match_label = (lambda d: len([l for l in d.labels if l.name == label_name]) > 0)
    ds = DashboardsService(client.api_client)
    if org_id == None:
      org_id = client.org
    dashboards = ds.get_dashboards(org_id=org_id).dashboards
    matches = [d for d in dashboards if match_label(d)]
    if len(matches) == 0:
      return None
    else:
      return cls(client, matches[0].id, org_id=org_id)
