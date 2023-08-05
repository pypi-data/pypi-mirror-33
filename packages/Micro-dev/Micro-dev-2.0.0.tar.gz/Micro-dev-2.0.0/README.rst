Micro-dev
=========

Micro-dev is the only thing needed to create plugins for Micro and
use the Micro’s endpoints to send tasks.

Installation
------------

PyPi:

::

    $ pip install micro-dev

Development version:

::

    $ git clone git@github.com:humu1us/micro-dev.git:
    $ cd micro-dev
    $ pip install .

or direct from repository:

::

    $ pip install git+ssh://git@github.com/humu1us/micro-dev.git

Usage
-----

Create Plugins
~~~~~~~~~~~~~~

Write a Micro plugin is very simple. All that you need to do is create a
file named ``interface.py`` which defines the plugin as follow:

.. code:: python

    from micro.plugin.pluginbase import PluginBase
    from micro.plugin.pluginbase import PluginDescription


    class ExamplePlugin(PluginBase):
      def __init__(self):
          print("This is an example plugin")

    # This is the method executed by Micro
      def run(self, **kwargs):
          return "Hello " + kwargs["name"] + "!!!"

    # This description is required by Micro
    plugin = PluginDescription(
      name="Example Plugin",
      author="Jhon Doe",
      short_desc="A very simple example plugin",
      long_desc="This plugin is a very simple example, "
                "for that reason, we don't have a long description"
      help_str="Params: name type string; A name to greet",
      instance=ExamplePlugin
    )

Send tasks
~~~~~~~~~~

.. code:: python

    >>> from micro.api.endpoints import Requests
    >>>
    >>> req = Requests(BROKER_URL, QUEUE_NAME)
    >>>
    >>> req.plugins.delay().wait()
    {'Example plugin': 'A very simple example plugin'}
    >>>
    >>> req.run.delay("Example plugin", name="Micro").wait()
    'Hello Micro!!!'
