Minimal code to get started

```python
c = InfluxDBClient(url='https://eu-central-1-1.aws.cloud2.influxdata.com', token=TOKEN, org=ORG)
d = InfluxDBDashboardView.find_by_label(c, ORG_ID, LABEL)
cells = list(d.cells())
height = max(map(lambda cell: cell.yh, cells)) if len(list(cells)) > 0 else 1
o = InfluxDBDashboardOutput(dpi=150, rows=height)
img = o.draw(d)
img.save('./image1.png')
```
