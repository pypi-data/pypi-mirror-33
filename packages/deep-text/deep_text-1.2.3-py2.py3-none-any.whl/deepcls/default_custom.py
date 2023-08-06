from .transform import DeepCLSTransform
from common.utils import CorpusIterator


class DefaultCorpusIterator(CorpusIterator):
    def __init__(self, files):
        super(DefaultCorpusIterator, self).__init__(files)
        self.parts = []

    def analysis_line(self, line):
        return line.strip().split(" ")


class DefaultCLSTransform(DeepCLSTransform):
    def __init__(self, config):
        super(DefaultCLSTransform, self).__init__(config=config,
                                                  corpus_iter=DefaultCorpusIterator([config.train_input_path]))

    def parse_line(self, line):
        pair = line.strip().split(" ")
        ws = [p for p in pair if not p.startswith(self.config.label_prefix)]
        ls = [p.replace(self.config.label_prefix, "") for p in pair if p.startswith(self.config.label_prefix)]
        return ws, ls


