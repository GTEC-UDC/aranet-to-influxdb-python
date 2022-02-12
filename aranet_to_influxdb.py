import configparser
import datetime
import influxdb_client
import logging
import pandas
import re
from typing import Dict
import zoneinfo


# Default mapping of Aranet metric names to measurement
METRIC_MESUREMENT_DICT = {
    "temperature": "°C",
    "humidity": "%",
    "co2": "ppm",
    "atmosphericpressure": "hPa"}


# Mapping of default Aranet metric names to default names for InfluxDB data
INFLUXDB_METRICS_NAMES_DICT = {
    "temperature": "temperature",
    "humidity": "humidity",
    "co2": "CO2",
    "atmosphericpressure": "pressure"}


# Global logger object
logger = logging.getLogger(__name__)


def get_influxdb_point_settings(sensor_name: str, metric: str):
    # set default tags for this sensor and measurements
    entity_id = "aranet_" + sensor_name.replace('.', '') + "_" + \
                INFLUXDB_METRICS_NAMES_DICT[metric].lower()
    friendly_name = sensor_name + " " + INFLUXDB_METRICS_NAMES_DICT[metric]

    point_settings = influxdb_client.client.write_api.PointSettings()
    point_settings.add_default_tag("entity_id", entity_id)
    point_settings.add_default_tag("domain", "sensor")
    point_settings.add_default_tag("friendly_name", friendly_name)

    return point_settings


def aranet_to_influxdb(
        influxdb_client_object: influxdb_client.InfluxDBClient,
        inbluxdb_bucket: str,
        sensor_data: pandas.DataFrame,
        sensor_name: str,
        point_settings_fun=get_influxdb_point_settings,
        metric_measurement_dict: Dict[str, str] = METRIC_MESUREMENT_DICT,
        deduplicate_data: bool = True,
        influxdb_org: str = None,
        dry_run: bool = False):
    df = sensor_data

    # Determine timezone of datetime column from its name
    datetime_column_name = next(x for x in df.columns if x.startswith('datetime'))
    datetime_match = re.match(r"datetime[ ]*\((.*)\)", datetime_column_name)
    tz_match = None if datetime_match is None else datetime_match.group(1)

    if tz_match is None or tz_match == "UTC":
        timezone = datetime.timezone.utc
    elif tz_match.startswith("UTC"):
        tz_delta_match = re.match(r"UTC([+-])(\d{2})(\d{2})?", tz_match)

        timezone_sign = 1 if tz_delta_match.group(1) == '+' else -1
        timezone_hours = int(tz_delta_match.group(2))
        timezone_min = int(m) if (m := tz_delta_match.group(3)) is not None else 0

        timezone = datetime.timezone(datetime.timedelta(
            hours=timezone_sign*timezone_hours,
            minutes=timezone_sign*timezone_min))
    else:
        # try to use the tz_match string as a IANA time zone key
        timezone = zoneinfo.ZoneInfo(tz_match)

    # rename columns to remove any substring matching [ ]*\(.*\) at the end
    df.rename(columns={c: re.sub(r'[ ]*\(.*?\)', '', c) for c in df.columns},
              inplace=True)

    # convert type of datetime column from string to datetime
    df['datetime'] = pandas.to_datetime(
        df['datetime'], format="%Y.%m.%d %H:%M:%S").dt.tz_localize(timezone)

    # get one dataframe per metric and remove consecutive duplicates
    df_dict = {}
    for x in metric_measurement_dict.keys():
        if x not in df:
            continue

        # get a dataframe with only the datatime and the desired metric column
        df_col = df[['datetime', x]]

        if deduplicate_data:
            # remove consecutive duplicates
            df_col = df_col.loc[df_col[x] != df_col[x].shift()]

        # rename column of measurements to "value"
        df_col.rename(columns={x: 'value'}, inplace=True)

        # set datetime column as index
        df_col.set_index(keys='datetime', drop=True, inplace=True)
        df_col.rename_axis(None, inplace=True)

        # convert value column type to float64 if needed
        if df_col.value.dtypes != 'float64':
            df_col = df_col.astype('float64')

        # assign result
        df_dict[x] = df_col

    # InfluxDB client write options
    influxdb_write_options = influxdb_client.WriteOptions(
        batch_size=500,
        flush_interval=10000,
        jitter_interval=2000,
        retry_interval=5000,
        max_retries=5,
        max_retry_delay=30000,
        exponential_base=2)

    if dry_run:
        print("Dry run: no data will be written to InfluxDB")

    for (key, val) in df_dict.items():
        point_settings = get_influxdb_point_settings(sensor_name, key)
        measurement_name = metric_measurement_dict[key]

        if dry_run:
            print("-"*80)
            print("Sensor:", sensor_name)
            print('Metric:', key)
            print("Measurement name:", measurement_name)
            print('Default tags:', str(point_settings.defaultTags))
            print('Data ({} points):'.format(len(val)))
            print(val.to_string())
            continue

        # write data into InfluxDB
        with influxdb_client_object.write_api(
                write_options=influxdb_write_options,
                point_settings=point_settings) as wc:
            logger.info("Writing " + str(len(val)) + " data records " +
                        "of " + key + " data of sensor " + sensor_name)
            wc.write(inbluxdb_bucket, influxdb_org, record=df_dict[x],
                     data_frame_measurement_name=measurement_name)


def read_influxdb_conf(file):
    influxdb_conf = configparser.ConfigParser()
    with open(file) as f:
        influxdb_conf.read_file(f)
    return influxdb_conf


def create_influxdb_client(influxdb_conf):
    return influxdb_client.InfluxDBClient(
        url="https://" + influxdb_conf['DEFAULT']['host'] + ":" +
            str(influxdb_conf['DEFAULT']['port']),
        org=influxdb_conf['DEFAULT']['org'],
        token=influxdb_conf['DEFAULT']['token'])
