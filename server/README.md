# InfluxDB 2.0 Dashboard Renderer - Web Server

## Running using pre-built docker image

The docker image is available on DockerHub as [`wojciechka/influxdb-dashboard-renderer`](https://hub.docker.com/repository/docker/wojciechka/influxdb-dashboard-renderer).

```bash
$ docker run -p 5000:5000 wojciechka/influxdb-dashboard-renderer
```

The above will run a pre-built container for running the dashboard renderer web server and expose it on local port 5000.

## Running locally with Python

To get started with the server, go to root folder of the `influxdb-dashboard-renderer`.

Installation of all dependencies are needed and has to be done once before starting development.

This can be done using PIP - such as:

```bash
$ pip install -r requirements.txt`
```
For some Linux distributions, explicitly specifying Python 3 may be needed - such as:

```bash
$ pip3 install -r requirements.txt`
```

Next, to run the server, you can simply run:

```bash
$ PYTHONPATH=. ./server/server.py
```

For some Linux distributions, explicitly specifying Python 3 may be needed - such as:

```bash
$ PYTHONPATH=. python3 ./server/server.py
```

The `PYTHONPATH` environment variable is requied so that Python can access the `influxdb_dashboard` package in the current directory.

## Building and running using Docker

The InfluxDB Dashboard Renderer Web Server

```bash
$ docker build -t local-influxdb-dashboard-renderer .
$ docker run -p 5000:5000 local-influxdb-dashboard-renderer
```

# Rendering images

You can invoke the `/render` endpoint to retrieve a ready to use image in PNG format. Such as:

```bash
curl --header "Content-Type: application/json" -X POST \
--data '{
  "url": "(url)",
  "token": "(access token)",
  "org_id": "(organization id)",
  "id": "(dashboard id)",
  "width": 1280,
  "height": 720,
  "dpi": 75
}' http://127.0.0.1:5000/render >image.png
```

Where `(url)` is the URL to the InfluxDB - such as `https://us-west-2-1.aws.cloud2.influxdata.com` for [InfluxDB Cloud](https://www.influxdata.com/products/influxdb-cloud/) US West-2 region.

The `(access token)` should be an all-access token for your organization inside InfluxDB instance, as those are needed to retrieve information about dashboards.

The `(organization id)` and `(dashboard id)` as 16-letter hexadecimal identifiers of the organization and dashboard inside InfluxDB. The identifiers can be extracted from the dashboard view URL, where the URL is `https://hostname/orgs/(organization id)/dashboards/(dashboard id)`.

The server accepts passing or pre-setting some of the configuration as environment variables. For example, setting `INFLUXDB_URL`, `INFLUXDB_TOKEN` and `INFLUXDB_ORG_ID` environment variables allows running an instance of dashboard renderer web server that defaults to a specific InfluxDB instance and organization, so then the query can only include dashboard identifier and optional output options.

The server accepts POST and GET requests. For a POST request, the `Content-Type` header has to be set to `application/json` and then the query body should include a JSON object with all of the parameters.

For GET requests, the parameters should be passed as query string - such as `http://127.0.0.1:5000/render?id=1234123400000000`. If `INFLUXDB_URL`, `INFLUXDB_TOKEN` and `INFLUXDB_ORG_ID` environment variables were set, this would render a dashbord for preconfigured InfluxDB instance and organization.

## Available options

The following parameters can be passed as query string, inside the JSON object as well as overwritten by environment variables:

| Input parameter | Environment variable       | Default   | Description                                                                      |
| --------------- | -------------------------- | --------- | -------------------------------------------------------------------------------- |
| `url`           | `INFLUXDB_URL`             | *(unset)* | URL to InfluxDB instance to connect to                                           |
| `org_id`        | `INFLUXDB_ORG_ID`          | *(unset)* | InfluxDB organization ID to use for retrieving                                   |
| `token`         | `INFLUXDB_TOKEN`           | *(unset)* | InfluxDB token to use for dashboard and query APIs                               |
| `id`            | `INFLUXDB_DASHBOARD_ID`    | *(unset)* | If specified, use dashboard with this id (overrides `label`)                     |
| `label`         | `INFLUXDB_DASHBOARD_LABEL` | *(unset)* | If specified, use dashboard with specified label                                 |
| `bright`        | *(N/A)*                    | *(unset)* | If specified, render on white background ; defaults to black                     |
| `start_offset`  | *(N/A)*                    | -10080    | Offset, in `offset_unit`, for start of query period (maps to `v.timeRangeStart`) |
| `end_offset`    | *(N/A)*                    | 0         | Offset, in `offset_unit`, for end of query period (maps to `v.timeRangeStop`)    |
| `window_period` | *(N/A)*                    | 15        | Offset, in `offset_unit`, for window period (maps to `v.windowPeriod`)           |
| `offset_unit`   | *(N/A)*                    | m         | Unit to use for offsets ; should be one of `s`, `m` or `h`                       |
| `width`         | *(N/A)*                    | 1920      | Width of the output image                                                        |
| `height`        | *(N/A)*                    | 1080      | Height of the output image                                                       |
| `mode`          | `INFLUXDB_DASHBOARD_MODE`  | color     | Mode of the output image ; see [../](main README) for details on supported modes |
| `dpi`           | `INFLUXDB_DASHBOARD_DPI`   | 150       | DPI to use in image output                                                       |
