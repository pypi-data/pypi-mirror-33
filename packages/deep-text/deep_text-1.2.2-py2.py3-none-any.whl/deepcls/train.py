# -*- coding=utf-8 -*-

from common.train import Trainer
from deepcls.textrnn import BiAttGRU
from .textcnn import TextCNN
import logging


class TextCNNTrainer(Trainer):
    def __init__(self, config, _transform_class, need_transform=False, rebuild_word2vec=False,
                 restore_model=False, optimizer=None):
        super(TextCNNTrainer, self).__init__(config, _transform_class, TextCNN,
                                             need_transform, rebuild_word2vec,
                                             restore_model, optimizer)

    def train_step(self, batch_data):
        feed_dict = {
            self.model.input: batch_data["doc_batch"],
            self.model.target: batch_data["label_batch"],
            self.model.input_keep_prob: self.config.input_keep_prob,
            self.model.output_keep_prob: self.config.output_keep_prob,
            self.model.batch_size: self.config.batch_size
        }

        _, step, summaries, loss, acc = self.session.run(self.train_ops, feed_dict)

        logging.info("step {}, loss {:g}, acc {:g}".format(step, loss, acc))
        self.train_summary_writer.add_summary(summaries, step)

    def dev_step(self, batch_data):
        feed_dict = {
            self.model.input: batch_data["doc_batch"],
            self.model.target: batch_data["label_batch"],
            self.model.input_keep_prob: 1.,
            self.model.output_keep_prob: 1.,
            self.model.batch_size: batch_data["label_batch"].shape[0]
        }

        step, summaries, loss, acc = self.session.run(self.dev_ops, feed_dict)

        logging.info("step {}, loss {:g}, acc {:g}".format(step, loss, acc))
        self.dev_summary_writer.add_summary(summaries, step)


class TextRNNTrainer(Trainer):
    def __init__(self, config, _transform_class, need_transform=False, rebuild_word2vec=False,
                 restore_model=False, optimizer=None):
        super(TextRNNTrainer, self).__init__(config, _transform_class, BiAttGRU,
                                             need_transform, rebuild_word2vec,
                                             restore_model, optimizer)

    def train_step(self, batch_data):
        feed_dict = {
            self.model.input: batch_data["doc_batch"],
            self.model.target: batch_data["label_batch"],
            self.model.input_keep_prob: self.config.input_keep_prob,
            self.model.output_keep_prob: self.config.output_keep_prob,
        }

        _, step, summaries, loss, acc = self.session.run(self.train_ops, feed_dict)

        logging.info("step {}, loss {:g}, acc {:g}".format(step, loss, acc))
        self.train_summary_writer.add_summary(summaries, step)

    def dev_step(self, batch_data):
        feed_dict = {
            self.model.input: batch_data["doc_batch"],
            self.model.target: batch_data["label_batch"],
            self.model.input_keep_prob: 1.,
            self.model.output_keep_prob: 1.,
        }

        step, summaries, loss, acc = self.session.run(self.dev_ops, feed_dict)

        logging.info("step {}, loss {:g}, acc {:g}".format(step, loss, acc))
        self.dev_summary_writer.add_summary(summaries, step)

