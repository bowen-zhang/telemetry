import datetime

from protos import telemetry_pb2
from protos import telemetry_pb2_grpc


class TelemetryServicer(telemetry_pb2_grpc.TelemetryServicer):
  def __init__(self, grpc_server, telemetry):
    self._telemetry = telemetry
    telemetry_pb2_grpc.add_TelemetryServicer_to_server(self, grpc_server)

  def GetMetrics(self, request, context):
    now = datetime.datetime.utcnow()
    coll = telemetry_pb2.MetricCollection(namespace=self._telemetry.namespace)
    for counter in self._telemetry.counters:
      counter_proto = coll.counters.add(
          name=counter.name, last_min_count=counter.last_minute_count)
      counter_proto.timestamp.FromDatetime(now)
    return coll