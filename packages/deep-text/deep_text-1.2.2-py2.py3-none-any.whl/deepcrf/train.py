# -*- coding=utf-8 -*-

from common import utils
from common.train import Trainer
from .model import Bi_LSTM_CRF
import logging


class DeepCRFTrainer(Trainer):
    def __init__(self, config, _transform_class, need_transform=False, rebuild_word2vec=False,
                 restore_model=False, optimizer=None):
        super(DeepCRFTrainer, self).__init__(config, _transform_class, Bi_LSTM_CRF,
                                             need_transform, rebuild_word2vec,
                                             restore_model, optimizer)
        if not utils.tf_version_uper_than("1.3.0"):
            self.train_ops.append(self.model.logits)
            self.train_ops.append(self.model.transition_params)
            self.dev_ops.append(self.model.logits)
            self.dev_ops.append(self.model.transition_params)

    def train_step(self, batch_data):
        feed_dict = {
            self.model.input: batch_data["doc_batch"],
            self.model.labels: batch_data["label_batch"],
            self.model.sequence_lengths: batch_data["seq_lens"],
            self.model.input_keep_prob: self.config.input_keep_prob,
            self.model.output_keep_prob: self.config.output_keep_prob,
        }

        if utils.tf_version_uper_than("1.3.0"):
            _, step, summaries, loss, acc = self.session.run(self.train_ops, feed_dict)
        else:
            _, step, summaries, loss, logits, transition_params = \
                self.session.run(self.train_ops, feed_dict)
            acc = self.model.acc(logits, transition_params, batch_data["seq_lens"], batch_data["label_batch"])

        logging.info("step {}, loss {:g}, acc {:g}".format(step, loss, acc))
        self.train_summary_writer.add_summary(summaries, step)

    def dev_step(self, batch_data):
        feed_dict = {
            self.model.input: batch_data["doc_batch"],
            self.model.labels: batch_data["label_batch"],
            self.model.sequence_lengths: batch_data["seq_lens"],
            self.model.input_keep_prob: 1.,
            self.model.output_keep_prob: 1.,
        }

        if utils.tf_version_uper_than("1.3.0"):
            step, summaries, loss, acc = self.session.run(self.dev_ops, feed_dict)
        else:
            step, summaries, loss, logits, transition_params = \
                self.session.run(self.dev_ops, feed_dict)
            acc = self.model.acc(logits, transition_params, batch_data["seq_lens"], batch_data["label_batch"])

        logging.info("step {}, loss {:g}, acc {:g}".format(step, loss, acc))
        self.dev_summary_writer.add_summary(summaries, step)

