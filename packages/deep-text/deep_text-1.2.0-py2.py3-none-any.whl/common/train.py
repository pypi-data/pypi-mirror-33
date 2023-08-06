# -*- coding=utf-8 -*-
from abc import abstractmethod

from . import utils
import tensorflow as tf
import os
import shutil
import logging


class Trainer(object):
    def __init__(self, config, _transform_class, _model_class, need_transform=False, rebuild_word2vec=False,
                 restore_model=False, optimizer=None, summaries=None):
        if summaries is None:
            summaries = ["loss", "accuracy"]
        self.restore_model = restore_model
        self.train_ops = []
        self.dev_ops = []
        self.config = config
        self.graph = tf.Graph()
        with self.graph.as_default():
            session_conf = tf.ConfigProto(
              allow_soft_placement=config.allow_soft_placement,
              log_device_placement=config.log_device_placement)
            session_conf.gpu_options.allow_growth = True
            self.session = tf.Session(config=session_conf, graph=self.graph)
            with self.session.as_default():
                self.transformer = _transform_class(config)
                if need_transform:
                    self.transformer.transform(rebuild_word2vec)
                else:
                    self.transformer.load()

                self.model = _model_class(self.session, self.transformer, self.config)

                self.global_step = tf.Variable(0, name="global_step", trainable=False)

                self.optimizer = optimizer
                if self.optimizer is None:
                    self.optimizer = tf.train.AdamOptimizer(config.lr)

                grads_and_vars = self.optimizer.compute_gradients(self.model.loss)
                train_op = self.optimizer.apply_gradients(grads_and_vars, global_step=self.global_step)
                self.train_ops.append(train_op)
                self.train_ops.append(self.global_step)
                self.dev_ops.append(self.global_step)

                grad_summaries = []
                for g, v in grads_and_vars:
                    if g is not None:
                        grad_hist_summary = tf.summary.histogram("{}/grad/hist".format(v.name.replace(":", "_")), g)
                        sparsity_summary = tf.summary.scalar("{}/grad/sparsity".format(v.name.replace(":", "_")), tf.nn.zero_fraction(g))
                        grad_summaries.append(grad_hist_summary)
                        grad_summaries.append(sparsity_summary)
                grad_summaries_merged = tf.summary.merge(grad_summaries)

                self.saver = tf.train.Saver(max_to_keep=config.num_checkpoints)

                # Summaries
                summary_scalars = []
                for summary in summaries:
                    if hasattr(self.model, summary):
                        summary_scalar = tf.summary.scalar(summary, getattr(self.model, summary))
                        summary_scalars.append(summary_scalar)

                dev_summary_op = tf.summary.merge(summary_scalars)
                summary_scalars.append(grad_summaries_merged)
                train_summary_op = tf.summary.merge(summary_scalars)
                self.train_ops.append(train_summary_op)
                self.dev_ops.append(dev_summary_op)

                for summary in summaries:
                    if hasattr(self.model, summary):
                        self.train_ops.append(getattr(self.model, summary))
                        self.dev_ops.append(getattr(self.model, summary))

                # Output directory for models and summaries
                out_dir = os.path.abspath(os.path.join(os.path.curdir, "runs"))
                checkpoint_dir = os.path.abspath(os.path.join(out_dir, "checkpoints"))
                ckpt = tf.train.get_checkpoint_state(checkpoint_dir)
                if restore_model:
                    init_op = tf.group(tf.global_variables_initializer(), tf.local_variables_initializer())
                    self.session.run(init_op)
                    self.saver.restore(self.session, ckpt.model_checkpoint_path)
                else:
                    if os.path.exists(out_dir + "/checkpoints"):
                        shutil.rmtree(out_dir + "/checkpoints")
                    if os.path.exists(out_dir + "/summaries"):
                        shutil.rmtree(out_dir + "/summaries")

                #Train Summaries
                train_summary_dir = os.path.join(out_dir, "summaries", "train")
                self.train_summary_writer = tf.summary.FileWriter(train_summary_dir, self.graph)

                # Dev summaries
                dev_summary_dir = os.path.join(out_dir, "summaries", "dev")
                self.dev_summary_writer = tf.summary.FileWriter(dev_summary_dir, self.graph)

                # Checkpoint directory. Tensorflow assumes this directory already exists so we need to create it
                self.checkpoint_prefix = os.path.join(checkpoint_dir, "model")
                if not os.path.exists(checkpoint_dir):
                    os.makedirs(checkpoint_dir)

                self.checkpoint_index_dev = os.path.join(out_dir, "summaries", "dev", "checkpoint")
                self.checkpoint_index = os.path.join(checkpoint_dir, "checkpoint")

                if not self.restore_model:
                    init_op = tf.group(tf.global_variables_initializer(), tf.local_variables_initializer())
                    self.session.run(init_op)

    def train(self):
        coord = tf.train.Coordinator()
        threads = tf.train.start_queue_runners(coord=coord, sess=self.session)
        try:
            while not coord.should_stop():
                data = self.transformer.pull_batch(self.session)
                self.train_step(data)
                current_step = tf.train.global_step(self.session, self.global_step)
                if current_step % self.config.evaluate_every == 0:
                    logging.info("\nEvaluation:")
                    self.dev_step(self.transformer.get_test_data())
                    logging.info("")
                if current_step % self.config.checkpoint_every == 0:
                    path = self.saver.save(self.session, self.checkpoint_prefix, global_step=current_step)
                    utils.copy_file(self.checkpoint_index, self.checkpoint_index_dev)
                    logging.info("Saved model checkpoint to {}\n".format(path))
        except tf.errors.OutOfRangeError:
            logging.info ('Done training -- epoch limit reached')

        coord.request_stop()
        coord.join(threads)
        return self.model

    @abstractmethod
    def train_step(self, batch_data):
        pass

    @abstractmethod
    def dev_step(self, batch_data):
        pass

