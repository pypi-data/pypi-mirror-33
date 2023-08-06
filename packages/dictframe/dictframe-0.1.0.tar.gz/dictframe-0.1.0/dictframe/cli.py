import argparse
from .dictframe import load_corpus, load_tokenizer_cls


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('corpus', type=str)
    parser.add_argument('userdict', type=str)

    parser.add_argument('--output', type=str, default='')

    parser.add_argument('--skip', type=int, default=0)
    parser.add_argument('--size', type=int, default=20)
    parser.add_argument('--random', dest='random', action='store_true', default=False)

    parser.add_argument('--tokenizer', type=str, default='jieba')
    parser.add_argument('--tokenizer-sep', type=str, default=' / ')

    args = parser.parse_args()

    lines = load_corpus(args.corpus, args.skip, args.size, args.random)

    tokenizer = load_tokenizer_cls(args.tokenizer)()
    tokenizer.load_dictionary(args.userdict)

    ret = []
    for line in lines:
        toks = tokenizer.tokenize(line)
        ret.append(args.tokenizer_sep.join(toks))
    ret = '\n'.join(ret)

    if not args.output:
        print(ret)
    else:
        with open(args.output, 'w') as fout:
            fout.write(ret)
