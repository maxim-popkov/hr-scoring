import re
from dataclasses import dataclass


@dataclass
class NerInfo:
    """
    Class for handle NER Parsing results
    """
    org: str = ''
    org_text: str = ''
    date: str = ''
    name: str = ''
    course: str = ''
    course_text: str = ''
    univer_text: str = ''
    skills: str = ''

    def to_dict(self) -> dict:
        info = {
            'ORG': self.org,
            'ORG_TEXT': self.org_text,
            'DATE': self.date,
            'NAME': self.name,
            'COURSE': self.course,
            'COURSE_TEXT': self.course_text,
            'UNIVER_TEXT': self.univer_text,
            'SKILLS': self.skills
        }
        return info


def skills_detector(text, skills=None):
    """
    search skills in text
    """
    if skills == None:
        skills = {
            'data analyst','sql', 'аналитик', 'разработчик', 'pandas', 'numpy', 'scipy', 'excel', 'matplotlib', 'seaborn',
            'statistics','tableau','sas','power bi','powerbi', 'ltv', 'cac', 'retention',
            'data engineer', 'Kubernetes','asyncio', 'flask', 'django', 'api', 'linux', 'bash', 
            'mongodb', 'sqlalchemy','fastapi', 'kafka', 'etl', 'spark','python','data warehousing',
            'pig','hive','hadoop','hbase','elastic', 'jenkins', 'git', 'docker', 'airflow', 'scala', 'java','lucene',
            'data science', 'random forest', 'logistic regression' 'machine learning', 'scikit',
            'computer vision','data mining','matlab', 'cnn', 'rnn', 'statistics','linear algebra',
            'keras','tensorflow','pytorch','torch','bert','theano', 'deep learning','image processing',
            'digital signal processing','opencv','uplift', 'lgd', 'catboost', 'xgboost', 'scikit', 'lightgbm',
            'computer vision', 'ocr', 'tensorrt', 'openvino', 'object detection', 'cnn', 'rnn', 'unet', 
            'u-net', 'vgg', 'resnet','pytorch','bert', 'nltk', 'gensim','image processing','opencv'
        }

    detected_skills = []
    text = text.lower()
    for skill in skills:
        if skill in text:
            detected_skills.append(skill)

    return detected_skills



def university_detector(text, ed_keywords=None):
    text = text.lower()
    if ed_keywords == None:
        ed_keywords = {
            'институт', 'университет', 'пту', 'техникум','образование', 'лицей', 'школа'
        }
    
    for word in ed_keywords:
        if word in text:
            return word
    return ''  


def year_detector(text):
    first_year = ''
    matches = re.search(r"(?<!\d)\d{4}(?!\d)", text)
    if matches:
        first_year = matches.group()

    return first_year
    


def courses_detector(text, courses_keywords=None):
    """
    detect if course in text
    """
    text = text.lower()
    if courses_keywords == None:
        courses_keywords = {
            'coursera', 'skillfactory', 'skillbox', 
            'яндекс.практикум', 'практикум', 'udemy', 'курс', 'сертефикат', 
            'обучение', 'newprolab', 'stepik', 'geekbrains', 'гикбреинс'
        }
    
    for word in courses_keywords:
        if word in text:
            return word
    return ''


# @profile
def extract_entities(text, dates_extractor=None, ner_tagger=None, names_extractor=None):
    """
    Extract DATE, ORG, PERSON, COURSE
    return  info = {
        'ORG': first_org in text,
        'ORG_TEXT': txt
        'DATE': first_date in text,
        'NAME': first name in text,
        'COURSE': is_courses_block
        'COURSE_TEXT: txt
    }
    """
    import re
    
    info = {}

    # take first 3 lines for optimisation
    block_text = text
    text = ' '.join(block_text.splitlines()[:3])

    first_date = ''
    first_date = year_detector(text)
    if len(first_date) != 4:
        date_spans = dates_extractor(text)
        date_spans = list(date_spans)

        if len(date_spans) > 0:
            date = date_spans[0].fact
            first_date = date.year

    if first_date == '':
        return info

    skills = skills_detector(block_text)

    courses = courses_detector(text)
    courses = courses.strip()

    if courses != '':
        ner_data = NerInfo(
            date=first_date, 
            course=courses, 
            course_text=' '.join(text.split()),
            skills=skills
        )
        info = ner_data.to_dict()
        return info

    univer = university_detector(text)
    if univer != '':
        ner_data = NerInfo(
            date=first_date, 
            univer_text=' '.join(text.split()),
            skills=skills
        )
        info = ner_data.to_dict()
        return info


    first_org = ''
    org_spans = [span for span in ner_tagger(text).spans if span.type == 'ORG']
    if len(org_spans) > 0:
        first_org_span = org_spans[0]
        first_org = text[first_org_span.start:first_org_span.stop]
        first_org = ' '.join(first_org.split()).strip()
        if len(first_org) < 4:
            first_org = ''


    name = ''
    names_spans = names_extractor(text)
    names_spans = list(names_spans)
    if len(names_spans) > 0:
        name_span = names_spans[0].fact
        name = {
            'first': name_span.first if name_span.first else '',
            'middle': name_span.middle if name_span.middle else '',
            'last': name_span.last if name_span.last else '',
        }


    # clean
    matches = [1,1,1]
    if name != '':
        if not ((len(name['first']) > 0 and len(name['middle']) > 0) 
            or (len(name['first']) > 0 and len(name['last']) > 0)):
            name = ''
            matches[0] = 0
    else:
        matches[0] = 0

    if first_org == '':
        matches[1] = 0

    if courses == '':
        matches[2] = 0

    if sum(matches) == 0:
        return info    

    ner_data = NerInfo(
        date=first_date,
        org=first_org,
        org_text=' '.join(block_text.split()) if first_org != '' else '',
        name=name,
        skills=skills
    )
    info = ner_data.to_dict()
    return info


def text_to_blocks(text):
    """
    split text to logiacal blocks
    rule: search for spaces between paragraphs
    111111
    ______
    222222
    """
    INIT = 0
    BLOCK = 1
    SPACE = 2
    END = 3
    status = INIT

    blocks = []
    block_text = ''

    for line in text.splitlines():

        #skip колонтитул
        line_lower = line.lower()
        if 'резюме обновлено' in line_lower:
            continue
        
        if 'история общения с кандидатом' in line_lower:
            break

        len_line = len(line.strip())
        len_leading_spaces = len(line) - len(line.lstrip())

        if status == INIT:
            if len_line > 0:
                block_text += line + '\n'
                status = BLOCK
        elif status == BLOCK:
            if len_line > 0:
                block_text += line + '\n'
                status = BLOCK
            elif len_line == 0:
                status = SPACE
        elif status == SPACE:
            if (len_line > 0) and (len_leading_spaces > 0):
                block_text += line + '\n'
                status = BLOCK
            elif (len_line > 0) and (len_leading_spaces == 0):
                blocks.append(block_text)
                block_text = line + '\n'
                status = BLOCK
            elif (len_line == 0) and (len_leading_spaces == 0):
                status = SPACE

    if status in (BLOCK, SPACE):
        blocks.append(block_text)
        block_text = ''
        status = END

    return blocks
