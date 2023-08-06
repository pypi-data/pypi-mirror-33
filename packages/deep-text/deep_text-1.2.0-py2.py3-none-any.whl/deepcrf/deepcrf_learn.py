# -*- coding=utf-8 -*-

from common import utils
from .train import DeepCRFTrainer
from .default_custom import DefaultTransform
import sys
import getopt


def main():
    train_input_path = ""
    test_input_path = ""
    config_file_path = ""
    model_save_path = ""
    need_transform = False
    need_build_word2vec = False
    try:
        opts, args = getopt.getopt(sys.argv[1:], "ht:e:c:m:fw",
                                   ["train=", "test=", "config=", "model="])
    except getopt.getopt.GetoptError:
        print('deepcrf_learn -t <trainfile> -e <testfile> -c <configfile> -m <model save path> '
              '[-f <do transform> -w <build word2vec>]')
        sys.exit(2)
        
    if len(opts) == 0:
        print('deepcrf_learn -t <trainfile> -e <testfile> -c <configfile> -m <model save path> '
              '[-f <do transform> -w <build word2vec>]')
        sys.exit()
        
    for opt, arg in opts:
        if opt == '-h':
            print('deepcrf_learn -t <trainfile> -e <testfile> -c <configfile> -m <model save path> '
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
            
    config = utils.load_deep_crf_config(config_file_path, train_input_path, test_input_path)

    trainer = DeepCRFTrainer(config, DefaultTransform, need_transform, need_build_word2vec)

    model = trainer.train()
    model.save(model_save_path)