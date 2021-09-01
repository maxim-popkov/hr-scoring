# -*- coding: utf-8 -*-
"""
1. PARSE Data from pdf docx rtf <---
2. PARSE NER from texts
3. Predict
"""

import os
import json
from glob import glob
import codecs

import click
import logging

import pdftotext
import docx2txt
from striprtf.striprtf import rtf_to_text


INPUT_DIRPATH =  r'D:\develop\hr-scoring\data\raw\test-data'
OUTPUT_FILEPATH = r'D:\develop\hr-scoring\data\interim\parsed-test.json'


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


# @profile
@click.command()
@click.argument('input_dirpath', default=INPUT_DIRPATH)
@click.argument('output_filepath', type=click.Path(), default=OUTPUT_FILEPATH)
def main(input_dirpath, output_filepath):
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """
    logger = logging.getLogger(__name__)
    logger.info('Extract Text data set from raw data')
    logger.info(f'Input DIR: {input_dirpath}')
    logger.info(f'Output FILE: "{output_filepath}')


    fpaths = [y for x in os.walk(input_dirpath) for y in glob(os.path.join(x[0], '*.*'))]
    logger.info(f'Find {len(fpaths)} files')

    pdf_fpaths = [fpath for fpath in fpaths if fpath.endswith(".pdf")]
    docx_fpaths = [fpath for fpath in fpaths if fpath.endswith(".docx")]
    rtf_fpaths = [fpath for fpath in fpaths if fpath.endswith(".rtf")]

    skip_paths = [fpath for fpath in fpaths if fpath not in set(pdf_fpaths + docx_fpaths + rtf_fpaths)]
    logger.info(f'Find PDFs:{len(pdf_fpaths)} | DOCXs:{len(docx_fpaths)} | RTFs:{len(rtf_fpaths)} | SKIP: {len(skip_paths)}')

    fpath_txts = [(fpath, pdf2text(fpath)) for fpath in pdf_fpaths]
    fpath_txts = fpath_txts + [(fpath, docx2txt.process(fpath)) for fpath in docx_fpaths]
    fpath_txts = fpath_txts + [(fpath, rtf2text(fpath)) for fpath in rtf_fpaths]

    processed_data = []

    for fpath, txt in fpath_txts:
        resume_info = make_resume_info_dict(fpath, txt)
        processed_data.append(resume_info)

    logger.info(f'Processed {len(processed_data)}')

    for fpath in skip_paths:
        resume_info = make_resume_info_dict(fpath, None)
        processed_data.append(resume_info)

    with open(output_filepath, 'w',  encoding='utf8') as fd:
        json.dump(processed_data, fd, indent=4, ensure_ascii=False)

    logger.info(f'Write to JSON {len(processed_data)}')


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    main()
