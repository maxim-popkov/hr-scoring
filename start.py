# -*- coding: utf-8 -*-
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
    fname = 'cvs-' + time_str + '.json'

    interim_fpath = os.path.join(INTERIM_DIRPATH, fname)
    cmd_extract = f"python .\src\data\make_dataset.py {cvs_dirpath} {interim_fpath}"
    cmd_predict = f"python .\src\models\predict_model.py {interim_fpath} {output_dirpath} {search_roles}"

    logger.info(f'CMD extract: {cmd_extract}')
    logger.info(f'CMD predict: {cmd_predict}')

    exit_code_extract = os.system(cmd_extract)
    exit_code_predict = os.system(cmd_predict)



if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    main()
