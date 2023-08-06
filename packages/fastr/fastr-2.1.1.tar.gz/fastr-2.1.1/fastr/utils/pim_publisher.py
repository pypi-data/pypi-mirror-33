from abc import ABCMeta, abstractmethod
import getpass
import itertools
import json
import os

import requests
import fastr

from fastr.execution.job import JobState
from fastr.execution.sourcenoderun import SourceNodeRun, ConstantNodeRun
from fastr.execution.sinknoderun import SinkNodeRun


class BasePimAPI(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def pim_update_status(self, network, job):
        """
        Update the status of a job

        :param NetworkRun network: The network run the job belongs to
        :param Job job: The job which to update
        """

    @abstractmethod
    def pim_register_run(self, network):
        """
        Send the basic Network layout to PIM and register the run.

        :param NetworkRun network: The network run to register to PIM
        """


class PimAPI_v1(object):
    """
    Class to publish to PIM
    """
    PIM_STATUS_MAPPING = {
        JobState.nonexistent: 'unknown',
        JobState.created: 'idle',
        JobState.queued: 'idle',
        JobState.hold: 'idle',
        JobState.running: 'running',
        JobState.execution_done: 'running',
        JobState.execution_failed: 'running',
        JobState.processing_callback: 'running',
        JobState.finished: 'success',
        JobState.failed: 'failed',
        JobState.cancelled: 'failed',
    }

    def __init__(self, uri=None):
        self.pim_uri = uri
        self.registered = False
        self.run_id = None

        # Some data
        self.counter = itertools.count()
        self.scopes = {None: 'root'}
        self.nodes = {}

    def pim_update_status(self, network_run, job):
        if self.pim_uri is None:
            return

        if not self.registered:
            fastr.log.debug('Did not register a RUN with PIM yet! Cannot'
                            ' send status updates!')
            return

        node = network_run[job.node_global_id]

        # Create PIM job data
        pim_job_data = {
            "id": job.id,
            "node_id": self.nodes[node],
            "run_id": network_run.id,
            "sample_id": str(job.sample_id),
            "status": self.PIM_STATUS_MAPPING[job.status]
        }

        # Send the data to PIM
        fastr.log.debug('Updating PIM job status {} => {} ({})'.format(job.id,
                                                                       job.status,
                                                                       self.PIM_STATUS_MAPPING[job.status]))
        uri = '{pim}/api/runs/{run_id}/jobs/{job_id}'.format(pim=fastr.config.pim_host,
                                                             run_id=network_run.id,
                                                             job_id=job.id)

        fastr.log.debug('Send PUT to pim at {}:\n{}'.format(uri, pim_job_data))
        try:
            response = requests.put(uri, json=pim_job_data)
        except requests.ConnectionError as exception:
            fastr.log.error('Could no publish status to PIM, encountered exception: {}'.format(exception))

    def pim_serialize_network(self, network, scope=None, network_data=None):
        """
        Serialize Network in the correct for to use with PIM.

        :return: json data for PIM
        """
        node_classes = {
            'NodeRun': 'node',
            'SourceNodeRun': 'source',
            'ConstantNodeRun': 'constant',
            'SinkNodeRun': 'sink'
        }

        if network_data is None:
            network_data = {
                "description": network.description,
                "nodes": [],
                "links": [],
                "groups": [],
            }

        # Add the steps to the network
        for step in network.stepids.keys():
            group_id = '{}_{}'.format(next(self.counter), step)
            self.scopes['_'.join(x for x in [scope, step] if x)] = group_id

            group_data = {
                "id": group_id,
                "description": "undefined",
                "parent_group": self.scopes[scope]
            }

            network_data['groups'].append(group_data)

        # Add the nodes
        for node in network.nodelist.values():
            if type(node).__name__ == 'MacroNodeRun':
                # MacroNodes are a weird tool-less Node that will fail

                group_id = '{}_{}'.format(next(self.counter), node.id)
                new_scope = "{}_{}".format(scope, node.id) if scope else node.id
                self.scopes[new_scope] = group_id

                # Add a scope group for the new macro
                network_data['groups'].append(
                    {
                        "id": group_id,
                        "description": "undefined",
                        "parent_group": self.scopes[scope]
                    }
                )

                # Serialize the internal macro network
                self.pim_serialize_network(
                    node.network_run,
                    scope=new_scope,
                    network_data=network_data
                )
            else:
                node_class = node.__class__.__name__
                step = None
                for stepid, nodes in network.stepids.items():
                    if node in nodes:
                        step = stepid
                        break

                group_id = self.scopes['_'.join(x for x in [scope, step] if x) or None]
                node_id = "{}_{}".format(next(self.counter), node.id)
                self.nodes[node] = node_id

                node_data = {
                    "group_id": group_id,
                    "id": node_id,
                    "in_ports": [{'id': 'in_' + x.id, 'description': x.description} for x in node.tool.inputs.values()],
                    "out_ports": [{'id': 'out_' + x.id, 'description': x.description} for x in node.tool.outputs.values()],
                    "type": node_classes[node_class] if node_class in node_classes else 'node'
                }

                # Add special pass-through ports to source and sink if we are in a macro
                if scope and isinstance(node, SourceNodeRun) and not isinstance(node, ConstantNodeRun):
                    node_data['in_ports'].append({
                        "id": "in_source",
                        "description": "The feed of the source data to the internal macro network",
                    })

                if scope and isinstance(node, SinkNodeRun):
                    node_data['out_ports'].append({
                        "id": "out_sink",
                        "description": "The result sink data from the internal macro network to be transported back",
                    })

                network_data["nodes"].append(node_data)

        # Add the links
        for link in network.linklist.values():
            # If links go to/from macro network, set them to the source/sink inside instead
            if type(link.source.node).__name__ == 'MacroNodeRun':
                from_node = self.nodes[link.source.node.network_run.sinklist[link.source.id]]
                from_port = "out_sink"
            else:
                from_node = self.nodes[link.source.node]
                from_port = 'out_' + link.source.id

            if type(link.target.node).__name__ == 'MacroNodeRun':
                to_node = self.nodes[link.target.node.network_run.sourcelist[link.target.id]]
                to_port = 'in_source'
            else:
                to_node = self.nodes[link.target.node]
                to_port = 'in_' + link.target.id

            # Generate and save link data
            link_data = {
                "id": '{}_{}'.format(next(self.counter), link.id),
                "from_node": from_node,
                "from_port": from_port,
                "to_node": to_node,
                "to_port": to_port,
                "type": link.source.resulting_datatype.id
            }

            network_data["links"].append(link_data)

        return network_data

    def pim_register_run(self, network):
        if self.pim_uri is None:
            fastr.log.debug('No valid PIM uri known. Cannot register to PIM!')
            return

        self.run_id = network.id
        pim_run_data = {
            "collapse": False,
            "description": "Run of {} started at {}".format(network.id,
                                                            network.timestamp),
            "id": self.run_id,
            "network": self.pim_serialize_network(network),
            "workflow_engine": "fastr"
        }

        uri = '{pim}/api/runs/'.format(pim=fastr.config.pim_host)
        fastr.log.info('Registering {} with PIM at {}'.format(self.run_id, uri))

        fastr.log.debug('Send PUT to pim at {}:\n{}'.format(uri, json.dumps(pim_run_data, indent=2)))

        # Send out the response and record if we registered correctly
        try:
            response = requests.put(uri, json=pim_run_data)
            if response.status_code in [200, 201]:
                self.registered = True
                fastr.log.info('Run registered in PIM at {}/run/{}'.format(fastr.config.pim_host,
                                                                           self.run_id))
            else:
                fastr.log.warning('Could not register run at PIM, got a {} response'.format(response.status_code))
        except requests.ConnectionError as exception:
            fastr.log.error('Could no register network to PIM, encountered'
                            ' exception: {}'.format(exception))


class PimAPI_v2(object):
    """
    Class to publish to PIM
    """
    PIM_STATUS_MAPPING = {
        JobState.nonexistent: 5,
        JobState.created: 0,
        JobState.queued: 0,
        JobState.hold: 0,
        JobState.running: 1,
        JobState.execution_done: 1,
        JobState.execution_failed: 1,
        JobState.processing_callback: 1,
        JobState.finished: 2,
        JobState.failed: 3,
        JobState.cancelled: 4,
    }

    NODE_CLASSES = {
        'NodeRun': 'node',
        'SourceNodeRun': 'source',
        'ConstantNodeRun': 'constant',
        'SinkNodeRun': 'sink'
    }

    STATUS_TYPES = [
        {
            "color": "#aaccff",
            "description": "Jobs that are waiting for input",
            "title": "idle"
        },
        {
            "color": "#daa520",
            "description": "Jobs that are running",
            "title": "running"
        },
        {
            "color": "#23b22f",
            "description": "Jobs that finished successfully",
            "title": "success"
        },
        {
            "color": "#dd3311",
            "description": "Jobs that have failed",
            "title": "failed"
        },
        {
            "color": "#334477",
            "description": "Jobs which were cancelled",
            "title": "cancelled"
        },
        {
            "color": "#ccaa99",
            "description": "Jobs with an undefined state",
            "title": "undefined"
        }
    ]

    def __init__(self, uri=None):
        self.pim_uri = uri
        self.registered = False
        self.run_id = None

        # Some data
        self.counter = itertools.count()
        self.scopes = {None: 'root'}
        self.nodes = {}
        self.job_states = {}

    def pim_update_status(self, network_run, job):
        if self.pim_uri is None:
            return

        if not self.registered:
            fastr.log.debug('Did not register a RUN with PIM yet! Cannot'
                            ' send status updates!')
            return

        if job.status not in [
            JobState.created,
            JobState.running,
            JobState.finished,
            JobState.cancelled,
            JobState.failed,
        ]:
            return

        if job.id in self.job_states and self.job_states[job.id] == self.PIM_STATUS_MAPPING[job.status]:
            # Not a valid update
            fastr.log.debug('Ignoring non-PIM update')
            return
        else:
            self.job_states[job.id] = self.PIM_STATUS_MAPPING[job.status]

        try:
            node = self.nodes[job.node_global_id]
        except KeyError:
            fastr.log.info('NODES: {}'.format(self.nodes))
            raise

        # Create PIM job data
        pim_job_data = {
            "path": '{}/{}'.format(node, job.id),
            "title": "",
            "customData": {
                "sample_id": list(job.sample_id),
                "sample_index": list(job.sample_index),
                "errors": job.errors,
            },
            "status": self.PIM_STATUS_MAPPING[job.status],
            "description": "",
        }

        # Send the data to PIM
        fastr.log.debug('Updating PIM job status {} => {} ({})'.format(job.id,
                                                                       job.status,
                                                                       self.PIM_STATUS_MAPPING[job.status]))

        if job.status == JobState.failed and os.path.exists(job.extrainfofile):
            with open(job.extrainfofile) as extra_info_file:
                extra_info = json.load(extra_info_file)

                process = extra_info.get('process')

                if process:
                    # Process information
                    pim_job_data['customData']['stdout'] = process.get('stdout')
                    pim_job_data['customData']['stderr'] = process.get('stderr')
                    pim_job_data['customData']['command'] = process.get('command')
                    pim_job_data['customData']['returncode'] = process.get('returncode')
                    pim_job_data['customData']['time_elapsed'] = process.get('time_elapsed')

                # Host information
                pim_job_data['customData']['hostinfo'] = extra_info.get('hostinfo')

                # Input output hashes for validation of files
                pim_job_data['customData']['input_hash'] = extra_info.get('input_hash')
                pim_job_data['customData']['output_hash'] = extra_info.get('output_hash')

                # Tool information
                pim_job_data['customData']['tool_name'] = extra_info.get('tool_name')
                pim_job_data['customData']['tool_version'] = extra_info.get('tool_version')

        if job.status == JobState.created:
            uri = '{pim}/api/runs/{run_id}/jobs'.format(pim=fastr.config.pim_host,
                                                        run_id=network_run.id)
            try:
                response = requests.post(uri, json=[pim_job_data])
                if response.status_code >= 300:
                    fastr.log.info('Sent POST to pim at {}:\n{}'.format(uri, json.dumps(pim_job_data)))
                    fastr.log.warning('Response: [{r.status_code}] {r.text}'.format(r=response))
            except requests.ConnectionError as exception:
                fastr.log.error('Could no publish status to PIM, encountered exception: {}'.format(exception))
        else:
            uri = '{pim}/api/runs/{run_id}/job'.format(pim=fastr.config.pim_host,
                                                       run_id=network_run.id)
            try:
                response = requests.put(uri, json=pim_job_data)
                if response.status_code >= 300:
                    fastr.log.info('Sent PUT to pim at {}:\n{}'.format(uri, pim_job_data))
                    fastr.log.warning('Response: [{r.status_code}] {r.text}'.format(r=response))
            except requests.ConnectionError as exception:
                fastr.log.error('Could no publish status to PIM, encountered exception: {}'.format(exception))

    def pim_serialize_node(self, node, scope, links):
        # Fish out macros and use specialized function
        if type(node).__name__ == 'MacroNodeRun':
            return self.pim_serialize_macro(node, scope, links)

        node_data = {
            "name": node.id,
            "title": node.id,
            "children": [],
            "customData": {},
            "inPorts": [
                {
                    "name": output.id,
                    "title": output.id,
                    "customData": {
                        "input_group": output.input_group,
                        "datatype": output.datatype.id,
                        "dimension_names": [x.name for x in output.dimensions],
                    },
                } for output in node.inputs.values()
                ],
            "outPorts": [
                {
                    "name": output.id,
                    "title": output.id,
                    "customData": {
                        "datatype": output.resulting_datatype.id,
                        "dimension_names": [x.name for x in output.dimensions],
                    },
                } for output in node.outputs.values()
                ],
            "type": type(node).__name__,
        }

        if type(node).__name__ == 'SourceNodeRun':
            node_data['inPorts'].append(
                {
                    "name": 'input',
                    "title": 'input',
                    "customData": {
                        "datatype": node.output.datatype.id,
                        "dimension_names": [node.id],
                    },
                }
            )

        if type(node).__name__ == 'SinkNodeRun':
            node_data['outPorts'].append(
                {
                    "name": 'output',
                    "title": 'output',
                    "customData": {
                        "datatype": node.input.datatype.id,
                        "dimension_names": [x.name for x in node.dimnames],
                    },
                }
            )

        # Register node id mapping
        self.nodes[node.global_id] = '{}/{}'.format(scope, node.id)

        return node_data

    def pim_serialize_macro(self, node, scope, links):
        new_scope = '{}/{}'.format(scope, node.id)
        self.nodes[node.global_id] = new_scope

        # Set node data
        node_data = {
            "name": node.id,
            "title": node.id,
            "children": [],
            "customData": {},
            "inPorts": [],
            "outPorts": [],
            "type": type(node).__name__,
        }

        # Serialize underlying network
        self.pim_serialize_network(node.network_run, new_scope, node_data, links)

        return node_data

    def pim_serialize_network(self, network, scope, parent, links):
        visited_nodes = set()

        for step_name, step_nodes in network.stepids.items():
            step_data = {
                "name": step_name,
                "title": step_name,
                "children": [],
                "customData": {},
                "inPorts": [],
                "outPorts": [],
                "type": "NetworkStep",
            }

            parent['children'].append(step_data)

            # Serialize nodes to parents child list
            for node in step_nodes:
                step_data['children'].append(self.pim_serialize_node(node, '{}/{}'.format(scope, step_name), links))
                visited_nodes.add(node.id)

        # Serialize nodes to parents child list
        for node in network.nodelist.values():
            if node.id not in visited_nodes:
                parent['children'].append(self.pim_serialize_node(node, scope, links))

        # Serialize links to global link list
        for link in network.linklist.values():
            links.append(self.pim_serialize_link(link))

    def pim_serialize_link(self, link):
        if type(link.source.node).__name__ == 'MacroNodeRun':
            from_port = "{}/{}/output".format(self.nodes[link.source.node.global_id],
                                       link.source.id)
        else:
            from_port = "{}/{}".format(self.nodes[link.source.node.global_id],
                                       link.source.id)

        if type(link.target.node).__name__ == 'MacroNodeRun':
            to_port = "{}/{}/input".format(self.nodes[link.target.node.global_id],
                                     link.target.id)
        else:
            to_port = "{}/{}".format(self.nodes[link.target.node.global_id],
                                     link.target.id)

        link_data = {
            "customData": {
                "expand": link.expand,
                "collapse": link.collapse
            },
            "description": "",
            "fromPort": from_port,
            "name": link.id,
            "title": link.id,
            "toPort": to_port,
        }

        return link_data

    def pim_register_run(self, network):
        if self.pim_uri is None:
            fastr.log.warning('No valid PIM uri known. Cannot register to PIM!')
            return

        self.run_id = network.id
        pim_run_data = {
            "title": self.run_id,
            "name": self.run_id,
            "assignedTo": [],
            "user": getpass.getuser(),
            "root": {
                "name": "root",
                "title": network.network_id,
                "description": "",
                "children": [],
                "customData": {},
                "inPorts": [],
                "outPorts": [],
                "type": "NetworkRun",
            },
            "links": [],
            "description": "Run of {} started at {}".format(network.id,
                                                            network.timestamp),
            "customData": {
                "workflow_engine": "fastr",
                "tmpdir": network.tmpdir,
            },
            "statusTypes": self.STATUS_TYPES,
        }

        self.pim_serialize_network(network=network,
                                   scope="root",
                                   parent=pim_run_data["root"],
                                   links=pim_run_data["links"])

        uri = '{pim}/api/runs/'.format(pim=fastr.config.pim_host)
        fastr.log.info('Registering {} with PIM at {}'.format(self.run_id, uri))

        fastr.log.debug('Send PUT to pim at {}:\n{}'.format(uri, json.dumps(pim_run_data, indent=2)))

        # Send out the response and record if we registered correctly
        try:
            response = requests.post(uri, json=pim_run_data)
            if response.status_code in [200, 201]:
                self.registered = True
                fastr.log.info('Run registered in PIM at {}/runs/{}'.format(fastr.config.pim_host,
                                                                           self.run_id))
            else:
                fastr.log.warning('Could not register run at PIM, got a {} response'.format(response.status_code))
                fastr.log.warning('Response: {}'.format(response.text))
        except requests.ConnectionError as exception:
            fastr.log.error('Could no register network to PIM, encountered'
                            ' exception: {}'.format(exception))


class PimPublisher(object):
    SUPPORTED_APIS = {
        1: PimAPI_v1,
        2: PimAPI_v2,
    }

    def __init__(self, uri=None):
        # Parse URI
        if uri is None and fastr.config.pim_host == '':
            fastr.log.info("No valid PIM host given, PIM publishing will be disabled!")
            self.pim_uri = None
        else:
            self.pim_uri = uri or fastr.config.pim_host

        # Without a valid PIM URI, stop here
        if not self.pim_uri:
            self.api = None
            return

        try:
            response = requests.get('{pim}/api/info'.format(pim=self.pim_uri))
            if response.status_code >= 300:
                version = 1
            else:
                version = response.json().get('version', 1)
        except requests.ConnectionError as exception:
            fastr.log.error('Could no publish status to PIM, encountered exception: {}'.format(exception))
            return

        try:
            api_class = self.SUPPORTED_APIS[version]
            fastr.log.info('Using PIM API version {}'.format(version))
        except KeyError:
            fastr.log.error('PIM API version {} not supported!'.format(version))
            return

        self.api = api_class(self.pim_uri)

    def pim_update_status(self, network, job):
        if self.pim_uri and self.api:
            self.api.pim_update_status(network, job)

    def pim_register_run(self, network):
        if self.pim_uri and self.api:
            self.api.pim_register_run(network)
