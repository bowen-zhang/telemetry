import datetime
import grpc
import threading
import time

from absl import app
from absl import flags
from absl import logging
from google.protobuf import empty_pb2

from protos import telemetry_pb2
from protos import telemetry_pb2_grpc
from third_party.mongo_utils import storage

FLAGS = flags.FLAGS

flags.DEFINE_list('sources', None, 'List of gRPC addresses to monitor.')


class Server(object):
  def __init__(self, collect_interval=datetime.timedelta(seconds=60)):
    self._threads = []
    self._abort = threading.Event()
    self._collect_interval_sec = collect_interval.total_seconds()

    self._metadata_storage = storage.ProtobufMongoStorage(
        database='Telemetry',
        collection='Metadata',
        auto_id_field='id',
        proto_cls=telemetry_pb2.Metadata)
    self._counter_storage = storage.ProtobufMongoStorage(
        database='Telemetry',
        collection='Counters',
        proto_cls=telemetry_pb2.Counter)
    self._lookup_map = {}
    self._lock = threading.Lock()

  def start(self):
    for source in FLAGS.sources:
      thread = threading.Thread(
          target=self._monitor, kwargs={'source': source})
      self._threads.append(thread)
      thread.start()

  def stop(self):
    self._abort.set()
    for thread in self._threads:
      thread.join()

  def _monitor(self, source):
    channel = grpc.insecure_channel(source)
    stub = telemetry_pb2_grpc.TelemetryStub(channel)

    while not self._abort.is_set():
      try:
        logging.info('[%s] Getting metrics...', source)
        coll = stub.GetMetrics(empty_pb2.Empty())
      except grpc.RpcError:
        self._sleep(5)
        continue

      logging.info('[%s] Saving metrics...', source)
      for counter in coll.counters:
        self._save_counter(coll.namespace, counter)

      self._sleep(self._collect_interval_sec)

  def _sleep(self, seconds):
    self._abort.wait(seconds)

  def _save_counter(self, namespace, counter):
    key = (namespace, counter.name)
    if key not in self._lookup_map:
      metadata = self._metadata_storage.find_or_create(
          filter={
              'namespace': namespace,
              'name': counter.name
          },
          proto=telemetry_pb2.Metadata(namespace=namespace, name=counter.name))
      self._lookup_map[key] = metadata.id

    counter.id = self._lookup_map[key]
    counter.ClearField('name')
    self._counter_storage.save(counter)


def main(argv):
  server = Server()
  server.start()
  try:
    while True:
      time.sleep(1)
  finally:
    server.stop()


if __name__ == '__main__':
  app.run(main)