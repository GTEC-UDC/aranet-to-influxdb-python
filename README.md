# aranet-to-influxdb-python

This repository contains the module `aranet_to_influxdb.py` and the example script `aranet_to_influxdb_main.py`, which allows transferring data of the [Aranet4 CO₂ sensors](https://aranet.com) from the [Aranet Cloud](https://aranet.cloud/) to an InfluxDB database.


## Usage

First, import the module

```python
import aranet_to_influxdb
```

For uploading data to InfluxDB, a configuration file with the required information is needed, for this copy the file `influxdb.conf.template` to a new file `influxdb.conf` and fill in the appropriated data. Then load the file with

```python
influxdb_conf = aranet_to_influxdb.read_influxdb_conf("influxdb.conf")
```

Then, we have to create an `InfluxDBClient` object (using the official InfluxDB python client, [influxdb-client-python](https://github.com/influxdata/influxdb-client-python)), for this we include the `create_influxdb_client` function, which it can be called with the previously loaded configuration:

```python
influxdb_client = aranet_to_influxdb.create_influxdb_client(influxdb_conf)
```

Then, data can be uploaded to InfluxDB with the function `aranet_to_influxdb`:

```python
aranet_to_influxdb(
    influxdb_client_object: influxdb_client.InfluxDBClient,
    inbluxdb_bucket: str,
    sensor_data: pandas.DataFrame,
    sensor_name: str,
    point_settings_fun=get_influxdb_point_settings,
    metric_measurement_dict: Dict[str, str] = METRIC_MESUREMENT_DICT,
    deduplicate_data: bool = True,
    influxdb_org: str = None,
    dry_run: bool = False):
```

where
- `influxdb_client` is the `InfluxDBClient` object.

- `inbluxdb_bucket` is the name of the InfluxDB bucket.

- `sensor_data` is a Pandas DataFrame with the Aranet4 sensor data. The expected data format in the `sensor_data` parameter is the format used by the Aranet Cloud when exporting data in CSV format, this format is shown in this example output from the Aranet Cloud:
  ```
            datetime(UTC)  temperature(C)  humidity(%)  co2(ppm)  atmosphericpressure(hPa)
  0   2022.02.01 12:00:01            21.0         41.0       743                      1033
  1   2022.02.01 12:01:03            21.1         41.0       769                      1033
  2   2022.02.01 12:02:01            21.1         41.0       775                      1033
  3   2022.02.01 12:03:01            21.1         41.0       772                      1033
  4   2022.02.01 12:04:03            21.1         41.0       770                      1033
  5   2022.02.01 12:05:03            21.0         41.0       769                      1033
  6   2022.02.01 12:06:02            21.1         41.0       760                      1033
  7   2022.02.01 12:07:05            21.1         41.0       765                      1033
  8   2022.02.01 12:08:06            21.1         41.0       742                      1033
  9   2022.02.01 12:09:06            21.0         41.0       741                      1033
  10  2022.02.01 12:10:07            21.0         41.0       736                      1033
  11  2022.02.01 12:11:07            21.0         41.0       726                      1033
  12  2022.02.01 12:12:05            21.0         41.0       710                      1032
  13  2022.02.01 12:13:05            21.0         41.0       707                      1032
  14  2022.02.01 12:14:06            21.0         41.0       712                      1032
  15  2022.02.01 12:15:06            21.0         41.0       697                      1032
  16  2022.02.01 12:16:05            21.0         41.0       688                      1032
  17  2022.02.01 12:17:05            21.0         41.0       681                      1032
  18  2022.02.01 12:18:05            21.0         41.0       675                      1032
  19  2022.02.01 12:19:06            21.0         41.0       668                      1032
  ```

  Thus, `sensor_data` must have a `datetime` field, and one or more metric fields (`temperature`, `humidity`, `co2`, and/or `atmosphericpressure`). The column names shall be (brackets indicate optional parts):
  - datetime [(*timezone*)]: The datetime for each measurement. The *timezone* string, if exists, will indicate the timezone, and it will be automatically taken into acount by the function.
  - temperature [(*temperature unit*)]: The temperature for the corresponding datetime.
  - humidity [(*humidity unit*)]: The humidity for the corresponding datetime.
  - co2 [(*CO₂ unit*)]: The CO₂ for the corresponding datetime.
  - atmosphericpressure [(*pressure unit*)]: The atmospheric pressure for the corresponding datetime.

- `sensor_name` is the name of the sensor.

- `point_settings_fun` is a function with parameters `sensor_name` and `metric` that will be called for each data `metric` in `sensor_data` (i.e., `temperature`, `humidity`, `co2`, and `atmosphericpressure`) and it shall return an [`influxdb.client.write_api.PointSettings`](https://influxdb-client.readthedocs.io/en/latest/usage.html?#default-tags) object with the default tags for the corresponding `metric`.

- `metric_measurement_dict` is a dictionary containing for each `metric` the measurement name to use for uploading the data to InfluxDB. By default the variable `METRIC_MESUREMENT_DICT` is used, defined as
  ```python
  METRIC_MESUREMENT_DICT = {
    "temperature": "°C",
    "humidity": "%",
    "co2": "ppm",
    "atmosphericpressure": "hPa"}
  ```

- `deduplicate_data`, if true indicates that for several consecutive equal values only the first should be uploaded, discarding the others.

- `influxdb_org` is the InfluxDB organization. By default, the organization of the `influxdb_client` is used.

- `dry_run`, if true no data will be written to InfluxDB, instead the data to be written will be printed on the screen.


## Example

The included script `aranet_to_influxdb_main.py` uses the module [aranet-cloud](https://github.com/tombolano/aranet-cloud-python) to query the Aranet Cloud for one sensor data in a time range interval, and then uploads the data to InfluxDB.

**Note:** The parameter `dry_run` is set to `True`, so no data will be written and instead it will be printed on the screen. Set this parameter to `False` to actually write the data to InfluxDB.

Considering the same example data shown in the Usage section for the `sensor_data` parameter, the output of the script (using `deduplicate_data = True` and `dry_run = True`) is the following:

```
INFO:aranet_cloud:Login cache expired
INFO:aranet_cloud:Making login request to Aranet cloud
INFO:aranet_cloud:Saved login data to cache file
INFO:aranet_cloud:Making request for sensor 4196648 data to Aranet cloud
INFO:aranet_cloud:Downloaded 60 data records for sensor 4196648 from Aranet cloud
Dry run: no data will be written to InfluxDB
--------------------------------------------------------------------------------
Sensor: 1.01
Metric: temperature
Measurement name: °C
Default tags: {'entity_id': 'aranet_101_temperature', 'domain': 'sensor', 'friendly_name': '1.01 temperature'}
Data (5 points):
                           value
2022-02-01 12:00:01+00:00   21.0
2022-02-01 12:01:03+00:00   21.1
2022-02-01 12:05:03+00:00   21.0
2022-02-01 12:06:02+00:00   21.1
2022-02-01 12:09:06+00:00   21.0
--------------------------------------------------------------------------------
Sensor: 1.01
Metric: humidity
Measurement name: %
Default tags: {'entity_id': 'aranet_101_humidity', 'domain': 'sensor', 'friendly_name': '1.01 humidity'}
Data (1 points):
                           value
2022-02-01 12:00:01+00:00   41.0
--------------------------------------------------------------------------------
Sensor: 1.01
Metric: co2
Measurement name: ppm
Default tags: {'entity_id': 'aranet_101_co2', 'domain': 'sensor', 'friendly_name': '1.01 CO2'}
Data (20 points):
                           value
2022-02-01 12:00:01+00:00  743.0
2022-02-01 12:01:03+00:00  769.0
2022-02-01 12:02:01+00:00  775.0
2022-02-01 12:03:01+00:00  772.0
2022-02-01 12:04:03+00:00  770.0
2022-02-01 12:05:03+00:00  769.0
2022-02-01 12:06:02+00:00  760.0
2022-02-01 12:07:05+00:00  765.0
2022-02-01 12:08:06+00:00  742.0
2022-02-01 12:09:06+00:00  741.0
2022-02-01 12:10:07+00:00  736.0
2022-02-01 12:11:07+00:00  726.0
2022-02-01 12:12:05+00:00  710.0
2022-02-01 12:13:05+00:00  707.0
2022-02-01 12:14:06+00:00  712.0
2022-02-01 12:15:06+00:00  697.0
2022-02-01 12:16:05+00:00  688.0
2022-02-01 12:17:05+00:00  681.0
2022-02-01 12:18:05+00:00  675.0
2022-02-01 12:19:06+00:00  668.0
--------------------------------------------------------------------------------
Sensor: 1.01
Metric: atmosphericpressure
Measurement name: hPa
Default tags: {'entity_id': 'aranet_101_pressure', 'domain': 'sensor', 'friendly_name': '1.01 pressure'}
Data (2 points):
                            value
2022-02-01 12:00:01+00:00  1033.0
2022-02-01 12:12:05+00:00  1032.0
```


## License

This code is available as open source under the terms of the [MIT License](https://opensource.org/licenses/MIT).
