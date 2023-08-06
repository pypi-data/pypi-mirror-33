""" Base class definition """
import tensorflow as tf
from contextlib import contextmanager
from dxpy.core.path import Path
from dxpy.collections.dicts import DXDict
from typing import Dict

# On restrict mode, tensors as allocated to CPU memory if not specified.
RESTRICT_MODE = True


class GraphsManager:
    _graphs = dict()

    @classmethod
    def get_graph(cls, name):
        return cls._graphs.get(name)

    # @classmethod
    # def get_name(cls, name):
    #     import re
    #     while name in _graphs:
    #         base = name.name
    #         p = re.compile("(\w+)_(\d+)")
    #         mat = p.match(base)
    #         if mat:
    #             prefix = mat[1]
    #             gid = mat[2]
    #             base = "{}_{}".format(prefix, gid + 1)
    #         else:
    #             base = base + '_1'
    #         return name.father_path / base

    @classmethod
    def register(cls, graph):
        if graph.name in cls._graphs:
            raise ValueError(
                "Graph with name {} already registed".format(str(graph.name)))


class NodeKeys:
    """
    Pre-defined frequently used keys
    """
    EVALUATE = 'evaluate'
    INFERENCE = 'inference'
    TRAINER = 'trainer'
    SAVER = 'saver'
    LOSS = 'loss'
    MAIN = 'main'
    INPUT = 'input'
    LABEL = 'label'
    OUTPUT = 'output'
    MAIN_MODEL = 'main_model'
    CHILD_MODEL = 'child_model'
    TASK = 'task'


