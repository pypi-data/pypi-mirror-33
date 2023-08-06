import tensorflow as tf
import logging
from common.model import BaseModel
from tensorflow.contrib.tensorboard.plugins import projector


class BiAttGRU(BaseModel):
    def __init__(self, session, transformer, config):
        super(BiAttGRU, self).__init__(session, transformer, config)

        self.input = tf.placeholder(tf.int32, [None, self.config.sequence_length], name="input")
        self.target = tf.placeholder(tf.int32, [None, self.transformer.class_num], name="target")
        self.input_keep_prob = tf.placeholder(tf.float32, name="input_keep_prob")
        self.output_keep_prob = tf.placeholder(tf.float32, name="output_keep_prob")

        def gru_cell():
            gru = tf.contrib.rnn.GRUCell(self.config.hidden_size)
            gru = tf.contrib.rnn.DropoutWrapper(cell=gru, input_keep_prob=self.input_keep_prob,
                                                output_keep_prob=self.output_keep_prob)
            return gru

        # embedding layer
        with tf.device('/cpu:0'), tf.name_scope("embedding"):
            if self.config.use_w2v_embedding:
                logging.info("Init embedding with word vector. (%d,%d)",
                             transformer.word_vector.shape[0], transformer.word_vector.shape[1])
                embedding_initializer = tf.constant_initializer(transformer.word_vector)
            else:
                logging.info("Init embedding with xavier initializer.")
                embedding_initializer = tf.contrib.layers.xavier_initializer()
            self._W = tf.get_variable("W", shape=[transformer.vocab_size, config.embedding_size],
                                      initializer=embedding_initializer,
                                      dtype=tf.float32)
            embedded = tf.nn.embedding_lookup(self._W, self.input)
            # shape: (batch_size, seq_length, cell.input_size) => (seq_length, batch_size, cell.input_size)
            inputs = tf.split(embedded, self.config.sequence_length, 1)
            inputs = [tf.squeeze(input_, [1]) for input_ in inputs]

        fw_cell = tf.contrib.rnn.MultiRNNCell([gru_cell() for _ in range(self.config.hidden_layer_num)], state_is_tuple=True)
        bw_cell = tf.contrib.rnn.MultiRNNCell([gru_cell() for _ in range(self.config.hidden_layer_num)], state_is_tuple=True)

        outputs, _, _ = tf.contrib.rnn.static_bidirectional_rnn(fw_cell, bw_cell, inputs, dtype=tf.float32, scope='rnn_layer')

        attention_outputs = self.attention(outputs, self.config.attention_dim)

        with tf.variable_scope('softmax_layer'):
            softmax_w = tf.get_variable('w', [self.config.hidden_size * 2, self.transformer.class_num])
            softmax_b = tf.get_variable('b', [self.transformer.class_num])
            logits = tf.matmul(attention_outputs, softmax_w) + softmax_b
            self.probs = tf.nn.softmax(logits, name="probs")

        with tf.name_scope("loss"):
            cross_entropy_loss = tf.nn.softmax_cross_entropy_with_logits(logits=logits + 1e-10, labels=self.target)
            self.loss = tf.reduce_mean(cross_entropy_loss)

        with tf.name_scope("accuracy"):
            self.prediction = tf.argmax(self.probs, 1, name="predict")
            correct_prediction = tf.equal(self.prediction, tf.argmax(self.target, 1))
            self.correct_num = tf.reduce_sum(tf.cast(correct_prediction, tf.float32))
            self.accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32), name="accuracy")

    def attention(self, inputs, attention_size):
        """
        Attention mechanism layer.
        :param inputs: outputs of RNN/Bi-RNN layer (not final state)
        :param attention_size: linear size of attention weights
        :return: outputs of the passed RNN/Bi-RNN reduced with attention vector
        """
        # In case of Bi-RNN input we need to concatenate outputs of its forward and backward parts
        if isinstance(inputs, tuple):
            inputs = tf.concat(inputs, 2)

        inputs = tf.transpose(inputs, [1, 0, 2])

        sequence_length = inputs.get_shape()[1].value  # the length of sequences processed in the antecedent RNN layer
        hidden_size = inputs.get_shape()[2].value  # hidden size of the RNN layer

        # Attention mechanism
        W_omega = tf.get_variable("W_omega", initializer=tf.random_normal([hidden_size, attention_size], stddev=0.1))
        b_omega = tf.get_variable("b_omega", initializer=tf.random_normal([attention_size], stddev=0.1))
        u_omega = tf.get_variable("u_omega", initializer=tf.random_normal([attention_size], stddev=0.1))

        v = tf.tanh(tf.matmul(tf.reshape(inputs, [-1, hidden_size]), W_omega) + tf.reshape(b_omega, [1, -1]))
        vu = tf.matmul(v, tf.reshape(u_omega, [-1, 1]))
        exps = tf.reshape(tf.exp(vu), [-1, sequence_length])
        alphas = tf.div(exps, tf.reshape(tf.reduce_sum(exps, 1), [-1, 1]), name="alphas")

        # Output of Bi-RNN is reduced with attention vector
        output = tf.reduce_sum(inputs * tf.reshape(alphas, [-1, sequence_length, 1]), 1, name="attention_outputs")

        return output

    def apply_embedding_visuel(self, summary_writer):
        config = projector.ProjectorConfig()
        embedding = config.embeddings.add()
        embedding.tensor_name = self._W.name
        embedding.metadata_path = 'embedding.csv'
        projector.visualize_embeddings(summary_writer, config)

    def save(self, output_path):
        scopes = ["accuracy/predict"]
        graph = tf.graph_util.convert_variables_to_constants(self.session, self.session.graph_def, scopes)
        with tf.gfile.GFile(output_path, "wb") as f:
            f.write(graph.SerializeToString())

