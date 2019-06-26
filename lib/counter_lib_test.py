import datetime
import time
import unittest

import counter_lib


class _MockTime(object):
  def __init__(self):
    self._time = time.time()
    self._offset = 0

  def set_offset(self, offset):
    self._offset = offset

  def get_time(self):
    return self._time + self._offset


class _ThreadIdGetter(object):
  def __init__(self):
    self._thread_id = 0

  def set_thread_id(self, id):
    self._thread_id = id

  def get_thread_id(self):
    return self._thread_id


class SingleThreadCounterTests(unittest.TestCase):
  def testNoCount(self):
    mock_time = _MockTime()
    counter = counter_lib._SingleThreadCounter(
        duration=datetime.timedelta(seconds=10), time_func=mock_time.get_time)
    self.assertEqual(counter.get(), 0)
    mock_time.set_offset(5)
    self.assertEqual(counter.get(), 0)
    mock_time.set_offset(15)
    self.assertEqual(counter.get(), 0)

  def testOneCount(self):
    mock_time = _MockTime()
    counter = counter_lib._SingleThreadCounter(
        duration=datetime.timedelta(seconds=10), time_func=mock_time.get_time)
    mock_time.set_offset(5)
    counter.add()
    self.assertEqual(counter.get(), 1)
    mock_time.set_offset(14)
    self.assertEqual(counter.get(), 1)
    mock_time.set_offset(15)
    self.assertEqual(counter.get(), 0)

  def testMultipleCountInSameBucket(self):
    mock_time = _MockTime()
    counter = counter_lib._SingleThreadCounter(
        duration=datetime.timedelta(seconds=10), time_func=mock_time.get_time)
    mock_time.set_offset(5)
    counter.add()
    counter.add()
    counter.add()
    self.assertEqual(counter.get(), 3)
    mock_time.set_offset(14)
    self.assertEqual(counter.get(), 3)
    mock_time.set_offset(15)
    self.assertEqual(counter.get(), 0)

  def testMultipleCountInDiffBucket(self):
    mock_time = _MockTime()
    counter = counter_lib._SingleThreadCounter(
        duration=datetime.timedelta(seconds=10), time_func=mock_time.get_time)
    counter.add()
    mock_time.set_offset(5)
    counter.add()
    mock_time.set_offset(7)
    counter.add()
    self.assertEqual(counter.get(), 3)
    mock_time.set_offset(10)
    self.assertEqual(counter.get(), 2)
    mock_time.set_offset(14)
    self.assertEqual(counter.get(), 2)
    mock_time.set_offset(15)
    self.assertEqual(counter.get(), 1)
    mock_time.set_offset(16)
    self.assertEqual(counter.get(), 1)
    mock_time.set_offset(17)
    self.assertEqual(counter.get(), 0)

  def testMultipleCountOverLongPeriod(self):
    mock_time = _MockTime()
    counter = counter_lib._SingleThreadCounter(
        duration=datetime.timedelta(seconds=10), time_func=mock_time.get_time)
    counter.add()
    mock_time.set_offset(20)
    counter.add()
    self.assertEqual(counter.get(), 1)
    mock_time.set_offset(29)
    self.assertEqual(counter.get(), 1)
    mock_time.set_offset(30)
    self.assertEqual(counter.get(), 0)


class MultiThreadCounterTests(unittest.TestCase):
  def testMultiThread(self):
    mock_time = _MockTime()
    thread_id_getter = _ThreadIdGetter()
    counter = counter_lib._MultiThreadCounter(
        duration=datetime.timedelta(seconds=10),
        time_func=mock_time.get_time,
        thread_id_func=thread_id_getter.get_thread_id)

    mock_time.set_offset(5)
    thread_id_getter.set_thread_id(0)
    counter.add()
    thread_id_getter.set_thread_id(1)
    counter.add()
    thread_id_getter.set_thread_id(2)
    counter.add()

    mock_time.set_offset(7)
    thread_id_getter.set_thread_id(1)
    counter.add()

    mock_time.set_offset(9)
    thread_id_getter.set_thread_id(3)
    self.assertEqual(counter.get(), 4)


if __name__ == '__main__':
  unittest.main()