from collections import defaultdict

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, ClusterMixin
from sklearn.utils.validation import check_array


class KeyWordClassifier(BaseEstimator, ClusterMixin):

    def __init__(self, roles_dict=None, roles2vote_num=None):
        if roles_dict == None:
            roles = {
                'da': ['Data Analyst','sql', 'pandas', 'numpy', 'scipy', 'excel', 'Matplotlib', 'Seaborn',
                        'statistics','Data Analyst','tableau','sas','power bi','powerbi', 'ltv', 'cac', 'Retention'],
                'de': ['data engineer', 'Kubernetes','asyncio', 'flask', 'django', 'api', 'linux', 'bash', 
                        'mongodb', 'SQLAlchemy','fastapi', 'kafka', 'etl', 'spark','python','data warehousing',
                        'pig','hive','hadoop','hbase','elastic', 'jenkins', 'git', 'docker', 'airflow', 'scala', 'java','lucene'],
                'ds': ['Data Science', 'Random Forest', 'logistic regression' 'machine learning', 'scikit',
                        'Computer Vision','data mining','matlab', 'cnn', 'rnn', 'statistics','linear algebra',
                        'keras','tensorflow','pytorch','torch','bert','theano', 'deep learning','image processing',
                        'digital signal processing','opencv','uplift', 'lgd', 'catboost', 'xgboost', 'scikit', 'LightGBM'],
                'cv_nlp': ['Computer Vision', 'OCR', 'tensorrt', 'OpenVINO', 'object detection', 'cnn', 'rnn', 'unet', 
                            'u-net', 'vgg', 'resnet','pytorch','bert', 'nltk', 'gensim','image processing','opencv'],
                'grade': ['senior', 'middle', 'старший', 'ведущий', 'доцент', 'руководитель', 'директор', 'team lead', 'tech lead'],
                'courses': []

            }
            roles2vote_num = {
                'da':1, 'de':3, 'ds':3, 'cv_nlp':2, 'grade':0
            }

        roles = { role: list(map(str.lower, words)) for (role, words) in roles.items() }

        self.roles = roles
        self.roles2vote_num = roles2vote_num
        self._role2ix = {role:ix_role for ix_role, role in enumerate(self.roles)}
        self.ix2words = defaultdict(lambda: defaultdict(set))
        self._ix2roles = defaultdict(set)
        self._results = None


    def fit_predict(self, X):

        X = check_array(X, dtype=str, ensure_2d=False)

        self.ix2words = defaultdict(lambda: defaultdict(set))
        self._ix2roles = defaultdict(set)


        num_roles = len(self.roles)
        n_rows = len(X)
        n_cols = num_roles
        results = np.zeros(shape=(n_rows,n_cols))

        for ix, text in enumerate(X):
            text = text.lower()
            iter_result =  np.zeros(shape=(n_cols))

            if len(text) == 0:
                continue
            
            # check for keywords
            for role in self.roles:
                success_role = None

                for key_words in self.roles[role]: 
                    if key_words in text:
                        self.ix2words[ix][role].add(key_words)
            
            # assign role
            for role in self.roles:
                ix_role = self._role2ix[role]
                vote_num = self.roles2vote_num[role]
                number_keywords = len(self.ix2words[ix][role])

                if number_keywords > 0:
                    success_role = role
                if number_keywords > vote_num:
                    self._ix2roles[ix].add(role)
                    iter_result[ix_role] = 1
                
                if (len(self._ix2roles[ix]) == 0) and (success_role != None):
                    self._ix2roles[ix].add(success_role)
                    ix_success_role = self._role2ix[success_role]
                    iter_result[ix_success_role] = 1
                    
                elif (len(self._ix2roles[ix]) == 0):
                    self._ix2roles[ix] = set()

            # assign result by text
            results[ix] = iter_result

        self._results = results
        return results


    def results_to_df(self, labels=None):
        _labels = labels
        if not labels:
            _labels = self._results
            
        df_labels = pd.DataFrame(_labels, columns=self.roles.keys())
        return df_labels


    def results_to_dict(self):
        return self._ix2roles
