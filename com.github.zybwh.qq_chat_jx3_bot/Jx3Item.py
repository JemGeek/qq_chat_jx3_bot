# -*- coding:gbk -*-

import sys
reload(sys)
sys.setdefaultencoding('gbk')

import Utils

ITEM_LIST = {
    "zhen_cheng_zhi_xin": {
        "display_name": "���֮��",
        "rank": 2, 
        "cost": {"money": 999},
        'firework': [
            "    [CQ:face,id=145][CQ:face,id=145]    [CQ:face,id=145][CQ:face,id=145]    \n[CQ:face,id=145]         [CQ:face,id=145]         [CQ:face,id=145]\n    [CQ:face,id=145]                [CQ:face,id=145]\n          [CQ:face,id=145]    [CQ:face,id=145]\n               [CQ:face,id=145]",
            "����������������[CQ:at,qq={0}] ��ʿ�� [CQ:at,qq={1}] ��ʿʹ���˴�˵�еġ����֮�ġ����Դ������������䰮Ľ֮�ģ���������Ϊ�ˣ��������Ϊ����Хɽ����Ϊ֤����������Ϊƾ���Ӵ�ɽ�߲�����־����������У����겻�����⣬��˪�������顣��Ȼǰ·������Ұ���ཫ̹Ȼ�޾��̽����С��������������벻��������������������ӣ���"
        ]
    },
    "hai_shi_shan_meng": {"display_name": "����ɽ��", "rank": 1, "cost": {"money": 9999}},
    "jin_zhuan": {"display_name": "��ש", "rank": 5, "effect": {"money": 50}},
    "jin_ye_zi": {"display_name": "��Ҷ��", "rank": 6, "effect": {"money": 10}},
    "zhuan_shen_can": {"display_name": "ת���", "rank": 5, "effect": {"energy": 5}, "cost": {"money": 100}},
    "jia_zhuan_shen_can": {"display_name": "�ѡ�ת���", "rank": 3, "effect": {"energy": 30}, "cost": {"money": 500}},
    "rong_ding": {"display_name": "�۶�", "rank": 3, "effect": {'pve_weapon': 5}, "cost": {"banggong": 5000}},
    "mo_shi": {"display_name": "ĥʯ", "rank": 3, "effect": {'pvp_weapon': 5}, "cost": {"weiwang": 5000}},
    "ran": {"display_name": "��", "rank": 0, "effect": {'pve_armor': 10}},
    "xiu": {"display_name": "��", "rank": 4, "effect": {'pve_armor': 10}, "cost": {"banggong": 2000}},
    "yin": {"display_name": "ӡ", "rank": 4, "effect": {'pvp_armor': 10}, "cost": {"weiwang": 2000}},
    "sui_rou": {"display_name": "����", "rank": 4, "cost": {"money": 10}},
    "cu_bu": {"display_name": "�ֲ�", "rank": 4, "cost": {"money": 10}},
    "gan_cao": {"display_name": "�ʲ�", "rank": 4, "cost": {"money": 10}},
    "hong_tong": {"display_name": "��ͭ", "rank": 4, "cost": {"money": 10}},
    "hun_hun_zheng_ming": {"display_name": "���ץ��֤��", "rank": 0}
}

USER_STAT_DISPLAY = {
    'banggong': '',
    'weiwang': '',
    'money': '',
    'energy': ''
}

def load_item_data(data, item_list):
    return {k: {'object': item_list[k], 'count': v} for k, v in data.items()}

def get_item_display_name(item_name):
    return ITEM_LIST[item_name]['display_name'] if item_name in ITEM_LIST else ""

def Jx3Item(object):
    _name = ''
    _display_name = ''
    _rank = 0
    _cost = {}
    _effect = {}
    _firework = []

    def __init__(self, name, data):
        self._name = name
        self._display_name = data['display_name']
        self._rank = data['rank']
        self._cost = Utils.get_key_or_return_default(data, 'cost', {})
        self._effect = Utils.get_key_or_return_default(data, 'effect', {})
        self._firework = Utils.get_key_or_return_default(data, 'firework', [])
    
    def is_firework(self):
        return self._firework != []
    
    def use_item(self, user, amount, toQQ, group):
        if self._firework != []:
            return self.use_firework(user.get_qq_account_str(), toQQ, group)
        returnMsg = "[CQ:at,qq={0}]\nʹ�� {1} x {2}\n"
        for stat, v in self._effect.items():
            if stat in USER_STAT_DISPLAY:
                if stat == 'weiwang':
                    user.modify_weiwang(v * item_amount)
                elif stat == 'banggong':
                    user.modify_banggong(v * item_amount)
                elif stat == 'money':
                    user.modify_money(v * item_amount)
                elif stat == 'energy':
                    user.modify_energy(v * item_amount)
                returnMsg += "{0}+{1} ".format(USER_STAT_DISPLAY[stat], v * item_amount)
            elif k == 'pve_weapon':
                self.equipment[qq_account_str]['weapon']['pve'] += v * item_amount
                returnMsg += "\n����pve�˺�+{0}".format(v * item_amount)
                self._update_gear_point(qq_account_str)
            elif k == 'pvp_weapon':
                self.equipment[qq_account_str]['weapon']['pvp'] += v * item_amount
                returnMsg += "\n����pvp�˺�+{0}".format(v * item_amount)
                self._update_gear_point(qq_account_str)
            elif k == 'pve_armor':
                self.equipment[qq_account_str]['armor']['pve'] += v * item_amount
                returnMsg += "\n����pveѪ��+{0}".format(v * item_amount)
                self._update_gear_point(qq_account_str)
            elif k == 'pvp_armor':
                self.equipment[qq_account_str]['armor']['pvp'] += v * item_amount
                returnMsg += "\n����pvpѪ��+{0}".format(v * item_amount)
                self._update_gear_point(qq_account_str)
        return returnMsg

    def use_firework(self, fromQQ, toQQ, group):
        import CQSDK
        for msg in self._firework:
            if msg != "" and group != "":
                CQSDK.SendGroupMsg(int(group), msg.format(fromQQ, toQQ))
        return ""