User Manual
===========

In this chapter we will discuss the parts of Fastr in more detail. We will give a more complete overview of the system
and describe the more advanced features.

.. _tools:

Tools
-----

The :py:class:`Tools <fastr.core.tool.Tool>` in Fastr are the building blocks of each workflow.
A tool represents a program/script/binary that can be called by Fastr and can be seens as a template.
A :py:class:`Node <fastr.core.node.Node>` can be created based on a :py:class:`Tool <fastr.core.tool.Tool>`.
The Node will be one processing step in a workflow, and the tool defines what the step does.

On the import of Fastr, all available :py:class:`Tools <fastr.core.tool.Tool>` will be loaded in a default
:py:class:`ToolManager <fastr.core.toolmanager.ToolManager>` that can be accessed via ``fastr.toollist``. To get an
overview of the tools in the system, just print the :func:`repr` of the :py:class:`ToolManager <fastr.core.toolmanager.ToolManager>`:

.. code-block:: python

    >>> fastr.toollist
    AddImages                v0.1    :  /home/hachterberg/dev/fastr/fastr/resources/tools/addimages/v1_0/addimages.xml
    AddInt                   v0.1    :  /home/hachterberg/dev/fastr/fastr/resources/tools/addint/v1_0/addint.xml

As you can see it gives the tool id, version and the file from which it was loaded for each tool in the system.
To view the layout of a tool, just print the :func:`repr` of the tool itself.

.. code-block:: python

    >>> fastr.toollist['AddInt']
    Tool AddInt v0.1 (Add two integers)
           Inputs          |       Outputs
    ---------------------------------------------
    left_hand  (Int)       |  result   (Int)
    right_hand (Int)       |

To add a :py:class:`Tool <fastr.core.tool.Tool>` to the system a file should be added to one of the path
in ``fastr.config.tools_path``. The structure of a tool file is described in :ref:`Tool description <tool-schema>`

Create your own tool
~~~~~~~~~~~~~~~~~~~~

There are 4 steps in creating a tool:

1. **Create folders.** We will call the tool ThrowDie. Create the folder throw_die in the folder fastr-tools. In this folder create another folder called bin.
2. **Place executable in correct place.** In this example we will use a snippet of executable python code:

   .. code-block:: python

       #!/usr/bin/env python
       import sys
       import random
       import json

       if (len(sys.argv) > 1):
           sides = int(sys.argv[1])
       else:
           sides = 6
       result = [int(random.randint(1, sides ))]

       print('RESULT={}'.format(json.dumps(result)))

   Save this text in a file called ``throw_die.py``

   Place the executable python script in the folder ``throw_die/bin``
3. **Create and edit xml file for tool.** See :ref:`tool definition reference <tool-schema>` for all the fields
   that can be defined in a tool.

   Put the following text in file called ``throw_die.xml``.

   .. code-block:: xml

       <tool id="ThrowDie" description="Simulates a throw of a die. Number of sides of the die is provided by user"
             name="throw_die" version="1.0">
         <authors>
           <author name="John Doe" />
         </authors>
         <command version="1.0" >
           <authors>
             <author name="John Doe" url="http://a.b/c" />
           </authors>
           <targets>
             <target arch="*" bin="throw_die.py" interpreter="python" os="*" paths='bin/'/>
           </targets>
           <description>
              throw_die.py number_of_sides
              output = simulated die throw
           </description>
         </command>
         <interface>
           <inputs>
             <input cardinality="1" datatype="Int" description="Number of die sides" id="die_sides" name="die sides" nospace="False" order="0" required="True"/>
            </inputs>
           <outputs>
             <output id="output" name="output value" datatype="Int" automatic="True" cardinality="1" method="json" location="^RESULT=(.*)$" />
           </outputs>
         </interface>
       </tool>

   Put throw_die.xml in the folder example_tool. All Attributes in the example above are required. For a complete overview of the xml Attributes that can be used to define a tool, check the :ref:`Tool description <tool-schema>`. The most important Attributes in this xml are:
   ::
    id      : The id is used in in FASTR to create an instance of your tool, this name will appear in the toollist when you type fastr.toollist.
    targets : This defines where the executables are located and on which platform they are available.
    inputs  : This defines the inputs that you want to be used in FASTR, how FASTR should use them and what data is allowed to be put in there.

   More xml examples can be found in the fastr-tools folder.

4) **Edit configuration file.** Append the line ``[PATH TO LOCATION OF FASTR-TOOLS]/fastr-tools/throw_die/``
   to the the ``config.py`` (located in ~/.fastr/ directory) to the ``tools_path``. See  :ref:`Config file <config-file>` for more
   information on configuration.



   You should now have a working tool. To test that everything is ok do the following in python:

   .. code-block:: python

       >>> import fastr
       >>> fastr.toollist

Now a list of available tools should be produced, including the tool throw_die

To test the tool create the script test_throwdie.py:

   .. code-block:: python

    import fastr
    network = fastr.Network()
    source1 = network.create_source(fastr.typelist['Int'], id_='source1')
    sink1 = network.create_sink(fastr.typelist['Int'], id_='sink1')
    throwdie = network.create_node(fastr.toollist['ThrowDie'], id_='throwdie')
    link1 = network.create_link(source1.output, throwdie.inputs['die_sides'])
    link2 = network.create_link(throwdie.outputs['output'], sink1.inputs['input'])
    source_data = {'source1': {'s1': 4, 's2': 5, 's3': 6, 's4': 7}}
    sink_data = {'sink1': 'vfs://tmp/fastr_result_{sample_id}.txt'}
    network.draw_network()
    network.execute(source_data, sink_data)


Call the script from commandline by

 .. code-block:: python

    $ python test_throwdie.py

An image of the network will be created in the current directory and result files will be put in the tmp directory. The result files are called
``fastr_result_s1.txt``, ``fastr_result_s2.txt``, ``fastr_result_s3.txt``, and ``fastr_result_s4.txt``

