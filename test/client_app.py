import grpc
import random
import time

from absl import app
from absl import flags
from concurrent import futures

from client import telemetry_lib

FLAGS = flags.FLAGS

flags.DEFINE_integer('grpc_port', 50090, 'Port for gRPC services.')


def main(argv):
  server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
  telemetry_lib.init('__test__', server)
  server.add_insecure_port('[::]:{0}'.format(FLAGS.grpc_port))
  server.start()

  print 'Running...'
  try:
    while True:
      telemetry_lib.add_counter('counter1', random.randint(1, 10))
      time.sleep(1)
  except:
    server.stop(0)
    raise


if __name__ == '__main__':
  app.run(main)