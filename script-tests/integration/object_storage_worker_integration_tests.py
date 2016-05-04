# Copyright 2016 PerfKitBenchmarker Authors. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Integration tests for the object_storage_service benchmark worker process."""

import time
import unittest

import object_storage_api_tests


class MockObjectStorageBackend(object_storage_api_tests.ObjectStorageBackend):
  def __init__(self):
    self.bucket = None
    self.objects = {}

  def _CheckBucket(self, bucket):
    """Make sure that we are only passed one bucket name.

    Args:
      bucket: the name of a bucket.

    Raises: ValueError, if this object has been passed a different
    bucket name previously.
    """

    if self.bucket is None:
      self.bucket = bucket
    elif self.bucket != bucket:
      raise ValueError(
          'MockObjectStorageBackend passed two bucket names: %s and %s' %
          (self.bucket, bucket))

  def ListObjects(self, bucket, prefix):
    self._CheckBucket(bucket)

    return [value
            for name, value in self.objects.iteritems()
            if name.startswith(prefix)]

  def DeleteObjects(self, bucket, objects_to_delete, objects_deleted=None):
    self._CheckBucket(bucket)

    for name in objects_to_delete:
      if name in self.objects:
        del self.objects[name]
        if objects_deleted is not None:
          objects_deleted.append(name)

  def WriteObjectFromBuffer(self, bucket, object, stream, size):
    self._CheckBucket(bucket)

    stream.seek(0)
    self.objects[object] = stream.read(size)

    return time.time(), 0.001

  def ReadObject(self, bucket, object):
    self._CheckBucket(bucket)

    self.objects[object]

    return time.time(), 0.001


class TestScenarios(unittest.TestCase):
  """Test that the benchmark scenarios complete.

  Specifically, given a correctly operating backend
  (MockObjectStorageBackend), verify that every scenario except
  MultiStreamRead runs to completion without raising an exception.
  """

  def setUp(self):
    object_storage_api_tests.FLAGS([])

  def testOneByteRW(self):
    object_storage_api_tests.OneByteRWBenchmark(MockObjectStorageBackend())

  def testListConsistency(self):
    object_storage_api_tests.ListConsistencyBenchmark(
        MockObjectStorageBackend())

  def testSingleStreamThroughput(self):
    object_storage_api_tests.SingleStreamThroughputBenchmark(
        MockObjectStorageBackend())

  def testCleanupBucket(self):
    object_storage_api_tests.CleanupBucket(MockObjectStorageBackend())

  def testMultiStreamWrite(self):
    object_storage_api_tests.MultiStreamWrites(MockObjectStorageBackend())

  # Can't test MultiStreamRead this way because it depends on a file
  # with a list of objects written by MultiStreamWrites.

  def testTestBackend(self):
    object_storage_api_tests.TestBackend(MockObjectStorageBackend())



if __name__ == '__main__':
  unittest.main()
