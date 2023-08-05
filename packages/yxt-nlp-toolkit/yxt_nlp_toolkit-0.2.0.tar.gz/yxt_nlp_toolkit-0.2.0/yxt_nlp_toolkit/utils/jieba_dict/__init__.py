import os
import re

_current_dir = os.path.dirname(os.path.abspath(__file__))
_user_custom_dict = _current_dir + '/dict.dat'
_stopwords_data = _current_dir + '/stopwords.dat'

_loaded_dict = False


def jieba_load_userdict():
    global _loaded_dict
    import jieba
    if _loaded_dict:
        return
    jieba.load_userdict(_user_custom_dict)
    _loaded_dict = True


def read_user_custom_words():
    with open(_user_custom_dict, 'r') as f:
        for line in f:
            try:
                word, *_ = re.split('\s', line)
                yield word
            except ValueError as e:
                print(e)


def _read_stopwords():
    with open(_stopwords_data, 'r') as f:
        for line in f:
            line = line.replace('\n', '').strip()
            if line:
                yield line


_stopword_set = set(_read_stopwords())


def is_stopword(word):
    return word in _stopword_set


def get_stopwords():
    return _stopword_set
