from functools import lru_cache
from nltk.corpus import floresta
from fcache.cache import FileCache
import nltk

from lab_text_processing.stemmize import stemmize


@lru_cache()
def simplify_tag(tag):
    if "+" in tag:
        return tag[tag.index("+") + 1:]
    else:
        return tag


@lru_cache()
def default_stopwords():
    twords = floresta.tagged_words()
    stopwords = nltk.corpus.stopwords.words('portuguese')
    stopwords += ['srs', 'sr', 'sras', 'sra', 'deputado', 'presidente',
                  'é', 'nº', 's.a.', 'v.exa.', 'v.exa', '#', 'anos', 'º',
                  'exa', 'mesa', 'legislatura', 'sessão', 'maioria',
                  'seguinte', 'mandato', 'bilhões', 'quilômetros', 'maçã',
                  'ª', 'parabéns', 'membros', 'convido', 'usual', 'biênio',
                  'brasil', 'palavra', 'discussão', 'período', 'início',
                  'pronunciamento', 'suplente', 'atividade', 'ação', 'ações',
                  'daqueles', 'diferenças', 'pasta', 'milhares', 'srªs',
                  'emenda', 'àqueles', 'tamanha', 'mês', 'capaz', 'km',
                  'modelo', 'tarefas', 'colegas', 'programa', 'voz',
                  'meios de comunicação', 'pronunciamento', 'casa', 'sessão',
                  'deliberativa', 'solene', 'ordinária', 'extraordinária',
                  'encaminhado', 'orador', 'tv', 'divulgar', 'deputado',
                  'parlamento', 'parlamentar', 'projeto',
                  'proposta', 'requerimento', 'destaque', 'veto', 'federal',
                  'câmara', 'senado', 'congresso', 'nacional', 'país',
                  'estado', 'brasil', 'lei', 'política', 'povo', 'voto',
                  'partido', 'liderança', 'bancada', 'bloco', 'líder',
                  'lider', 'frente', 'governo', 'oposição', 'presença',
                  'presente', 'passado', 'ausência', 'ausencia', 'ausente',
                  'obstrução', 'registrar', 'aprovar', 'rejeitar', 'rejeição',
                  'sabe', 'matéria', 'materia', 'questão', 'ordem', 'emenda',
                  'sistema', 'processo', 'legislativo', 'plenário', 'pedir',
                  'peço', 'comissão', 'especial', 'permanente', 'apresentar',
                  'encaminhar', 'encaminho', 'orientar', 'liberar', 'apoiar',
                  'situação', 'fato', 'revisão', 'tempo', 'pauta', 'discutir',
                  'discussão', 'debater', 'retirar', 'atender', 'colegas',
                  'autor', 'texto', 'medida', 'união', 'república',
                  'audiência', 'audiencia', 'público', 'publico', 'reunião',
                  'agradecer', 'solicitar', 'assistir', 'contrário',
                  'favorável', 'pessoa', 'comemorar', 'ato', 'momento',
                  'diretora', 'possível', 'atenção', 'agradeço', 'naquele',
                  'necessárias', 'presidenta', 'compromisso']

    valid_tags = ['adj', 'n']
    for (word, tag) in twords:
        tag = simplify_tag(tag)
        words = word.casefold().split('_')
        if tag not in valid_tags:
            stopwords += words

    return list(set(stopwords))


def get_stopwords(extra_stopwords=[]):
    cache = FileCache('stopwords')
    stopwords = cache.get('stopwords', [])
    if stopwords:
        return set(stopwords + extra_stopwords)
    else:
        cache['stopwords'] = default_stopwords()
        cache.sync()
        return set(cache['stopwords'] + extra_stopwords)


def get_stemmed_stopwords(extra_stopwords=[]):
    cache = FileCache('stopwords')
    stemmed_stopwords = cache.get('stemmed_stopwords', [])
    stemmed_extra = list(set([stemmize(w) for w in extra_stopwords]))
    if stemmed_stopwords:
        return set(stemmed_stopwords + stemmed_extra)
    else:
        stemmed = list(set(stemmize(w) for w in get_stopwords()))
        cache['stemmed_stopwords'] = stemmed
        cache.sync()
        return set(stemmed + stemmed_extra)
