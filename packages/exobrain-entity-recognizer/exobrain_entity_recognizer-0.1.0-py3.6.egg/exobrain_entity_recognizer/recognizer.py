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
    WILDCARD = '*'

    _dict = None
    _nlp = None

    def __init__(self, model='en_core_web_lg'):
        # init NLP
        self._init_nlp(model)

        # Init or Load entity dictionary
        self._init_dict()

    def __call__(self, text):
        entities = self._get_entities(text)
        return entities

    def _get_entities(self, text):
        """Recognize and return entities and contexts from text

        Args:
            text (str): text
        Returns:
            list: list of recognized entities and contexts

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
                'text': ent.text.lower(),
                'lemma': ent.lemma_,
                'left_contexts': [tok.text.lower() for tok in ent.lefts],
                'right_contexts': [tok.text.lower() for tok in ent.rights],
                'label': ent.label_
            } for ent in doc.ents]
        # 2. NP chunks
        entities += [
            {
                'id': self._get_text_id(np.lemma_),
                'text': np.text.lower(),
                'lemma': np.lemma_,
                'left_contexts': [tok.text.lower() for tok in np.lefts],
                'right_contexts': [tok.text.lower() for tok in np.rights],
                'label': ""
            }
            for np in doc.noun_chunks
            if np not in doc.ents
        ]
        return entities

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

    def load_dict(self, dict_path):
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

    def save_dict(self, dict_path):
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
            spacy_cmd = 'python -m spacy download {}'.format(model)
            logger.warning(
                'The required spaCy model not found. Run \'{}\'.'.format(spacy_cmd))


if __name__ == '__main__':
    recognizer = EntityRecognizer()
