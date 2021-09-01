# -*- coding: utf-8 -*-

"""
1. PARSE Data from pdf docx rtf
2. PARSE NER from texts <---
3. Predict
"""

import os
import json
from glob import glob
import codecs

import click
import logging
from pathlib import Path

import pdftotext
import docx2txt
from striprtf.striprtf import rtf_to_text

from natasha import (
    MorphVocab,   
    NewsEmbedding,
    NewsNERTagger,
    NamesExtractor,
    DatesExtractor
)

import ner


INPUT_FILEPATH =  r'D:\develop\hr-scoring\data\interim\parse-test.json'
OUTPUT_FILEPATH = r'D:\develop\hr-scoring\data\interim\parse-with-ner-test.json'

morph_vocab = MorphVocab()
emb = NewsEmbedding()
ner_tagger = NewsNERTagger(emb)

names_extractor = NamesExtractor(morph_vocab)
dates_extractor = DatesExtractor(morph_vocab)


def pdf2text(pdf_path):
    raw_text, pdf = None, None
    with open(pdf_path, "rb") as f:
        pdf = pdftotext.PDF(f)
        raw_text = "\n\n".join(pdf)
        
    return raw_text


def rtf2text(fpath):
    with codecs.open(fpath, 'r', encoding='cp1251') as file:
        text = file.read()
    text = rtf_to_text(text)
    return text


def make_resume_info_dict(fpath, text=None):
    resume_info = {
        'filepath':os.path.abspath(fpath),
        'filename': os.path.basename(fpath),
        'skip': False if text != None else True,
        'ner':[],
        'text': text if text != None else ''
    }
    return resume_info


def prepare_ner(text):
    blocks = ner.text_to_blocks(text)
    block_info = []
    for ix, block_text in enumerate(blocks):
        entities = ner.extract_entities(block_text, dates_extractor, ner_tagger, names_extractor)
        # print(f'-----{ix}-----')
        # print(block_text)
        # print(entities)

        if len(entities) == 0:
            continue
        block_info.append(entities)

    return block_info


# @profile
@click.command()
@click.argument('input_filepath', default=INPUT_FILEPATH)
@click.argument('output_filepath', type=click.Path(), default=OUTPUT_FILEPATH)
def main(input_filepath, output_filepath):
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """
    logger = logging.getLogger(__name__)
    logger.info('Extract Text data set from raw data')
    logger.info(f'Input FILE: {input_filepath}')
    logger.info(f'Output FILE: "{output_filepath}')

    data = None
    with open(input_filepath, encoding='utf8') as fd:
        data = json.load(fd, encoding='utf8')

    logger.info(f'Find {len(data)} CVs')

    processed_data = []
    for cv_item in data:
        if cv_item['skip'] == True:
            processed_data.append(cv_item)
            continue
        
        cv_item['ner'] = prepare_ner(cv_item['text'])
        processed_data.append(cv_item)

    logger.info(f'Processed {len(processed_data)}')

    with open(output_filepath, 'w',  encoding='utf8') as fd:
        json.dump(processed_data, fd, indent=4, ensure_ascii=False)

    logger.info(f'Write to JSON {len(processed_data)}')


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    main()
