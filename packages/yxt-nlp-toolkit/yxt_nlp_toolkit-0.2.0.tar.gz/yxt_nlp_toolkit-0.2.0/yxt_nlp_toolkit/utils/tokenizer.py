from functools import lru_cache

from .str_algo import is_ascii_alpha, is_digit, ascii_punctuations


def token_stream(file_or_files, with_postag=False, skip_space=False, use_lib='jieba'):
    if isinstance(file_or_files, str):
        files = (file_or_files,)
    else:
        files = tuple(file_or_files)

    for file in files:
        with open(file, 'r') as f:
            for line in f:
                yield from tokenizer(line,
                                     with_postag=with_postag,
                                     skip_space=skip_space,
                                     use_lib=use_lib)


@lru_cache(maxsize=32)
def _load_spacy_lang(lang):
    import spacy
    return spacy.load(lang)


def _cut(text, use_lib, lang):
    if use_lib == 'hanlp':
        from pyhanlp import HanLP
        for term in HanLP.segment(text):
            yield term.word, term.nature
    elif use_lib == 'jieba':
        import jieba.posseg as posseg
        for token in posseg.cut(text):
            yield token.word, token.flag
    elif use_lib == 'spacy':
        nlp = _load_spacy_lang(lang)
        for token in nlp(text):
            yield token.text, token.pos_
    elif use_lib == 'naive':
        acc = []
        for ch in text:
            if ch == ' ':
                if acc:
                    yield ''.join(acc), None
                acc = []
            elif ch in ascii_punctuations:
                if acc:
                    yield ''.join(acc), None
                yield ch, None
                acc = []
            else:
                acc.append(ch)
        if acc:
            yield ''.join(acc), None
    else:
        raise ValueError('only support jieba or spacy, but found:{}'.format(use_lib))


def tokenizer(text,
              with_postag=False,
              to_upper=True,
              skip_space=False,
              cut_digits=False,
              cut_ascii=False,
              use_lib='jieba',
              lang='en'):
    for word, postag in _cut(text, use_lib, lang):
        if skip_space and word == ' ':
            continue
        if to_upper:
            word = word.upper()

        if (cut_digits and all(is_digit(c) for c in word)) or (cut_ascii and all(is_ascii_alpha(c) for c in word)):
            for c in word:
                if with_postag:
                    yield c, postag
                else:
                    yield c
        else:
            if with_postag:
                yield word, postag
            else:
                yield word
