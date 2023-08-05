from . import wordembedding


class WordEmbedding(wordembedding.WordEmbedding):
    def __init__(self, model_path):
        super(WordEmbedding, self).__init__()
        self.model_path = model_path
        self._model = None

    def _ensure_model_loaded(self):
        import gensim
        if self._model is None:
            self._model = gensim.models.Word2Vec.load(self.model_path)

    def __repr__(self):
        return "<gensim({})>".format(self.model_path)

    def get_raw_word2vec(self, word):
        return self._model.wv[word]
