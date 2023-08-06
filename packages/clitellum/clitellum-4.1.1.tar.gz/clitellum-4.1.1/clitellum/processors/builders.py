
from clitellum.processors.agents import AgentProcessor
from clitellum.endpoints import gateways
from clitellum.endpoints.gateways import SenderGateway, ReceiverGateway
from clitellum.core.monitoring import MonitoringBuilder

def create_agent_from_config(identification, cfg):
    '''
    Crea un agente desde la configuracion
    Ej:
    {
      input_gateway : ...
      output_gateway : ...
    }
    '''

    builder = AgentProcessorBuilder.create()
    builder.set_identification(identification)
    builder.set_receiver(gateways.CreateReceiverFromConfig(cfg["receiver_gateway"]))
    builder.set_sender(gateways.CreateSenderFromConfig(cfg["sender_gateway"]))

    if not cfg.get("error_gateway") is None:
        builder.set_error_gateway(gateways.CreateSenderFromConfig(cfg["error_gateway"]))

    if 'reply' in cfg:
        if 'sender_gateway' in cfg['reply']:
            builder.set_reply_sender(gateways.CreateSenderFromConfig(cfg['reply']["sender_gateway"]))

        if 'receiver_gateway' in cfg['reply']:
            builder.set_reply_receiver(gateways.CreateReceiverFromConfig(cfg['reply']["receiver_gateway"]))     

        if 'routing_key' in cfg['reply']:
            builder.set_reply_routing_key(cfg['reply']['routing_key'])         

    if 'monitoring' in cfg:
        monitoring_builder = MonitoringBuilder()
        if 'host' in cfg['monitoring']:
            monitoring_builder.set_host(cfg['monitoring']['host'])

        if 'port' in cfg['monitoring']:
            monitoring_builder.set_port(cfg['monitoring']['port'])

        if 'user' in cfg['monitoring']:
            monitoring_builder.set_user(cfg['monitoring']['user'])

        if 'password' in cfg['monitoring']:
            monitoring_builder.set_password(cfg['monitoring']['password'])

        if 'dbname' in cfg['monitoring']:
            monitoring_builder.set_dbname(cfg['monitoring']['dbname'])

        builder.set_monitoring(monitoring_builder.build())

    return builder.build()

class AgentProcessorBuilder(object):

    @classmethod
    def create(cls):
        return AgentProcessorBuilder()

    def __init__(self):
        self._identification = None
        self._receiver_gateway = None
        self._sender_gateway = None
        self._error_gateway = None
        self._reply_sender_gateway = None
        self._reply_receiver_gateway = None
        self._reply_routing_key = None
        self._monitoring = None

    def set_identification(self, identification):
        self._identification = identification
        return self

    def set_receiver(self, receiver_gateway):
        self._receiver_gateway = receiver_gateway
        return self

    def set_sender(self, sender_gateway):
        self._sender_gateway = sender_gateway
        return self

    def set_error_gateway(self, error_gateway):
        self._error_gateway = error_gateway
        return self

    def set_reply_sender(self, sender_gateway):
        self._reply_sender_gateway = sender_gateway
        return self

    def set_reply_receiver(self, receiver_gateway):
        self._reply_receiver_gateway = receiver_gateway
        return self

    def set_reply_routing_key(self, routing_key):
        self._reply_routing_key = routing_key
        return self

    def set_monitoring(self, monitoring):
        self._monitoring = monitoring
        return self

    def build(self):
        if self._reply_routing_key is not None:
            self._identification.set_reply_key(self._reply_routing_key)

        ag = AgentProcessor(self._identification, self._receiver_gateway, \
                            self._sender_gateway, self._error_gateway)
        
        if self._reply_sender_gateway is not None:
            ag.set_reply_sender(self._reply_sender_gateway)

        if self._reply_receiver_gateway is not None:
            ag.set_reply_receiver(self._reply_receiver_gateway)

        if self._monitoring is not None:
            ag.set_monitoring(self._monitoring)

        return ag
