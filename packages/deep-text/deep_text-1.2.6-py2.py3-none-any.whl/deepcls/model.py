from abc import abstractmethod

import tensorflow as tf
from common import utils
import numpy as np
import logging
from common.model import BaseModel
from deepcls.default_custom import DefaultCLSTransform


class DeepCLSModel(BaseModel):
    def __init__(self, session, transformer, config):
        super(DeepCLSModel, self).__init__(session, transformer, config)
        self.input = None
        self.batch_size = None
        self.input_keep_prob = None
        self.output_keep_prob = None
        self.prediction = None
        self.probs = None

    @abstractmethod
    def predict(self, docs, top_n):
        pass

    def eval(self, line_iter):
        rets = []
        total = 0
        correct = 0
        for line in line_iter:
            ws, ls = self.transformer.parse_line(line)
            if len(ws) == 0:
                continue
            mws = [ws]
            pred_ret = self.predict(mws, 1)
            rets.append(pred_ret)
            for label, pred in zip(ls, pred_ret):
                ptags = [p[1] for p in pred]
                for to, tp in zip(tags, ptags):
                    total += 1
                    if to == tp:
                        correct += 1
        logging.info("[Eval] total: %d , correct: %d, accuracy: %f" % (total, correct, float(correct)/float(total)))
        return rets


class GraphTextCNNModel(DeepCLSModel):
    def __init__(self, model_path, config, TransformClass=None):
        if TransformClass is None:
            super(GraphTextCNNModel, self).__init__(tf.Session(graph=utils.load_graph_file(model_path)), DefaultCLSTransform(config), config)
        else:
            super(GraphTextCNNModel, self).__init__(tf.Session(graph=utils.load_graph_file(model_path)), TransformClass(config), config)
        self.transformer.load_pre_data()
        self.session.as_default()
        self.input = self.session.graph.get_tensor_by_name("input:0")
        self.input_keep_prob = self.session.graph.get_tensor_by_name("input_keep_prob:0")
        self.output_keep_prob = self.session.graph.get_tensor_by_name("output_keep_prob:0")
        self.prediction = self.session.graph.get_tensor_by_name("accuracy/predict:0")
        self.probs = self.session.graph.get_tensor_by_name("softmax_layer/probs:0")
        self.batch_size = self.session.graph.get_tensor_by_name("batch_size:0")

    def predict(self, docs, top_n):
        doc_ids = self.transformer.transform_docs(docs)
        feed_dict = {self.input: doc_ids,
                     self.input_keep_prob: 1.0,
                     self.output_keep_prob: 1.0,
                     self.batch_size: len(docs)}

        probs = self.session.run([self.probs], feed_dict=feed_dict)[0]
        index = np.argsort(-probs)[:, :top_n]
        labels = self.transformer.transform_labels(index)
        ret = []
        for prob, ins, lbs in zip(probs, index, labels):
            ret.append([(l, prob[i]) for i, l in zip(ins, lbs)])

        return ret
