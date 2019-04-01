# -*- coding:gbk -*-

import sys
reload(sys)
sys.setdefaultencoding('gbk')

import Utils

QIYU_LIST = {
    'hong_fu_qi_tian': {
        "display_name": '���˵�ͷ',
        "description": "��������ɱ���[CQ:at,qq={0}]��ʿǩ��ʱ�鸣���٣��������������������˵�ͷ����ǩ��ʱ��ö��⽱����",
        "chance": 0.1,
        "cooldown": 0,
        "reward": {"money": DALIY_MONEY_REWARD, "weiwang": DALIY_REWARD_MIN, "banggong": DALIY_REWARD_MIN}
    },
    'luan_shi_wu_ji': {
        "display_name": '�����輧',
        "description": "��������ɱ���[CQ:at,qq={0}]��ʿ���ݾ��޾��ף�������䴥�������������輧������Ƕ�������ϡ����������Ӱ���ң�",
        "chance": 0.01,
        "cooldown": 1 * 60 * 60,
        "reward": {"money": 200, "energy": 100}
    },
    'hu_xiao_shan_lin': {
        "display_name": '��Хɽ��',
        "description": "��������ɱ���[CQ:at,qq={0}]��ʿ����ԡѪ��ս��������䴥����������Хɽ�֡�������νʮ��ĥһ������©���â��ֻ�����ʳ���ն������­��",
        "chance": 0.05,
        "cooldown": 2 * 60 * 60,
        "reward": {"weiwang": 5000}
    },
    'hu_you_cang_sheng': {
        "display_name": '���Ӳ���',
        "description": "��������ɱ���[CQ:at,qq={0}]��ʿ���ı������ˣ�������䴥�����������Ӳ���������������ϵ��һ�ģ��˷��ص��ܷ�һ�絣�����乲�㣡",
        "chance": 0.05,
        "cooldown": 2 * 60 * 60,
        "reward": {"weiwang": 5000}
    },
    'fu_yao_jiu_tian': {
        "display_name": '��ҡ����',
        "description": "��������ɱ���[CQ:at,qq={0}]��ʿ�Ṧ������������������ҡ���졿������������ǧ���ҡ�쳾��",
        "chance": 0.01,
        "cooldown": 1 * 60 * 60,
        "reward": {"money": 200, "energy": 100}
    },
    'cha_guan_qi_yuan': {
        "display_name": '�����Ե',
        "description": "��������ɱ���[CQ:at,qq={0}]��ʿ���ڲ��������������䴥�������������Ե�������ǣ�߳�彭�����������˹˻������������ȴ�������Ƿǣ�",
        "chance": 0.05,
        "cooldown": 2 * 60 * 60,
        "require": {'money': 10000},
        "reward": {"money": 1000, "banggong": 5000}
    },
    'qing_feng_bu_wang': {
        "display_name": "��粶��",
        "description": "��������ɱ���[CQ:at,qq={0}]��ʿ��������������������䴥����������粶������",
        "chance": 0.05,
        "cooldown": 0,
        "reward": {"money": 500, "weiwang": 5000}
    },
    'san_shan_si_hai': {
        "display_name": "��ɽ�ĺ�",
        "description": "��������ɱ���[CQ:at,qq={0}]��ʿ�������飬������䴥����������ɽ�ĺ��������ǣ�������ɽ���ĺ����о����������",
        "chance": 0.01,
        "cooldown": 2 * 60 * 60,
        "reward": {"money": 1000}
    },
    'yin_yang_liang_jie': {
        "display_name": "��������",
        "description": "��������ɱ���[CQ:at,qq={0}]��ʿ��Ե��ǳ�������������������硿����ǧ����Ե�������������������������������",
        "chance": 0.05,
        "cooldown": 24 * 60 * 60,
        "require": {"pvp_gear_point": 3000, "pve_gear_point": 3000},
        "reward": {"money": 500, "weiwang": 5000}
    }
}

def convert_old_qiyu_to_new_list(old_qiyu):
    return {'unknown': {'object': None, 'count': old_qiyu}}

class Jx3Qiyu(object):
    _name = ''
    _display_name = ''
    _description = ''
    _chance = 0
    _cooldown = 0
    _reward = {}
    _require = {}

    def __init__(self, name, data):
        self._name = name
        self._display_name = data['display_name']
        self._description = data['description']
        self._chance = data['chance']
        self._cooldown = data['cooldown']
        self._reward = data['reward']
        self._require = Utils.get_key_or_return_default(data, 'require', {})
    