class Graph:
    """
    Base class of components.

    A `Graph` is an dict like collections of nodes and edges. Nodes of `Graph` can be a tensor another sub `Graph`.
    Edges representing relations of sub graphs/tensors, flow of information.

    A `Graph` is an generalization of `tf.Graph`, which is designed for following features:
        1. An unified interface of `tf.Graph` and general compute graph or operations/procedures;
        2. Seperate config and implementation, use TreeDict for configs, and supports multiple ways of config;
        3. An easy-to-use way of seperate/reuse subgraphs;
        4. Supports an warp of sessions.run/normal python function.
            Please add member method for tasks, and register them to tasks

    Config module:
    Configs module is designed to support externel hierachy configs, thus with name of graph,
    graph can load/search configs. This is designed to reduce complecity of config complex networks.
    To achieve this, use more configurable than directly pass arguments to init functions.
    For sub-models, in most cases do not pass arguments by its parent graph, directly use config system.
    There are some exceptions to this design, for some simple/frequently used blocks, some simple arguments
    may be passed to simplify config procedure. Another simulation is the case with lots of child models and
    they all share simple but same configurations, you may pass the shared arguments by its parent Graph.

    In most cases, Graph should communicate(connect) with others via dict of Tensors/Graph.


    Methods:

    -   as_tensor(self):
        return self.nodes['main'], which is designed for sub_graphs.

    -   get_feed_dict(self, task=None):
        A method which returns a feed_dict, which can be used to update parent (in most cases, the graph which called 
        subgraph.get_feed_dict()) graph's get_feed_dict() or run task.
        Which is used to garantee output nodes (if is Tensor) to be valid under certain tasks, if task is None,
        a feed_dict should be provided so that all nodes are valid.

    -   run(self, task_name, feeds):
        Call a registered function. # TODO: make it different from directly call function, provide default feeds / unified feeds, etc.

    Properties:
        name: Path, name is used for:
            1. loading configs from global config object;
            2. its basename sometimes used for namescope/variable name in TensorFlow;
    """

    def __init__(self, name, **config):
        self.name = Path(name)
        self.c = self.__load_config(config)
        self.nodes = dict()
        self.tasks = dict()

    # Methods to be overrided:
    @classmethod
    def _default_config(cls):
        """ Override this method to provide default configs. """
        return dict()

    def __hash__(self):
        return self.name.__hash__()

    def keys(self):
        return self.nodes.keys()

    def values(self):
        return self.nodes.values()

    def items(self):
        return self.nodes.items()

    def __iter__(self):
        return self.nodes.__iter__()

    def _externel_feeds(self):
        return dict()

    def get_feed_dict(self, feeds=None, task=None):
        """
        Return feed dict for this graph to work for specific tasks.

        In most cases, it works as an translator for feeds to feed_dict,
        thus replacing name of feeds to tf.Tensor.
        """
        from dxpy.collections.dicts import combine_dicts
        result = self._externel_feeds()
        if feeds is None:
            return result
        for n in self.nodes:
            if n in feeds:
                result[self.tensor(n)] = feeds[n]
            if self.nodes[n] in feeds:
                result[self.tensor(n)] = feeds[self.nodes[n]]
        return result

    def _print_config_kernel(self, recursive, indent, fout):
        title = "{ind}>{cls}:{name}({fullname})".format(ind=" " * indent,
                                                        cls=__class__,
                                                        name=self.parse_name())
        indent_sub = indent + 4
        for k in self.nodes:
            if isinstance(self.nodes[k], tf.Tensor):
                print('{ind}tf.Tensor:{name}({sp})'.format(ind=" " * indent_sub,
                                                           name=k, sp=self.nodes[k].shape), file=fout)
            elif isinstance(self.nodes[k], Graph):
                if recursive:
                    self.nodes[k].print_config(recursive, fout, indent_sub)
                else:
                    print('{ind}Graph:{name}({sub_name})'.format(ind=" " * indent_sub,
                                                                 name=k, sub_name=self.nodes[k].name), file=fout)

    @property
    def basename(self):
        """
        Get the base name of graph name. Useful for variable_scope or name_scope of graph.
        """
        return self.name.basename

    def register_node(self, name=None, tensor_or_subgraph=None):
        from .utils import refined_tensor_or_graph_name
        if tensor_or_subgraph is None:
            tensor_or_subgraph = name
            name = refined_tensor_or_graph_name(tensor_or_subgraph)
        self.nodes[name] = tensor_or_subgraph

    def register_task(self, name, func):
        self.tasks[name] = func

    def register_main_node(self, tensor_or_subgraph):
        self.register_node(NodeKeys.MAIN, tensor_or_subgraph)

    def register_main_task(self, func):
        self.register_task(NodeKeys.MAIN, func)

    def create_variable_node(self, dtype, shape, name, *, trainable=False, init_value=None):
        if init_value is not None:
            initer = tf.constant_initializer(init_value)
        else:
            initer = None
        self.register_node(name, tf.get_variable(
            name, shape, dtype, trainable=trainable, initializer=initer))
        return self.nodes[name]

    def create_placeholder_node(self, dtype, shape, name):
        self.register_node(name, tf.placeholder(dtype, shape, name))
        return self.nodes[name]

    def create_sub_graph_node(self, name, create_func):
        self.register_node(name, create_func())
        return self.nodes[name]

    def param(self, key, feeds=None, *,  default=None, raise_key_error=True):
        """
        Best practice: always use param instead of directly using self.c
        """
        if isinstance(feeds, dict) and key in feeds:
            return feeds[key]
        result = self.c.get(key, default)
        if result is None and raise_key_error:
            raise KeyError(key)
        return result

    def tensor(self, key=None):
        if key is None:
            return self.as_tensor()
        if not key in self.nodes:
            if isinstance(key, tf.Tensor):
                for n in self.nodes:
                    if self.nodes[n] == key:
                        return self.nodes[n]
        if isinstance(self.nodes[key], tf.Tensor):
            return self.nodes[key]
        elif isinstance(self.nodes[key], Graph):
            return self.nodes[key].as_tensor()
        raise KeyError("Key {} not found in graph {}.".format(key, self.name))

    def graph(self, key=None):
        if key is None:
            key = NodeKeys.MAIN
        if key in self.nodes:
            if isinstance(self.nodes[key], Graph):
                return self.nodes[key]
            else:
                raise TypeError("Type of  self.nodes[{}] of in graph {} is {}, required Graph.".format(
                    key, self.name, type(self.nodes[key])))
        raise KeyError("Key {} not found in graph {}.".format(key, self.name))

    def print_config(self, fout=None, recursive=False, indent=0):
        self._print_config_kernel(recursive, indent, fout)

    def __getitem__(self, name):
        if name in self.nodes:
            return self.nodes[name]
        elif name in self.tasks:
            return self.tasks[name]
        else:
            return None

    def __call__(self, feeds=None):
        return self.run(NodeKeys.MAIN, feeds)

    def run(self, task_name, feeds=None):
        return self.tasks[task_name](feeds)

    def as_tensor(self):
        return self.nodes.get(NodeKeys.MAIN)

    def __load_config(self, config_direct):
        from .config import config as config_global
        from dxpy.collections.dicts import combine_dicts
        return combine_dicts(config_direct, config_global, self._default_config())
