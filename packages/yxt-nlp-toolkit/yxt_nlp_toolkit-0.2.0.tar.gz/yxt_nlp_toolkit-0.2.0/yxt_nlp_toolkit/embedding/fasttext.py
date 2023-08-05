import fasttext
from . import wordembedding


class WordEmbedding(wordembedding.WordEmbedding):
    def __init__(self, model_path):
        super(WordEmbedding, self).__init__()
        self._model = None
        self.model_path = model_path

    def _ensure_model_loaded(self):
        if self._model is None:
            self.model = fasttext.load_model(self.model_path)

    def __repr__(self):
        return '<fasttext({})>'.format(self.model_path)

    def get_raw_word2vec(self, word):
        self._ensure_model_loaded()
        return self._model[word]
