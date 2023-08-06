# -*- coding: utf-8 -*-

"""Main module."""
import spacy
from textblob import TextBlob
import logging
from subprocess import call
import ujson as json
import os
from pathlib import Path
from collections import OrderedDict

logger = logging.getLogger(__name__)


class EntityRecognizer:
    WILDCARD = '*'

    _dict = None
    _nlp = None

    def __init__(self, model='en_core_web_lg'):
        # init NLP
        self._init_nlp(model)

        # Init or Load entity dictionary
        self._init_dict()

    def __call__(self, text):
        return self._get_entities(text)

    def _get_entities(self, text):
        """Recognize and return entities and contexts from text

        Args:
            text (str): text
        Yields:
            dict: dict of recognized entity and contexts

            [{
                'ent_id': ID of entity,
                'ent_text': orginal text,
                'ent_lemma': lemmatized(normalized) text,
                'token_start': start token index of entity,
                'token_end': end token index of entity,
                'label': the type of entity ('NP' if noun_chunk)
            }, ...]
        """
        def _get_entity_dict(ent, doc):
            return {
                'ent_id': self._get_text_id(ent.lemma_),
                'ent_text': ent.text,
                'ent_lemma': ent.lemma_,
                'left_contexts': [tok.text for tok in doc[:ent.start]],
                'right_contexts': [tok.text for tok in doc[ent.end:]],
                'label': ent.label_
            }
        # the recognized entities
        # recognize NEs & Noun Chunks
        try:
            sentences = TextBlob(text).sentences
        except LookupError:  # need dataset download
            # textblob_cmd = 'python -m textblob.download_corpora'
            textblob_cmd = 'exobrain_entity_recognizer download_models'
            logging.error(
                'The required TextBlob dataset not found. Run \'{}\'.'.format(textblob_cmd))
        for sent in sentences:
            doc = self._nlp(sent.string)
            # 1. named entities
            named_entities = (_get_entity_dict(ent, doc) for ent in doc.ents)
            for ent in named_entities:
                yield ent
            # # 2. NP chunks
            noun_chunks = (
                _get_entity_dict(np, doc)
                for np in list(doc.noun_chunks)
                if np not in doc.ents
            )
            for ent in noun_chunks:
                yield ent

    def _get_text_id(self, text):
        """Get or add unique ID of given text.

        Args:
            text (str): text to endorse unique ID
        Returns:
            int: the unique ID for the text
        """
        if self._dict is None:
            raise ValueError('Dictionary is not initialized!')
        if self.WILDCARD in text:
            text = self.WILDCARD
        if text in self._dict:
            return self._dict[text]
        else:
            new_id = len(self._dict)
            self._dict[text] = new_id
            return new_id

    def load_dict(self, dict_path='exobrain-ent-dict.json'):
        """Load entity dictionary

        Args:
            dict_path (str): dictionary path
        """
        dict_path = Path(dict_path)
        if dict_path.is_file():
            try:
                _dict = json.load(dict_path)
                self._dict = OrderedDict(_dict)
            except:
                raise ValueError('Unable to load dictionary file.')
        else:
            raise ValueError('Provided dictionary path is invalid.')

    def save_dict(self, dict_path='exobrain-ent-dict.json'):
        """Save entity dictionary

        Args:
            dict_path (str): dictionary path
        """
        dict_path = Path(dict_path)
        with dict_path.open('w', encoding='utf-8') as fout:
            json.dump(self._dict, fout)

    def _init_dict(self):
        """Init entity dictionary"""
        self._dict = OrderedDict()

    def _init_nlp(self, model):
        """Init internal NLP module for entity recognition
            (use spaCy by default)
        """
        try:
            logger.info('Loading spaCy model...')
            self._nlp = spacy.load(model)
        except OSError:
            # spacy_cmd = 'python -m spacy download {}'.format(model)
            spacy_cmd = 'exobrain_entity_recognizer download_models'
            logger.error(
                'The required spaCy model not found. Run \'{}\'.'.format(spacy_cmd))


if __name__ == '__main__':
    recognizer = EntityRecognizer('en')
    text = """
        spaCy excels at large-scale information extraction tasks. 
        It's written from the ground up in carefully memory-managed Cython. 
        Independent research has confirmed that spaCy is the fastest in the world. 
        If your application needs to process entire web dumps, spaCy is the library you want to be using.
    """
    for ent in recognizer(text):
        print(ent)
