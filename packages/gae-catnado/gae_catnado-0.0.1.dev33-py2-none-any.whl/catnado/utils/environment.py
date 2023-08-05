import sys


def setup_cloud_sdk_paths():
  """Set up Cloud SDK on `sys.path`.

  Requires `$APPENGINE_SDK_DIR` be set to your App Engine SDK directory at
  `google-cloud-sdk/platform/google_appengine`.

  Useful for setting up tests that require App Engine stubs.
  """
  paths_need_setup = not any(['google_appengine' in path for path in sys.path])
  if paths_need_setup:
    import os
    gae_dir = os.environ.get('APPENGINE_SDK_DIR')
    assert gae_dir is not None, 'Please set $APPENGINE_SDK_DIR'
    sys.path.append(gae_dir)
    # importing dev_appserver handles adding rest of libraries to sys.path
    import dev_appserver
    dev_appserver.fix_sys_path()
