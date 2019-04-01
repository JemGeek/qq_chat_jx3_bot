# -*- coding:gbk -*-

import sys
reload(sys)
sys.setdefaultencoding('gbk')

CLASS_LIST = {
    'da_xia': '������',
    'tian_ce': '���',
    'chun_yang': '����',
    'shao_lin': '����',
    'qi_xiu': '����',
    'wan_hua': '��',
    'cang_jian': '�ؽ�',
    'wu_du': '�嶾',
    'tang_men': '����',
    'ming_jiao': '����',
    'gai_bang': 'ؤ��',
    'cang_yun': '����',
    'chang_ge': '����',
    'ba_dao': '�Ե�',
    'peng_lai': '����'
}

OLD_CLASS_LIST_TO_NEW_LIST = [
    'da_xia',
    'tian_ce',
    'chun_yang',
    'shao_lin',
    'qi_xiu',
    'wan_hua',
    'cang_jian',
    'wu_du',
    'tang_men',
    'ming_jiao',
    'gai_bang',
    'cang_yun',
    'chang_ge',
    'ba_dao',
    'peng_lai'
]

def convert_old_class_id_to_new_class_id(old_id):
    if old_id in OLD_CLASS_LIST_TO_NEW_LIST:
        return old_id
    return OLD_CLASS_LIST_TO_NEW_LIST[old_id]

class Jx3Class(object):
    _display_name = ''
    _name = ''

    def __init__(self, name, display_name):
        self._name = name
        self._display_name = display_name
    
    def get_display_name(self):
        return self._display_name
    
    def dump_data(self):
        return self._name