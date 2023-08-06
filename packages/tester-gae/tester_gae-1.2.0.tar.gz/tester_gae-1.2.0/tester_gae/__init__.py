"""
Module for GAE specific test stuff
"""
import os
import sys
import unittest


# https://cloud.google.com/sdk/
# gcloud components install app-engine-python
# Start -> Control Panel -> User Accounts -> Change environment variables
# APP_ENGINE_DIR = C:\Users\u\AppData\Local\Google\Cloud SDK\google-cloud-sdk\platform\google_appengine
def path_setup():
    """
    appengine libraries path
    """
    app_engine = os.environ["APP_ENGINE_DIR"]
    if not app_engine:
        raise Exception('Environment variable APP_ENGINE_DIR not set.')

    sys.path.insert(1, app_engine)
    sys.path.insert(1, os.path.join(app_engine, 'lib', 'yaml', 'lib'))
    import dev_appserver
    dev_appserver.fix_sys_path()


path_setup()


class TestGae(unittest.TestCase):
    """
    Init GAE stuff for local testing
    """
    def setUp(  # pylint: disable=arguments-differ,too-many-arguments,too-many-locals,too-many-branches
      self,
      project_dir,
      datastore=True,
      memcache=True,
      app_identity=True,
      blobstore=True,
      files=True,
      images=True,
      taskqueue=True,
      urlfetch=True,
      mail=True,
      user=True,
      capability=True,
      channel=True,
      logservice=True,
      xmpp=True,
      search=True
    ):
        """
        https://cloud.google.com/appengine/docs/python/refdocs/google.appengine.ext.testbed
        """
        from google.appengine.ext import testbed

        self.testbed = testbed.Testbed()
        self.testbed.activate()

        self.policy = None
        self.blobstore_stub = None
        self.taskqueue_stub = None

        if datastore:
            # Create a consistency policy that will simulate the High
            # Replication consistency model. It's easier to test with
            # probability 1.
            from google.appengine.datastore import datastore_stub_util

            self.policy = datastore_stub_util.PseudoRandomHRConsistencyPolicy(probability=1)
            self.testbed.init_datastore_v3_stub(require_indexes=True, root_path=project_dir)

        if memcache:
            self.testbed.init_memcache_stub()

        if app_identity:
            self.testbed.init_app_identity_stub()

        if blobstore:
            self.testbed.init_blobstore_stub()
            self.blobstore_stub = self.testbed.get_stub(testbed.BLOBSTORE_SERVICE_NAME)

        if files:
            self.testbed.init_files_stub()

        if images:
            self.testbed.init_images_stub()

        if taskqueue:
            self.testbed.init_taskqueue_stub(root_path=project_dir)
            self.taskqueue_stub = self.testbed.get_stub(testbed.TASKQUEUE_SERVICE_NAME)

        if urlfetch:
            self.testbed.init_urlfetch_stub()

        if mail:
            self.testbed.init_mail_stub()

        if user:
            self.testbed.init_user_stub()

        if capability:
            self.testbed.init_capability_stub()

        if channel:
            self.testbed.init_channel_stub()

        if logservice:
            self.testbed.init_logservice_stub()

        if xmpp:
            self.testbed.init_xmpp_stub()

        if search:
            # search stub is not available via testbed, so doing this by myself.
            from google.appengine.api import apiproxy_stub_map
            from google.appengine.api.search import simple_search_stub

            apiproxy_stub_map.apiproxy.RegisterStub(
              'search',
              simple_search_stub.SearchServiceStub()
            )

    def tearDown(self):
        self.testbed.deactivate()

    def reread(self, ndbkey):
        """
        drop GAE memcash and read db record
        """
        if not self.policy:
            raise Exception('init_datastore_v3_stub not install.')

        return ndbkey.get(use_cache=False, use_memcache=False)

    def check_db_tables(self, db_state):
        """
        check record count for given db tables
        """
        if not self.policy:
            raise Exception('init_datastore_v3_stub not install.')

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
        if not self.taskqueue_stub:
            raise Exception('init_taskqueue_stub not install.')

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
        if not self.taskqueue_stub:
            raise Exception('init_taskqueue_stub not install.')

        tasks = self.taskqueue_stub.GetTasks(queue_name)
        if flush_queue:
            self.taskqueue_stub.FlushQueue(queue_name)

        return tasks