.. note:: If you have code which is operating system depend you will have to edit the xml file. The following gives and
          example of how the elastix tool does this:

          .. code-block:: xml

              <targets>
                    <target os="windows" arch="*" bin="elastix.exe">
                      <paths>
                        <path type="bin" value="vfs://apps/elastix/4.7/install/" />
                        <path type="lib" value="vfs://apps/elastix/4.7/install/lib" />
                      </paths>
                    </target>
                    <target os="linux" arch="*" modules="elastix/4.7" bin="elastix">
                      <paths>
                        <path type="bin" value="vfs://apps/elastix/4.7/install/" />
                        <path type="lib" value="vfs://apps/elastix/4.7/install/lib" />
                      </paths>
                    </target>
                    <target os="darwin" arch="*" modules="elastix/4.7" bin="elastix">
                      <paths>
                        <path type="bin" value="vfs://apps/elastix/4.7/install/" />
                        <path type="lib" value="vfs://apps/elastix/4.7/install/lib" />
                      </paths>
                    </target>
                 </targets>

``vfs`` is the virtual file system path, more information can be found at
:py:class:`VirtualFileSystem <fastr.core.vfs.VirtualFileSystem>`.


.. _network:

Network
-------

A :py:class:`Network <fastr.core.network.Network>` represented an entire workflow.
It hold all :py:class:`Nodes <fastr.core.node.Node>`, :py:class:`Links <fastr.core.link.Link>` and other information
required to execute the workflow. Networks can be visualized as a number of building blocks (the Nodes) and links
between them:

.. image:: images/network_multi_atlas.*

An empty network is easy to create, all you need is to name it:

.. code-block:: python

    >>> network = fastr.Network(id_="network_name")

The :py:class:`Network <fastr.core.network.Network>` is the main interface to Fastr, from it you can create all elements
to create a workflow. In the following sections the different elements of a
:py:class:`Network <fastr.core.network.Network>` will be described in more detail.


.. _node:

Node
~~~~

:py:class:`Nodes <fastr.core.node.Node>` are the point in the :py:class:`Network <fastr.core.network.Network>` where
the processing happens. A :py:class:`Node <fastr.core.node.Node>` takes the input data and executes jobs as specified
by the underlying :py:class:`Tool <fastr.core.tool.Tool>`. A :py:class:`Nodes <fastr.core.node.Node>` can be created in a two different ways:

.. code-block:: python

    >>> node1 = fastr.Node(tool, id_='node1', parent=network)
    >>> node2 = network.create_node(tool, id_='node2', stepid='step1')

In the first way, we specifically create a :py:class:`Node <fastr.core.node.Node>` object. We pass it an ``id`` and
the ``parent`` network.
If the ``parent`` is ``None`` the ``fastr.curent_network`` will be used.
The :py:class:`Node <fastr.core.node.Node>` constructor will automaticaly add the new node to the ``parent`` network.

.. note::

    For a Node, the tool can be given both as the :py:class:`Tool <fastr.core.tool.Tool>` class or the id of the
tool.

The second way, we tell the ``network`` to create a :py:class:`Node <fastr.core.node.Node>`.
The ``network`` will automatically assign itself as the ``parent``.
Optionally you can add define a ``stepid`` for the node which is a logical grouping of
:py:class:`Nodes <fastr.core.node.Node>` that is mostly used for visualization.

A :py:class:`Node <fastr.core.node.Node>` contains :py:class:`Inputs  <fastr.core.inputoutput.Input>` and
:py:class:`Outputs <fastr.core.inputoutput.Output>`. To see the layout of the :py:class:`Node <fastr.core.node.Node>`
one can simply look at the :func:`repr`.

.. code-block:: python

    >>> addint = fastr.Node(fastr.toollist['AddInt'], id_='addint')
    >>> addint
    Node addint (tool: AddInt v1.0)
           Inputs          |       Outputs
    ---------------------------------------------
    left_hand  (Int)       |  result   (Int)
    right_hand (Int)       |

The inputs and outputs are located in mappings with the same name:

