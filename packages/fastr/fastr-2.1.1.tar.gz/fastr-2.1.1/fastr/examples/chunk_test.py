#!/usr/bin/env python

# Copyright 2011-2014 Biomedical Imaging Group Rotterdam, Departments of
# Medical Informatics and Radiology, Erasmus MC, Rotterdam, The Netherlands
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import fastr

IS_TEST = True


def create_network():
    network = fastr.Network('chunk_test')
    # create sources
    source_1 = network.create_source(fastr.typelist['Int'],
                                     id_='source_1')
    source_2 = network.create_source(fastr.typelist['Int'],
                                     id_='source_2')
    source_3 = network.create_source(fastr.typelist['Int'],
                                     id_='source_3')

    # create nodes
    range_node = network.create_node('Range', id_='range')
    sum_node = network.create_node('Sum', id_='sum')

    add_1 = network.create_node('AddInt', id_='step_1')
    add_2 = network.create_node('AddInt', id_='step_2')

    # Create sinks
    sink_1 = network.create_sink(fastr.typelist['Int'], id_='sink_1')
    sink_2 = network.create_sink(fastr.typelist['Int'], id_='sink_2')

    # create links
    range_node.inputs['value'] = source_1.output
    sum_node.inputs['values'] = range_node.outputs['result']

    add_1.inputs['left_hand'] = sum_node.outputs['result']
    add_1.inputs['right_hand'] = source_2.output

    add_2.inputs['left_hand'] = source_2.output
    add_2.inputs['right_hand'] = source_3.output

    sink_1.input = add_1.outputs['result']
    sink_2.input = add_2.outputs['result']

    # Check/Draw/execute network
    return network


def source_data(network):
    fastr.log.info('Creating source data for {}'.format(network.id))
    return {
        'source_1': {'sample_1': 'vfslist://example_data/add_ints/values'},
        'source_2': {'sample_1': 'vfslist://example_data/add_ints/values'},
        'source_3': {'sample_1': 'vfslist://example_data/add_ints/values'},
    }


def sink_data(network):
    fastr.log.info('Creating sink data for {}'.format(network.id))
    return {
        'sink_1': 'vfs://tmp/results/{}/sink_1_{{sample_id}}_{{cardinality}}{{ext}}'.format(network.id),
        'sink_2': 'vfs://tmp/results/{}/sink_2_{{sample_id}}_{{cardinality}}{{ext}}'.format(network.id),
    }


def main():
    network = create_network()
    network.draw_network(name=network.id, draw_dimension=True)
    network.execute(source_data(network), sink_data(network))


if __name__ == '__main__':
    main()
