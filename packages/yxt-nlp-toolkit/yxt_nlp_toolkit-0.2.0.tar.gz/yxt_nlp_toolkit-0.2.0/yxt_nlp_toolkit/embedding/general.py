from . import wordembedding
import numpy


class WordEmbedding(wordembedding.WordEmbedding):

    def __init__(self, model_path):
        super(WordEmbedding, self).__init__()
        self.model_path = model_path
        self._model = None

    def _ensure_model_loaded(self):
        if self._model is None:
            self._model = dict(self._load(self.model_path))

    @staticmethod
    def _load(path):
        with open(path, 'r') as f:
            for line in f:
                word, *vec = line.split(' ')
                vec = numpy.array(tuple(float(v) for v in vec))
                yield word.upper(), vec

    def __repr__(self):
        return "<general({})>".format(self.model_path)

    def get_raw_word2vec(self, word):
        return self._model[word]
