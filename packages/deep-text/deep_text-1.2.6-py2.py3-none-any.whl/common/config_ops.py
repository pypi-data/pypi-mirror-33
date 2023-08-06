from deepcls.config import TextCNNConfig
from deepcls.config import TextRNNConfig
from deepcrf.config import DeepCRFConfig


def load_deep_crf_config(path, train_input_path=None, test_input_path=None):
    with open(path, "r") as fp:
        json_str = fp.read()
        return DeepCRFConfig(json_str, train_input_path, test_input_path)


def load_deep_cls_cnn_config(path, train_input_path=None, test_input_path=None):
    with open(path, "r") as fp:
        json_str = fp.read()
        return TextCNNConfig(json_str, train_input_path, test_input_path)


def load_deep_cls_rnn_config(path, train_input_path=None, test_input_path=None):
    with open(path, "r") as fp:
        json_str = fp.read()
        return TextRNNConfig(json_str, train_input_path, test_input_path)
