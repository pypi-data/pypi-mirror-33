# -*- coding=utf-8 -*-
import os
from abc import abstractmethod

import numpy as np
import tensorflow as tf
from gensim.models import word2vec
from common.transform import Transform
import logging


class CLSTransform(Transform):
    def __init__(self, config, temp_dir="runs", corpus_iter=None):
        super(CLSTransform, self).__init__(config, temp_dir, corpus_iter)

        self.label_path = self.data_path + "/labels.txt"

        self.label2id = {}
        self.id2label = {}
        self.label_queue = None
        self.doc_queue = None
        self.test_label_data = np.array([])
        self.test_doc_data = np.array([])
        self.class_num = 0

    @abstractmethod
    def transform_docs(self, docs):
        pass

    def transform_labels(self, index):
        label_ids = []
        for ins in index:
            labels = []
            for i in ins:
                labels.append(self.id2label[i])
            label_ids.append(labels)
        return label_ids

    def load_custom_data(self):
        if os.path.exists(self.label_path):
            count = 0
            with open(self.label_path) as fp:
                for line in fp:
                    line = line.strip()
                    self.id2label[count] = line
                    self.label2id[line] = count
                    count += 1
            self.class_num = count

    @abstractmethod
    def parse_line(self, line):
        pass


class DeepCLSTransform(CLSTransform):
    def __init__(self, config, temp_dir="runs", corpus_iter=None):
        super(DeepCLSTransform, self).__init__(config, temp_dir, corpus_iter)

    def transform_docs(self, docs):
        doc_ids = []
        for doc in docs:
            ids = np.array([self.w2id.get(word, 0) for word in doc])
            doc_ids.append(self.pad(ids, self.config.sequence_length, 0))
        return np.array(doc_ids)

    def transform_impl(self):
        logging.info("Build tfrecord file...")

        writer = tf.python_io.TFRecordWriter(self.tfrecord_path)
        word_count = 1
        label_count = 0

        vocab_fp = open(self.vocab_path, "w")
        label_fp = open(self.label_path, "w")

        w2v_model = word2vec.Word2Vec.load(self.w2v_model_path)
        w2v_size = w2v_model.layer1_size

        counter = 0
        vecs = [0.0] * w2v_size
        with open(self.train_input_path, "r") as fp:
            for line in fp:
                try:
                    ws, ls = self.parse_line(line.strip())
                except Exception as e:
                    logging.error("Parse line error! error: {} line: {}", (e, line))
                    continue

                counter += 1
                if counter % 10000 == 0:
                    logging.info("Transform %d" % counter)

                if len(ls) != 1:
                    continue

                for w in ws:
                    if w not in self.w2id:
                        self.w2id[w] = word_count
                        self.id2w[word_count] = w

                        v = self.get_word2vec(w2v_model, w)
                        vecs.extend(v)

                        word_count += 1
                        vocab_fp.write(w + "\n")

                if ls[0] not in self.label2id:
                    self.label2id[ls[0]] = label_count
                    self.id2label[label_count] = ls[0]
                    label_count += 1
                    label_fp.write(ls[0] + "\n")

                label = self.label2id[ls[0]]
                words = [self.w2id[w] for w in ws]
                example = tf.train.Example(features=tf.train.Features(feature={
                    'label': tf.train.Feature(int64_list=tf.train.Int64List(value=[label])),
                    'doc': tf.train.Feature(int64_list=tf.train.Int64List(value=words)),
                }))
                writer.write(example.SerializeToString())

        self.vocab_size = word_count
        self.class_num = label_count
        self.word_vector = np.array(vecs).reshape([word_count, w2v_size])
        np.save(self.word_vector_path, self.word_vector)

        vocab_fp.flush()
        vocab_fp.close()
        label_fp.flush()
        label_fp.close()
        writer.flush()
        writer.close()

        if os.path.exists(self.tfrecord_path):
            self.load_tfrecords_data()

        if os.path.exists(self.test_input_path):
            self.load_test_data()

    def load_tfrecords_data(self):
        logging.info("Load tfrecord data %s", self.tfrecord_path)
        filename_queue = tf.train.string_input_producer([self.tfrecord_path], num_epochs=self.config.epoch)
        reader = tf.TFRecordReader()
        _, serialized_example = reader.read(filename_queue)
        features = tf.parse_single_example(
            serialized_example,
            features={
                'label': tf.FixedLenFeature([], tf.int64),
                'doc': tf.VarLenFeature(tf.int64)
            })

        label = features['label']
        doc = features['doc']

        label_q, doc_q = tf.train.shuffle_batch([label, doc], batch_size=self.config.batch_size,
                                                capacity=self.config.batch_queue_capacity,
                                                num_threads=self.config.batch_queue_thread,
                                                min_after_dequeue=self.config.batch_min_after_dequeue)
        self.label_queue = label_q
        self.doc_queue = doc_q

    def load_test_data(self):
        with open(self.test_input_path, "r", errors="ignore") as fp:
            logging.info("Load test data %s" % self.test_input_path)
            wss = []
            lss = []
            for line in fp:
                try:
                    ws, ls = self.parse_line(line)
                except Exception as e:
                    logging.error("Parse line error! error: {} line: {}", (e, line))
                    continue
                if ws is None or len(ws) == 0:
                    continue
                if 0 < self.config.sequence_length < len(ws):
                    ws = ws[:self.config.sequence_length]
                wss.append(ws)
                lss.append(ls[0])

            test_data_labels = []
            test_data_docs = []
            for ws, l in zip(wss, lss):
                pos = self.label2id[l]
                label = [0] * self.class_num
                label[pos] = 1

                words = [self.w2id.get(w, 0) for w in ws]
                words = self.pad(words, self.config.sequence_length, 0)

                test_data_labels.append(label)
                test_data_docs.append(words)

            self.test_label_data = np.array(test_data_labels)
            self.test_doc_data = np.array(test_data_docs)
            logging.info("Load test data, size %d" % (self.test_label_data.shape[0]))

    def pull_batch(self, sess):
        _labels, _doc_sparse = sess.run([self.label_queue, self.doc_queue])
        _docs = self.sparse_to_dense(_doc_sparse.indices, _doc_sparse.dense_shape, _doc_sparse.values, -1)

        labels = []
        docs = []
        for i in range(self.config.batch_size):
            pos = _labels[i]
            label = [.0] * self.class_num
            label[pos] = 1.
            labels.append(label)
            docs.append(self.pad(_docs[i], self.config.sequence_length, 0))

        return {"doc_batch": np.array(docs), "label_batch": np.array(labels)}

    def get_test_data(self):
        return {"doc_batch": self.test_doc_data, "label_batch": self.test_label_data}

