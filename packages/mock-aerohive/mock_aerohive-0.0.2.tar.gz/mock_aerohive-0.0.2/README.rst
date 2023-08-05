Mock Aerohive
-------------
.. image:: https://img.shields.io/pypi/v/mock-aerohive.svg
  :target: https://pypi.org/project/mock-aerohive/

.. image:: https://gitlab.com/pencot/mock_aerohive/badges/master/pipeline.svg
  :target: https://github.com/pencot/mock_aerohive/commits/master

.. image:: https://codecov.io/gh/pencot/mock_aerohive/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/pencot/mock_aerohive

A mock SSH server emulating Aerohive devices.

Install::

  pip install mock_aerohive

Basic usage::

  from mock_aerohive import MockAerohive

  aerohive = MockAerohive()
  # You must add at least 1 user before starting the server!  (Library limitation)
  aerohive.addUser("admin", "aerohive")

  port = aerohive.run("127.0.0.1")
  # Or provide a port: aerohive.run("127.0.0.1", 2222)

  aerohive.stop() # Stop a single server.

  aerohive.stopAll() # Terminate the background thread running all SSH servers (otherwise the process will hang)
                     # Once you stop the background thread, you may not start another server (with 'run') -
                     # another library limitation.

For an example of a py.test fixture that automates starting and stopping servers
(which cleans up servers at the end of the testing session, but allows multiple servers to be run),
see ``test/util/MockAerohiveFixture.py``, and ``test/integration/auth/test_addUser_and_login.py`` for an example.

Versioning
^^^^^^^^^^

This package uses semantic versioning.
