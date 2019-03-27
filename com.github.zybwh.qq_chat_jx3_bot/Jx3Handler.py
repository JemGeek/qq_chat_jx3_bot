# -*- coding:gbk -*-

import sys
reload(sys)
sys.setdefaultencoding('gbk')

import os
import logging
import time
import math

logging.basicConfig(
    level       = logging.INFO,
    format      = '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    datefmt     = '%Y-%m-%d %H:%M:%S',
    filename    = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'CQHanlder.log'),
    filemode    = 'w+'
)

import sqlite3
import json
import copy
import random

from threading import Lock

DATABASE_PATH = os.path.join('data', 'app', 'com.github.qq_jx3_chat_bot')

DATA_JSON_FILE = os.path.join(DATABASE_PATH, 'jx3.json')
DATA_JSON_FILE_OLD = os.path.join(DATABASE_PATH, 'jx3.json.old')
DATA_JSON_FILE_OLD_2 = os.path.join(DATABASE_PATH, 'jx3.json.old2')

LOVE_ITEM_REQUIRED = "zhen_cheng_zhi_xin"

DALIY_REFRESH_OFFSET = 7 * 60 * 60
DALIY_COUNT_SAVE_DAY = 3
DALIY_REWARD_MIN = 1000
DALIY_REWARD_MAX = 3000
DALIY_ENERGY_REWARD = 500
DALIY_MONEY_REWARD = 100

DALIY_MAX_SPEECH_ENERGY_GAIN = 500
SPEECH_ENERGY_GAIN = 5

YA_BIAO_ENERGY_REQUIRED = 100
MAX_DALIY_YA_BIAO_COUNT = 3
DALIY_YA_BIAO_REWARD_MIN = 4000
DALIY_YA_BIAO_REWARD_MAX = 6000
DALIY_YA_BIAO_MONEY_REWARD = 50

WA_BAO_ENERGY_REQUIRED = 50
MAX_DALIY_WA_BAO_COUNT = 10
WA_BAO_COOLDOWN = 10 * 60
WA_BAO_RARE_FACTOR = 2

MAX_DALIY_CHA_GUAN_COUNT = 5
CHA_GUAN_ENERGY_COST = 30

FACTION_REJOIN_CD_SECS = 24 * 60 * 60
FACTION_TRANSFER_WEIWANG_COST = 20000
NO_FACTION_ALLOW_YA_BIAO = False

ROB_ENERGY_COST = 50
ROB_PROTECT_COUNT = 2
ROB_PROTECT_DURATION = 60 * 60

WANTED_MONEY_REWARD = 1000
WANTED_DURATION = 24 * 60 * 60
WANTED_COOLDOWN = 10 * 60
WANTED_ENERGY_COST = 50

JAIL_DURATION = 1 * 60 * 60
JAIL_TIMES_PROTECTION = 2

FACTION_DISPLAY_NAME = ['����', '���˹�', '������']

ITEM_LIST = [
    {"name": "zhen_cheng_zhi_xin", "display_name": "���֮��", "rank": 2, "cost": {"money": 999}},
    {"name": "hai_shi_shan_meng", "display_name": "����ɽ��", "rank": 1, "cost": {"money": 9999}},
    {"name": "jin_zhuan", "display_name": "��ש", "rank": 5, "effect": {"money": 50}},
    {"name": "jin_ye_zi", "display_name": "��Ҷ��", "rank": 6, "effect": {"money": 10}},
    {"name": "zhuan_shen_can", "display_name": "ת���", "rank": 4, "effect": {"energy": 50}, "cost": {"money": 100}},
    {"name": "jia_zhuan_shen_can", "display_name": "�ѡ�ת���", "rank": 3, "effect": {"energy": 300}, "cost": {"money": 500}},
    {"name": "rong_ding", "display_name": "�۶�", "rank": 4, "effect": {'pve_weapon': 5}, "cost": {"banggong": 5000}},
    {"name": "mo_shi", "display_name": "ĥʯ", "rank": 4, "effect": {'pvp_weapon': 5}, "cost": {"weiwang": 5000}},
    {"name": "ran", "display_name": "��", "rank": 4, "effect": {'pve_armor': 10}, "cost": {"banggong": 2000}},
    {"name": "yin", "display_name": "ӡ", "rank": 4, "effect": {'pvp_armor': 10}, "cost": {"weiwang": 2000}},
    {"name": "sui_rou", "display_name": "����", "rank": 6, "cost": {"money": 10}},
    {"name": "cu_bu", "display_name": "�ֲ�", "rank": 6, "cost": {"money": 10}},
    {"name": "gan_cao", "display_name": "�ʲ�", "rank": 6, "cost": {"money": 10}},
    {"name": "hong_tong", "display_name": "��ͭ", "rank": 6, "cost": {"money": 10}},
    {"name": "hun_hun_zheng_ming", "display_name": "���ץ��֤��", "rank": 0}
]

CHA_GUAN_QUEST_INFO = {
    "cha_guan_sui_rou": {"display_name": "��ݣ�����", 
                            "description": "��Ҫ�ύһ�����⣬�����̵깺��",
                            "require": {"sui_rou": 1},
                            "reward": {"money": 50, "banggong": 500}},
    "cha_guan_cu_bu": {"display_name": "��ݣ��ֲ�", 
                            "description": "��Ҫ�ύһ�ݴֲ��������̵깺��",
                            "require": {"cu_bu": 1},
                            "reward": {"money": 50, "banggong": 500}},
    "cha_guan_gan_cao": {"display_name": "��ݣ��ʲ�", 
                            "description": "��Ҫ�ύһ�ݸʲݣ������̵깺��",
                            "require": {"gan_cao": 1},
                            "reward": {"money": 50, "banggong": 500}},
    "cha_guan_hong_tong": {"display_name": "��ݣ���ͭ", 
                            "description": "��Ҫ�ύһ�ݺ�ͭ�������̵깺��",
                            "require": {"hong_tong": 1},
                            "reward": {"money": 50, "banggong": 500}},
    "cha_guan_hun_hun": {"display_name": "��ݣ�ץ�����", 
                            "description": "ץ�����������ʹ��ָ�� ץ�����",
                            "require": {"hun_hun_zheng_ming": 3},
                            "reward": {"money": 50, "banggong": 500}}
}

NPC_LIST = {
    "hun_hun": {
        "equipment": {'weapon': {"display_name": "����", 'pvp': 0, 'pve': 10}, 
                        'armor': {"display_name": "�����", 'pvp': 0, 'pve': 50}},
        "reward": {"money": 50},
        "reward_chance": 0.5
    }
}

QIYU_LIST = {
    'hong_fu_qi_tian': {"description": "��������ɱ���[CQ:at,qq={0}]��ʿ���˵�ͷ��ǩ��ʱ��ö��⽱����",
                        "chance": 0.1,
                        "cooldown": 0,
                        "reward": {"money": DALIY_MONEY_REWARD, "weiwang": DALIY_REWARD_MAX, "banggong": DALIY_REWARD_MAX}},
    'luan_shi_wu_ji': {"description": "��������ɱ���[CQ:at,qq={0}]��ʿ���ݾ��޾��ף�������䴥�������������輧������Ƕ�������ϡ����������Ӱ���ң�",
                        "chance": 0.01,
                        "cooldown": 1 * 60 * 60,
                        "reward": {"money": 200, "energy": 100}},
    'hu_xiao_shan_lin': {"description": "��������ɱ���[CQ:at,qq={0}]��ʿ����ԡѪ��ս��������䴥����������Хɽ�֡�������νʮ��ĥһ������©���â��ֻ�����ʳ���ն������­��",
                        "chance": 0.05,
                        "cooldown": 2 * 60 * 60,
                        "reward": {"weiwang": 5000}},
    'hu_you_cang_sheng': {"description": "��������ɱ���[CQ:at,qq={0}]��ʿ���ı������ˣ�������䴥�����������Ӳ���������������ϵ��һ�ģ��˷��ص��ܷ�һ�絣�����乲�㣡",
                        "chance": 0.05,
                        "cooldown": 0,
                        "reward": {"weiwang": 5000}},
    'fu_yao_jiu_tian': {"description": "��������ɱ���[CQ:at,qq={0}]��ʿ�Ṧ������������������ҡ���졿������������ǧ���ҡ�쳾��",
                        "chance": 0.01,
                        "cooldown": 1 * 60 * 60,
                        "reward": {"money": 200, "energy": 100}},
    'cha_guan_qi_yuan': {"description": "��������ɱ���[CQ:at,qq={0}]��ʿ���ڲ��������������䴥�������������Ե�������ǣ�߳�彭�����������˹˻������������ȴ�������Ƿǣ�",
                        "chance": 0.05,
                        "cooldown": 2 * 60 * 60,
                        "require": {'money': 10000},
                        "reward": {"money": 1000, "banggong": 5000}},
    'qing_feng_bu_wang': {"description": "��������ɱ���[CQ:at,qq={0}]��ʿ��������������������䴥����������粶������",
                        "chance": 0.05,
                        "cooldown": 0,
                        "reward": {"money": 500, "weiwang": 5000}},
    'san_shan_si_hai': {"description": "��������ɱ���[CQ:at,qq={0}]��ʿ�������飬������䴥����������ɽ�ĺ��������ǣ�������ɽ���ĺ����о����������",
                        "chance": 0.01,
                        "cooldown": 2 * 60 * 60,
                        "reward": {"money": 1000}},
    'yin_yang_liang_jie': {"description": "��������ɱ���[CQ:at,qq={0}]��ʿ��Ե��ǳ�������������������硿����ǧ����Ե�������������������������������",
                        "chance": 0.05,
                        "cooldown": 24 * 60 * 60,
                        "require": {"pvp_gear_point": 3000, "pve_gear_point": 3000},
                        "reward": {"money": 500, "weiwang": 5000}},
}

STAT_DISPLAY_NAME = {
    "weiwang": "����",
    "banggong": "�ﹱ",
    "money": "��Ǯ",
    "energy": "����"
}

QIYU_CHANCE = 0.1

