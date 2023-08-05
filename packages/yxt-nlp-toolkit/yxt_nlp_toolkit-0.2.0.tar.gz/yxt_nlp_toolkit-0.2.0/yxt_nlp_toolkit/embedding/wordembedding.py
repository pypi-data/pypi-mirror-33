import numpy as np


class WordEmbedding:
    def __init__(self):
        self._embedding_dim = None

    @property
    def embedding_dim(self):
        if self._embedding_dim is not None:
            return self._embedding_dim
        self._ensure_model_loaded()
        for word in ('中国', '知识', '能力'):
            try:
                self._embedding_dim = len(self.get_raw_word2vec(word))
                return self._embedding_dim
            except KeyError:
                pass
        raise ValueError('Fail to detect wordvec len')

    def __getitem__(self, item):
        self._ensure_model_loaded()
        vec = self.get_raw_word2vec(item)
        return np.array(vec)

    def _ensure_model_loaded(self):
        raise NotImplementedError

    def get_raw_word2vec(self, word):
        raise NotImplementedError
