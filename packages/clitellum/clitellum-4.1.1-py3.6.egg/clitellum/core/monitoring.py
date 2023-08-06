from influxdb import InfluxDBClient
import datetime

class MonitoringConfig(object):
    def __init__(self):
        self.host = 'localhost'
        self.port = 8086
        self.dbname = 'clitellum_monitoring'
        self.user = None
        self.password = None

class MonitoringBuilder(object):
    def __init__(self):
        self._config = MonitoringConfig()

    def set_host(self, host):
        self._config.host = host

    def set_port(self, port):
        self._config.port = port

    def set_dbname(self, dbname):
        self._config.dbname = dbname

    def set_user(self, user):
        self._config.user = user

    def set_password(self, password):
        self._config.password = password

    def build(self):
        return Monitoring.create(self._config)


class Monitoring(object):
    def __init__(self, influx_client, config: MonitoringConfig):
        self.influx_client = influx_client
        self.config = config

    @classmethod
    def create(cls, config: MonitoringConfig):
        influx_client = InfluxDBClient(config.host, config.port, config.user, config.password, config.dbname)
        influx_client.create_database(config.dbname)
        return Monitoring(influx_client, config)

    def message_recieved(self, identification, message_key, size):
        data_points = [{
            "measurement": "messages",
            "tags": {
                "micro": identification.id,
                "micro_type": identification.type,
                "message_key": message_key
            },
            "time": datetime.datetime.utcnow(),
            "fields": {
                "size": size
            }
        }]

        try:
            self.influx_client.write_points(data_points)
        except:
            pass

    def send_heartbeat(self, identification):
        data_points = [{
            "measurement": "status",
            "tags": {
                "micro": identification.id,
                "micro_type": identification.type
            },
            "time": datetime.datetime.utcnow(),
            "fields": {
                "beat": 1
            }
        }]
        
        try:
            self.influx_client.write_points(data_points)
        except:
            pass
