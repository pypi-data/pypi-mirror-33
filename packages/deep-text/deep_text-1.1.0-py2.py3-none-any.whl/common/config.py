# -*- coding=utf-8 -*-
import json
import multiprocessing


class Config(object):
    def __init__(self, json_str):
        self._config_object = json.loads(json_str)

    def show(self):
        for attr, value in sorted(self.__dict__.items()):
            if attr == "_config_object":
                continue
            print("{}={}".format(attr.upper(), value))
        print("")

    def dump(self, path):
        obj = {}
        for attr, value in sorted(self.__dict__.items()):
            if attr == "_config_object" or attr == "test_input_path" or attr == "train_input_path":
                continue
            obj[attr] = value
        json_str = json.dumps(obj, indent=4)
        with open(path, "w") as fp:
            fp.write(json_str)


class BaseConfig(Config):
    def __init__(self, json_str, train_input_path, test_input_path=None):
        super(BaseConfig, self).__init__(json_str)
        self.train_input_path = train_input_path
        self.test_input_path = test_input_path

        self.lr = self._config_object.get("lr", 0.0001)
        self.epoch = self._config_object.get("epoch", 5)
        self.batch_size = self._config_object.get("batch_size", 64)

        self.evaluate_every = self._config_object.get("evaluate_every", 1000)
        self.checkpoint_every = self._config_object.get("checkpoint_every", 1000)
        self.num_checkpoints = self._config_object.get("num_checkpoints", 5)

        self.allow_soft_placement = self._config_object.get("allow_soft_placement", True)
        self.log_device_placement = self._config_object.get("log_device_placement", False)

        # config for word2vec
        self.alpha = self._config_object.get("alpha", 0.025)
        self.window = self._config_object.get("window", 5)
        self.min_count = self._config_object.get("min_count", 3)
        self.sample = self._config_object.get("sample", 0.001)
        self.workers = self._config_object.get("workers", multiprocessing.cpu_count())
        self.negative = self._config_object.get("negative", 5)
        self.iter_times = self._config_object.get("iter_times", 5)

