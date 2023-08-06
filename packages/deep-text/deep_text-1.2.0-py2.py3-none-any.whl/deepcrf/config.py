# -*- coding=utf-8 -*-
from common.config import BaseConfig


class DeepCRFConfig(BaseConfig):
    def __init__(self, json_str, train_input_path, test_input_path=None):
        super(DeepCRFConfig, self).__init__(json_str, train_input_path, test_input_path)

        self.num_tags = self._config_object.get("num_tags", 4)
        self.embedding_size = self._config_object.get("embedding_size", 100)
        self.seq_cut_length = self._config_object.get("seq_cut_length", -1)

        self.input_keep_prob = self._config_object.get("input_keep_prob", 0.8)
        self.output_keep_prob = self._config_object.get("output_keep_prob", 0.5)

        self.hidden_size = self._config_object.get("hidden_size", 20)
        self.hidden_layer_num = self._config_object.get("hidden_layer_num", 1)

        self.show()

