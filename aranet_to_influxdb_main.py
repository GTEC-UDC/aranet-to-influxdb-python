import aranet_to_influxdb
import logging
import pathlib
import sys

script_path = pathlib.Path(__file__).parent.absolute()

# Set the path to the aranet_cloud module
aranet_cloud_path = script_path / ".." / "aranet_cloud"
aranet_cloud_path = aranet_cloud_path.resolve()
sys.path.append(str(aranet_cloud_path))

import aranet_cloud


def main():
    # configure logging
    logging.basicConfig(level=logging.INFO)

    # load configurations
    aranet_conf_path = aranet_cloud_path / "aranet_cloud.conf"
    aranet_conf = aranet_cloud.read_aranet_conf(aranet_conf_path)

    influxdb_conf_path = script_path / "influxdb.conf"
    influxdb_conf = aranet_to_influxdb.read_influxdb_conf(influxdb_conf_path)

    # Get influxdb_client object
    influxdb_client = aranet_to_influxdb.create_influxdb_client(influxdb_conf)

    # Sensor information
    sensor_id = "4196648"
    sensor_name = "1.01"

    # Settings for querying the sensor data from the Aranet Cloud
    from_time = "2022-02-01T12:00:00Z"
    to_time = "2022-02-01T12:20:00Z"
    timezone = "0000"
    metrics = list(aranet_cloud.METRICS_DICT.keys())

    # Query sensor data from the Aranet Cloud
    aranet_cache_file = script_path / "aranet_login.json"
    sensor_data = aranet_cloud.get_sensor_data(
        aranet_conf, sensor_id, from_time, to_time, timezone,
        metrics=metrics, login_cache_file=aranet_cache_file)

    # Settings for saving the sensor data into InfluxDB
    inbluxdb_bucket = influxdb_conf['DEFAULT']['bucket']
    deduplicate_data = True
    dry_run = True  # <<< Set this to False to save the data into InfluxDB

    # Save data into InfluxDB
    aranet_to_influxdb.aranet_to_influxdb(
        influxdb_client, inbluxdb_bucket,
        sensor_data, sensor_name,
        deduplicate_data=deduplicate_data,
        dry_run=dry_run)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(str(e))
        sys.exit(1)
