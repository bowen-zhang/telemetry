import datetime
import flask

from google.protobuf import json_format

from protos import telemetry_pb2
from third_party.mongo_utils import storage


class App(object):
  def __init__(self):
    self._metadata_storage = storage.ProtobufMongoStorage(
        database='Telemetry',
        collection='Metadata',
        auto_id_field='id',
        proto_cls=telemetry_pb2.Metadata)
    self._counter_storage = storage.ProtobufMongoStorage(
        database='Telemetry',
        collection='Counters',
        proto_cls=telemetry_pb2.Counter)

    self._web = flask.Flask(__name__, static_folder='static')
    self._web.debug = True
    self._web.add_url_rule('/', view_func=self.index)
    self._web.add_url_rule(
        '/counter/<string:namespace>/<string:name>',
        view_func=self.get_counter)

  def run(self):
    self._web.run(host='0.0.0.0', port=8080, debug=True)

  def index(self):
    return flask.render_template('index.html')

  def get_counter(self, namespace, name):
    metadata = self._metadata_storage.find_one({
        'namespace': namespace,
        'name': name
    })
    if not metadata:
      return flask.abort(400)

    print {
        'id': metadata.id,
        'timestamp': {
            '$gt': datetime.datetime.utcnow() - datetime.timedelta(days=3)
        }
    }
    values = self._counter_storage.find({
        'id': metadata.id,
        'timestamp': {
            '$gt': datetime.datetime.utcnow() - datetime.timedelta(days=3)
        }
    })

    metric_collection = telemetry_pb2.MetricCollection(counters=values)
    data = json_format.MessageToJson(metric_collection)
    return flask.Response(data, status=200, mimetype='application/json')


if __name__ == '__main__':
  App().run()