.. code-block:: python

    >>> addint.inputs
    InputDict([('left_hand', <Input: fastr:///networks/unnamed_network/nodelist/addint/inputs/left_hand>), ('right_hand', <Input: fastr:///networks/unnamed_network/nodelist/addint/inputs/right_hand>)])

    >>> addint.outputs
    OutputDict([('result', Output fastr:///networks/unnamed_network/nodelist/addint/outputs/result)])

The :py:class:`InputDict <fastr.core.node.InputDict>` and :py:class:`OutputDict <fastr.core.node.OutputDict>` are
classes that behave like mappings. The :py:class:`InputDict <fastr.core.node.InputDict>` also facilitaties the linking
shorthand. By assigning an :py:class:`Output <fastr.core.inputoutput.Output>` to an existing key, the
:py:class:`InputDict <fastr.core.node.InputDict>` will create a :py:class:`Link <fastr.core.link.Link>` between the
:py:class:`InputDict <fastr.core.inputoutput.Input>` and :py:class:`Output <fastr.core.inputoutput.Output>`.


.. _source-node:

SourceNode
~~~~~~~~~~

A :py:class:`SourceNode <fastr.core.node.SourceNode>` is a special kind of node that is the start of a workflow.
The :py:class:`SourceNodes <fastr.core.node.SourceNode>` are given data at run-time that fetched via
:py:class:`IOPlugins <fastr.core.ioplugin.IOPlugin>`. On create, only the datatype of the data that the
:py:class:`SourceNode <fastr.core.node.SourceNode>` supplied needs to be known. Creating a
:py:class:`SourceNode <fastr.core.node.SourceNode>` is very similar to an ordinary node:

.. code-block:: python

    >>> source1 = fastr.SourceNode('Int', id_='source1')
    >>> source2 = network.create_source(fastr.typelist['Int'], id_='source2', stepid='step1')

In both cases, the source is automatically automaticall assigned to a network.
In the first case to the ``fastr.current_network`` and in the second case to the ``network`` used to call the method.
A :py:class:`SourceNode <fastr.core.node.SourceNode>` only has a single output which has a short-cut access via ``source.output``.

.. note:: For a source or constant node, the datatype can be given both as the :py:class:`BaseDataType <fastr.datatypes.BaseDataType>` class or the id of the datatype.


.. _constant-node:

ConstantNode
~~~~~~~~~~~~

A :py:class:`ConstantNode <fastr.core.node.ConstantNode>` is another special node.
It is a subclass of the :py:class:`SourceNode <fastr.core.node.SourceNode>` and has a similar function.
However, instead of setting the data at run-time, the data of a constant is given at creation and saved in the object.
Creating a :py:class:`ConstantNode <fastr.core.node.ConstantNode>` is similar as creating a source, but with supplying data:

.. code-block:: python

    >>> constant1 = fastr.ConstantNode('Int', [42], id_='constant1')
    >>> constant2 = network.create_constant('Int', [42], id_='constant2', stepid='step1')

Often, when a :py:class:`ConstantNode <fastr.core.node.ConstantNode>` is created, it is created specifically for one input and will not be reused.
In this case there is a shorthand to create and link a constant to an input:

.. code-block:: python

    >>> addint.inputs['value1'] = [42]

will create a constant node with the value 42 and create a link between the output and input ``addint.value1``.


.. _sink-node:

SinkNode
~~~~~~~~

The :py:class:`SinkNode <fastr.core.node.SinkNode>` is the counter-part of the source node.
Instead of get data into the workflow, it saves the data resulting from the workflow.
For this a rule has to be given at run-time that determines where to store the data.
The information about how to create such a rule is described at :py:meth:`SinkNode.set_data <fastr.core.node.SinkNode.set_data>`.
At creation time, only the datatype has to be specified:

.. code-block:: python

    >>> sink1 = fastr.Sink('Int', id_='sink1')
    >>> sink2 = network.create_sink(fastr.typelist['Int'], id_='sink2', stepid='step1')


.. _link:

Link
~~~~


:py:class:`Links <fastr.core.link.Link>` indicate how the data flows between :py:class:`Nodes <fastr.core.node.Node>`.
Links can be created explicitly using on of the following:

.. code-block:: python

    >>> link = fastr.Link(node1.outputs['image'], node2.inputs['image'])
    >>> link = network.create_link(node1.outputs['image'], node2.inputs['image'])

or can be create implicitly by assigning an :py:class:`Output <fastr.core.inputoutput.Output>` to an
:py:class:`Input <fastr.core.inputoutput.Input>` in the :py:class:`InputDict <fastr.core.node.InputDict>`.

.. code-block:: python

    # This style of assignment will create a Link similar to above
    >>> node2.inputs['image'] = node1.outputs['image']

Note that a :py:class:`Link <fastr.core.link.Link>` is also create automatically when using the short-hand for the
:py:class:`ConstantNode <fastr.core.node.ConstantNode>`

Data Flow
---------

The data enters the :py:class:`Network <fastr.core.network.Network>` via
:py:class:`SourceNodes <fastr.core.node.SourceNode>`, flows via other :py:class:`Nodes <fastr.core.node.Node>` and
leaves the :py:class:`Network <fastr.core.network.Network>` via :py:class:`SinkNodes <fastr.core.node.SinkNode>`.
The flow between :py:class:`Nodes <fastr.core.node.Node>` goes from an
:py:class:`Output <fastr.core.inputoutput.Output>` via a :py:class:`Link <fastr.core.link.Link>` to an
:py:class:`Input  <fastr.core.inputoutput.Input>`. In the following image it is simple to track the data from
the :py:class:`SourceNodes <fastr.core.node.SourceNode>` at the left to the
:py:class:`SinkNodes <fastr.core.node.SinkNode>` at right side:

.. image:: images/network1.*

Note that the data in Fastr is stored in the :py:class:`Output <fastr.core.inputoutput.Output>` and the
:py:class:`Link <fastr.core.link.Link>` and :py:class:`Input  <fastr.core.inputoutput.Input>` just give access to it
(possible while transforming the data).


Data flow inside a Node
~~~~~~~~~~~~~~~~~~~~~~~

In a :py:class:`Node <fastr.core.node.Node>` all data from the :py:class:`Inputs  <fastr.core.inputoutput.Input>` will
be combined and the jobs will be generated. There are strict rules to how this combination is performed. In the default
case all inputs will be used pair-wise, and if there is only a single value for an input, it it will be considered as
a constant.

To illustrate this we will consider the following :py:class:`Tool <fastr.core.tool.Tool>` (note this is a simplified
version of the real tool):

.. code-block:: python

    >>> fastr.toollist['Elastix']
    Tool Elastix v4.8 (Elastix Registration)
                             Inputs                            |             Outputs
    ----------------------------------------------------------------------------------------------
    fixed_image       (ITKImageFile)                           |  transform (ElastixTransformFile)
    moving_image      (ITKImageFile)                           |
    parameters        (ElastixParameterFile)                   |

Also it is important to know that for this tool (by definition) the cardinality of the ``transform`` :py:class:`Output <fastr.core.inputoutput.Output>`
will match the cardinality of the ``parameters`` :py:class:`Inputs  <fastr.core.inputoutput.Input>`

If we supply a :py:class:`Node <fastr.core.node.Node>` based on this :py:class:`Tool <fastr.core.tool.Tool>` with a
single sample on each :py:class:`Input  <fastr.core.inputoutput.Input>`, there will be one single matching
:py:class:`Output <fastr.core.inputoutput.Output>` sample created:

.. image:: images/flow/flow_simple_one_sample.*

If the cardinality of the ``parameters`` sample would be increased to 2, the resulting ``transform`` sample would also
become 2:

.. image:: images/flow/flow_simple_one_sample_two_cardinality.*

Now if the number of samples on ``fixed_image`` would be increased to 3, the ``moving_image`` and ``parameters``
will be considered constant and be repeated, resulting in 3 ``transform`` samples.

.. image:: images/flow/flow_simple_three_sample.*

Then if the amount of samples for ``moving_image`` is also increased to 3, the ``moving_image`` and ``fixed_image`` will
be used pairwise and the ``parameters`` will be constant.

.. image:: images/flow/flow_simple_three_sample_two_cardinality.*

.. _advanced-flow-node:

Advanced flows in a Node
````````````````````````

Sometimes the default pairwise behaviour is not desirable. For example if you want to test all combinations of certain
input samples. To achieve this we can change the :py:meth:`input_group <fastr.core.inputoutput.Input.input_group>` of
:py:class:`Inputs  <fastr.core.inputoutput.Input>` to set them apart from the rest. By default all
:py:class:`Inputs  <fastr.core.inputoutput.Input>` are assigned to the ``default`` input group. Now let us change that:

.. code-block:: python

    >>> node = network.create_node('Elastix', id_='elastix')
    >>> node.inputs['moving_image'].input_group = 'moving'

This will result in ``moving_image`` to be put in a different input group. Now if we would supply ``fixed_image`` with
3 samples and ``moving_image`` with 4 samples, instead of an error we would get the following result:

.. image:: images/flow/flow_cross_three_sample.*

.. warning:: TODO: Expand this section with the merging dimensions

Data flows in a Link
~~~~~~~~~~~~~~~~~~~~

As mentioned before the data flows from an :py:class:`Output <fastr.core.inputoutput.Output>` to an
:py:class:`Input  <fastr.core.inputoutput.Input>` throuhg a :py:class:`Link <fastr.core.link.Link>`. By default the
:py:class:`Link <fastr.core.link.Link>` passed the data as is, however there are two special directives that change
the shape of the data:

1. Collapsing flow, this collapses certain dimensions from the sample array into the cardinality. As a user you have to
   specify the dimension or tuple of dimensions you want to collapse.

   .. image:: images/flow/flow_collapse.*

   This is useful in situation where you want to use a tool that aggregates over a number of samples (e.g. take a mean
   or sum).

   To achieve this you can set the :py:meth:`collapse <fastr.core.link.Link.collapse>` property of the
   :py:class:`Link <fastr.core.link.Link>` as follows:

   .. code-block:: python

       >>> link.collapse = 'dim1'
       >>> link.collapse = ('dim1', 'dim2')  # In case you want to collapse multiple dimensions

2. Expanding flow, this turns the cardinality into a new dimension. The new dimension will be named after the
   :py:class:`Output <fastr.core.inputoutput.Output>` from which the link originates. It will be in the form of
   ``{nodeid}__{outputid}``

   .. image:: images/flow/flow_expand.*

   This flow directive is useful if you want to split a large sample in multiple smaller samples. This could be because
   processing the whole sample is not feasible because of resource constraints. An example would be splitting a 3D image
   into slices to process separately to avoid high memory use or to achieve parallelism.

   To achieve this you can set the :py:meth:`expand <fastr.core.link.Link.expand>` property of the
   :py:class:`Link <fastr.core.link.Link>` to ``True``:

   .. code-block:: python

       >>> link.expand = True

.. note:: both collapsing and expanding can be used on the same link, it will executes similar to a expand-collapse
          sequence, but the newly created expand dimension is ignored in the collapse.

          .. image:: images/flow/flow_expand_collapse.*

          .. code-block:: python

              >>> link.collapse = 'dim1'
              >>> link.expand = True


Data flows in an Input
~~~~~~~~~~~~~~~~~~~~~~

If an :py:class:`Inputs  <fastr.core.inputoutput.Input>` has multiple :py:class:`Links <fastr.core.link.Link>` attached
to it, the data will be combined by concatenating the values for each corresponding sample in the cardinality.

Broadcasting (matching data of different dimensions)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sometimes you might want to combine data that does not have the same number of dimensions. As long as all dimensions of
the lower dimensional datasets match a dimension in the higher dimensional dataset, this can be achieved using
*broadcasting*. The term *broadcasting* is borrowed from `NumPy <http://www.numpy.org/>`_ and described as:

    "The term broadcasting describes how numpy treats arrays with different shapes during arithmetic operations.
    Subject to certain constraints, the smaller array is “broadcast” across the larger array so that they have
    compatible shapes."

    -- `NumPy manual on broadcasting <http://docs.scipy.org/doc/numpy-1.10.1/user/basics.broadcasting.html>`_

In fastr it works similar, but to combined different Inputs in an InputGroup. To illustrate broadcasting it is best to
use an example, the following network uses broadcasting in the ``transformix`` Node:

.. image:: images/network_multi_atlas.*

As you can see this visualization prints the dimensions for each Input and Output (e.g. the ``elastix.fixed_image``
Input has dimensions ``[N]``). To explain what happens in more detail, we present an image illustrating the
details for the samples in ``elastix`` and ``transformix``:

.. image:: images/flow/flow_broadcast.*

In the figure the ``moving_image`` (and references to it) are identified with different colors, so they are easy to
track across the different steps.

At the top the Inputs for the ``elastix`` Node are illustrated. Because the input groups a set differently, output
samples are generated for all combinations of ``fixed_image`` and ``moving_image`` (see :ref:`advanced-flow-node` for
details).

In the ``transformix`` Node, we want to combine a list of samples that is related to the ``moving_image`` (it has the
same dimension name and sizes) with the resulting ``transform`` samples from the ``elastix`` Node. As you can see the
sizes of the sample collections do not match (``[N]`` vs ``[N x M]``). This is where *broadcasting* comes into play, it
allows the system to match these related sample collections. Because all the dimensions in ``[N]`` are known in
``[N x M]``, it is possible to match them uniquely. This is done automatically and the result is a new ``[N xM]`` sample
collection. To create a matching sample collections, the samples in the ``transformix.image`` Input are reused as
indicated by the colors.


.. warning:: Note that this might fail when there are data-blocks with non-unique dimension names, as it will be not
             be clear which of the dimensions with identical names should be matched!

DataTypes
---------

In Fastr all data is contained in object of a specific type. The types in Fastr are represented by classes that subclass :py:class:`BaseDataType <fastr.datatypes.BaseDataType>`. There are a few different other classes under :py:class:`BaseDataType <fastr.datatypes.BaseDataType>` that are each a base class for a family of types:

* :py:class:`DataType <fastr.datatypes.DataType>` -- The base class for all types that hold data

  * :py:class:`ValueType <fastr.datatypes.ValueType>` -- The base class for types that contain simple data (e.g. Int, String) that can be represented as a str
  * :py:class:`EnumType <fastr.datatypes.EnumType>` -- The base class for all types that are a choice from a :class:`set` of options
  * :py:class:`URLType <fastr.datatypes.URLType>` -- The base class for all types that have their data stored in files (which are referenced by URL)

* :py:class:`TypeGroup <fastr.datatypes.TypeGroup>` -- The base class for all types that actually represent a group of types

.. figure:: images/datatype_diagram.*

   The relation between the different DataType classes

The types are defined in xml files and created by the :py:class:`DataTypeManager <fastr.core.datatypemanager.DataTypeManager>`.
The :py:class:`DataTypeManager <fastr.core.datatypemanager.DataTypeManager>` acts as a container containing all Fastr types.
It is automatically instantiated as ``fastr.typelist``.
In fastr the created DataTypes classes are also automatically place in the :py:mod:`fastr.datatypes` module once created.

Resolving Datatypes
~~~~~~~~~~~~~~~~~~~
:py:class:`Outputs <fastr.core.inputoutput.Output>` in fastr can have a :py:class:`TypeGroup <fastr.datatypes.TypeGroup>` or a number of :py:class:`DataTypes <fastr.datatypes.DataType>` associated with them. The final :py:class:`DataType <fastr.datatypes.DataType>` used will
depend on the linked :py:class:`Inputs <fastr.core.inputoutput.Input>`. The :py:class:`DataType <fastr.datatypes.DataType>` resolving works as a two-step procedure.

1. All possible :py:class:`DataTypes <fastr.datatypes.DataType>` are determined and considered as *options*.
2. The best possible :py:class:`DataType <fastr.datatypes.DataType>` from *options* is selected for non-automatic Outputs

The *options* are defined as the intersection of the set of possible values for the :py:class:`Output <fastr.core.inputoutput.Output>` and each separate :py:class:`Input <fastr.core.inputoutput.Input>`
connected to the :py:class:`Output <fastr.core.inputoutput.Output>`. Given the resulting *options* there are three scenarios:

* If there are no valid :py:class:`DataTypes <fastr.datatypes.DataType>` (*options* is empty) the result will be None.
* If there is a single valid :py:class:`DataType <fastr.datatypes.DataType>`, then this is automatically the result (even if it is not a preferred :py:class:`DataType <fastr.datatypes.DataType>`).
* If there are multiple valid :py:class:`DataTypes <fastr.datatypes.DataType>`, then the preferred :py:class:`DataTypes <fastr.datatypes.DataType>` are used to resolve conflicts.

There are a number of places where the preferred :py:class:`DataTypes <fastr.datatypes.DataType>` can be set, these are used in the order as given:

1. The *preferred* keyword argument to :py:meth:`match_types <fastr.core.datatypemanager.DataTypeManager.match_types>`
2. The preferred types specified in the :ref:`fastr.config <config-file>`

.. _manual_execution:

Execution
---------

Executing a Network is very simple:

.. code-block:: python

    >>> source_data = {'source_id1': ['val1', 'val2'],
                       'source_id2': {'id3': 'val3', 'id4': 'val4'}}
    >>> sink_data = {'sink_id1': 'vfs://some_output_location/{sample_id}/file.txt'}
    >>> network.execute(source_data, sink_data)

The :py:meth:`Network.execute <fastr.core.network.Network.execute>` method takes a :class:`dict` of source data
and a :class:`dict` sink data as arguments. The dictionaries should have a key for each
:py:class:`SourceNode <fastr.core.node.SourceNode>` or :py:class:`SinkNode <fastr.core.node.SinkNode>`.

TODO: add ``.. figure:: images/execution_layers.*``

The execution of a Network uses a layered model:

* :py:meth:`Network.execute <fastr.core.network.Network.execute>` will analyze the Network and call all Nodes.
* :py:meth:`Node.execute <fastr.core.node.Node.execute>` will create jobs and fill their payload
* :py:func:`execute_job <fastr.execution.executionscript.execute_job>` will execute the job on the execute machine
  and resolve any deferred values (``val://`` urls).
* :py:meth:`Tool.execute <fastr.core.tool.Tool.execute>` will find the correct target and call the interface and if
  required resolve ``vfs://`` urls
* :py:meth:`Interface.execute <fastr.core.interface.Interface.execute>` will actually run the required command(s)

The :py:class:`ExecutionPlugin <fastr.execution.executionpluginmanager.ExecutionPlugin>` will call call
the :py:mod:`executionscript.py <fastr.execution.executionscript>` for each job, passing the job as a
gzipped pickle file. The :py:mod:`executionscript.py <fastr.execution.executionscript>` will resolve deferred values and
then call :py:meth:`Tool.execute <fastr.core.tool.Tool.execute>` which analyses the required target and executes the
underlying :py:class:`Interface <fastr.core.interface.Interface>`. The Interface actually executes the job and collect
the results. The result is returned (via the Tool) to the :py:mod:`executionscript.py <fastr.execution.executionscript>`.
There we save the result, provenance and profiling in a new gzipped pickle file. The execution system will use a
callback to load the data back into the Network.

The selection and settings of the :py:class:`ExecutionPlugin <fastr.execution.executionpluginmanager.ExecutionPlugin>`
are defined in the :ref:`fastr config <config-file>`.

.. _continuing-network:

Continuing a Network
~~~~~~~~~~~~~~~~~~~~

Normally a random temporary directory is created for each run. To continue a previously stopped/crashed network, you should call the :py:meth:`Network.execute <fastr.core.network.Network.execute>` method using the same temporary  directory(tmp dir). You can set the temporary directory to a fixed value using the following code:

.. code-block:: python

    >>> tmpdir = '/tmp/example_network_rerun'
    >>> network.execute(source_data, sink_data, tmpdir=tmpdir)

.. warning:: Be aware that at this moment, Fastr will rerun only the jobs where not all output files are present or if the job/tool parameters have been changed. It will not rerun if the input data of the node has changed or the actual tools have been adjusted. In these cases you should remove the output files of these nodes, to force a rerun.


IOPlugins
---------

Sources and sink are used to get data in and out of a :py:class:`Network <fastr.core.network.Network>` during execution.
To make the data retrieval and storage easier, a plugin system was created that selects different plugins based on the
URL scheme used. So for example, a url starting with ``vfs://`` will be handles by the
:py:class:`VirtualFileSystem plugin <fastr.core.vfs.VirtualFileSystem>`. A list of all the
:py:class:`IOPlugins <fastr.core.ioplugin.IOPlugin>` known by the system and their use can
be found at :ref:`IOPlugin Reference <ioplugin-ref>`.

Secrets
---------
Fastr uses a secrets system for storing and retrieving login credentials. Currently the following keyrings are supported:

- Python keyring and keyrings.alt lib:
  - Mac OS X Keychain
  - Freedesktop Secret Service (requires secretstorage)
  - KWallet (requires dbus)
  - Windows Credential Vault
  - Gnome Keyring
  - Google Keyring (stores keyring on Google Docs)
  - Windows Crypto API (File-based keyring secured by Windows Crypto API)
  - Windows Registry Keyring (registry-based keyring secured by Windows Crypto API)
  - PyCrypto File Keyring
  - Plaintext File Keyring (not recommended)
- Netrc (not recommended)

When a password is retrieved trough the fastr SecretService it loops trough all of the available SecretProviders (currently keyring and netrc) until a match is found.

The Python keyring library automatically picks the best available keyring backend. If you wish to choose your own python keyring backend it is possible to do so by make a keyring configuration file according to the keyring library documentation. The python keyring library connects to one keyring. Currently it cannot loop trough all available keyrings until a match is found.

Debugging
---------

This section is about debugging Fastr tools wrappers, Fastr Networks (when building a Network) and Fastr Network Runs.

Debugging a Fastr tool
~~~~~~~~~~~~~~~~~~~~~~

When wrapping a Tool in Fastr sometimes it will not work as expected or not load properly.
Fastr is shipped with a command that helps checking Tools. The :ref:`fastr verify <cmdline-verify>` command
can try to load a Tool in steps to make it more easy to understand where the loading went wrong.

The ``fastr verify`` command will use the following steps:

* Try to load the tool with and without compression
* Try to find the correct serializer and make sure the format is correct
* Try to validate the Tool content against the json_schema of a proper Tool
* Try to create a Tool object
* If available, execute the tool test

An example of the use of ``fastr verify``::

    $ fastr verify tool fastr/resources/tools/fastr/math/0.1/add.xml
    [INFO]    verify:0020 >> Trying to read file with compression OFF
    [INFO]    verify:0036 >> Read data from file successfully
    [INFO]    verify:0040 >> Trying to load file using serializer "xml"
    [INFO]    verify:0070 >> Validating data against Tool schema
    [INFO]    verify:0080 >> Instantiating Tool object
    [INFO]    verify:0088 >> Loaded tool <Tool: Add version: 1.0> successfully
    [INFO]    verify:0090 >> Testing tool...

If your Tool is loading but not functioning as expected you might want to easily test your
Tool without building an entire Network around it that can obscure errors. It is possible
to run a tool from the Python prompt directly using :py:meth:`tool.execute <fastr.core.tool.Tool.execute>`::

    >>> tool.execute(left_hand=40, right_hand=2)
    [INFO] localbinarytarget:0090 >> Changing ./bin
    [INFO]      tool:0311 >> Target is <Plugin: LocalBinaryTarget>
    [INFO]      tool:0318 >> Using payload: {'inputs': {'right_hand': (2,), 'left_hand': (40,)}, 'outputs': {}}
    [INFO] localbinarytarget:0135 >> Adding extra PATH: ['/home/hachterberg/dev/fastr-develop/fastr/fastr/resources/tools/fastr/math/0.1/bin']
    [INFO] fastrinterface:0393 >> Execution payload: {'inputs': {'right_hand': (2,), 'left_hand': (40,)}, 'outputs': {}}
    [INFO] fastrinterface:0496 >> Adding (40,) to argument list based on <fastrinterface.InputParameterDescription object at 0x7fc950fa8850>
    [INFO] fastrinterface:0496 >> Adding (2,) to argument list based on <fastrinterface.InputParameterDescription object at 0x7fc950fa87d0>
    [INFO] localbinarytarget:0287 >> Options: ['/home/hachterberg/dev/fastr-develop/fastr/fastr/resources/tools/fastr/math/0.1/bin']
    [INFO] localbinarytarget:0201 >> Calling command arguments: ['python', '/home/hachterberg/dev/fastr-develop/fastr/fastr/resources/tools/fastr/math/0.1/bin/addint.py', '--in1', '40', '--in2', '2']
    [INFO] localbinarytarget:0205 >> Calling command: "'python' '/home/hachterberg/dev/fastr-develop/fastr/fastr/resources/tools/fastr/math/0.1/bin/addint.py' '--in1' '40' '--in2' '2'"
    [INFO] fastrinterface:0400 >> Collecting results
    [INFO] executionpluginmanager:0467 >> Callback processing thread ended!
    [INFO] executionpluginmanager:0467 >> Callback processing thread ended!
    [INFO] executionpluginmanager:0467 >> Callback processing thread ended!
    [INFO] jsoncollector:0076 >> Setting data for result with [42]
    <fastr.core.interface.InterfaceResult at 0x7fc9661ccfd0>



In this case an AddInt was ran from the python shell. As you can see it shows the payload it created based on the call, followed by
the options for the directories that contain the binary. Then the command that is called is given both as a list and
string (for easy copying to the prompt yourself). Finally the collected results is displayed.

.. note::

    You can give input and outputs as keyword arguments for execute. If an input and output have the same name,
    you can disambiguate them by prefixing them with ``in_`` or ``out_`` (e.g. ``in_image`` and ``out_image``)

Debugging an invalid Network
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The simplest command to check if your Network is considered valid is to use the
:py:meth:`Network.is_valid <fastr.core.network.Network.is_valid>` method. It will
simply check if the Network is valid::

    >>> network.is_valid()
    True

It will return a boolean that only indicates the validity of the Network, but it
will print any errors it found to the console/log with the ERROR log level, for
example when datatypes on a link do not match::

    >>> invalid_network.is_valid()
    [WARNING] datatypemanager:0388 >> No matching DataType available (args (<ValueType: Float class [Loaded]>, <ValueType: Int class [Loaded]>))
    [WARNING]      link:0546 >> Cannot match datatypes <ValueType: Float class [Loaded]> and <ValueType: Int class [Loaded]> or not preferred datatype is set! Abort linking fastr:///networks/add_ints/0.0/nodelist/source/outputs/output to fastr:///networks/add_ints/0.0/nodelist/add/inputs/left_hand!
    [WARNING] datatypemanager:0388 >> No matching DataType available (args (<ValueType: Float class [Loaded]>, <ValueType: Int class [Loaded]>))
    [ERROR]   network:0571 >> [add] Input left_hand is not valid: SubInput fastr:///networks/add_ints/0.0/nodelist/add/inputs/left_hand/0 is not valid: SubInput source (link_0) is not valid
    [ERROR]   network:0571 >> [add] Input left_hand is not valid: SubInput fastr:///networks/add_ints/0.0/nodelist/add/inputs/left_hand/0 is not valid: [link_0] source and target have non-matching datatypes: source Float and Int
    [ERROR]   network:0571 >> [link_0] source and target have non-matching datatypes: source Float and Int
    False

Because the messages might not always be enough to understand errors in the more
complex Networks, we would advice you to create a plot of the network using the
:py:meth:`network.draw_network <fastr.core.network.Network.draw_network>` method::

    >>> network.draw_network(network.id, draw_dimensions=True, expand_macro=True)
    'add_ints.svg'

The value returned is the path of the output image generated (it will be placed in
the current working directory. The ``draw_dimensions=True`` will make the drawing add
indications about the sample dimensions in each Input and Output, whereas
``expand_macro=True`` causes the draw to expand MacroNodes and draw the content of them.
If you have many nested MacroNodes, you can set ``expand_macro`` to an integer and that
is the depth until which the MacroNodes will be draw in detail.

An example of a simple multi-atlas segmentation Network nicely shows the use of drawing the
dimensions, the dimensions vary in certain Nodes due to the use of input_groups and a collapsing
link (drawn in blue):

.. image:: images/network_multi_atlas.*


Debugging a Network run with errors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If a Network run did finish but there were errors detected, Fastr will report those
at the end of the execution. We included an example of a Network that has failing
samples in ``fastr/examples/failing_network.py`` which can be used to test debugging.
An example of the output of a Network run with failures::

    [INFO] networkrun:0604 >> ####################################
    [INFO] networkrun:0605 >> #    network execution FINISHED    #
    [INFO] networkrun:0606 >> ####################################
    [INFO] networkrun:0618 >> ===== RESULTS =====
    [INFO] networkrun:0627 >> sink_1: 2 success / 2 failed
    [INFO] networkrun:0627 >> sink_2: 2 success / 2 failed
    [INFO] networkrun:0627 >> sink_3: 1 success / 3 failed
    [INFO] networkrun:0627 >> sink_4: 1 success / 3 failed
    [INFO] networkrun:0627 >> sink_5: 1 success / 3 failed
    [INFO] networkrun:0628 >> ===================
    [WARNING] networkrun:0651 >> There were failed samples in the run, to start debugging you can run:

        fastr trace $RUNDIR/__sink_data__.json --sinks

    see the debug section in the manual at https://fastr.readthedocs.io/en/default/static/user_manual.html#debugging for more information.

As you can see, there were failed samples in every sink. Also you already get the suggestion
to use :ref:`fastr trace <cmdline-trace>`. This command helps you inspect the staging directory of the Network run
and pinpoint the errors.

The suggested command will print a similar summary as given by the network execution::

    $ fastr trace $RUNDIR/__sink_data__.json --sinks
    sink_1 -- 2 failed -- 2 succeeded
    sink_2 -- 2 failed -- 2 succeeded
    sink_3 -- 3 failed -- 1 succeeded
    sink_4 -- 3 failed -- 1 succeeded
    sink_5 -- 3 failed -- 1 succeeded

Since this is not given us new information we can add the ``-v`` flag for more output and limit the output to one sink,
in this case ``sink_5``::

    $ fastr trace $RUNDIR/__sink_data__.json --sinks sink_5
    sink_5 -- 3 failed -- 1 succeeded
      sample_1_1: Encountered error: [FastrOutputValidationError] Could not find result for output out_2 (/home/hachterberg/dev/fastr-develop/fastr/fastr/execution/job.py:970)
      sample_1_2: Encountered error: [FastrOutputValidationError] Could not find result for output out_1 (/home/hachterberg/dev/fastr-develop/fastr/fastr/execution/job.py:970)
      sample_1_3: Encountered error: [FastrOutputValidationError] Could not find result for output out_1 (/home/hachterberg/dev/fastr-develop/fastr/fastr/execution/job.py:970)
      sample_1_3: Encountered error: [FastrOutputValidationError] Could not find result for output out_2 (/home/hachterberg/dev/fastr-develop/fastr/fastr/execution/job.py:970)

Now we are given one error per sample, but this does not yet give us that much information. To get a very detailed
report we have to specify one sink and one sample. This will make the ``fastr trace`` command print a complete error
report for that sample::

    $ fastr trace $RUNDIR/__sink_data__.json --sinks sink_5 --sample sample_1_1 -v
    Tracing errors for sample sample_1_1 from sink sink_5
    Located result pickle: /home/hachterberg/FastrTemp/fastr_failing_network_2017-09-04T10-44-58_uMWeMV/step_1/sample_1_1/__fastr_result__.pickle.gz


    ===== JOB failing_network___step_1___sample_1_1 =====
    Network: failing_network
    Run: failing_network_2017-09-04T10-44-58
    Node: step_1
    Sample index: (1)
    Sample id: sample_1_1
    Status: JobState.execution_failed
    Timestamp: 2017-09-04 08:45:19.238192
    Job file: /home/hachterberg/FastrTemp/fastr_failing_network_2017-09-04T10-44-58_uMWeMV/step_1/sample_1_1/__fastr_result__.pickle.gz

    Command:
    List representation: [u'python', u'/home/hachterberg/dev/fastr-develop/fastr/fastr/resources/tools/fastr/util/0.1/bin/fail.py', u'--in_1', u'1', u'--in_2', u'1', u'--fail_2']
    String representation: 'python' '/home/hachterberg/dev/fastr-develop/fastr/fastr/resources/tools/fastr/util/0.1/bin/fail.py' '--in_1' '1' '--in_2' '1' '--fail_2'

    Output data:
    {'out_1': [<Int: 2>]}

    Status history:
    2017-09-04 08:45:19.238212: JobState.created
    2017-09-04 08:45:21.537417: JobState.running
    2017-09-04 08:45:31.578864: JobState.execution_failed

    ----- ERRORS -----
    - FastrOutputValidationError: Could not find result for output out_2 (/home/hachterberg/dev/fastr-develop/fastr/fastr/execution/job.py:970)
    - FastrValueError: [failing_network___step_1___sample_1_1] Output values are not valid! (/home/hachterberg/dev/fastr-develop/fastr/fastr/execution/job.py:747)
    ------------------

    ----- STDOUT -----
    Namespace(fail_1=False, fail_2=True, in_1=1, in_2=1)
    in 1  : 1
    in 2  : 1
    fail_1: False
    fail_2: True
    RESULT_1=[2]

    ------------------

    ----- STDERR -----

    ------------------

As shown above, it finds the result files of the failed job(s) and prints the most important information. The first
paragraph shows the information about the Job that was involved. The second paragraph shows the command used both as a
list (which is clearer and internally used in Python) and as a string (which you can copy/paste to the shell to test
the command). Then there is the output data as determined by Fastr. The next section shows the status history of the
Job which can give an indication about wait and run times. Then there are the errors that Fastr encounted during the
execution of the Job. In this case it could not find the output for the Tool. Finally the stdout and stderr of the
subprocess are printed. In this case we can see that RESULT_2=[...] was not in the stdout, and so the result could
not be located.

.. note::

    Sometimes there are no Job results in a directory, this usually means the process got killed before the Job could
    finished. On cluster environments, this often means that the process was killed due to memory constraints.

Asking for help with debugging
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you would like help with debugging, you can contact us via the
`fastr-users google group <https://groups.google.com/forum/#!forum/fastr-users>`_.
To enable us to track the errors please include the following:

* The entire log of the fastr run (can be copied from console or from the end of ``~/.fastr/logs/info.log``.
* A dump of the network run, which can be created that by using the :ref:`fastr dump <cmdline-dump>`  command like::

    $ fastr dump $RUNDIR fastr_run_dump.zip

  This will create a zip file including all the job files, logs, etc but not
  the actual data files.

These should be enough information to trace most errors. In some cases we might need to ask for additional
information (e.g. tool files, datatype files) or actions from your side.


Naming Convention
-----------------

For the naming convention of the tools we tried to stay close to the Python :pep:`8` coding style. In short, we defined
toolnames as classes so they should be UpperCamelCased. The inputs and outputs of a tool we considered as functions or
method arguments, these should we named lower_case_with_underscores.

An overview of the mapping of Fastr to :pep:`8`:

=============== ================================================================= ===========================================
Fastr construct Python :pep:`PEP8 <8#prescriptive-naming-conventions>` equivalent Examples
=============== ================================================================= ===========================================
Network.id      :pep:`module <8#package-and-module-names>`                        brain_tissue_segmentation
Tool.id         :pep:`class <8#class-names>`                                      BrainExtractionTool, ThresholdImage
Node.id         :pep:`variable name <8#global-variable-names>`                    brain_extraction, threshold_mask
Input/Output.id :pep:`method <8#method-names-and-instance-variables>`             image, number_of_classes, probability_image
=============== ================================================================= ===========================================

Furthermore there are some small guidelines:

 * No input or output in the input or output names. This is already specified when setting or getting the data.
 * Add the type of the output that is named. i.e. enum, string, flag, image,

    * No File in the input/output name (Passing files around is what Fastr was developed for).
    * No type necessary where type is implied i.e. lower_threshold, number_of_levels, max_threads.

 * Where possible/useful use the fullname instead of an abbreviation.


Provenance
----------

For every data derived data object, Fastr records the `Provenance <https://en.wikipedia.org/wiki/Provenance>`_. The :py:class:`SinkNode <fastr.core.node.SinkNode>` write provenance records next to every data object it writes out. The records contain information on what operations were performed to obtain the resulting data object.

W3C Prov
~~~~~~~~

The provenance is recorded using the `W3C Prov Data Model (PROV-DM) <https://www.w3.org/TR/2013/REC-prov-dm-20130430/>`_. Behind the scences we are using the python `prov <https://github.com/trungdong/prov>`_ implementation.

The PROV-DM defines 3 Starting Point Classes and and their relating properties. See :numref:`provo` for a graphic representation of the classes and the relations.

.. _provo:

.. figure:: images/provo.svg
  :width: 600px
  :figclass: align-center

  The three Starting Point classes and the properties that relate them. The diagrams in this document depict Entities as yellow ovals, Activities as blue rectangles, and Agents as orange pentagons. The responsibility properties are shown in pink. [*]_


Implementation
~~~~~~~~~~~~~~

In the workflow document the provenance classes map to fastr concepts in the following way:

:Agent: Fastr, :ref:`Networks <network>`, :ref:`Tools <tools>`, :ref:`Nodes <node>`
:Activity: :py:class:`Jobs <fastr.execution.job.Job>`
:Entities: Data


Usage
~~~~~
The provenance is stored in ProvDocument objects in pickles. The convenience command line tool ``fastr prov`` can be used to extract the provenance in the `PROV-N <http://www.w3.org/TR/prov-n/>`_ notation and can be serialized to `PROV-JSON <http://www.w3.org/Submission/prov-json/>`_ and `PROV-XML <http://www.w3.org/TR/prov-xml/>`_. The provenance document can also be vizualized using the ``fastr prov`` command line tool.




.. rubric:: Footnotes

.. [*] This picture and caption is taken from http://www.w3.org/TR/prov-o/ . "Copyright © 2011-2013 World Wide Web Consortium, (MIT, ERCIM, Keio, Beihang). http://www.w3.org/Consortium/Legal/2015/doc-license"
