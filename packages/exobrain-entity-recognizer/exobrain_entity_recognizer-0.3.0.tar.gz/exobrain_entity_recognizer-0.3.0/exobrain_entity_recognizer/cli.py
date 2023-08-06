# -*- coding: utf-8 -*-

"""Console script for exobrain_entity_recognizer."""
import sys
import click
import logging
from subprocess import call

logger = logging.getLogger(__name__)


@click.group()
def main(args=None):
    """Console script for exobrain_entity_recognizer."""
    pass


@main.command()
def download_models(args=None):
    # spaCy
    click.echo('Downloading spaCy models...')
    call(['python', '-m', 'spacy', 'download', 'en'])
    call(['python', '-m', 'spacy', 'download', 'en_core_web_lg'])
    # TextBlob
    click.echo('Downloading TextBlob models...')
    call(['python', '-m',  'textblob.download_corpora'])


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
