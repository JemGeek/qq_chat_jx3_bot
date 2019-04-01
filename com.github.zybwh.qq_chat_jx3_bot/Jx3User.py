# -*- coding:gbk -*-

import sys
reload(sys)
sys.setdefaultencoding('gbk')

import Utils
import Jx3Item

import time
import copy

daliy_dict = {
    'qiandao': False,
    'speech_count': 0,
    'ya_biao': 0,
    'wa_bao': {'count': 0, 'last_time': None},
    'jailed': 0,
    'cha_guan': {'complete_quest': [], 'current_quest': ""},
    "speech_energy_gain": 0,
    'rob': {'weiwang': 0, 'money': 0, 'last_rob_time': None},
    'practise': {'weiwang': 0},
    'jjc': {'score': 0, 'last_time': None, 'win': 0, 'lose': 0}
}

default_equipment = {
    'weapon': {"display_name": "������", 'pvp': 10, 'pve': 10}, 
    'armor': {"display_name": "������", 'pvp': 100, 'pve': 100}
}

class Jx3User(object):

    _qq_account_str = ""
    _class_ptr = None
    _faction_ptr = None
    _faction_join_time = None

    _weiwang = 0
    _money = 0
    _banggong = 0
    _energy = 0

    _achievement = {}

    _lover = ""
    _lover_time = None

    _qiyu = {}

    register_time = None    
    _qiandao_count = 0

    _today = 0
    _daliy_count = {}

    _bag = {}
    _equipment = {}

    def __init__(self, data={})
        if data == {}:
            return
        self._qq_account_str = data['qq_account_str']
        self._class_ptr = Utils.get_key_or_return_default(data, 'class_ptr', None)
        self._faction_ptr = Utils.get_key_or_return_default(data, 'faction_ptr', None)
        self._faction_join_time = Utils.get_key_or_return_default(data, 'faction_join_time', None)

        self._weiwang = Utils.get_key_or_return_default(data, 'weiwang', 0)
        self._banggong = Utils.get_key_or_return_default(data, 'banggong', 0)
        self._money = Utils.get_key_or_return_default(data, 'money', 0)
        self._energy = Utils.get_key_or_return_default(data, 'energy', 0)

        self._achievement = Utils.get_key_or_return_default(data, 'achievement', {})
        
        self._lover = Utils.get_key_or_return_default(data, 'lover', "")
        self._lover_time = Utils.get_key_or_return_default(data, 'lover_time', None)

        self._qiyu = Utils.get_key_or_return_default(data, 'qiyu', {})
        self.register_time = Utils.get_key_or_return_default(data, 'register_time', time.time())
        self._qiandao_count = Utils.get_key_or_return_default(data, 'qiandao_count', 0)

        self._bag = Utils.get_key_or_return_default(data, 'bag', {})
        self._equipment = Utils.get_key_or_return_default(data, 'equipment', copy.deepcopy(default_equipment))

        self._today = Utils.get_key_or_return_default(data, 'today', 0)
        self._daliy_count = Utils.get_key_or_return_default(data, 'daliy_count', {})

    def dump_data(self):
        return {
            'qq_account_str': self._qq_account_str,
            'class_ptr': self._class_ptr.dump_data(),
            'faction_ptr': self._faction_ptr.dump_data(),
            'faction_join_time': self._faction_join_time,
            'weiwang': self._weiwang,
            'banggong': self._banggong,
            'money': self._money,
            'energy': self._energy,
            'achievement': self._achievement,
            'lover': self._lover,
            'lover_time': self._lover_time,
            'qiyu': {k: v['count'] for k, v in self_qiyu.items()},
            'register_time': self._register_time,
            'bag': {k, v['count'] for k, v in self._bag.items()},
            'equipment': self._equipment,
            'today': self._today,
            'daliy_count': self._daliy_count
        }
    
    def get_info(self, qq_group):
        return "[CQ:at,qq={0}]\n��Ե:\t\t{1}\n����:\t\t{2}\n��Ӫ:\t\t{3}\n����:\t\t{4}\n�ﹱ:\t\t{5}\n��Ǯ:\t\t{6}G\n����:\t{7}\nǩ��״̬:\t{8}\n����:\t\t{9}\n���շ���:\t{10}".format(
            self._qq_account_str,
            "" if self._lover == 0 else Utils.get_group_nick_name(int(qq_group), int(self._lover)),
            self._class_ptr.get_display_name(),
            self._faction_ptr.get_display_name(),
            self._weiwang,
            self._banggong,
            self._money,
            self._energy,
            self._daliy_count['qiandao'],
            0,
            self._daliy_count['speech_count'])
    
    def qiandao(self, weiwang_reward, banggong_reward, money_reward, energy_gain):
        self.modify_weiwang(weiwang_reward)
        self.modify_banggong(banggong_reward)
        self.modify_money(money_reward)
        self.modify_energy(energy_gain)
        
        self._qiandao_count += 1

        self._daliy_count['qiandao'] = True
        returnMsg = "[CQ:at,qq={0}] ǩ���ɹ���ǩ������: ����+{1} �ﹱ+{2} ��Ǯ+{3} ����+{4}".format(
            qq_account,
            weiwang_reward,
            banggong_reward,
            money_reward,
            energy_gain)
        
        faction_reward = self._faction_ptr.get_yesterday_faction_reward()

        if faction_reward != 0:
            self._weiwang += faction_reward
            returnMsg += "\n���������Ӫ����������+{0}".format(faction_reward)
        
        return returnMsg
    
    def modify_weiwang(self, weiwang_reward):
        self._weiwang += int(weiwang_reward)
    
    def modify_banggong(self, banggong_reward):
        self._banggong += int(banggong_reward)
    
    def modify_money(self, money_reward):
        self._money += int(money_reward)
    
    def modify_energy(self, energy_reward):
        self._energy += int(energy_reward)

    def has_qiandao(self):
        return self._daliy_count['qiandao']
    
    def has_energy(self, energy_require):
        return self._energy >= energy_require

    def add_speech_count(self, speech_energy_gain, max_speech_energy_gain):
        self._daliy_count['speech_count'] += 1

        if self._daliy_count['speech_energy_gain'] < max_speech_energy_gain:
            self._daliy_count['speech_energy_gain'] += speech_energy_gain
            self.modify_energy(speech_energy_gain)
    
    def can_ya_biao(self, daliy_max_ya_biao_count):
        return self._daliy_count['ya_biao'] < daliy_max_ya_biao_count

    def ya_biao(self, weiwang_reward, money_reward, energy_cost):
        self.modify_weiwang(weiwang_reward)
        self.modify_money(money_reward)
        self.modify_energy(0 - energy_cost)
        self._daliy_count['ya_biao'] += 1

    def get_faction(self):
        return self._faction_ptr
    
    def get_faction_join_time(self):
        return self._faction_join_time
    
    def get_lover(self):
        return self._lover
    
    def get_qq_account_str(self):
        return self._qq_account_str
    
    def addd_lover(self, lover_str):
        self._lover = lover_str
        self._lover_time = time.time()

    def join_faction(self, faction_ptr):
        self._faction_ptr.remove_member(self._qq_account_str)
        self._faction_ptr = faction_ptr
        self._faction_ptr.add_member(self._qq_account_str)
        self._faction_join_time = time.time()
    
    def display_bag(self):
        returnMsg = ""
        for item_name, v in self._bag.items():
            if v['amount'] != 0:
                returnMsg += "\n{0} x {1}".format(v['object'].get_display_name(), v['amount'])
        
        if returnMsg == "":
            returnMsg = "\n�տ���Ҳ"
        return returnMsg
    
    def check_item(self, item_name):
        return item_name in self.bag

    def use_item(self, item_name, amount=1, toQQ="", qq_group=""):
        returnMsg = self._bag[item_name]['object'].use_item(self, amount, toQQ, qq_group)
        self._bag[item_name]['amount'] -= amount
        if self._bag[item_name]['amount'] == 0:
            self.bag.pop(item_name)
        return returnMsg
    
    def buy_item(self, item, amount):
        if item not in self.bag:
            self.bag[item] = 0
        returnMsg = item(self, amount)
        self.bag[item] += amount
        return returnMsg
    
    def reset_daliy_count(self, yday, keep_jjc_data=False):
        return_dict = {}
        if yday != self._today:
            new_daliy = copy.deepcopy(daliy_dict)
            if keep_jjc_data:
                new_daliy['jjc'] = copy.deepcopy(self._daliy_count['jjc'])
            else:
                return_dict = copy.deepcopy(self._daliy_count['jjc'])
            self._daliy_count = new_daliy
            self._today = yday
        
        return return_dict

    def get_pve_gear_point(self):
        weapon = equipment['weapon']
        armor = equipment['armor']
        return weapon['pve'] * 50 + armor['pve'] * 10
    
    def get_pvp_gear_point(self):
        weapon = equipment['weapon']
        armor = equipment['armor']
        return weapon['pvp'] * 50 + armor['pvp'] * 10
    


