
def courses_detector(text, courses_keywords=None):
    """
    detect if course in text
    """
    text = text.lower()
    if courses_keywords == None:
        courses_keywords = {
            'coursera', 'skillfactory', 'skillbox', 
            'практикум', 'udemy', 'курс', 'сертефикат', 
            'обучение', 'newprolab', 'stepik'
            }
    
    for word in courses_keywords:
        if word in text:
            return word
    return ''


def extract_entities(text, dates_extractor=None, ner_tagger=None, names_extractor=None):
    """
    Extract DATE, ORG, PERSON, COURSE
    return  info = {
        'ORG': first_org in text,
        'DATE': first_date in text,
        'NAME': first name in text,
        'COURSE': is_courses_block
    }
    """
    import re        
    first_date = ''
    date_spans = dates_extractor(text)
    date_spans = list(date_spans)

    if len(date_spans) > 0:
        date = date_spans[0].fact
        first_date = date.year
    else:
        # matches = re.search(r'[12]\d{3}', text)
        matches = re.search(r"(?<!\d)\d{4}(?!\d)", text)
        if matches:
            first_date = matches.group()

    first_org = ''
    org_spans = [span for span in ner_tagger(text).spans if span.type == 'ORG']
    if len(org_spans) > 0:
        first_org_span = org_spans[0]
        first_org = text[first_org_span.start:first_org_span.stop]
        first_org = ' '.join(first_org.split()).strip()

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

    courses = courses_detector(text)
    courses = courses.strip()

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

    info = {}
    if first_date == '':
        return info

    if sum(matches) == 0:
        return info    

    info = {
        'ORG': first_org,
        'DATE': first_date,
        'NAME': name,
        'COURSE': courses
    }
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
