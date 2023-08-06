# Lab Text Processing

LabHacker's Toolbox to Text Processing

## Install
`pip install lab-text-processing`

## Usage

First of all you need to install all mandatory nltk data:
```
from lab_text_processing.nltk import download_modules
download_modules()
```

```
from lab_text_processing.pre_processing import bow
bow, stem_reference = bow.('Texto que será transformado em uma Bag-of-Words',
                           extra_stopwords=('lista', 'de', 'stopwords', 'adicionais'))
```