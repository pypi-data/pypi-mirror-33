# -*- coding=utf-8 -*-
import os
import shutil
from abc import abstractmethod

import numpy as np
from gensim.models import Word2Vec
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


class Transform(object):
    def __init__(self, config, temp_dir, corpus_iter):
        self.config = config
        self.train_input_path = config.train_input_path
        self.test_input_path = config.test_input_path
        self.temp_path = temp_dir
        self.data_path = self.temp_path + "/data"

        if not os.path.exists(self.temp_path):
            os.mkdir(self.temp_path)

        if not os.path.exists(self.data_path):
            os.mkdir(self.data_path)

        self.tfrecord_path = self.data_path + "/tfrecord.bin"

        # vocab
        self.id2w = {}
        self.w2id = {}
        self.vocab_path = self.data_path + "/vocab.txt"
        self.vocab_size = 0

        # word2vec
        self.word_vector = np.array([])
        self.word_vector_path = self.temp_path + "/word2vec/word_vector.npy"
        self.w2v_model_path = self.temp_path + "/word2vec/model.bin"
        self.corpus_iter = corpus_iter

    def build_word2vec(self):
        logging.info("Build word2vec...")
        model = Word2Vec(self.corpus_iter,
                         size=self.config.w2v_embedding_size,
                         alpha=self.config.w2v_alpha,
                         window=self.config.w2v_window,
                         min_count=self.config.w2v_min_count,
                         sample=self.config.w2v_sample,
                         workers=self.config.w2v_workers,
                         negative=self.config.w2v_negative,
                         iter=self.config.w2v_iter_times,
                         seed=3)

        model.save(self.w2v_model_path)

    def get_word2vec(self, w2v_model, word):
        w2v_model.init_sims()
        if word in w2v_model.wv.vocab:
            return w2v_model.wv.word_vec(word, use_norm=True)
        return np.array([0.0] * w2v_model.layer1_size)

    def sparse_to_dense(self,
                        sparse_indices,
                        output_shape,
                        sparse_values,
                        default_value=0):
        """
        sparse_indices: A 0-D, 1-D, or 2-D `Tensor` of type `int32` or `int64`.
          `sparse_indices[i]` contains the complete index where `sparse_values[i]`
          will be placed.
        output_shape: A 1-D `Tensor` of the same type as `sparse_indices`.  Shape
          of the dense output tensor.
        sparse_values: A 0-D or 1-D `Tensor`.  Values corresponding to each row of
          `sparse_indices`, or a scalar value to be used for all sparse indices.
        default_value: A 0-D `Tensor` of the same type as `sparse_values`.  Value
          to set for indices not specified in `sparse_indices`.  Defaults to zero.
        """

        arr = np.full(output_shape, default_value, dtype=np.int64)
        size = len(sparse_indices)
        for i in range(size):
            arr[sparse_indices[i][0]][sparse_indices[i][1]] = sparse_values[i]
        return arr

    def nparray_index(self, arr, ele=-1):
        for i in range(len(arr)):
            if arr[i] == ele:
                return i
        return len(arr) + 1

    def load_vocab(self):
        if not os.path.exists(self.vocab_path):
            return

        count = 1
        with open(self.vocab_path, 'r') as fp:
            for line in fp:
                line = line.strip()
                self.id2w[count] = line
                self.w2id[line] = count
                count += 1
        self.vocab_size = count
        logging.info("Load vocab, size %d" % (self.vocab_size))

    def pad(self, ndarr, pad_len, value=0):
        arr = ndarr[:self.nparray_index(ndarr)]
        fill_size = pad_len - len(arr)
        if fill_size > 0:
            pad_fill = [value] * fill_size
            return np.append(arr, pad_fill)
        elif fill_size < 0:
            return arr[:pad_len]
        else:
            return arr

    def clean_data(self):
        if os.path.exists(self.data_path):
            shutil.rmtree(self.data_path)
        os.mkdir(self.data_path)

    def load_pre_data(self):
        self.load_vocab()
        self.load_custom_data()

    def transform(self, rebuild_word2vec=False):
        logging.info("Transform data...")

        if self.corpus_iter is not None and (rebuild_word2vec or not os.path.exists(self.w2v_model_path)):
            if os.path.exists(self.temp_path + "/word2vec"):
                shutil.rmtree(self.temp_path + "/word2vec")
            os.mkdir(self.temp_path + "/word2vec")
            self.build_word2vec()

        self.transform_impl()

    def load(self):
        self.load_pre_data()

        if os.path.exists(self.word_vector_path):
            self.word_vector = np.load(self.word_vector_path)

        if os.path.exists(self.tfrecord_path):
            self.load_tfrecords_data()

        if os.path.exists(self.test_input_path):
            self.load_test_data()

    @abstractmethod
    def transform_impl(self):
        pass

    @abstractmethod
    def load_test_data(self):
        pass

    @abstractmethod
    def load_tfrecords_data(self):
        pass

    @abstractmethod
    def load_custom_data(self):
        pass

    @abstractmethod
    def pull_batch(self, sess):
        pass

    @abstractmethod
    def get_test_data(self):
        pass
