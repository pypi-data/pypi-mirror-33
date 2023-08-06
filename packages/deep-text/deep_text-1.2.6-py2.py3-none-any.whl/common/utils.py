# -*- coding:utf-8 -*-
from abc import abstractmethod
import tensorflow as tf


class CorpusIterator(object):
    def __init__(self, files):
        self.files = files

    def __iter__(self):
        for fn in self.files:
            with open(fn, "r", errors="ignore") as fp:
                for line in fp:
                    rets = self.analysis_line(line) 
                    if rets is not None and len(rets) > 0:
                        yield rets

    @abstractmethod
    def analysis_line(self, line):
        pass


def tf_version_uper_than(version):
    tf_vps = [p for p in tf.__version__.split(".")]
    vps = [p for p in version.split(".")]
    tf_vp = [int(tf_vps[0]), int(tf_vps[1])]
    vp = [int(vps[0]), int(vps[1])]
    if tf_vp[0] > vp[0]:
        return True
    elif tf_vp[0] == vp[0] and tf_vp[1] > vp[1]:
        return True
    return False


def load_graph_file(model_path):
    with tf.gfile.GFile(model_path, "rb") as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())
    with tf.Graph().as_default() as graph:
        tf.import_graph_def(graph_def, name = "")
    return graph


def load_session(sess_file, config):
    graph = tf.Graph()
    graph.as_default()
    session_conf = tf.ConfigProto(
      allow_soft_placement=config.allow_soft_placement,
      log_device_placement=config.log_device_placement)
    sess = tf.Session(config=session_conf)
    sess.as_default()
    saver = tf.train.import_meta_graph("{}.meta".format(sess_file))
    saver.restore(sess, sess_file)
    return sess


def copy_file(src, dst):
    fp = open(src, "r")
    buff = fp.read()
    fp.close()

    fp = open(dst, "w")
    fp.write(buff)
    fp.flush()
    fp.close()

