Quick start guide
=================

This manual will show users how to install Fastr, configure Fastr, construct and run simple networks, and add tool definitions.

.. _installation-chapter:

Installation
------------

You can install Fastr either using pip, or from the source code.

Installing via pip
``````````````````

You can simply install fastr using ``pip``:

.. code-block:: bash

    pip install fastr
	
.. note:: You might want to consider installing ``fastr`` in a `virtualenv <http://docs.python-guide.org/en/latest/dev/virtualenvs/>`_


Installing from source code
```````````````````````````

To install from source code, use Mercurial via the command-line:

.. code-block:: bash

    hg clone https://<yourusername>@bitbucket.org/bigr_erasmusmc/fastr  # for http
    hg clone ssh://hg@bitbucket.org/bigr_erasmusmc/fastr # for ssh

If you prefer a GUI you can try `TortoiseHG <http://tortoisehg.bitbucket.org/>`_ (Windows, Linux and Mac OS X) or `SourceTree <http://www.atlassian.com/software/sourcetree/overview>`_ (Windows and Mac OS X). The address of the repository is (given for both http and ssh):

.. code-block:: bash

    https://<yourusername>@bitbucket.org/bigr_erasmusmc/fastr
    ssh://hg@bitbucket.org/bigr_erasmusmc/fastr


.. _subsec-installing:

To install to your current Python environment, run:

.. code-block:: bash

    cd fastr/
    pip install .

This installs the scripts and packages in the default system folders. For
windows this is the python ``site-packages`` directory for the fastr python
library and ``Scripts`` directory for the executable scripts. For Ubuntu this
is in the ``/usr/local/lib/python2.7/dist-packages/`` and ``/usr/local/bin/``
respectively.

.. note:: If you want to develop fastr, you might want to use ``pip install -e .`` to get an editable install

.. note:: You might want to consider installing ``fastr`` in a `virtualenv <http://docs.python-guide.org/en/latest/dev/virtualenvs/>`_

.. note::

    - On windows ``python`` and the ``Scripts`` directory are not on the system PATH by default. You can add these by going to ``System -> Advanced Options -> Environment variables``. 
    - On mac you need the Xcode Command Line Tools. These can be installed using the command ``xcode-select --install``.


Configuration
-------------

Fastr has defaults for all settings so it can be run out of the box to test the examples.
However, when you want to create your own Networks, use your own data, or use your own Tools,
it is required to edit your config file.

Fastr will search for a config file named ``config.py`` in the ``$FASTRHOME`` and ``~/.fastr/``
directories. If both config files contain values for a single setting, the version in
``~/.fastr/`` has priority.

For a sample configuration file and a complete overview of the options in ``config.py`` see the :ref:`Config file <config-file>` section.

Creating a simple network
-------------------------

If Fastr is properly installed and configured, we can start creating networks. Creating a network is very simple:

.. code-block:: python

    >>> import fastr

    >>> network = fastr.Network()

Now we have an empty network, the next step is to create some nodes and links. Imagine we want to create the following network:

.. image:: images/network1.*

Creating nodes
``````````````

We will create the nodes and add them to the network. The easiest way to do this is via the network ``create_`` methods. Let's create two source nodes, one normal node, and one sink:

.. code-block:: python

    >>> source1 = network.create_source('Int', id_='source1')
    >>> constant1 = network.create_constant('Int', [1, 3, 3, 7], id_='const1')
    >>> sink1 = network.create_sink('Int', id_='sink1')
    >>> addint = network.create_node('AddInt', id_='addint')

The functions :py:meth:`Network.create_source <fastr.core.network.Network.create_source>`, :py:meth:`Network.create_constant <fastr.core.network.Network.create_constant>`, :py:meth:`Network.create_source <fastr.core.network.Network.create_sink>` and :py:meth:`Network.create_source <fastr.core.network.Network.create_node>` are shortcut functions for calling the :py:class:`SourceNodeRun <fastr.core.node.SourceNodeRun>`, :py:class:`ConstantNodeRun <fastr.core.node.ConstantNodeRun>`, :py:class:`SinkNodeRun <fastr.core.node.SinkNodeRun>` and :py:class:`NodeRun <fastr.core.node.NodeRun>` constructors and adding them to the network.
A :py:class:`SourceNodeRun <fastr.core.node.SourceNodeRun>` and :py:class:`SinkNodeRun <fastr.core.node.SinkNodeRun>` only require the datatype to be specified.
A :py:class:`ConstantNodeRun <fastr.core.node.ConstantNodeRun>` requires both the datatype and the data to be set on creation.
A :py:class:`NodeRun <fastr.core.node.NodeRun>` requires a :py:class:`Tool <fastr.core.tool.Tool>` template to be instantiated from.
The ``id_`` option is optional for all three, but makes it easier to identify the nodes and read the logs.

There is an easier way to add a constant to an input, by using a shortcut method. If you assign a :class:`list` or :class:`tuple` to an item in the input list, it will automatically create a :py:class:`ConstantNodeRun <fastr.core.node.ConstantNodeRun>` and a :py:class:`Link <fastr.core.link.Link>` between the contant and the input:

.. code-block:: python

    >>> addint.inputs['right_hand'] = [1, 3, 3, 7]

The created constant would have the id ``addint__right_hand__const`` as it automatically names the new constant ``$nodeid__$inputid__const``.

In an interactive python session we can simply look at the basic layout of the node using the ``repr`` function. Just type the name of the variable holding the node and it will print a human readable representation:

.. code-block:: python

    >>> source1
    SourceNodeRun source1 (tool: source v1.0)
          Inputs         |       Outputs      
    -------------------------------------------
                         |  output   (Int)     
    >>> addint
    NodeRun addint (tool: AddInt v1.0)
           Inputs          |       Outputs
    ---------------------------------------------
    left_hand  (Int)       |  result   (Int)
    right_hand (Int)       |


This tool has inputs of type Int, so the sources and sinks need to have a matching datatype.

The tools and datatypes available are stored in :py:attr:`fastr.toollist` and :py:attr:`fastr.typelist`. These variables are created when :py:mod:`fastr` is imported for the first time. They contain all the datatype and tools specified by the xml files in the search paths. To get an overview of the tools and datatypes loaded by fastr:

.. code-block:: python

    >>> fastr.toollist
    ToolManager
    Add                            v0.1           :  /home/hachterberg/dev/fastr-develop/fastr/fastr/resources/tools/add/v1_0/add.xml
    AddImages                      v0.1           :  /home/hachterberg/dev/fastr-develop/fastr/fastr/resources/tools/addimages/v1_0/addimages.xml
    AddInt                         v0.1           :  /home/hachterberg/dev/fastr-develop/fastr/fastr/resources/tools/addint/v1_0/addint.xml

    >>> fastr.typelist
    DataTypeManager
    AnyType                    :  <class 'fastr.datatypes.AnyType'>                                 
    Boolean                    :  <class 'fastr.datatypes.Boolean'>                                 
    Directory                  :  <class 'fastr.datatypes.Directory'> 
    Float                      :  <class 'fastr.datatypes.Float'>                                   
    Int                        :  <class 'fastr.datatypes.Int'>           
    String                     :  <class 'fastr.datatypes.String'>                                  

The ``fastr.toollist`` variable contains all tools that Fastr could find during initalization. Tools can be chosen in two tways:

   - ``toollist[id]`` which returns the newest version of the tool
   - ``toollist[id, version]`` which returns the specified version of the tool

Creating links
``````````````

So now we have a network with 4 nodes defined, however there is no relation between the nodes yet. For this we have to create some links.

.. code-block:: python

    >>> link1 = network.create_link(source1.output, addint.inputs['left_hand'])
    >>> link2 = network.create_link(constant1.output, addint.inputs['right_hand'])
    >>> link3 = network.create_link(addint.outputs['result'], sink1.inputs['input'])

This asks the network to create links and immediatly store them inside the network. A link always points from an Output to an Input (note that SubOutput or SubInputs are also valid). A SourceNodeRun has only 1 output which is fixed, so it is easy to find. However, addImage has two inputs and one output, this requires us to specify which output we need. A normal node has a mapping with Inputs and one with Outputs. They can be indexed with the approriate id's. The function returns the links, but you only need that if you are planning to change a link. If not, it is possible to use a short-hand which creates a link but gives you no easy access to it for later.

.. code-block:: python

    >>> addint.inputs['left_hand'] = source1.output
    >>> addint.inputs['right_hand'] = constant1.output
    >>> sink1.inputs['input'] = addint.outputs['result']

Create an image of the Network
``````````````````````````````

For checking your Network it is very useful to have a graphical representation of the network. This can be achieved using the :py:meth:`Network.draw_network <fastr.core.network.Network.draw_network>` method.

.. code-block:: python

    >>> network.draw_network()
    '/home/username/network_layout.dot.svg'

This will create a figure in the path returned by the function that looks like:

.. image:: images/network1.*

.. note:: for this to work you need to have graphviz installed

Running a Network
-----------------

Running a network locally is almost as simple as calling the :py:meth:`Network.execute <fastr.core.network.Network.execute>` method:

.. code-block:: python

    >>> source_data = {'source1': {'s1': 4, 's2': 5, 's3': 6, 's4': 7}}
    >>> sink_data = {'sink1': 'vfs://tmp/fastr_result_{sample_id}.txt'}
    >>> network.execute(source_data, sink_data)

As you can see the execute method needs data for the sources and sinks. This
has to be supplied in two :class:`dict` that have keys matching every
source/sink ``id`` in the network. Not supplying data for every source and
sink will result in an error, although it is possible to pass an empty
:class:`list` to a source.

.. note:: The values of the source data have to be simple values or urls
          and values of the sink data have to be url templates. To see 
          what url schemes are available and how they work see
          :ref:`IOPlugin Reference <ioplugin-ref>`. For the sink url
          templates see :py:meth:`SinkNodeRun.set_data <fastr.core.node.SinkNodeRun.set_data>`

For source nodes you can supply a :class:`list` or a :class:`dict` with values.
If you supply a :class:`dict` the keys will be interpreted as sample ids and
the values as the corresponding values. If you supply a :class:`list`, keys
will be generated in the form of ``id_{N}`` where N will be index of the value
in the list.

.. warning:: As a :class:`dict` does not have a fixed order, when a 
             :class:`dict` is supplied the samples are ordered by key to get
             a fixed order! For a ``list`` the original order is retained.

For the sink data, an url template has to be supplied that governs how the data
is stored. The mini-lanuage (the replacement fields) are described in the
:py:meth:`SinkNodeRun.set_data <fastr.core.node.SinkNodeRun.set_data>` method.

To rerun a stopped/crashed pipeline check the user manual on :ref:`Continuing a Network <continuing-network>`

