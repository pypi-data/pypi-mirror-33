import numpy as np
import pickle


class Lang:
    DEFAULT_NIL_TOKEN, NIL_INDEX = '<NIL>', 0

    def __init__(self, words, to_upper=True,
                 reserved_tokens=(), nil_token=DEFAULT_NIL_TOKEN):
        self._word2ix, self._ix2word = {}, {}
        self.to_upper = to_upper
        self._add_new_word(nil_token)
        for token in reserved_tokens:
            self._add_new_word(token)
        for word in words:
            self._add_new_word(word)

    def word_iter(self):
        return iter(self._word2ix.keys())

    def index_iter(self):
        return iter(self._ix2word.keys())

    def __len__(self):
        return len(self._word2ix)

    def __contains__(self, item):
        item = item.upper() if self.to_upper else item
        if isinstance(item, int):
            return item in self._ix2word
        elif isinstance(item, str):
            return item in self._word2ix
        else:
            return False

    def __iter__(self):
        return iter(self._word2ix.keys())

    def items(self):
        return self._word2ix.items()

    def __repr__(self):
        return str(self)

    def __str__(self):
        return 'Lang(vocab_size={vocab_size})'.format(vocab_size=self.vocab_size)

    def __getitem__(self, item):
        if isinstance(item, int):
            return self.word(item)
        elif isinstance(item, str):
            return self.ix(item)
        raise TypeError("only support int,str:but found:{}({})".format(
            type(item), item))

    def _add_new_word(self, word, index=None):
        word = word.upper() if self.to_upper else word
        if word in self._word2ix:
            if index is not None:
                assert self.ix(word) == index
            return
        index = len(self._word2ix) if index is None else index
        assert index not in self._ix2word
        self._word2ix[word], self._ix2word[index] = index, word

    def build_embedding(self, wv, out_embedding=None):
        from ..embedding.wordembedding import WordEmbedding
        if not isinstance(wv, WordEmbedding):
            raise TypeError('only support WordEmbedding,but found {}'.format(type(wv)))
        if out_embedding is None:
            out_embedding = np.random.randn(self.vocab_size, wv.embedding_dim)
        for ix, word in self._ix2word.items():
            try:
                if ix < len(out_embedding):
                    out_embedding[ix] = wv[word]
            except KeyError:
                pass
        return out_embedding

    @property
    def vocab_size(self):
        return len(self._word2ix)

    @property
    def nil_token(self):
        return self.word(0)

    def ix(self, word):
        assert isinstance(word, str)
        word = word.upper() if self.to_upper else word
        return self._word2ix.get(word, Lang.NIL_INDEX)

    def to_indices(self, words):
        return tuple(self.ix(w) for w in words)

    def to_words(self, indices):
        return tuple(self.word(i) for i in indices)

    def one_hot_of(self, word_or_index):
        vocab_len = self.vocab_size
        if isinstance(word_or_index, str):
            ix = self.ix(word_or_index)
        elif isinstance(word_or_index, int):
            ix = word_or_index
        else:
            raise TypeError("one hot only support str or int, but found:{}({})".format(
                type(word_or_index), word_or_index))

        assert 0 <= ix < vocab_len
        vec = [0] * vocab_len
        vec[ix] = 1
        return vec

    def word(self, index):
        assert isinstance(index, int)
        if index == Lang.NIL_INDEX:
            return Lang.NIL_TOKEN
        if index in self._ix2word:
            return self._ix2word[index]
        raise ValueError('unknown index:{}'.format(index))

    def vocabulary(self):
        return tuple(self._word2ix.keys())

    def dump(self, path, binary=False):
        if binary:
            with open(path, 'wb') as f:
                pickle.dump(self, f)
        else:
            with open(path, 'w') as f:
                for word, index in self._word2ix.items():
                    word = word.strip('\t ')
                    if word == '\n':
                        word = '<new_line>'
                    elif word == '\t':
                        word = '<tab>'
                    entry = '{} {}\n'.format(word, index)
                    f.write(entry)

    @classmethod
    def load(cls, path, binary=False):
        if binary:
            with open(path, 'rb') as f:
                return pickle.load(f)
        else:
            # TODO: loss the name, fix it
            lang = Lang(words=())
            lang._ix2word, lang._word2ix = {}, {}
            with open(path, 'r') as f:
                for line in f:
                    word, index = line.strip().split(' ')
                    if word == '<new_line>':
                        word = '\n'
                    elif word == '<tab>':
                        word = '\t'
                    index = int(index)
                    lang._add_new_word(word, index)
            return lang


def build_lang_from_token_stream(token_stream, min_count=1, lang_name='zh'):
    from collections import Counter
    words_freq = Counter(token_stream)
    words = tuple(w for w, freq in words_freq.items() if freq >= min_count)
    return Lang(name=lang_name, words=words)


def build_lang_from_corpus(corpus_or_corpus_seq, min_count=1, lang_name='zh'):
    from yxt_nlp_toolkit.utils.tokenizer import token_stream
    tokens = token_stream(corpus_or_corpus_seq)
    return build_lang_from_token_stream(tokens, min_count=min_count, lang_name=lang_name)
