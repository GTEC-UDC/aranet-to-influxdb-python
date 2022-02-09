# aranet-to-influxdb-python

This repository contains the module `aranet_to_influxdb.py` and the example script `aranet_to_influxdb_main.py`, which allows transferring data of the [Aranet4 CO2 sensors](https://aranet.com) from the [Aranet Cloud](https://aranet.cloud/) to an InfluxDB database.


## Usage

First, import the module

```python
import aranet_to_influxdb
```

For uploading data to InfluxDB, a configuration file with the required information is needed, for this copy the file `influxdb.conf.template` to a new file `influxdb.conf` and fill in the appropriated data. Then load the file with

```python
influxdb_conf = aranet_to_influxdb.read_influxdb_conf("influxdb.conf")
```

For uploading the data to influxdb, this module uses the official InfluxDB python client, [influxdb-client-python](https://github.com/influxdata/influxdb-client-python). The first thing needed is to create an `InfluxDBClient` object, for this call the `create_influxdb_client` function with the previously loaded configuration:

```python
influxdb_client = aranet_to_influxdb.create_influxdb_client(influxdb_conf)
```

Then, data can be uploaded to InfluxDB with the function `aranet_to_influxdb`:

```python
aranet_to_influxdb(
    influxdb_client, inbluxdb_bucket: str,
    sensor_data: pandas.DataFrame, sensor_name: str,
    point_settings_fun=get_influxdb_point_settings,
    deduplicate_data: bool = True,
    influxdb_org: str = None, dry_run: bool = False):
```

where
- `influxdb_client` is the `InfluxDBClient` object

- `inbluxdb_bucket` is the name of the InfluxDb bucket

- `sensor_data` is a Pandas DataFrame with the sensor data, with a `datetime` column with the datetime corresponding to each row, and the rest of columns containing the measurement data. The measurement columns names must be the ones used when exporting data from the Aranet Cloud:
  - `temperature`
  - `humidity`
  - `co2`
  - `atmosphericpressure`
  
  These names may also have any substring matching the regular expression `[ ]*\(.*\)` at the end, e.g., `temperature (°C)`.

- `sensor_name` is the name of the sensor.

- `point_settings_fun` is a function with parameters `sensor_name` and `metric` that will be called for each data `metric` in `sensor_data` (i.e., `temperature`, `humidity`, `co2`, and `atmosphericpressure`) and it should return an [`influxdb.client.write_api.PointSettings`](https://influxdb-client.readthedocs.io/en/latest/usage.html?#default-tags) object with the default point settings for the corresponding `metric`, i.e., the default tags which will be added to each point written.

- `deduplicate_data`, if true indicates that for several consecutive equal values only the first should be uploaded, discarding the others.

- `influxdb_org` is the InfluxDB organization. By default the organization of the `influxdb_client` is used.

- `dry_run`, if true no data will be written to InfluxDB and instead the data to be written will be printed on the screen.


## Example

The included script `aranet_to_influxdb_main.py` uses the module [aranet-cloud](https://github.com/tombolano/aranet-cloud-python) to query the Aranet Cloud for one sensor data in a time range interval, and then uploads the data to InfluxDB.

**Note:** By default the parameter `dry_run` is set to `True`, so no data will be written and instead it will be printed on the screen. Set this parameter to `False` to actually write the data to InfluxDB.

An example output of the script (using the default `dry_run = True`) is the following:

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
Data (9 points):
                     value
2022-02-01 12:00:01   21.0
2022-02-01 12:01:03   21.1
2022-02-01 12:05:03   21.0
2022-02-01 12:06:02   21.1
2022-02-01 12:09:06   21.0
2022-02-01 12:35:04   20.9
2022-02-01 12:45:05   21.0
2022-02-01 12:49:10   21.1
2022-02-01 12:53:10   21.2
--------------------------------------------------------------------------------
Sensor: 1.01
Metric: humidity
Measurement name: %
Default tags: {'entity_id': 'aranet_101_humidity', 'domain': 'sensor', 'friendly_name': '1.01 humidity'}
Data (2 points):
                     value
2022-02-01 12:00:01   41.0
2022-02-01 12:51:09   40.0
--------------------------------------------------------------------------------
Sensor: 1.01
Metric: co2
Measurement name: ppm
Default tags: {'entity_id': 'aranet_101_co2', 'domain': 'sensor', 'friendly_name': '1.01 CO2'}
Data (58 points):
                     value
2022-02-01 12:00:01  743.0
2022-02-01 12:01:03  769.0
2022-02-01 12:02:01  775.0
2022-02-01 12:03:01  772.0
2022-02-01 12:04:03  770.0
2022-02-01 12:05:03  769.0
2022-02-01 12:06:02  760.0
2022-02-01 12:07:05  765.0
2022-02-01 12:08:06  742.0
2022-02-01 12:09:06  741.0
2022-02-01 12:10:07  736.0
2022-02-01 12:11:07  726.0
2022-02-01 12:12:05  710.0
2022-02-01 12:13:05  707.0
2022-02-01 12:14:06  712.0
2022-02-01 12:15:06  697.0
2022-02-01 12:16:05  688.0
2022-02-01 12:17:05  681.0
2022-02-01 12:18:05  675.0
2022-02-01 12:19:06  668.0
2022-02-01 12:20:06  673.0
2022-02-01 12:21:05  648.0
2022-02-01 12:22:07  649.0
2022-02-01 12:23:05  650.0
2022-02-01 12:24:06  640.0
2022-02-01 12:25:05  651.0
2022-02-01 12:26:07  639.0
2022-02-01 12:27:07  653.0
2022-02-01 12:28:07  635.0
2022-02-01 12:29:07  631.0
2022-02-01 12:30:05  643.0
2022-02-01 12:32:07  637.0
2022-02-01 12:33:06  654.0
2022-02-01 12:34:06  614.0
2022-02-01 12:35:04  620.0
2022-02-01 12:36:06  624.0
2022-02-01 12:37:04  612.0
2022-02-01 12:38:06  632.0
2022-02-01 12:39:06  618.0
2022-02-01 12:41:06  625.0
2022-02-01 12:42:05  610.0
2022-02-01 12:43:04  604.0
2022-02-01 12:44:04  602.0
2022-02-01 12:45:05  607.0
2022-02-01 12:46:05  597.0
2022-02-01 12:47:04  603.0
2022-02-01 12:48:06  591.0
2022-02-01 12:49:10  601.0
2022-02-01 12:50:09  592.0
2022-02-01 12:51:09  588.0
2022-02-01 12:52:08  607.0
2022-02-01 12:53:10  608.0
2022-02-01 12:54:10  604.0
2022-02-01 12:55:10  602.0
2022-02-01 12:56:10  603.0
2022-02-01 12:57:09  606.0
2022-02-01 12:58:09  598.0
2022-02-01 12:59:09  599.0
--------------------------------------------------------------------------------
Sensor: 1.01
Metric: atmosphericpressure
Measurement name: hPa
Default tags: {'entity_id': 'aranet_101_pressure', 'domain': 'sensor', 'friendly_name': '1.01 pressure'}
Data (2 points):
                      value
2022-02-01 12:00:01  1033.0
2022-02-01 12:12:05  1032.0
```


## License

This code is available as open source under the terms of the [MIT License](https://opensource.org/licenses/MIT).
