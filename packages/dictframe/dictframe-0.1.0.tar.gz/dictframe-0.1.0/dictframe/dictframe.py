import jieba
import random
import logging


class Tokenizer:

    def load_dictionary(self, path):
        self.reload_dictionary(path)

    def reload_dictionary(self, path):
        pass

    def tokenize(self, text):
        pass


class JiebaTokenizer(Tokenizer):

    def __init__(self):
        super().__init__()
        jieba.setLogLevel(logging.INFO)
        self.tok = jieba.Tokenizer()

    def reload_dictionary(self, path):
        self.tok = jieba.Tokenizer()
        self.tok.load_userdict(path)

    def tokenize(self, text):
        return list(self.tok.cut(text))


def load_tokenizer_cls(name):
    mapping = {
        'jieba': JiebaTokenizer
    }
    return mapping[name]


def load_corpus(path, skip_cnt, line_cnt, randomized):
    with open(path) as fin:
        lines = list(filter(bool, map(lambda l: l.strip(), fin)))

    lines = lines[skip_cnt:]
    if randomized:
        random.shuffle(lines)
    return lines[:line_cnt]
