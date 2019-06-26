import threading

import counter_lib
import services


class _Telemetry(object):
  def __init__(self, namespace, grpc_server):
    self._namespace = namespace
    self._counters = {}
    self._lock = threading.Lock()

    services.TelemetryServicer(grpc_server, self)

  @property
  def namespace(self):
    return self._namespace

  @property
  def counters(self):
    return self._counters.values()

  def add_counter(self, name, count=1):
    if name not in self._counters:
      with self._lock:
        if name not in self._counters:
          self._counters[name] = counter_lib.Counter(name)

    counter = self._counters[name]
    counter.add(count)


_telemetry = None


def init(namespace, grpc_server):
  global _telemetry
  _telemetry = _Telemetry(namespace, grpc_server)


def add_counter(name, count=1):
  _telemetry.add_counter(name, count)