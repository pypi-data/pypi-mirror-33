# -*- coding=utf-8 -*-
from common import utils
from common import config_ops
from .train import TextCNNTrainer
from .train import TextRNNTrainer
from .default_custom import DefaultCLSTransform
import tensorflow as tf
import sys
import getopt


def main_learn():
    train_input_path = ""
    test_input_path = ""
    config_file_path = ""
    model_save_path = ""
    need_transform = False
    need_build_word2vec = False
    try:
        model_type = sys.argv[1]
        opts, args = getopt.getopt(sys.argv[2:], "ht:e:c:m:fw",
                                   ["train=", "test=", "config=", "model="])
    except getopt.getopt.GetoptError:
        print('deepcls_learn [cnn|rnn] -t <trainfile> -e <testfile> -c <configfile> -m <model save path> '
              '[-f <do transform> -w <build word2vec>]')
        sys.exit(2)
        
    if len(opts) == 0:
        print('deepcls_learn [cnn|rnn] -t <trainfile> -e <testfile> -c <configfile> -m <model save path> '
              '[-f <do transform> -w <build word2vec>]')
        sys.exit()
        
    for opt, arg in opts:
        if opt == '-h':
            print('deepcls_learn [cnn|rnn] -t <trainfile> -e <testfile> -c <configfile> -m <model save path> '
                  '[-f <do transform> -w <build word2vec>]')
            sys.exit()
        elif opt in ("-t", "--train"):
            train_input_path = arg
        elif opt in ("-e", "--test"):
            test_input_path = arg
        elif opt in ("-c", "--config"):
            config_file_path = arg
        elif opt in ("-m", "--model"):
            model_save_path = arg
        elif opt == "-f":
            need_transform = True
        elif opt == "-w":
            need_build_word2vec = True

    if train_input_path == "":
        print("Please input -t or --train to set train_input_path.")
        sys.exit()
         
    if test_input_path == "":
        print("Please input -e or --test to set test_input_path.")
        sys.exit()
        
    if config_file_path == "":
        print("Please input -c or --config to set config_file_path.")
        sys.exit()
            
    if model_save_path == "":
        print("Please input -m or --model to set model_save_path.")
        sys.exit()

    if model_type == "cnn":
        config = config_ops.load_deep_cls_cnn_config(config_file_path, train_input_path, test_input_path)
        trainer = TextCNNTrainer(config, DefaultCLSTransform, need_transform, need_build_word2vec)
        model = trainer.train()
    elif model_type == "rnn":
        config = config_ops.load_deep_cls_rnn_config(config_file_path, train_input_path, test_input_path)
        trainer = TextRNNTrainer(config, DefaultCLSTransform, need_transform, need_build_word2vec)
        model = trainer.train()
    else:
        print('The model type must be \'cnn\' or \'rnn\'')
        sys.exit()

    model.save(model_save_path)


def main_save():
    checkpoint_path = ""
    model_save_path = ""
    config_file_path = ""
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hc:p:m:", ["checkpoint=", "model="])
    except getopt.getopt.GetoptError:
        print('deepcls_save -c <checkpoint path> -m <model file path>')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('deepcls_save -c <checkpoint path> -m <model file path>')
            sys.exit()
        elif opt in ("-p", "--checkpoint"):
            checkpoint_path = arg
        elif opt in ("-m", "--model"):
            model_save_path = arg
        elif opt in ("-c", "--config"):
            config_file_path = arg

    if checkpoint_path == "":
        print("Please input -p or --checkpoint to set checkpoint_path.")
        sys.exit()

    if model_save_path == "":
        print("Please input -m or --model to set model_save_path.")
        sys.exit()

    if config_file_path == "":
        print("Please input -c or --config to set config_file_path.")
        sys.exit()

    config = config_ops.load_deep_crf_config(config_file_path)

    checkpoint_file = tf.train.latest_checkpoint(checkpoint_path)
    sess = utils.load_session(checkpoint_file, config)

    scopes = ["accuracy/predict"]
    graph = tf.graph_util.convert_variables_to_constants(sess, sess.graph_def, scopes)
    with tf.gfile.GFile(model_save_path+".pb", "wb") as f:
        f.write(graph.SerializeToString())

