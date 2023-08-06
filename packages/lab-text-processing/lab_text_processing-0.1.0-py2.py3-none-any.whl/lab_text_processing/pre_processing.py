from collections import Counter
from functools import lru_cache
from string import digits
import nltk

from lab_text_processing.stopwords import get_stemmed_stopwords
from lab_text_processing.stemmize import stemmize


def remove_numeric_characters(text):
    remove_digits = str.maketrans('', '', digits)
    return text.translate(remove_digits)


def tokenize(text):
    return nltk.tokenize.word_tokenize(text, language='portuguese')


def clear_tokens(tokens, stopwords):
    stem_reference = {}
    cleared_tokens = [
        stemmize(token, stem_reference=stem_reference)
        for token in tokens
        if stemmize(token) not in stopwords
    ]
    return cleared_tokens, stem_reference


@lru_cache()
def bow(text, extra_stopwords=[], ngrams=1):
    text = remove_numeric_characters(text)
    stopwords = get_stemmed_stopwords(extra_stopwords=extra_stopwords)
    tokens, stem_reference = clear_tokens(tokenize(text), stopwords)

    text_bow = Counter([
        ' '.join(token)
        for token in nltk.ngrams(tokens, ngrams)
    ])
    return text_bow, stem_reference


def most_common_words(text, n=None):
    text_bow, reference = bow(text)
    most_common = []

    for token in text_bow.most_common(n):
        stem, frequency = token

        # reference[stem] is a Counter and most_comon(1) return a list
        # of tuples: ('word', occurrences)
        word = reference[stem].most_common(1)[0][0]
        most_common.append((word, frequency))
    return most_common
