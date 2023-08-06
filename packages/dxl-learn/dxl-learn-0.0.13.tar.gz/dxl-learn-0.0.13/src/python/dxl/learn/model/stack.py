import tensorflow as tf
import numpy as np
from dxl.learn.core import Model
from dxl.learn.model.cnn import Conv2D, InceptionBlock

__all__ = [
    'Stack', 'StackV2'
]


class Stack(Model):
    class KEYS(Model.KEYS):
        class CONFIG(Model.KEYS.CONFIG):
            NB_LAYERS = 'nb_layers'

        class GRAPHS(Model.KEYS.GRAPH):
            MODELS = 'models'

    def __init__(self, info, inputs=None, models=None, nb_layers=None):
        super().__init__(
            info,
            tensors={self.KEYS.TENSOR.INPUT: inputs},
            graphs={self.KEYS.GRAPHS.MODELS: models},
            config={self.KEYS.CONFIG.NB_LAYERS: nb_layers}
        )

    @classmethod
    def _default_config(cls):
        return {cls.KEYS.CONFIG.NB_LAYERS: 2}

    def kernel(self, inputs):
        # x = inputs[self.KEYS.TENSOR.INPUT]
        # for _ in range(self.config(self.KEYS.CONFIG.NB_LAYERS)):
        nb_layers = self.config(self.KEYS.CONFIG.NB_LAYERS)
        if nb_layers is None:
            nb_layers = len(self.graphs)
        for i in range(nb_layers):
            x = self.graphs[self.KEYS.GRAPHS.MODELS][i](inputs)
        return x


from typing import List, Union
from dxl.data.function import Function


class StackV2(Model):
    def __init__(self, models: List[Union[Model, Function]], info='stack'):
        super().__init__(info, graphs=models)
        self.models = models

    def kernel(self, inputs):
        x = inputs
        for m in self.models:
            x = m(x)
        return x
