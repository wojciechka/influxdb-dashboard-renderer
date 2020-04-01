# InfluxDB 2.0 Dashboard Renderer

Code that renders (subset of) InfluxDB 2.0 Dashboards as images.

The first goal of the project is to render dashboards that only use a subset of InfluxDB 2.0 functionality as an image.

The longer term goal is to mimic most views and specifics of InfluxDB 2.0 dashboards to also allow rendering more complex dashboards.

# Example dashboard

Below is an example rendering of a dashboard:

![Example output dashboard](docs/example-dashboard.png)

Along with a screenshot of InfluxDB dashboard for comparsison:

![Example original dashboard](docs/example-dashboard-infludb.png)

# What is currently working

- Basic Flux queries
- Queries that require `v.timeRangeStart`, `v.timeRangeStop` and `v.windowPeriod`
- Graph cells
- Single stat cells
- Graph + single stat cells (with minor caveats regarding centering of single stat relative to graph)
- gauge cells (currently only partially rendering correct content)

Minimal code to get started:

```python
TOKEN='(your InfluxDB 2.0 token)'
ORG_ID='(your 16 characters org ID)'
LABEL='(label in InfluxDB 2.0 that has a dashboard associated with it)'

c = InfluxDBClient(url='https://eu-central-1-1.aws.cloud2.influxdata.com', token=TOKEN, org=ORG_ID)
d = InfluxDBDashboardView.find_by_label(c, LABEL)

# optionally set timeRangeStart, timeRangeStop and windowPeriod to show last 30 days, using 15 minute windows
d.set_time_range(start_offset=-(30*24*60), end_offset=0, window_period=15, offset_unit='m')

# render to an image - defaults to 1920x1080 pixels image, but this can be customized
o = InfluxDBDashboardOutput(dpi=150, rows=d.height)
img = o.draw(d)
img.save('./image1.png')

# render a black and white image, using white background instead of default black one ; image is suitable for eink displays
o = InfluxDBDashboardOutput(width=1200, height=825, rows=d.height, dpi=150, mode='bw', dark=False)
img = o.draw(d)
img.save('./image-eink.png')
```