def calculateRemainingTime(duration, last_time):
    remain_secs = int(math.floor(duration - (time.time() - last_time)))
    hours = remain_secs // 3600
    mins = (remain_secs - hours * 3600) // 60
    secs = remain_secs - hours * 3600 - mins * 60
    return {'hours': hours, 'mins': mins, 'secs': secs}

def calculateGearPoint(equipment):
    weapon = equipment['weapon']
    armor = equipment['armor']
    return {'pve': weapon['pve'] * 50 + armor['pve'] * 10, 'pvp': weapon['pvp'] * 50 + armor['pvp'] * 10}

def get_wa_bao_reward():
    max_index = 0
    wa_bao_items = {}
    for item in random.sample(ITEM_LIST, len(ITEM_LIST)):
        if item['rank'] != 0 and get_key_or_return_default(item, 'wa_bao', True):
            new_max_index = max_index + pow(item['rank'], WA_BAO_RARE_FACTOR)
            wa_bao_items[item['name']] = {'min': max_index, 'max': new_max_index}
            max_index = new_max_index
    
    rand_index = random.uniform(0, max_index)
    logging.info("wa_bao items: {1} rand index: {0}".format(rand_index, wa_bao_items))
    for item_name, min_max in wa_bao_items.items():
        if rand_index >= min_max['min'] and rand_index < min_max['max']:
            return item_name
    
    return ""

def isItemExists(item_name):
    return len([v for v in ITEM_LIST if v['name'] == item_name]) > 0

def print_cost(item_cost):
    returnMsg = ""
    for k, v in item_cost.items():
        if k in STAT_DISPLAY_NAME:
            returnMsg += "\n{0}��{1}".format(STAT_DISPLAY_NAME[k], v)
    return returnMsg

def find_item(item_display_name):
    for v in ITEM_LIST:
        if v['display_name'] == item_display_name:
            return v
    return None

def get_item_display_name(item_name):
    for v in ITEM_LIST:
        if v['name'] == item_name:
            return v['display_name']
    return ""

def isItemBuyable(item):
    return 'cost' in item

def isItemUsable(item):
    return 'effect' in item

def getGroupNickName(fromGroup, fromQQ):
    import CQSDK
    from CQGroupMemberInfo import CQGroupMemberInfo
    info = CQGroupMemberInfo(CQSDK.GetGroupMemberInfoV2(fromGroup, fromQQ))
    return info.Card if info.Card != None and info.Card != "" else info.Nickname

def use_zhen_cheng_zhi_xin(fromGroup, fromQQ, toQQ):
    import CQSDK
    try:
        CQSDK.SendGroupMsg(fromGroup, "    [CQ:face,id=145][CQ:face,id=145]    [CQ:face,id=145][CQ:face,id=145]    \n[CQ:face,id=145]         [CQ:face,id=145]         [CQ:face,id=145]\n    [CQ:face,id=145]                [CQ:face,id=145]\n          [CQ:face,id=145]    [CQ:face,id=145]\n               [CQ:face,id=145]")
        CQSDK.SendGroupMsg(fromGroup, "����������������[CQ:at,qq={0}] ��ʿ�� [CQ:at,qq={1}] ��ʿʹ���˴�˵�еġ����֮�ġ����Դ������������䰮Ľ֮�ģ���������Ϊ�ˣ��������Ϊ����Хɽ����Ϊ֤����������Ϊƾ���Ӵ�ɽ�߲�����־����������У����겻�����⣬��˪�������顣��Ȼǰ·������Ұ���ཫ̹Ȼ�޾��̽����С��������������벻��������������������ӣ���".format(fromQQ, toQQ))
    except Exception as e:
            logging.exception(e)


def isTimeSame(time_struct_1, time_struct_2):
    return time_struct_1.tm_year == time_struct_2.tm_year and time_struct_1.tm_yday == time_struct_2.tm_yday 

def get_key_or_return_default(dictionary, key, default_value):
    if key in dictionary:
        return dictionary[key]
    else:
        return default_value

def get_faction_display_name(faction_id):
    return FACTION_DISPLAY_NAME[faction_id] if faction_id >= 0 and faction_id < len(FACTION_DISPLAY_NAME) else ""

