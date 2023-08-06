from dictframe.dictframe import JiebaTokenizer
from tempfile import NamedTemporaryFile


def test_reload_dictionary():
    tok = JiebaTokenizer()
    text = '蚂蚁花呗解约'
    word = '蚂蚁花呗'

    assert word not in tok.tokenize(text)

    with NamedTemporaryFile() as userdict:
        with open(userdict.name, 'w') as fin:
            fin.write(word)
        tok.reload_dictionary(userdict.name)

        assert word in tok.tokenize(text)
