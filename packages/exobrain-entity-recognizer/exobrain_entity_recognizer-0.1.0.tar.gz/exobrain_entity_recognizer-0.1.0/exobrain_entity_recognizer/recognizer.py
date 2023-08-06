# -*- coding: utf-8 -*-

"""Main module."""
import spacy
import logging
import ujson as json
import os
from pathlib import Path
from collections import OrderedDict

logger = logging.getLogger(__name__)


class EntityRecognizer:
    ENT_DICT_PATH = './ents-dict.json'
    WILDCARD = '*'

    _dict = None
    _nlp = None

    def __init__(self, model='en_core_web_lg'):
        # init NLP
        self._init_nlp(model)

        # Init or Load entity dictionary
        self._init_dict()

    def __call__(self, text):
        entities, doc = self._get_entities(text)
        return (entities, [tok.text for tok in doc])

    def _get_entities(self, text):
        """Recognize and return entities from text

        Args:
            text (str): text
        Returns:
            list: list of recognized entities

            [{
                'id': ID of entity,
                'text': orginal text,
                'lemma': lemmatized(normalized) text,
                'token_start': start token index of entity,
                'token_end': end token index of entity,
                'label': the type of entity (empty if NP-chunk)
            }, ...]
            list: tokens of text
        """
        # the recognized entities
        entities = []
        # perform recognition
        doc = self._nlp(text)
        # 1. named entities
        entities += [
            {
                'id': self._get_text_id(ent.lemma_),
                'text': ent.text,
                'lemma': ent.lemma_,
                'token_start': ent.start,
                'token_end': ent.end,
                'label': ent.label_,
            } for ent in doc.ents]
        # 2. NP chunks
        entities += [
            {
                'id': self._get_text_id(np.lemma_),
                'text': np.text,
                'lemma': np.lemma_,
                'token_start': np.start,
                'token_end': np.end,
                'label': ''
            }
            for np in doc.noun_chunks
            if np not in doc.ents
        ]
        return entities, doc

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

    def _init_dict(self):
        """Init entity dictionary (ent-id pairs)"""
        if Path(self.ENT_DICT_PATH).is_file():
            self._dict = json.load(self.ENT_DICT_PATH)
        else:
            self._dict = OrderedDict()

    def _init_nlp(self, model):
        """Init internal NLP module for entity recognition
            (use spaCy by default)
        """
        try:
            logger.info('Loading spaCy model...')
            self._nlp = spacy.load(model)
        except OSError:
            spacy_cmd = 'python -m spacy download {}'.format(model)
            logger.warning(
                'The required spaCy model not found. Run \'{}\'.'.format(spacy_cmd))


if __name__ == '__main__':
    recognizer = EntityRecognizer()
