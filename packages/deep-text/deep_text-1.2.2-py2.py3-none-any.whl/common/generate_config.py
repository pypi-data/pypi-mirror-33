from deepcrf.config import DeepCRFConfig
from deepcls.config import TextCNNConfig
from deepcls.config import TextRNNConfig
import sys
import getopt


def generate_config_file():
    model = ""
    path = ""
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hm:o:", ["model=", "output="])
    except getopt.getopt.GetoptError:
        print('deeptext_gen_config -m <deepcrf|cls-rnn|cls-cnn> -o <output path>')
        sys.exit(2)

    if len(opts) == 0:
        print('deeptext_gen_config -m <deepcrf|cls-rnn|cls-cnn> -o <output path>')
        sys.exit()

    for opt, arg in opts:
        if opt == '-h':
            print('deeptext_gen_config -m <deepcrf|cls-rnn|cls-cnn> -o <output path>')
            sys.exit()
        elif opt in ("-o", "--output"):
            path = arg
        elif opt in ("-m", "--model"):
            model = arg

    if model == "deepcrf" or model == "deep-crf":
        config = DeepCRFConfig("{}", "", "")
        config.dump(path)
    elif model == "clscnn" or model == "cls-cnn":
        config = TextCNNConfig("{}", "", "")
        config.dump(path)
    elif model == "clsrnn" or model == "cls-rnn":
        config = TextRNNConfig("{}", "", "")
        config.dump(path)

