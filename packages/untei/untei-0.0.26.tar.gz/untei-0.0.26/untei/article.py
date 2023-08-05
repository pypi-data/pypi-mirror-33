from untei.constants import Const
from datetime import datetime
from untei import utils
import re
import subprocess
import os
import json
import traceback


# def is_markdown(path):
#     return utils.file_type(path) == Const.FILE_TYPE_MARKDOWN

def parse_markdown_to_json(markdown_path):
    dir_name = os.path.dirname(os.path.realpath(__file__))
    parse_result_from_node = subprocess.check_output(['node', dir_name + '/WrapParser.js', os.path.abspath(markdown_path)])
    return json.loads(str(parse_result_from_node, 'utf-8'))        

def regulate_property(property_dict, file_name, file_create_time):
    def complement_value(key, default):
        if key in property_dict.keys():
            return property_dict[key]
        else:
            return default
    def get_date(file_create_time):
        if 'date' in property_dict.keys():
            return datetime.date(datetime.strptime(property_dict['date'], '%Y-%m-%d'))
        else:
            modified_datetime = datetime.fromtimestamp(file_create_time)
            return datetime.date(modified_datetime)

    return {
        'title'       : complement_value('title', file_name),
        'path'        : complement_value('title', file_name) + '.html',
        'tags'        : filter(lambda x: x != '', re.split(r',\s*', complement_value('tags'    , ''))),
        'authors'     : filter(lambda x: x != '', re.split(r',\s*', complement_value('authors' , ''))),
        'date'        : get_date(file_create_time),
        'status'      : complement_value('status', Const.ARTICLE_STATUS_READY),
        'description' : complement_value('description', '')
    }

def create_article_from_markdown(markdown_path):
    file_name         = utils.file_name(markdown_path) + ".html"
    file_create_time  = os.stat(Const.FILES_PATH + markdown_path).st_mtime
    try:
        parse_result  = parse_markdown_to_json(markdown_path)
        property_dict = regulate_property(parse_result['config'], file_name, file_create_time)
        content       = ''.join(parse_result['body'])
    except:
        print('Error: Parse Failed in ' + markdown_path)
        traceback.print_exc()
        property_dict = regulate_property({}, file_name, file_create_time)
        content       = ''
    article = Article(property_dict, content)
    return article

class Article:
    def __init__(self, property_dict, content):
        self.set_property_dict(property_dict)
        self.content = content

    def is_publishable(self):
        if self.status in [ Const.STATUS_READY ]:
            return True
        elif self.status in [ Const.STATUS_DRAFT ]:
            return False
        else:
            print('Warn: Unrecognized status of file')
            print('* Status', self.status)
            print('* File', self.file_path)
            return False

    def save_to(self, directory, site_config):
        var_value_mapping = {
            Const.TEMPLATE_CONTENT_INDICATOR: self.content,
            Const.TEMPLATE_COPYRIGHT_INDICATOR: site_config.get(Const.SITE_CONFIG_KEY_COPYRIGHT),
            Const.TEMPLATE_SITE_TITLE_INDICATOR: site_config.get(Const.SITE_CONFIG_KEY_TITLE),
            Const.TEMPLATE_ARTICLE_TITLE : self.get_property('title') + " - " + site_config.get("title")
        }
        content = utils.safe_apply_template(site_config.template , var_value_mapping)
        path = directory + "/" + utils.file_name(self.get_property('title')) + ".html"
        f = open(path, "w")
        f.write(content)

    def set_property_dict(self, property_dict):
        '''
        Whenever you call this method, you at first regulate the property_dict
        '''
        self.property = property_dict

    def get_property(self, key):
        if key in self.property.keys():
            return self.property[key]
        else:
            # 'title' is always set, so no worry of infinite calls of get_property
            print('Warning: Failed to get property ' + key + ' of article ' + self.get_property('title'))
            return ''