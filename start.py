# -*- coding: utf-8 -*-
"""
ALL Steps in one file
1. PARSE Data from pdf docx rtf
2. PARSE NER from texts
3. Predict
"""


import os
import sys
import click
import logging
from pathlib import Path
import datetime as dt


from dotenv import find_dotenv
dotenv_path = find_dotenv()
project_dir = os.path.dirname(dotenv_path)
sys.path.append(project_dir)


CVS_DIRPATH = r"D:\develop\hr-scoring\data\raw\test-data"
OUTPUT_DIRPATH = r"D:\develop\hr-scoring\models\cv-with-labels"
INTERIM_DIRPATH = r"D:\develop\hr-scoring\data\interim"


@click.command()
@click.argument('cvs_dirpath', default=CVS_DIRPATH)
@click.argument('output_dirpath', type=click.Path(), default=OUTPUT_DIRPATH)
@click.argument('search_roles', default='all')
def main(cvs_dirpath, output_dirpath, search_roles):
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """
    logger = logging.getLogger(__name__)

    time_str = str(dt.datetime.now()).replace(' ','__').replace(':','-').split('.')[0]
    fname_parse = 'cvs-parse-' + time_str + '.json'
    fname_ner = 'cvs-ner-' + time_str + '.json'

    interim_parse_fpath = os.path.join(INTERIM_DIRPATH, fname_parse)
    interim_ner_fpath = os.path.join(INTERIM_DIRPATH, fname_ner)

    cmd_parse = f"python .\src\data\parse_data.py {cvs_dirpath} {interim_parse_fpath}"
    cmd_ner = f"python .\src\data\parse_ner.py {interim_parse_fpath} {interim_ner_fpath}"
    cmd_predict = f"python .\src\models\predict_model.py {interim_ner_fpath} {output_dirpath} {search_roles}"

    logger.info(f'CMD parse: {cmd_parse}')
    logger.info(f'CMD ner: {cmd_ner}')
    logger.info(f'CMD predict: {cmd_predict}')

    exit_code_extract = os.system(cmd_parse)
    exit_code_extract = os.system(cmd_ner)
    exit_code_predict = os.system(cmd_predict)



if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    main()
