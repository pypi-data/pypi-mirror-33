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

        cpu_count = multiprocessing.cpu_count()

        # config for word2vec
        self.w2v_alpha = self._config_object.get("w2v_alpha", 0.025)
        self.w2v_window = self._config_object.get("w2v_window", 5)
        self.w2v_min_count = self._config_object.get("w2v_min_count", 3)
        self.w2v_sample = self._config_object.get("w2v_sample", 0.001)
        self.w2v_workers = self._config_object.get("w2v_workers", cpu_count)
        self.w2v_negative = self._config_object.get("w2v_negative", 5)
        self.w2v_iter_times = self._config_object.get("w2v_iter_times", 5)

        # batch config
        self.batch_queue_thread = self._config_object.get("batch_queue_thread", cpu_count)
        self.batch_queue_capacity = self._config_object.get("batch_queue_capacity", 500000)
        self.batch_min_after_dequeue = self._config_object.get("batch_min_after_dequeue", 100000)

