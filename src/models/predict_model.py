# -*- coding: utf-8 -*-
import os
import sys
import shutil


from dotenv import find_dotenv
dotenv_path = find_dotenv()
project_dir = os.path.dirname(dotenv_path)
sys.path.append(project_dir)

from src.models.KeyWordsModel import KeyWordClassifier

import json
from glob import glob

import click
import logging
from pathlib import Path

import pandas as pd

INPUT_FILEPATH = r"D:\develop\hr-scoring\data\interim\pool-test.json"
OUTPUT_DIRPATH = r"D:\develop\hr-scoring\models\cv-with-labels"


def rm_files_in_dir(dir_path):
    folder = dir_path
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


@click.command()
@click.argument('input_filepath', default=INPUT_FILEPATH)
@click.argument('output_dirpath', type=click.Path(), default=OUTPUT_DIRPATH)
@click.argument('search_roles', default='all')
def main(input_filepath, output_dirpath, search_roles):
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """
    logger = logging.getLogger(__name__)
    logger.info(f'Input FILE: {input_filepath}')
    logger.info(f'Output Dir: {output_dirpath}')
    logger.info(f'Search Roles: {search_roles}')

    search_roles = search_roles.split('-')

    rm_files_in_dir(output_dirpath)
    logger.info(f'Delete Files in "{output_dirpath}')


    resumes = None
    with open(input_filepath, 'r', encoding='utf-8') as fd:
        resumes = json.load(fd)
    logger.info(f'Read Resumes {len(resumes)} in "{input_filepath}')


    df_resumes = pd.DataFrame(resumes)
    clf = KeyWordClassifier()
    labels = clf.fit_predict(df_resumes['text'])
    df_labels = clf.results_to_df()
    df_resumes = df_resumes.join(df_labels)


    roles = df_labels.columns
    resume_write_counter = 0
    for _, row in df_resumes.iterrows():
        fpath = row.filepath
        file_roles = sorted({role for role in roles if row[role] > 0}) 

        if 'grade' in file_roles:
            file_roles.remove('grade')
            file_roles = ['mngt'] + file_roles 
            
        if len(file_roles) == 0:
            file_roles = ['skip']

        skip_iteration = False
        if 'all' not in search_roles:
            for search_role in search_roles:
                if search_role not in file_roles:
                    skip_iteration = True
                    break
        
        if skip_iteration:
            continue

        logger.info(f"File {'-'.join(file_roles) + '-' + os.path.basename(fpath)}")
 
        src_path = fpath
        dst_path = os.path.join(OUTPUT_DIRPATH, '-'.join(file_roles) + '-' + os.path.basename(fpath))
        
        shutil.copy(src_path, dst_path)
        resume_write_counter += 1
    
    
    logger.info(f'Write: Resumes"{resume_write_counter}')




if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    main()
