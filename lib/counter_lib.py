import collections
import datetime
import threading
import time


class _SingleThreadCounter(object):
  def __init__(self, duration, resolution=0.1, time_func=time.time):
    self._time_func = time_func
    self._size = int(1 / resolution)
    self._buckets = [0] * self._size
    self._index = 0
    self._time_sec = self._time_func()
    self._duration_sec = duration.total_seconds()
    self._interval_sec = self._duration_sec * resolution

  def add(self, count=1):
    self._refresh()
    self._buckets[self._index] += count

  def get(self):
    self._refresh()
    return sum(self._buckets)

  def _refresh(self):
    now_sec = self._time_func()
    elapsed_sec = now_sec - self._time_sec
    if elapsed_sec >= self._duration_sec:
      for i in range(self._size):
        self._buckets[i] = 0
      self._index = 0
      self._time_sec = now_sec
    else:
      while elapsed_sec >= self._interval_sec:
        self._index = (self._index + 1) % self._size
        self._time_sec += self._interval_sec
        self._buckets[self._index] = 0
        elapsed_sec -= self._interval_sec


_LocalData = collections.namedtuple('_LocalData', ['lock', 'counter'])


class _MultiThreadCounter(object):
  def __init__(self,
               duration,
               resolution=0.1,
               time_func=time.time,
               thread_id_func=None):
    self._threads = {}
    self._duration = duration
    self._resolution = resolution
    self._time_func = time_func
    self._thread_id_func = thread_id_func or self._get_current_thread_id

  def add(self, count=1):
    data = self._get_local_data()
    with data.lock:
      data.counter.add(count)

  def get(self):
    total = 0
    for data in self._threads.values():
      with data.lock:
        total += data.counter.get()
    return total

  def _get_local_data(self):
    thread_id = self._thread_id_func()
    if thread_id not in self._threads:
      self._threads[thread_id] = _LocalData(
          lock=threading.Lock(),
          counter=_SingleThreadCounter(
              duration=self._duration,
              resolution=self._resolution,
              time_func=self._time_func))

    return self._threads[thread_id]

  def _get_current_thread_id(self):
    return threading.current_thread().ident


class Counter(object):
  def __init__(self, name):
    self._name = name
    self._last_min_counter = _MultiThreadCounter(datetime.timedelta(minutes=1))
    self._last_hour_counter = _MultiThreadCounter(datetime.timedelta(hours=1))
    self._last_day_counter = _MultiThreadCounter(datetime.timedelta(days=1))

  @property
  def name(self):
    return self._name

  @property
  def last_minute_count(self):
    return self._last_min_counter.get()

  @property
  def last_hour_count(self):
    return self._last_hour_counter.get()

  @property
  def last_day_count(self):
    return self._last_day_counter.get()

  def add(self, count=1):
    self._last_min_counter.add(count)
    self._last_hour_counter.add(count)
    self._last_day_counter.add(count)