class Jx3Handler(object):

    commandList = [
        "�鿴", "�鿴װ��", "����",
        "ǩ��",
        "Ѻ��",
        "����Ե",
        "������Ӫ",
        "�˳���Ӫ",
        "ת����Ӫ",
        "���",
        "����",
        "ʹ��",
        "�̵�",
        "�ڱ�",
        "�鿴��Ӫ", 
        "�鿴����",
        "����", "ץ��",
        "pveװ������", "pvpװ������", "��������", "��������", "��������", "��������", "��������", "���߸���",
        "���",
        "������", "ץ�����"]

    jx3_users = {}
    lover_pending = {}
    daliy_action_count = {}
    rob_protect = {}
    equipment = {}
    wanted_list = {}
    jail_list = {}
    qiyu_status = {}

    def __init__(self, qq_group):
        logging.info('Jx3Handler __init__')
        self.qq_group = qq_group # int

        self.json_file_folder = os.path.join(DATABASE_PATH, str(qq_group))
        self.json_file_path = os.path.join(self.json_file_folder, 'data.json')
        self.json_file_path_old = os.path.join(self.json_file_folder, 'data.json.old')
        self.json_file_path_old_2 = os.path.join(self.json_file_folder, 'data.json.old2')

        if not os.path.exists(self.json_file_folder):
            logging.info("path not exist. create a new one: {0}", self.json_file_folder)
            os.makedirs(self.json_file_folder)

        if os.path.exists(self.json_file_path):
            load_old_file = False
            try:
                with open(self.json_file_path, 'r') as f:
                    data = json.loads(f.readline(), encoding='gbk')
                    self.jx3_users = copy.deepcopy(get_key_or_return_default(data, "jx3_users", {}))
                    self.lover_pending = copy.deepcopy(get_key_or_return_default(data, "lover_pending", {}))
                    self.daliy_action_count = copy.deepcopy(get_key_or_return_default(data, "daliy_action_count", {}))
                    self.rob_protect = copy.deepcopy(get_key_or_return_default(data, "rob_protect", {}))
                    self.equipment = copy.deepcopy(get_key_or_return_default(data, "equipment", {}))
                    self.wanted_list = copy.deepcopy(get_key_or_return_default(data, "wanted_list", {}))
                    self.jail_list = copy.deepcopy(get_key_or_return_default(data, "jail_list", {}))
                    self.qiyu_status = copy.deepcopy(get_key_or_return_default(data, "qiyu_status", {}))
                    logging.info("loading complete")
            except Exception as e:
                load_old_file = True
                logging.exception(e)
            
            if load_old_file and os.path.exists(self.json_file_path_old):
                try:
                    with open(self.json_file_path_old, 'r') as f:
                        data = json.loads(f.readline(), encoding='gbk')
                        self.jx3_users = copy.deepcopy(get_key_or_return_default(data, "jx3_users", {}))
                        self.lover_pending = copy.deepcopy(get_key_or_return_default(data, "lover_pending", {}))
                        self.daliy_action_count = copy.deepcopy(get_key_or_return_default(data, "daliy_action_count", {}))
                        self.rob_protect = copy.deepcopy(get_key_or_return_default(data, "rob_protect", {}))
                        self.equipment = copy.deepcopy(get_key_or_return_default(data, "equipment", {}))
                        self.wanted_list = copy.deepcopy(get_key_or_return_default(data, "wanted_list", {}))
                        self.jail_list = copy.deepcopy(get_key_or_return_default(data, "jail_list", {}))
                        self.qiyu_status = copy.deepcopy(get_key_or_return_default(data, "qiyu_status", {}))
                        logging.info("loading old file complete")
                except Exception as e:
                    logging.exception(e)

        self.mutex = Lock()
        
    def __del__(self):
        logging.info('Jx3Handler __del__')

    def writeToJsonFile(self):
        returnMsg = ""
        self.mutex.acquire()
        try:
            if os.path.exists(self.json_file_path_old):
                if os.path.exists(self.json_file_path_old_2):
                    os.remove(self.json_file_path_old_2)
                os.rename(self.json_file_path_old, self.json_file_path_old_2)
            
            if os.path.exists(self.json_file_path):
                if os.path.exists(self.json_file_path_old):
                    os.remove(self.json_file_path_old)
                os.rename(self.json_file_path, self.json_file_path_old)

            with open(self.json_file_path, 'w', ) as f:
                data = {
                    "jx3_users": self.jx3_users,
                    "lover_pending": self.lover_pending,
                    "daliy_action_count": self.daliy_action_count,
                    "rob_protect": self.rob_protect,
                    "equipment": self.equipment,
                    "wanted_list": self.wanted_list,
                    "jail_list": self.jail_list,
                    "qiyu_status": self.qiyu_status
                }
                f.write(json.dumps(data, ensure_ascii=False, encoding='gbk'))
        except Exception as e:
            logging.exception(e)
        self.mutex.release()

    
    def _reset_daliy_count(self, qq_account_str):
        yday = time.localtime(time.time() - DALIY_REFRESH_OFFSET).tm_yday
        yday_str = str(yday)
        if yday_str not in self.daliy_action_count:
            self.daliy_action_count[yday_str] = {}
            for k in self.daliy_action_count:
                if int(k) < yday - DALIY_COUNT_SAVE_DAY:
                    self.daliy_action_count.pop(k)

        if qq_account_str not in self.daliy_action_count[yday_str]:
            self.daliy_action_count[yday_str][qq_account_str] = {
                'qiandao': False,
                'speech_count': 0,
                'ya_biao': 0,
                'wa_bao': {'count': 0, 'last_time': None},
                'jailed': 0,
                'cha_guan': {'complete_quest': [], 'current_quest': ""},
                "speech_energy_gain": 0
            }

        return yday
    
    def getCommandList(self):
        return self.commandList

    def register(self, qq_account):
        returnMsg = ""
        try:
            self.mutex.acquire()

            qq_account_str = str(qq_account)
            if qq_account_str in self.jx3_users.keys():
                returnMsg = "[CQ:at,qq={0}] ע��ʧ�ܣ����Ѿ�ע����ˡ�".format(qq_account)
            else:
                self.equipment[qq_account_str] = {
                    'weapon': {"display_name": "������", 'pvp': 10, 'pve': 10}, 
                    'armor': {"display_name": "������", 'pvp': 100, 'pve': 100}
                }
            
                gear_point = calculateGearPoint(self.equipment[qq_account_str])

                self.jx3_users[qq_account_str] = {
                    "class_id": 0,
                    "faction_id": 0,
                    "faction_join_time": None,
                    "weiwang": 0,
                    "banggong": 0,
                    "money": 0,
                    "pvp_gear_point": gear_point['pvp'],
                    "pve_gear_point": gear_point['pve'],
                    "achievement": 0,
                    "lover": 0,
                    "lover_time": None,
                    "qiyu": 0,
                    "energy": 0,
                    "register_time": time.time(),
                    "qiandao_count": 0,
                    "bag": {}
                }
                returnMsg = "ע��ɹ���\n[CQ:at,qq={0}]\nע��ʱ�䣺{1}".format(qq_account, time.strftime('%Y-%m-%d', time.localtime(self.jx3_users[qq_account_str]["register_time"])))
        
            self.mutex.release()
            return returnMsg
        except Exception as e:
            logging.exception(e)
        finally:
            self.writeToJsonFile()
    
    def isUserRegister(self, qq_account):
        try:
            return str(qq_account) in self.jx3_users.keys()
        except Exception as e:
            logging.exception(e)
    
    # TODO: not thread safe
    def _update_gear_point(self, qq_account_str):
        gear_point = calculateGearPoint(self.equipment[qq_account_str])
        self.jx3_users[qq_account_str]['pve_gear_point'] = gear_point['pve']
        self.jx3_users[qq_account_str]['pvp_gear_point'] = gear_point['pvp']
    
    def getInfo(self, qq_group, qq_account):
        returnMsg = ""
        try:
            self.mutex.acquire()
            qq_account_str = str(qq_account)
            self._update_gear_point(qq_account_str)

            val = self.jx3_users[qq_account_str]
            self.mutex.release()

            yday = self._reset_daliy_count(qq_account_str)
            yday_str = str(yday)

            if self.daliy_action_count[yday_str][qq_account_str]['qiandao']:
                qiandao_status = "��ǩ��"
            else:
                qiandao_status = "δǩ��"

            return "[CQ:at,qq={0}]\n��Ե:\t\t{1}\n����:\t\t{2}\n��Ӫ:\t\t{3}\n����:\t\t{4}\n�ﹱ:\t\t{5}\n��Ǯ:\t\t{6}G\nPVPװ��:\t{7}\nPVEװ��:\t{8}\n����:\t\t{9}\nǩ��״̬:\t{10}\nǩ������:\t{11}\n����:\t\t{12}\nע��ʱ��:\t{13}\n���շ���:\t{14}\n����:\t\t{15}".format(
                    qq_account,
                    "" if val['lover'] == 0 else getGroupNickName(qq_group, val['lover']),
                    "������" if val['class_id'] == 0 else val['class_id'],
                    get_faction_display_name(val['faction_id']),
                    val['weiwang'],
                    val['banggong'],
                    int(val['money']),
                    val['pvp_gear_point'],
                    val['pve_gear_point'],
                    val['achievement'],
                    qiandao_status,
                    val['qiandao_count'],
                    val['qiyu'],
                    time.strftime('%Y-%m-%d', time.localtime(val['register_time'])),
                    self.daliy_action_count[yday_str][qq_account_str]['speech_count'],
                    val['energy'])

        except Exception as e:
            logging.exception(e)

    def qianDao(self, qq_account):
        returnMsg = ""
        try:
            qq_account_str = str(qq_account)
            self.mutex.acquire()
            val = self.jx3_users[qq_account_str]
            
            yday = self._reset_daliy_count(qq_account_str)
            yday_str = str(yday)

            if self.daliy_action_count[yday_str][qq_account_str]['qiandao']:
                returnMsg = "[CQ:at,qq={0}]�����Ѿ�ǩ������!".format(qq_account)
            else:
                banggong_reward = random.randint(DALIY_REWARD_MIN, DALIY_REWARD_MAX)
                weiwang_reward = random.randint(DALIY_REWARD_MIN, DALIY_REWARD_MAX)
                self.jx3_users[qq_account_str]['weiwang'] += weiwang_reward
                self.jx3_users[qq_account_str]['banggong'] += banggong_reward
                self.jx3_users[qq_account_str]['qiandao_count'] += 1
                self.jx3_users[qq_account_str]['energy'] += DALIY_ENERGY_REWARD
                self.jx3_users[qq_account_str]['money'] += DALIY_MONEY_REWARD
                
                self.daliy_action_count[yday_str][qq_account_str]['qiandao'] = True

                returnMsg = "[CQ:at,qq={0}] ǩ���ɹ�!\n����ǩ������:\n����+{1}\n�ﹱ+{2}\n��Ǯ+{3}\n����+{4}".format(
                                qq_account,
                                weiwang_reward,
                                banggong_reward,
                                DALIY_MONEY_REWARD,
                                DALIY_ENERGY_REWARD)
            
            self.mutex.release()
            return returnMsg
        except Exception as e:
            logging.exception(e)
        finally:
            self.writeToJsonFile()
    
    def addSpeechCount(self, qq_account):
        try:
            qq_account_str = str(qq_account)
            self.mutex.acquire()

            yday = self._reset_daliy_count(qq_account_str)
            yday_str = str(yday)

            self.daliy_action_count[yday_str][qq_account_str]['speech_count'] += 1

            if 'speech_energy_gain' not in self.daliy_action_count[yday_str][qq_account_str]:
                self.daliy_action_count[yday_str][qq_account_str]['speech_energy_gain'] = 0
            
            if self.daliy_action_count[yday_str][qq_account_str]['speech_energy_gain'] < DALIY_MAX_SPEECH_ENERGY_GAIN:
                self.daliy_action_count[yday_str][qq_account_str]['speech_energy_gain'] += SPEECH_ENERGY_GAIN
                self.jx3_users[qq_account_str]['energy'] += SPEECH_ENERGY_GAIN
            
            self.mutex.release()

        except Exception as e:
            logging.exception(e)
        finally:
            self.writeToJsonFile()
    
    def addLover(self, fromQQ, toQQ):
        returnMsg = ""
        try:
            self.mutex.acquire()

            if str(toQQ) not in self.jx3_users.keys():
                returnMsg = "[CQ:at,qq={0}] ��û��ע��Ŷ������ע���ٰ���Ե��".format(toQQ)
            else:
                fromQQ_stat = self.jx3_users[str(fromQQ)]
                toQQ_stat = self.jx3_users[str(toQQ)]

                if LOVE_ITEM_REQUIRED != "" and LOVE_ITEM_REQUIRED not in fromQQ_stat['bag'].keys():
                    returnMsg = "[CQ:at,qq={0}] ����Ե��Ҫ����1��{1}��\n�㲢û�д���Ʒ�����ȹ���".format(fromQQ, get_item_display_name(LOVE_ITEM_REQUIRED))
                else:
                    if str(fromQQ_stat['lover']) == str(toQQ):
                        returnMsg = "[CQ:at,qq={0}] �����Ѿ��󶨹�������������������".format(fromQQ)
                    elif fromQQ_stat['lover'] != 0:
                        returnMsg = "[CQ:at,qq={0}]  ��ʲô�أ���Ͳ���[CQ:at,qq={1}]������".format(fromQQ, fromQQ_stat['lover'])
                    elif toQQ_stat['lover'] != 0:
                        returnMsg = "[CQ:at,qq={0}] �˼��Ѿ�����Ե������������818��".format(fromQQ)
                    elif toQQ in self.lover_pending and self.lover_pending[str(toQQ)] != fromQQ:
                        returnMsg = "[CQ:at,qq={0}] �Ѿ�������[CQ:at,qq={1}]����Ե�������ǲ����ٿ���һ�£�".format(fromQQ, toQQ)
                    else:
                        pendingList = [k for k, v in self.lover_pending.items() if v == fromQQ]
                        for p in pendingList:
                            self.lover_pending.pop(p)
                        self.lover_pending[str(toQQ)] = fromQQ
                        returnMsg = "[CQ:at,qq={1}]\n[CQ:at,qq={0}] ϣ���������Ե�������� ͬ�� ���� �ܾ���".format(fromQQ, toQQ)

            self.mutex.release()
            return returnMsg
        except Exception as e:
            logging.exception(e)

    def acceptLover(self, fromGroup, toQQ):
        returnMsg = ""
        try:
            self.mutex.acquire()
            toQQ_str = str(toQQ)
            if toQQ_str in self.lover_pending.keys():
                fromQQ = self.lover_pending.pop(toQQ_str)
                fromQQ_str = str(fromQQ)

                if LOVE_ITEM_REQUIRED != "" and LOVE_ITEM_REQUIRED not in self.jx3_users[fromQQ_str]['bag'].keys():
                    returnMsg = "[CQ:at,qq={1}] ��Ȼ�˼�ͬ���˵����㲢û��1��{1}��".format(fromQQ, get_item_display_name(LOVE_ITEM_REQUIRED))
                else:
                    self.jx3_users[fromQQ_str]['lover'] = toQQ
                    self.jx3_users[fromQQ_str]['lover_time'] = time.time()
                    self.jx3_users[toQQ_str]['lover'] = fromQQ
                    self.jx3_users[toQQ_str]['lover_time'] = time.time()
                    if LOVE_ITEM_REQUIRED != "":
                        self.jx3_users[fromQQ_str]['bag'][LOVE_ITEM_REQUIRED] -= 1
                        if self.jx3_users[fromQQ_str]['bag'][LOVE_ITEM_REQUIRED] == 0:
                            self.jx3_users[fromQQ_str]['bag'].pop(LOVE_ITEM_REQUIRED)
                        use_zhen_cheng_zhi_xin(fromGroup, fromQQ, toQQ)

                    returnMsg = "[CQ:at,qq={0}] �� [CQ:at,qq={1}]��ϲ���ռ�����ɣ���Ե��ޡ�ʫӽ���£��Ÿ���ֺ����Ҷ����������鿪����֮����ͬ��ͬ�£������˼ҡ��ྴ�������г��ˮ֮�����������ϣ�����ԧ��֮��".format(fromQQ, toQQ)
            self.mutex.release()
            return returnMsg
        except Exception as e:
            logging.exception(e)
        finally:
            self.writeToJsonFile()

    def rejectLover(self, toQQ):
        returnMsg = ""
        try:
            self.mutex.acquire()
            if str(toQQ) in self.lover_pending.keys():
                fromQQ = self.lover_pending.pop(str(toQQ))
                returnMsg = "�仨���⣬��ˮ���飬[CQ:at,qq={1}] ����� [CQ:at,qq={0}]��".format(fromQQ, toQQ)
            self.mutex.release()
            return returnMsg
        except Exception as e:
            logging.exception(e)
    
    def yaBiao(self, qq_account):
        returnMsg = ""
        try:
            self.mutex.acquire()
            qq_account_str = str(qq_account)
            val = self.jx3_users[qq_account_str]
            if val['faction_id'] == 0 and not NO_FACTION_ALLOW_YA_BIAO:
                returnMsg = "[CQ:at,qq={0}] ������Ӫ�޷�Ѻ�ڡ�".format(qq_account)
            elif val['energy'] < YA_BIAO_ENERGY_REQUIRED:
                returnMsg = "[CQ:at,qq={0}] �������㣡�޷�Ѻ�ڡ�".format(qq_account)
            elif qq_account_str in self.jail_list and time.time() - self.jail_list[qq_account_str] < JAIL_DURATION:
                    time_val = calculateRemainingTime(JAIL_DURATION, self.jail_list[qq_account_str])
                    returnMsg = "[CQ:at,qq={0}] ��ʵ�㣬�㻹Ҫ�ڼ������{1}Сʱ{2}��{3}�롣".format(
                                    qq_account,
                                    time_val['hours'],
                                    time_val['mins'],
                                    time_val['secs'])
            else:
                if qq_account in self.jail_list:
                    self.jail_list.pop(qq_account)

                yday = self._reset_daliy_count(qq_account_str)
                yday_str = str(yday)

                if self.daliy_action_count[yday_str][qq_account_str]['ya_biao'] < MAX_DALIY_YA_BIAO_COUNT:
                    reward = random.randint(DALIY_YA_BIAO_REWARD_MIN, DALIY_YA_BIAO_REWARD_MAX)
                    self.jx3_users[qq_account_str]['weiwang'] += reward
                    self.jx3_users[qq_account_str]['energy'] -= YA_BIAO_ENERGY_REQUIRED
                    self.jx3_users[qq_account_str]['money'] += DALIY_YA_BIAO_MONEY_REWARD
                    self.daliy_action_count[yday_str][qq_account_str]["ya_biao"] += 1
                    returnMsg = "[CQ:at,qq={0}] Ѻ�ڳɹ���\n����-{1}\n����+{2}\n��Ǯ+{3}".format(qq_account, YA_BIAO_ENERGY_REQUIRED, reward, DALIY_YA_BIAO_MONEY_REWARD)
                else:
                    returnMsg = "[CQ:at,qq={0}] һ�����Ѻ��{1}�Ρ����Ѿ�Ѻ��{1}���������������ɡ�".format(qq_account, MAX_DALIY_YA_BIAO_COUNT)

            self.mutex.release()
            return returnMsg
        except Exception as e:
            logging.exception(e)
        finally:
            self.writeToJsonFile()

    def checkBag(self, qq_account):
        returnMsg = ""
        try:
            self.mutex.acquire()
            bag = get_key_or_return_default(self.jx3_users[str(qq_account)], 'bag', {})
            if bag == {}:
                itemMsg = "\n�տ���Ҳ"
            else:
                itemMsg = ""
                for k, v in bag.items():
                    itemMsg += "\n{0} x {1}".format(get_item_display_name(k), v)
            returnMsg = "[CQ:at,qq={0}] �ı�����".format(qq_account) + itemMsg
            self.mutex.release()
            return returnMsg
        except Exception as e:
            logging.exception(e)
    
    def joinFaction(self, qq_account, faction_str):
        returnMsg = ""
        try:
            self.mutex.acquire()
            if faction_str in FACTION_DISPLAY_NAME:
                qq_account_str = str(qq_account)
                qq_stat = self.jx3_users[qq_account_str]
                qq_faction_str = get_faction_display_name(qq_stat['faction_id'])
                if faction_str == qq_faction_str:
                    returnMsg = "[CQ:at,qq={0}] ���Ѿ������� {1}��".format(qq_account, faction_str)
                elif qq_stat['faction_id'] != 0:
                    returnMsg = "[CQ:at,qq={0}] ���Ѿ������� {1}��{2} ���������������롣".format(qq_account, qq_faction_str, faction_str)
                elif qq_stat['faction_join_time'] != None and time.time() - qq_stat['faction_join_time'] < FACTION_REJOIN_CD_SECS:
                    time_val = calculateRemainingTime(FACTION_REJOIN_CD_SECS, qq_stat['faction_join_time'])
                    returnMsg = "[CQ:at,qq={0}] ���ڲ���ǰ���˳���Ӫ������Ҫ�ȴ�{1}Сʱ{2}��{3}��֮��������¼��롣".format(
                                    qq_account,
                                    time_val['hours'],
                                    time_val['mins'],
                                    time_val['secs'])
                else:
                    self.jx3_users[qq_account_str]['faction_id'] = FACTION_DISPLAY_NAME.index(faction_str)
                    self.jx3_users[qq_account_str]['faction_join_time'] = time.time()
                    returnMsg = "[CQ:at,qq={0}] �ɹ����� {1}��".format(qq_account, faction_str)
            
            self.mutex.release()
            return returnMsg
        except Exception as e:
            logging.exception(e)
        finally:
            self.writeToJsonFile()
    
    def quitFaction(self, qq_account):
        returnMsg = ""
        try:
            self.mutex.acquire()
            qq_account_str = str(qq_account)
            qq_stat = self.jx3_users[qq_account_str]
            if qq_stat['faction_id'] == 0:
                returnMsg = "[CQ:at,qq={0}] �㲢û�м����κ���Ӫ��".format(qq_account)
            else:
                pre_faction_id = qq_stat['faction_id']
                self.jx3_users[qq_account_str]['faction_id'] = 0
                self.jx3_users[qq_account_str]['faction_join_time'] = time.time()
                returnMsg = "[CQ:at,qq={0}] �˳��˽��������������� {1}".format(qq_account, get_faction_display_name(pre_faction_id))
            self.mutex.release()
            return returnMsg
        except Exception as e:
            logging.exception(e)
        finally:
            self.writeToJsonFile()
    
    def transferFaction(self, qq_account):
        returnMsg = ""
        try:
            self.mutex.acquire()
            qq_account_str = str(qq_account)
            qq_stat = self.jx3_users[qq_account_str]
            if qq_stat['faction_id'] == 0:
                returnMsg = "[CQ:at,qq={0}] �㲢û�м����κ���Ӫ��".format(qq_account)
            elif qq_stat['weiwang'] < FACTION_TRANSFER_WEIWANG_COST:
                returnMsg = "[CQ:at,qq={0}] ת����Ӫ��Ҫ����{1}��������ǰ�������㡣".format(qq_account, FACTION_TRANSFER_WEIWANG_COST)
            elif qq_stat['faction_join_time'] != None and time.time() - qq_stat['faction_join_time'] < FACTION_REJOIN_CD_SECS:
                remain_secs = int(math.floor(FACTION_REJOIN_CD_SECS - (time.time() - qq_stat['faction_join_time'])))
                hours = remain_secs // 3600
                mins = (remain_secs - hours * 3600) // 60
                secs = remain_secs - hours * 3600 - mins * 60
                returnMsg = "[CQ:at,qq={0}] ���ڲ���ǰ�Ÿ�����Ӫ������Ҫ�ȴ�{1}Сʱ{2}��{3}��֮����ܸ��ġ�".format(qq_account, hours, mins, secs)
            else:
                pre_faction_id = qq_stat['faction_id']
                new_faction_id = 1 if pre_faction_id == 2 else 2
                self.jx3_users[qq_account_str]['faction_id'] = new_faction_id
                self.jx3_users[qq_account_str]['faction_join_time'] = time.time()
                returnMsg = "[CQ:at,qq={0}] ͨ�����½��ף��ɹ��������� {1}�������� {2}��".format(qq_account, get_faction_display_name(pre_faction_id), get_faction_display_name(new_faction_id))
            self.mutex.release()
            return returnMsg
        except Exception as e:
            logging.exception(e)
        finally:
            self.writeToJsonFile()
    
    def _calculate_battle(self, fromQQ_str, toQQ_str, gear_mode):

        if toQQ_str in NPC_LIST:
            toQQ_equipment = NPC_LIST[toQQ_str]['equipment']
            toQQ_gear_point = calculateGearPoint(toQQ_equipment)[gear_mode]
        else:
            toQQ_equipment = self.equipment[toQQ_str]
            toQQ_gear_point = calculateGearPoint(toQQ_equipment)[gear_mode]

        fromQQ_equipment = self.equipment[fromQQ_str]
        fromQQ_gear_point = calculateGearPoint(fromQQ_equipment)[gear_mode]

        random_base = random.uniform(0.4, 0.5)
        success_chance = random_base + 0.2 * ((fromQQ_gear_point - toQQ_gear_point) / float(toQQ_gear_point)) + 0.3 * float(fromQQ_equipment['weapon'][gear_mode]) / float(toQQ_equipment['armor'][gear_mode])
        
        logging.info("success_chance: {0} + 0.3 * {1} + 0.2 * {2}".format(
                        random_base,
                        (fromQQ_gear_point - toQQ_gear_point) / float(toQQ_gear_point), 
                        float(fromQQ_equipment['weapon'][gear_mode]) / float(toQQ_equipment['armor'][gear_mode])))
        
        chance = random.uniform(0, 1)
        logging.info("chance: {0}, success_chance: {1}".format(chance, success_chance))
        if chance <= success_chance:
            winner = fromQQ_str
            loser = toQQ_str
        else:
            winner = toQQ_str
            loser = fromQQ_str
        
        return {'winner': winner, 'loser': loser, 'success_chance': success_chance}

    def rob(self, fromGroup, fromQQ, toQQ):
        returnMsg = ""
        try:
            if not self.isUserRegister(toQQ):
                returnMsg = "[CQ:at,qq={0}] �Է���δע�ᣬ�޷���١�".format(fromQQ)
            else:
                self.mutex.acquire()
                fromQQ_str = str(fromQQ)
                fromQQ_stat = self.jx3_users[fromQQ_str]
                toQQ_str = str(toQQ)
                toQQ_stat = self.jx3_users[toQQ_str]

                if fromQQ_stat['faction_id'] == 0:
                    returnMsg = "[CQ:at,qq={0}] ������Ӫ�޷���٣����ȼ�����Ӫ��".format(fromQQ)
                elif toQQ_stat['faction_id'] == 0:
                    returnMsg = "[CQ:at,qq={0}] �Է���������Ӫ���޷���١�".format(fromQQ)
                elif fromQQ_stat['faction_id'] == toQQ_stat['faction_id']:
                    returnMsg = "[CQ:at,qq={0}] ͬ��Ӫ�޷���٣�".format(fromQQ)
                elif toQQ_str in self.rob_protect and ROB_PROTECT_COUNT != 0 and self.rob_protect[toQQ_str]['count'] >= ROB_PROTECT_COUNT and (time.time() - self.rob_protect[toQQ_str]['rob_time']) <= ROB_PROTECT_DURATION:
                    time_val = calculateRemainingTime(ROB_PROTECT_DURATION, self.rob_protect[toQQ_str]['rob_time'])
                    returnMsg = "[CQ:at,qq={0}] �Է���������̫��������Ѿ��ܵ�����֮���ӡ�\nʣ��ʱ�䣺{1}Сʱ{2}��{3}��".format(
                                    fromQQ, 
                                    time_val['hours'],
                                    time_val['mins'],
                                    time_val['secs'])
                elif fromQQ_str in self.jail_list and time.time() - self.jail_list[fromQQ_str] < JAIL_DURATION:
                    time_val = calculateRemainingTime(JAIL_DURATION, self.jail_list[fromQQ_str])
                    returnMsg = "[CQ:at,qq={0}] ��ʵ�㣬�㻹Ҫ�ڼ������{1}Сʱ{2}��{3}�롣".format(
                                    fromQQ,
                                    time_val['hours'],
                                    time_val['mins'],
                                    time_val['secs'])
                elif toQQ_str in self.jail_list and time.time() - self.jail_list[toQQ_str] < JAIL_DURATION:
                    returnMsg = "[CQ:at,qq={0}] �Է��ڼ���������أ�������Ҫ������".format(fromQQ)
                elif fromQQ_stat['energy'] < ROB_ENERGY_COST:
                    returnMsg = "[CQ:at,qq={0}] �������㣡�޷���١�".format(fromQQ)
                else:
                    if fromQQ_str in self.jail_list:
                        self.jail_list.pop(fromQQ_str)

                    battle_result = self._calculate_battle(fromQQ_str, toQQ_str, 'pvp')

                    winner = battle_result['winner']
                    loser = battle_result['loser']
                    success_chance = battle_result['success_chance']

                    weiwang_amount = int(self.jx3_users[loser]['weiwang'] * random.uniform(0.1, 0.2))
                    money_amount = int(self.jx3_users[loser]['money'] * random.uniform(0.1, 0.2))
                    self.jx3_users[winner]['weiwang'] += weiwang_amount
                    self.jx3_users[loser]['weiwang'] -= weiwang_amount

                    self.jx3_users[winner]['money'] += money_amount
                    self.jx3_users[loser]['money'] -= money_amount

                    self.jx3_users[fromQQ_str]['energy'] -= ROB_ENERGY_COST

                    if toQQ_str == loser:
                        if loser not in self.rob_protect or self.rob_protect[loser]['count'] >= ROB_PROTECT_COUNT:
                            self.rob_protect[loser] = {'count': 0, 'rob_time': None}
                        self.rob_protect[loser]['count'] += 1
                        self.rob_protect[loser]['rob_time'] = time.time()

                    logging.info("{0} rob {1} weiwang: {2} money: {3}".format(fromQQ, toQQ, weiwang_amount, money_amount))

                    returnMsg = "���{0}���ɹ��ʣ�{1}%".format("�ɹ�" if winner == fromQQ_str else "ʧ��", int(math.floor(success_chance * 100)))
                    returnMsg += "\n[CQ:at,qq={0}] ��Ұ������ [CQ:at,qq={1}]\n{2} ����+{4} ��Ǯ+{5} ����-{6}\n{3} ����-{4} ��Ǯ-{5}".format(
                                    fromQQ,
                                    toQQ,
                                    getGroupNickName(fromGroup, int(winner)),
                                    getGroupNickName(fromGroup, int(loser)),
                                    weiwang_amount,
                                    money_amount,
                                    ROB_ENERGY_COST)
                self.mutex.release()
            return returnMsg
        except Exception as e:
            logging.exception(e)
        finally:
            self.writeToJsonFile()
    
    def buyItem(self, qq_account, item_display_name, item_amount):
        returnMsg = ""
        try:
            item = find_item(item_display_name)
            if item != None:
                if not isItemBuyable(item):
                    returnMsg = "[CQ:at,qq={0}] {1} ���ɹ���".format(qq_account, item_display_name)
                else:
                    self.mutex.acquire()
                    qq_account_str = str(qq_account)
                    qq_stat = self.jx3_users[qq_account_str]

                    cost_list = item['cost']
                    can_afford = True
                    for k, v in cost_list.items():
                        can_afford = can_afford and (k in qq_stat and qq_stat[k] >= v * item_amount)

                    if can_afford:
                        if item['name'] not in self.jx3_users[qq_account_str]['bag']:
                            self.jx3_users[qq_account_str]['bag'][item['name']] = 0
                        self.jx3_users[qq_account_str]['bag'][item['name']] += item_amount
                        returnMsg = "[CQ:at,qq={0}] ����ɹ���\n{1}+{2}".format(qq_account, item_display_name, item_amount)
                        for k, v in cost_list.items():
                            if k in qq_stat:
                                self.jx3_users[qq_account_str][k] -= v * item_amount
                                returnMsg += "\n{0}-{1}".format(STAT_DISPLAY_NAME[k], v * item_amount)
                    else:
                        returnMsg = "[CQ:at,qq={0}] ����ʧ�ܣ�\n����1�� {1} ��Ҫ:{2}".format(qq_account, item_display_name, print_cost(cost_list))
                    self.mutex.release()
                return returnMsg
        except Exception as e:
            logging.exception(e)
        finally:
            self.writeToJsonFile()
    
    def useItem(self, qq_account, item_display_name, item_amount):
        returnMsg = ""
        try:
            item = find_item(item_display_name)
            if item != None:
                if not isItemUsable(item):
                    returnMsg = "[CQ:at,qq={0}] {1} ����ʹ�á�".format(qq_account, item_display_name)
                else:
                    self.mutex.acquire()
                    qq_account_str = str(qq_account)
                    qq_stat = self.jx3_users[qq_account_str]

                    effect_list = item['effect']

                    if item['name'] not in self.jx3_users[qq_account_str]['bag']:
                        returnMsg = "[CQ:at,qq={0}] �㲢û�� {1}���޷�ʹ�á�".format(qq_account, item_display_name)
                    elif self.jx3_users[qq_account_str]['bag'][item['name']] < item_amount:
                        returnMsg = "[CQ:at,qq={0}] �㲢û����ô�� {1}��".format(qq_account, item_display_name)
                    else:
                        self.jx3_users[qq_account_str]['bag'][item['name']] -= item_amount
                        if self.jx3_users[qq_account_str]['bag'][item['name']] == 0:
                            self.jx3_users[qq_account_str]['bag'].pop(item['name'])

                        returnMsg = "[CQ:at,qq={0}]\nʹ�� {1} x {2}".format(qq_account, item_display_name, item_amount)
                        for k, v in effect_list.items():
                            if k in qq_stat:
                                self.jx3_users[qq_account_str][k] += v * item_amount
                                returnMsg += "\n{0}+{1}".format(STAT_DISPLAY_NAME[k], v * item_amount)
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

                    self.mutex.release()

                return returnMsg
        except Exception as e:
            logging.exception(e)
        finally:
            self.writeToJsonFile()
    
    def shopList(self, qq_account):
        try:
            returnMsg = "[CQ:at,qq={0}]\n---------�ӻ���---------\n--�����ʵ��ͯ������--".format(qq_account)
            for item in ITEM_LIST:
                if 'cost' in item:
                    returnMsg += "\n*��{0}��".format(item['display_name'])
                    for k, v in item['cost'].items():
                        returnMsg += "----{0}��{1}".format(STAT_DISPLAY_NAME[k], v)
            return returnMsg
        except Exception as e:
            logging.exception(e)

    def waBao(self, qq_account):
        returnMsg = ""
        try:
            self.mutex.acquire()
            qq_account_str = str(qq_account)
            val = self.jx3_users[qq_account_str]
            if val['energy'] < WA_BAO_ENERGY_REQUIRED:
                returnMsg = "[CQ:at,qq={0}] �������㣡�޷��ڱ���".format(qq_account)
            elif qq_account_str in self.jail_list and time.time() - self.jail_list[qq_account_str] < JAIL_DURATION:
                    time_val = calculateRemainingTime(JAIL_DURATION, self.jail_list[qq_account_str])
                    returnMsg = "[CQ:at,qq={0}] ��ʵ�㣬�㻹Ҫ�ڼ������{1}Сʱ{2}��{3}�롣".format(
                                    qq_account,
                                    time_val['hours'],
                                    time_val['mins'],
                                    time_val['secs'])
            else:
                if qq_account in self.jail_list:
                    self.jail_list.pop(qq_account)    

                yday = self._reset_daliy_count(qq_account_str)
                yday_str = str(yday)

                if self.daliy_action_count[yday_str][qq_account_str]["wa_bao"]['count'] < MAX_DALIY_WA_BAO_COUNT:
                    last_time = self.daliy_action_count[yday_str][qq_account_str]["wa_bao"]['last_time']
                    if last_time != None and time.time() - last_time <= WA_BAO_COOLDOWN:
                        time_val = calculateRemainingTime(WA_BAO_COOLDOWN, last_time)
                        returnMsg = "[CQ:at,qq={0}] ������ո����걦�أ�������Щƣ�������{1}��{2}��֮�����ڡ�".format(
                                        qq_account,
                                        time_val['mins'],
                                        time_val['secs'])
                    else:
                        reward_item_name = get_wa_bao_reward()
                        self.daliy_action_count[yday_str][qq_account_str]["wa_bao"]['count'] += 1
                        self.daliy_action_count[yday_str][qq_account_str]["wa_bao"]['last_time'] = time.time()

                        self.jx3_users[qq_account_str]['energy'] -= WA_BAO_ENERGY_REQUIRED

                        returnMsg = '[CQ:at,qq={0}]\n�����ڱ�������{1}/{2}'.format(
                                            qq_account, 
                                            self.daliy_action_count[yday_str][qq_account_str]["wa_bao"]['count'], 
                                            MAX_DALIY_WA_BAO_COUNT)

                        if reward_item_name == "":
                            returnMsg += "\n��һ������ȥ��ʲôҲû�ڵ���"
                        else:
                            if reward_item_name not in self.jx3_users[qq_account_str]['bag']:
                                    self.jx3_users[qq_account_str]['bag'][reward_item_name] = 0
                            self.jx3_users[qq_account_str]['bag'][reward_item_name] += 1
                            returnMsg += "\n��һ������ȥ���ڵ���һ�����صĶ���\n{0}+1\n����-{1}".format(
                                            get_item_display_name(reward_item_name),
                                            WA_BAO_ENERGY_REQUIRED)
                else:
                    returnMsg = "[CQ:at,qq={0}] һ������ڱ�{1}�Ρ����Ѿ�����{1}������������Ϣ��Ϣ�ɡ�".format(qq_account, MAX_DALIY_WA_BAO_COUNT)

            self.mutex.release()
            return returnMsg
        except Exception as e:
            logging.exception(e)
        finally:
            self.writeToJsonFile()


    def use_firework(self, item_display_name, fromQQ, toQQ):
        returnMsg = ""
        try:
            item = find_item(item_display_name)
            if item != None:
                self.mutex.acquire()
                fromQQ_str = str(fromQQ)
                qq_stat = self.jx3_users[fromQQ_str]

                if item['name'] not in self.jx3_users[fromQQ_str]['bag']:
                    returnMsg = "[CQ:at,qq={0}] �㲢û�� {1}���޷�ʹ�á�".format(fromQQ, item_display_name)
                else:
                    self.jx3_users[fromQQ_str]['bag'][item['name']] -= 1
                    if self.jx3_users[fromQQ_str]['bag'][item['name']] == 0:
                        self.jx3_users[fromQQ_str]['bag'].pop(item['name'])

                    use_zhen_cheng_zhi_xin(self.qq_group, fromQQ, toQQ)

                self.mutex.release()
            return returnMsg
        except Exception as e:
            logging.exception(e)
        finally:
            self.writeToJsonFile()
    
    def get_equipment_info(self, qq_account):
        returnMsg = ""
        try:
            self.mutex.acquire()
            val = self.equipment[str(qq_account)]

            returnMsg = "[CQ:at,qq={0}]\nװ����Ϣ��\n������{1}\n----pve������{2}----pvp������{3}\n���ߣ�{4}\n----pveѪ����{5}----pvpѪ����{6}".format(
                qq_account,
                val['weapon']['display_name'],
                val['weapon']['pve'],
                val['weapon']['pvp'],
                val['armor']['display_name'],
                val['armor']['pve'],
                val['armor']['pvp'])

            self.mutex.release()
            return returnMsg
        except Exception as e:
            logging.exception(e)
    
    def change_weapon_name(self, qq_account, name):
        returnMsg = ""
        try:
            self.mutex.acquire()
            self.equipment[str(qq_account)]['weapon']['display_name'] = name
            returnMsg = "[CQ:at,qq={0}] �������Ѹ���Ϊ {1}".format(qq_account, name)
            self.mutex.release()
            return returnMsg
        except Exception as e:
            logging.exception(e)
        finally:
            self.writeToJsonFile()

    def change_armor_name(self, qq_account, name):
        returnMsg = ""
        try:
            self.mutex.acquire()
            self.equipment[str(qq_account)]['armor']['display_name'] = name
            returnMsg = "[CQ:at,qq={0}] �ķ����Ѹ���Ϊ {1}".format(qq_account, name)
            self.mutex.release()
            return returnMsg
        except Exception as e:
            logging.exception(e)
        finally:
            self.writeToJsonFile()
    
    def get_faction_info(self):
        returnMsg = "��Ⱥ��Ӫ��Ϣ\n"
        try:
            self.mutex.acquire()
            no_faction = 0
            hao_qi = 0
            e_ren = 0
            for key, value in self.jx3_users.items():
                if value['faction_id'] == 0:
                    no_faction += 1
                elif value['faction_id'] == 1:
                    e_ren += 1
                elif value['faction_id'] == 2:
                    hao_qi += 1
            returnMsg += "��ȺΪ{0}Ⱥ\n���˹�����:\t{1}\n����������:\t{2}\n��������:\t{3}".format(
                        "����ǿ��" if hao_qi > e_ren else "����ǿ��" if e_ren > hao_qi else "�ƾ�����",
                        e_ren,
                        hao_qi,
                        no_faction)

            self.mutex.release()
            return returnMsg
        except Exception as e:
            logging.exception(e)
    
    def get_pve_gear_point_rank(self):
        returnMsg = "��Ⱥpveװ�����а�"
        try:
            self.mutex.acquire()
            rank_list = sorted(self.jx3_users.items(), lambda x, y: cmp(x[1]['pve_gear_point'], y[1]['pve_gear_point']), reverse=True)
            list_len = len(rank_list)
            for i in range(10):
                if i < list_len:
                    returnMsg += '\n{0}. {1} {2}'.format(i + 1, getGroupNickName(self.qq_group, int(rank_list[i][0])), rank_list[i][1]['pve_gear_point'])
                else:
                    break
            self.mutex.release()
            return returnMsg
        except Exception as e:
            logging.exception(e)

    def get_pvp_gear_point_rank(self):
        returnMsg = "��Ⱥpvpװ�����а�"
        try:
            self.mutex.acquire()
            rank_list = sorted(self.jx3_users.items(), lambda x, y: cmp(x[1]['pvp_gear_point'], y[1]['pvp_gear_point']), reverse=True)
            list_len = len(rank_list)
            for i in range(10):
                if i < list_len:
                    returnMsg += '\n{0}. {1} {2}'.format(i + 1, getGroupNickName(self.qq_group, int(rank_list[i][0])), rank_list[i][1]['pvp_gear_point'])
                else:
                    break
            self.mutex.release()
            return returnMsg
        except Exception as e:
            logging.exception(e)

    def get_money_rank(self):
        returnMsg = "��Ⱥ�������а�"
        try:
            self.mutex.acquire()
            rank_list = sorted(self.jx3_users.items(), lambda x, y: cmp(x[1]['money'], y[1]['money']), reverse=True)
            list_len = len(rank_list)
            for i in range(10):
                if i < list_len and rank_list[i][1]['money'] != 0:
                    returnMsg += '\n{0}. {1} {2}'.format(i + 1, getGroupNickName(self.qq_group, int(rank_list[i][0])), int(rank_list[i][1]['money']))
                else:
                    break
            self.mutex.release()
            return returnMsg
        except Exception as e:
            logging.exception(e)

    def get_speech_rank(self, qq_account):
        returnMsg = "��Ⱥ�����������а�"
        try:
            self.mutex.acquire()

            yday = self._reset_daliy_count(str(qq_account))
            yday_str = str(yday)

            rank_list = sorted(self.daliy_action_count[yday_str].items(), lambda x, y: cmp(x[1]['speech_count'], y[1]['speech_count']), reverse=True)
            list_len = len(rank_list)
            for i in range(10):
                if i < list_len and rank_list[i][1]['speech_count'] != 0:
                    returnMsg += '\n{0}. {1} {2}'.format(
                        i + 1,
                        getGroupNickName(self.qq_group, int(rank_list[i][0])), 
                        rank_list[i][1]['speech_count'])
                else:
                    break
            self.mutex.release()
            return returnMsg
        except Exception as e:
            logging.exception(e)

    def get_qiyu_rank(self):
        returnMsg = "��Ⱥ�������а�"
        try:
            self.mutex.acquire()
            rank_list = sorted(self.jx3_users.items(), lambda x, y: cmp(x[1]['qiyu'], y[1]['qiyu']), reverse=True)
            list_len = len(rank_list)
            for i in range(10):
                if i < list_len and rank_list[i][1]['qiyu'] != 0:
                    returnMsg += '\n{0}. {1} {2}'.format(i + 1, getGroupNickName(self.qq_group, int(rank_list[i][0])), rank_list[i][1]['qiyu'])
                else:
                    break
            self.mutex.release()
            return returnMsg
        except Exception as e:
            logging.exception(e)

    def get_weiwang_rank(self):
        returnMsg = "��Ⱥ�������а�"
        try:
            self.mutex.acquire()
            rank_list = sorted(self.jx3_users.items(), lambda x, y: cmp(x[1]['weiwang'], y[1]['weiwang']), reverse=True)
            list_len = len(rank_list)
            for i in range(10):
                if i < list_len and rank_list[i][1]['weiwang'] != 0:
                    returnMsg += '\n{0}. {1} {2}'.format(i + 1, getGroupNickName(self.qq_group, int(rank_list[i][0])), rank_list[i][1]['weiwang'])
                else:
                    break
            self.mutex.release()
            return returnMsg
        except Exception as e:
            logging.exception(e)
    
    def put_wanted(self, fromQQ, toQQ):
        returnMsg = ""
        try:
            if not self.isUserRegister(toQQ):
                returnMsg = "[CQ:at,qq={0}] �Է���δע�ᣬ�޷����͡�".format(fromQQ)
            else:
                self.mutex.acquire()
                fromQQ_str = str(fromQQ)
                toQQ_str = str(toQQ)

                yday = self._reset_daliy_count(toQQ_str)
                yday_str = str(yday)

                if self.jx3_users[fromQQ_str]['money'] < WANTED_MONEY_REWARD:
                    returnMsg = "[CQ:at,qq={0}] ��Ǯ���㣬�޷����͡�".format(fromQQ)
                elif self.daliy_action_count[yday_str][toQQ_str]['jailed'] >= JAIL_TIMES_PROTECTION:
                    returnMsg = "[CQ:at,qq={0}] �Է������Ѿ���ץ��ȥ{1}���ˣ��޷����͡�".format(fromQQ, JAIL_TIMES_PROTECTION)
                else:
                    self.jx3_users[fromQQ_str]['money'] -= WANTED_MONEY_REWARD
                    if toQQ_str in self.wanted_list:
                        if time.time() - self.wanted_list[toQQ_str]['wanted_time'] > WANTED_DURATION:
                            self.wanted_list[toQQ_str]['reward'] = WANTED_MONEY_REWARD
                        else:
                            self.wanted_list[toQQ_str]['reward'] += WANTED_MONEY_REWARD
    
                        self.wanted_list[toQQ_str]['wanted_time'] = time.time()
                    else:
                        self.wanted_list[toQQ_str] = {'reward': WANTED_MONEY_REWARD, 'wanted_time': time.time(), 'failed_try': {}}
                    
                    import CQSDK
                    CQSDK.SendGroupMsg(self.qq_group, "[CQ:at,qq={0}] ���ͳɹ���\n��Ǯ-{1}".format(fromQQ, WANTED_MONEY_REWARD))

                    returnMsg = "������Թһ���壬Ω��Ⱥ����Ԯ�֡�������Ը��{0}��� {1} �������ͣ����ͽ��Ѵ�{2}������ʿ��������".format(
                                    WANTED_MONEY_REWARD,
                                    getGroupNickName(self.qq_group, int(toQQ)),
                                    self.wanted_list[toQQ_str]['reward'])

                self.mutex.release()
            return returnMsg
        except Exception as e:
            logging.exception(e)
        finally:
            self.writeToJsonFile()

    def get_wanted_list(self):
        returnMsg = "��Ⱥ���Ͱ�"
        msg_list = ""
        try:
            self.mutex.acquire()
            rank_list = sorted(self.wanted_list.items(), lambda x, y: cmp(x[1]['reward'], y[1]['reward']), reverse=True)
            list_len = len(rank_list)
            index = 1
            for k, v in rank_list:
                if time.time() - self.wanted_list[k]['wanted_time'] < WANTED_DURATION:
                    time_val = calculateRemainingTime(WANTED_DURATION, self.wanted_list[k]['wanted_time'])
                    msg_list += '\n{0}. {1} {2}�� {3}Сʱ{4}��{5}��'.format(
                                    index,
                                    getGroupNickName(self.qq_group, int(k)),
                                    v['reward'],
                                    time_val['hours'],
                                    time_val['mins'],
                                    time_val['secs'])
                    index += 1

            self.mutex.release()

            if msg_list == "":
                msg_list = "\n��������"
            return returnMsg + msg_list
        except Exception as e:
            logging.exception(e)

    def catch_wanted(self, fromQQ, toQQ):
        returnMsg = ""
        try:
            self.mutex.acquire()
            fromQQ_str = str(fromQQ)
            toQQ_str = str(toQQ)

            yday = self._reset_daliy_count(toQQ_str)
            yday_str = str(yday)

            if fromQQ_str in self.jail_list and time.time() - self.jail_list[fromQQ_str] < JAIL_DURATION:
                    time_val = calculateRemainingTime(JAIL_DURATION, self.jail_list[fromQQ_str])
                    returnMsg = "[CQ:at,qq={0}] ��ʵ�㣬�㻹Ҫ�ڼ������{1}Сʱ{2}��{3}�롣".format(
                                    fromQQ,
                                    time_val['hours'],
                                    time_val['mins'],
                                    time_val['secs'])
            elif toQQ_str in self.jail_list and time.time() - self.jail_list[toQQ_str] < JAIL_DURATION:
                    returnMsg = "[CQ:at,qq={0}] �Է��ڼ���������أ�������Ҫ������".format(fromQQ)
            elif toQQ_str in self.wanted_list and time.time() - self.wanted_list[toQQ_str]['wanted_time'] < WANTED_DURATION:
                if 'failed_try' in self.wanted_list[toQQ_str] and fromQQ_str in self.wanted_list[toQQ_str]['failed_try'] and time.time() - self.wanted_list[toQQ_str]['failed_try'][fromQQ_str] < WANTED_COOLDOWN:
                    time_val = calculateRemainingTime(WANTED_COOLDOWN, self.wanted_list[toQQ_str]['failed_try'][fromQQ_str])
                    returnMsg = "[CQ:at,qq={0}] ���Ѿ����Թ�ץ���ˣ��κμ��ղ��ѡ������{1}Сʱ{2}��{3}���������ս��".format(
                                    fromQQ,
                                    time_val['hours'],
                                    time_val['mins'],
                                    time_val['secs'])
                elif self.jx3_users[fromQQ_str]['energy'] < WANTED_ENERGY_COST:
                    returnMsg = "[CQ:at,qq={0}] �������㣡��Ҫ����{1}������".format(fromQQ, WANTED_ENERGY_COST)
                else:                
                    battle_result = self._calculate_battle(fromQQ_str, toQQ_str, 'pvp')
                    winner = battle_result['winner']
                    loser = battle_result['loser']
                    success_chance = battle_result['success_chance']

                    self.jx3_users[fromQQ_str]['energy'] -= WANTED_ENERGY_COST

                    if winner == fromQQ_str:
                        reward = int(0.9 * self.wanted_list[toQQ_str]['reward'])
                        self.jx3_users[fromQQ_str]['money'] += reward
                        self.wanted_list.pop(toQQ_str)
                        self.jail_list[toQQ_str] = time.time()

                        self.daliy_action_count[yday_str][toQQ_str]['jailed'] += 1

                        returnMsg = "{0}��ʱ���ڱ�{1}�ɹ�ץ�������ͽ�����ɹ��ʣ�{2}%\n[CQ:at,qq={3}] ��ã�\n��Ǯ+{4}��\n����-{5}".format(
                                        getGroupNickName(self.qq_group, int(toQQ)),
                                        getGroupNickName(self.qq_group, int(fromQQ)),
                                        int(math.floor(success_chance * 100)),
                                        fromQQ,
                                        reward,
                                        WANTED_ENERGY_COST)
                    else:
                        if 'failed_try' not in self.wanted_list[toQQ_str]:
                            self.wanted_list[toQQ_str]['failed_try'] = {}
                        self.wanted_list[toQQ_str]['failed_try'][fromQQ_str] = time.time()
                        returnMsg = "[CQ:at,qq={0}] ץ��ʧ�ܣ��ɹ��ʣ�{1}%\n����-{2}".format(
                                        fromQQ,
                                        int(math.floor(success_chance * 100)),
                                        WANTED_ENERGY_COST)

            self.mutex.release()
            return returnMsg
        except Exception as e:
            logging.exception(e)
        finally:
            self.writeToJsonFile()
    
    def get_cha_guan_quest(self, qq_account):
        returnMsg = ""
        try:
            self.mutex.acquire()
            qq_account_str = str(qq_account)

            yday = self._reset_daliy_count(qq_account_str)
            yday_str = str(yday)
            
            daliy_stat = self.daliy_action_count[yday_str][qq_account_str]['cha_guan']

            if qq_account_str in self.jail_list and time.time() - self.jail_list[qq_account_str] < JAIL_DURATION:
                    time_val = calculateRemainingTime(JAIL_DURATION, self.jail_list[qq_account_str])
                    returnMsg = "[CQ:at,qq={0}] ��ʵ�㣬�㻹Ҫ�ڼ������{1}Сʱ{2}��{3}�롣".format(
                                    qq_account,
                                    time_val['hours'],
                                    time_val['mins'],
                                    time_val['secs'])
            elif len(daliy_stat['complete_quest']) >= len(CHA_GUAN_QUEST_INFO):
                returnMsg = "[CQ:at,qq={0}] ���Ѿ������{1}����������������������ɡ�".format(qq_account, len(CHA_GUAN_QUEST_INFO))
            elif self.jx3_users[qq_account_str]['energy'] < CHA_GUAN_ENERGY_COST:
                returnMsg = "[CQ:at,qq={0}] �������㣡��Ҫ����{1}������".format(qq_account, CHA_GUAN_ENERGY_COST)
            elif daliy_stat['current_quest'] != "":
                returnMsg = "[CQ:at,qq={0}] ���Ѿ�����һ����������\n��ǰ����{1}".format(qq_account, CHA_GUAN_QUEST_INFO[daliy_stat['current_quest']]['display_name'])
            else:
                remain_quest = list(set(CHA_GUAN_QUEST_INFO.keys()) - set(daliy_stat['complete_quest']))

                quest_name = remain_quest[random.randint(0, len(remain_quest) - 1)]

                self.daliy_action_count[yday_str][qq_account_str]['cha_guan']['current_quest'] = quest_name
                quest = CHA_GUAN_QUEST_INFO[quest_name]

                rewardMsg = ""
                for k, v in quest['reward'].items():
                    rewardMsg += "\n{0}+{1}".format(STAT_DISPLAY_NAME[k], v)

                requireMsg = ""
                for k, v in quest['require'].items():
                    requireMsg += "\n{0} x {1}".format(get_item_display_name(k), v)
                requireMsg += "\n������{0}".format(CHA_GUAN_ENERGY_COST)

                returnMsg = "[CQ:at,qq={0}] �������({1}/{2})\n{3}\n{4}\n����:{5}\n������{6}".format(
                                qq_account,
                                len(daliy_stat['complete_quest']) + 1,
                                len(CHA_GUAN_QUEST_INFO.keys()),
                                quest['display_name'],
                                quest['description'],
                                requireMsg,
                                rewardMsg)

            self.mutex.release()
            return returnMsg
        except Exception as e:
            logging.exception(e)
        finally:
            self.writeToJsonFile()
    
    def complete_cha_guan_quest(self, qq_account):
        returnMsg = ""
        try:
            self.mutex.acquire()
            qq_account_str = str(qq_account)

            yday = self._reset_daliy_count(qq_account_str)
            yday_str = str(yday)

            if qq_account_str in self.jail_list and time.time() - self.jail_list[qq_account_str] < JAIL_DURATION:
                    time_val = calculateRemainingTime(JAIL_DURATION, self.jail_list[qq_account_str])
                    returnMsg = "[CQ:at,qq={0}] ��ʵ�㣬�㻹Ҫ�ڼ������{1}Сʱ{2}��{3}�롣".format(
                                    qq_account,
                                    time_val['hours'],
                                    time_val['mins'],
                                    time_val['secs'])
            elif self.daliy_action_count[yday_str][qq_account_str]['cha_guan']['current_quest'] != "":

                daliy_stat = self.daliy_action_count[yday_str][qq_account_str]['cha_guan']
                quest = CHA_GUAN_QUEST_INFO[daliy_stat['current_quest']]

                if self.jx3_users[qq_account_str]['energy'] < CHA_GUAN_ENERGY_COST:
                    returnMsg = "[CQ:at,qq={0}] �������㣡��Ҫ����{1}������".format(qq_account, CHA_GUAN_ENERGY_COST)
                else:
                    
                    has_require = True
                    for k, v in quest['require'].items():
                        has_require = has_require and k in self.jx3_users[qq_account_str]['bag'] and self.jx3_users[qq_account_str]['bag'][k] >= v

                    if has_require:
                        itemMsg = ""

                        for k, v in quest['require'].items():
                            self.jx3_users[qq_account_str]['bag'][k] -= v
                            if self.jx3_users[qq_account_str]['bag'][k] == 0:
                                self.jx3_users[qq_account_str]['bag'].pop(k)
                            itemMsg += "\n{0}-{1}".format(get_item_display_name(k), v)

                        self.jx3_users[qq_account_str]['energy'] -= CHA_GUAN_ENERGY_COST
                        self.daliy_action_count[yday_str][qq_account_str]['cha_guan']['complete_quest'].append(daliy_stat['current_quest'])
                        self.daliy_action_count[yday_str][qq_account_str]['cha_guan']['current_quest'] = ""

                        rewardMsg = ""
                        for k, v in quest['reward'].items():
                            if k in self.jx3_users[qq_account_str]:
                                self.jx3_users[qq_account_str][k] += v
                                rewardMsg += "\n{0}+{1}".format(STAT_DISPLAY_NAME[k], v)

                        returnMsg = "[CQ:at,qq={0}] ���������ɣ�{1}/{2}\n����������Ʒ��{3}\n����-{4}\n��ý�����{5}".format(
                                        qq_account,
                                        len(self.daliy_action_count[yday_str][qq_account_str]['cha_guan']['complete_quest']),
                                        len(CHA_GUAN_QUEST_INFO),
                                        itemMsg,
                                        CHA_GUAN_ENERGY_COST,
                                        rewardMsg)
                    else:
                        returnMsg = "[CQ:at,qq={0}] ������Ʒ���㣡".format(qq_account)

            self.mutex.release()
            return returnMsg
        except Exception as e:
            logging.exception(e)
        finally:
            self.writeToJsonFile()
    
    def catch_hun_hun(self, qq_account):
        returnMsg = ""
        try:
            self.mutex.acquire()
            qq_account_str = str(qq_account)

            yday = self._reset_daliy_count(qq_account_str)
            yday_str = str(yday)

            if qq_account_str in self.jail_list and time.time() - self.jail_list[qq_account_str] < JAIL_DURATION:
                    time_val = calculateRemainingTime(JAIL_DURATION, self.jail_list[qq_account_str])
                    returnMsg = "[CQ:at,qq={0}] ��ʵ�㣬�㻹Ҫ�ڼ������{1}Сʱ{2}��{3}�롣".format(
                                    qq_account,
                                    time_val['hours'],
                                    time_val['mins'],
                                    time_val['secs'])
            elif self.daliy_action_count[yday_str][qq_account_str]['cha_guan']['current_quest'] == "cha_guan_hun_hun":
                if 'hun_hun_zheng_ming' in self.jx3_users[qq_account_str]['bag'] and self.jx3_users[qq_account_str]['bag']['hun_hun_zheng_ming'] >= 3:
                    returnMsg = "[CQ:at,qq={0}] ���Ѿ�ץ��̫����������Ϣһ�°ɡ�".format(qq_account_str)
                else:
                    battle_result = self._calculate_battle(qq_account_str, "hun_hun", 'pve')
                    winner = battle_result['winner']
                    loser = battle_result['loser']
                    success_chance = battle_result['success_chance']

                    if winner == qq_account_str:

                        npc = NPC_LIST["hun_hun"]

                        reward_list = npc['reward']

                        rewardMsg = ""
                        for k, v in reward_list.items():
                            if k in self.jx3_users[qq_account_str]:
                                rand = random.uniform(0, 1)
                                if rand <= npc['reward_chance']:
                                    self.jx3_users[qq_account_str][k] += v
                                    rewardMsg = "\n{0}+{1}".format(STAT_DISPLAY_NAME[k], v)
                        
                        if 'hun_hun_zheng_ming' not in self.jx3_users[qq_account_str]['bag']:
                            self.jx3_users[qq_account_str]['bag']['hun_hun_zheng_ming'] = 0
                        self.jx3_users[qq_account_str]['bag']['hun_hun_zheng_ming'] += 1
                        rewardMsg += '\n{0}+1'.format(get_item_display_name('hun_hun_zheng_ming'))

                        returnMsg = "[CQ:at,qq={0}] ץ�����ɹ����ɹ��ʣ�{1}%\n��ý�����{2}".format(
                                        qq_account,
                                        int(math.floor(success_chance * 100)),
                                        rewardMsg)
                    else:
                        returnMsg = "[CQ:at,qq={0}] ץ��ʧ�ܣ��ɹ��ʣ�{1}%".format(
                                        qq_account,
                                        int(math.floor(success_chance * 100)))

            self.mutex.release()
            return returnMsg
        except Exception as e:
            logging.exception(e)
        finally:
            self.writeToJsonFile()
    
    def do_qiyu(self, qiyu_type):
        returnMsg = ""
        try:
            self.mutex.acquire()
            logging.info(qiyu_type)

            for qq_account_str, qiyu_name in qiyu_type.items():
                qiyu = QIYU_LIST[qiyu_name]

                if qiyu_name in self.qiyu_status and self.qiyu_status[qiyu_name]['qq'] == qq_account_str and time.time() - self.qiyu_status[qiyu_name]['last_time'] < qiyu['cooldown']:
                    time_val = calculateRemainingTime(qiyu['cooldown'], self.qiyu_status[qiyu_name]['last_time'])
                    logging.info("qiyu in cd! qq: {0} remain_time: {1}hour {2}min {3}sec".format(
                                    qq_account_str,
                                    time_val['hours'],
                                    time_val['mins'],
                                    time_val['secs']))
                else:
                    requireMsg = ""
                    require_meet = True
                    if 'require' in qiyu:
                        for k, v in qiyu['require'].items():
                            if k in self.jx3_users[qq_account_str]:
                                require_meet = require_meet and (self.jx3_users[qq_account_str][k] >= v)
                                requireMsg += "{0}:{1} > {2}; ".format(k, self.jx3_users[qq_account_str][k], v)

                    if not require_meet:
                        logging.info("qiyu require not met! qq: {0} require: {1}".format(
                                        qq_account_str,
                                        requireMsg))
                    else:
                        rand = random.uniform(0, 1)

                        if rand > qiyu['chance']:
                            logging.info("No qiyu qq: {0} chance: {1} > {2}".format(
                                            qq_account_str,
                                            rand,
                                            qiyu['chance']))
                        else:
                            rewardMsg = ""
                            for k, v in qiyu['reward'].items():
                                if k in self.jx3_users[qq_account_str]:
                                    self.jx3_users[qq_account_str][k] += v
                                    rewardMsg += "\n{0}+{1}".format(STAT_DISPLAY_NAME[k], v)
                            
                            self.jx3_users[qq_account_str]['qiyu'] += 1
                            
                            if qiyu_name not in self.qiyu_status:
                                self.qiyu_status[qiyu_name] = {'qq': "", "last_time": None}
                            self.qiyu_status[qiyu_name]['qq'] = qq_account_str
                            self.qiyu_status[qiyu_name]['last_time'] = time.time()

                            returnMsg = "{0}\n��ý�����{1}".format(qiyu['description'].format(qq_account_str), rewardMsg)
                            
                            logging.info("qiyu! qq: {0} qiyu_name: {1} success_chance: {2} < {3}".format(
                                            qq_account_str,
                                            qiyu_name,
                                            rand,
                                            qiyu['chance']))

            self.mutex.release()
            return returnMsg
        except Exception as e:
            logging.exception(e)
        finally:
            self.writeToJsonFile()
