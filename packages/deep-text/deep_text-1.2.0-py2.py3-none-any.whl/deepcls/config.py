# -*- coding=utf-8 -*-
from common.config import BaseConfig


class TextCNNConfig(BaseConfig):
    def __init__(self, json_str, train_input_path, test_input_path=None):
        super(TextCNNConfig, self).__init__(json_str, train_input_path, test_input_path)

        self.embedding_size = self._config_object.get("embedding_size", 100)
        self.sequence_length = self._config_object.get("sequence_length", 50)
        self.num_filters = self._config_object.get("num_filters", 128)
        self.filter_sizes = self._config_object.get("filter_sizes", [3, 4, 5])
        self.label_prefix = self._config_object.get("label_prefix", "__label__")

        self.input_keep_prob = self._config_object.get("input_keep_prob", 0.8)
        self.output_keep_prob = self._config_object.get("output_keep_prob", 0.5)

        self.show()


class TextRNNConfig(BaseConfig):
    def __init__(self, json_str, train_input_path, test_input_path=None):
        super(TextRNNConfig, self).__init__(json_str, train_input_path, test_input_path)

        self.embedding_size = self._config_object.get("embedding_size", 100)
        self.sequence_length = self._config_object.get("sequence_length", 50)
        self.attention_dim = self._config_object.get("attention_dim", 32)
        self.label_prefix = self._config_object.get("label_prefix", "__label__")

        self.input_keep_prob = self._config_object.get("input_keep_prob", 0.8)
        self.output_keep_prob = self._config_object.get("output_keep_prob", 0.5)

        self.hidden_size = self._config_object.get("hidden_size", 20)
        self.hidden_layer_num = self._config_object.get("hidden_layer_num", 2)

        self.show()

