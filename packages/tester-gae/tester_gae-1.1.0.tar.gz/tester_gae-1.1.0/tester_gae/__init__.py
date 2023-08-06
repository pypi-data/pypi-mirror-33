"""
Module for GAE specific test stuff
"""
import os
import sys
import unittest


def path_setup():
    """
    appengine libraries path
    """
    app_engine = os.environ["APP_ENGINE_DIR"]
    sys.path.insert(1, app_engine)
    sys.path.insert(1, os.path.join(app_engine, 'lib', 'yaml', 'lib'))
    import dev_appserver
    dev_appserver.fix_sys_path()


path_setup()
from google.appengine.ext import testbed  # noqa: F401 pylint: disable=wrong-import-position
from google.appengine.datastore import datastore_stub_util  # noqa: F401 pylint: disable=wrong-import-position


class TestGae(unittest.TestCase):
    """
    Init GAE stuff for local testing
    """
    def setUp(self, project_dir):  # pylint: disable=arguments-differ
        """
        https://cloud.google.com/appengine/docs/python/refdocs/google.appengine.ext.testbed
        """
        self.testbed = testbed.Testbed()
        self.testbed.activate()

        # Create a consistency policy that will simulate the High
        # Replication consistency model. It's easier to test with
        # probability 1.
        self.policy = datastore_stub_util.PseudoRandomHRConsistencyPolicy(probability=1)

        self.testbed.init_datastore_v3_stub(require_indexes=True, root_path=project_dir)
        self.testbed.init_memcache_stub()
        self.testbed.init_app_identity_stub()

        self.testbed.init_blobstore_stub()
        self.blobstore_stub = self.testbed.get_stub(testbed.BLOBSTORE_SERVICE_NAME)

        self.testbed.init_files_stub()
        self.testbed.init_images_stub()

        self.testbed.init_taskqueue_stub(root_path=project_dir)
        self.taskqueue_stub = self.testbed.get_stub(testbed.TASKQUEUE_SERVICE_NAME)

        self.testbed.init_urlfetch_stub()
        self.testbed.init_mail_stub()

        # self.testbed.init_user_stub()
        # init_capability_stub
        # init_channel_stub
        # init_logservice_stub
        # init_xmpp_stub

        # search stub is not available via testbed, so doing this by myself.
        # apiproxy_stub_map.apiproxy.RegisterStub(
        #   'search',
        #   simple_search_stub.SearchServiceStub()
        # )

    def tearDown(self):
        self.testbed.deactivate()

    @staticmethod
    def reread(ndbkey):
        """
        drop GAE memcash and read db record
        """
        return ndbkey.get(use_cache=False, use_memcache=False)

    def check_db_tables(self, db_state):
        """
        check record count for given db tables
        """
        for table, count in db_state:
            i = len(table.query().fetch(300, keys_only=True))
            self.assertEqual(
              i,
              count,
              "{} items: {} must be {}".format(
                table._get_kind(),  # pylint: disable=protected-access
                i,
                count
              )
            )

    def assert_tasks_num(self, tasks_number, queue_name='default'):
        """
        check task count for given GAE taskqueue
        """
        tasks = self.taskqueue_stub.GetTasks(queue_name)
        count = len(tasks)
        self.assertEqual(
          count,
          tasks_number,
          "task count: %d (must be %d) %s" % (
            count, tasks_number, [task['url'] for task in tasks]
          )
        )

    def gae_tasks(self, queue_name='default', flush_queue=True):
        """
        return all tasks for given GAE taskqueue
        """
        tasks = self.taskqueue_stub.GetTasks(queue_name)
        if flush_queue:
            self.taskqueue_stub.FlushQueue(queue_name)

        return tasks
