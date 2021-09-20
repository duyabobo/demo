# -*- coding: utf-8 -*-
# 脚本用于监控新旧数据同步:
# 同步某个表之后，执行一次全量数据对比，只执行一次。
# update_time 在24小时内，且在十秒之前的新旧数据记录核对，每天检查一次。
# update_time 在三分钟之内，且在十秒之前的新旧数据记录核对，每隔一分钟检查一次。
import sys

import fire
import os
from datetime import datetime, timedelta
from time import time

current_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.dirname(current_dir))
from configs import ENV
from hd_lib.services.dingding import DingDingThird
from monitors.config import check_config
from utils.logger_tool import check_data_logger

reload(sys)
sys.setdefaultencoding('utf-8')

ABSOLUTE_DIR = '{}/models'.format(os.path.dirname(current_dir))
OLD_DIR_NAME = 'oldage'
NEW_DIR_NAME = 'young'
UK_VALUE_SPLIT_STR = '_uk_'


class Config(object):
    def __init__(self, config):
        self.config = config
        self.old_db = self.config['old_db']
        self.new_db = self.config['new_db']
        self.old_table = self.config['old_table']
        self.new_table = self.config['new_table']
        self.old_uks = self.config['old_uks']
        self.new_uks = self.config['new_uks']
        self.old_special_filter_dict = self.config.get('old_special_filter_dict', {})
        self.new_special_filter_dict = self.config.get('new_special_filter_dict', {})
        self.old_model = None
        self.new_model = None
        self.parse_config()

    def parse_config(self):
        def _is_model(m):
            if not getattr(m, '_meta', None):
                return None
            if not getattr(m._meta, 'table_name', None):
                return None
            if m._meta.table_name != table_name:
                return None
            return m

        for _root, _dirs, _files in os.walk(ABSOLUTE_DIR):
            if _dirs:
                continue

            db_name = _root.split('/')[-1]
            db_type = _root.split('/')[-2]
            for fname in _files:
                if fname.startswith('_') or not fname.endswith('.py'):
                    continue

                table_name = fname.split('.')[0]
                _paths = ABSOLUTE_DIR.split('/')[-1:] + [db_type, db_name, table_name]
                _mdu = __import__('.'.join(_paths), fromlist=[table_name])

                if db_type == NEW_DIR_NAME and db_name == self.new_db and table_name == self.new_table:
                    for m in _mdu.__dict__.values():
                        if _is_model(m):
                            self.new_model = m

                if db_type == OLD_DIR_NAME and db_name == self.old_db and table_name == self.old_table:
                    for m in _mdu.__dict__.values():
                        if _is_model(m):
                            self.old_model = m

    @property
    def property_map(self):
        return self.config['old_2_new_column_map']

    @classmethod
    def get_one_instance(cls, old_db_name, old_table_name):
        for config in check_config:
            if config['old_db'] == old_db_name and config['old_table'] == old_table_name:
                return cls(config)
        return None


class Checker(object):
    def __init__(self, config, from_time, to_time=datetime.now()-timedelta(seconds=10)):
        """
        初始化
        :param config: 一个 Config 实例
        :param from_time: 检查的起始时间（datetime）
        :param to_time: 检查的结束时间（datetime)
        """
        self.config = config
        self.from_time = from_time
        self.to_time = to_time
        self.old_model = self.config.old_model
        self.new_model = self.config.new_model
        self.property_map = self.config.property_map
        self.old_unique_keys = self.config.old_uks
        self.new_unique_keys = self.config.new_uks
        self.old_special_filter_dict = self.config.old_special_filter_dict
        self.new_special_filter_dict = self.config.new_special_filter_dict
        self.old_table_name = '{}.{}'.format(self.config.old_db, self.config.old_table)
        self.new_table_name = '{}.{}'.format(self.config.new_db, self.config.new_table)
        self.err_msg_list = []

        self.old_cnt = 0
        self.new_cnt = 0
        self.set_data_cnt()

    def set_data_cnt(self):
        self.old_cnt = self.old_model.get_cnt(from_time=self.from_time, to_time=self.to_time)
        self.new_cnt = self.new_model.get_cnt(from_time=self.from_time, to_time=self.to_time)

    @property
    def noti_msg(self):
        return '数据对比起始时间：{}\n'\
               '旧库表：{}，旧表唯一键：{}，旧数据对比总量：{}\n'\
               '新库表：{}，新表唯一键：{}，新数据对比总量：{}\n' \
               '错误信息：\n{}'.\
            format(self.from_time.strftime("%Y-%m-%d %H:%M:%S"),
                   self.old_table_name, self.old_unique_keys, self.old_cnt,
                   self.new_table_name, self.new_unique_keys, self.new_cnt,
                   '\n'.join(self.err_msg_list))

    @staticmethod
    def get_uk_value(record, unique_keys):
        uk_value_list = [str(getattr(record, unique_key, '')) for unique_key in unique_keys]
        return UK_VALUE_SPLIT_STR.join(uk_value_list)

    @staticmethod
    def split_uk_values(uk_value):
        return uk_value.split(UK_VALUE_SPLIT_STR)

    @staticmethod
    def get_uk_filters(model, unique_keys, uk_values):
        special_filters = []
        assert unique_keys and uk_values and len(unique_keys) == len(uk_values)
        for i, uk in enumerate(unique_keys):
            special_filters.append(getattr(model, uk) == uk_values[i])
        return special_filters

    @staticmethod
    def get_filters(model, from_time, to_time, special_filter_dict):
        special_filters = [model.update_time > from_time, model.update_time <= to_time]
        for property_name, property_value in special_filter_dict.items():
            special_filters.append(getattr(model, property_name) == property_value)
        return special_filters

    def get_record_dict(self, model, unique_keys, special_filter_dict=None):
        if special_filter_dict is None:
            special_filter_dict = {}
        filters = self.get_filters(model, self.from_time, self.to_time, special_filter_dict)

        record_dict = {}
        records = model.get_records(*filters)
        if not records:
            return record_dict

        for record in records:
            uk_value = self.get_uk_value(record, unique_keys)
            record_dict[uk_value] = record
        return record_dict

    @staticmethod
    def pop_item(from_record_dict, to_record_dict, uk_value):
        if uk_value in from_record_dict:
            from_record_dict.pop(uk_value)
        if uk_value in to_record_dict:
            to_record_dict.pop(uk_value)

    def exist_check(self, from_record_dict, to_record_dict, is_old_2_new=True):
        """from有都，to一定有"""
        for uk_value, from_record in from_record_dict.items():
            if getattr(from_record, 'no_need_check', False):  # 特殊规则：这些记录不需要检查。比如新重构后确实会出现一下不需要旧数据存在的数据
                check_data_logger.info("不需要检查：is_old_2_new={} uk_value={}".format(is_old_2_new, uk_value))
                self.pop_item(from_record_dict, to_record_dict, uk_value)
                continue

            if uk_value not in to_record_dict:
                to_model, to_unique_keys = (self.new_model, self.new_unique_keys) if is_old_2_new \
                    else (self.old_model, self.old_unique_keys)
                uk_values = self.split_uk_values(uk_value)
                uk_filters = self.get_uk_filters(to_model, to_unique_keys, uk_values)
                to_record = to_model.get_by_uks(*uk_filters)
                if not to_record:  # 确实是数据不存在，不是update_time被更新了
                    err_msg = '数据不存在：is_old_2_new={} uk_value={}'.format(is_old_2_new, uk_value)
                    self.err_msg_list.append(err_msg)
                self.pop_item(from_record_dict, to_record_dict, uk_value)  # 数据存在，只不过update_time被更新了
                continue

    def value_check(self, from_record_dict, to_record_dict, is_old_2_new=True):
        """to的值，一定和from的值等价"""
        for uk_value, from_record in from_record_dict.items():
            to_record = to_record_dict[uk_value]  # 经过 exist_check，这里都肯定存在
            for old_property, new_property in self.property_map.items():
                from_property, to_property = (old_property, new_property) if is_old_2_new \
                    else (new_property, old_property)

                from_property_value = getattr(from_record, from_property, None)
                to_property_value = getattr(to_record, to_property, None)
                from_value = from_property_value.encode('utf8') if isinstance(from_property_value, unicode) \
                    else from_property_value
                to_value = to_property_value.encode('utf8') if isinstance(to_property_value, unicode) \
                    else to_property_value

                if from_property_value is None or to_property_value is None or str(from_property_value) != str(to_property_value):
                    err_msg = '新旧数据字段值不一致 is_old_2_new={} uk_value={} from_column_name={} to_column_name={} ' \
                              'from_column_value={} to_column_value={}'. \
                        format(is_old_2_new, uk_value, from_property, to_property, from_value, to_value)
                    self.err_msg_list.append(err_msg)
                    self.pop_item(from_record_dict, to_record_dict, uk_value)
                    continue

    def check_data(self):
        """
        检查一个表的新旧数据
        :return:
        """
        old_record_dict = self.get_record_dict(self.old_model, self.old_unique_keys, self.old_special_filter_dict)
        new_record_dict = self.get_record_dict(self.new_model, self.new_unique_keys, self.new_special_filter_dict)
        self.exist_check(old_record_dict, new_record_dict)
        self.exist_check(new_record_dict, old_record_dict, is_old_2_new=False)
        self.value_check(old_record_dict, new_record_dict)
        self.value_check(new_record_dict, old_record_dict, is_old_2_new=False)


class Notify(object):

    @classmethod
    def send_noti(cls, msg):
        sms_text = '【线上】数据同步监控报警：\n{}' if ENV == 'online' else '【测试】数据同步监控报警：\n{}'
        sms_text = sms_text.format(msg)
        DingDingThird.send_dingmsg(
            warn_message=sms_text,
            access_token='324798aa4bb6e4a3ded153be8f7b1b128b5c52910b027254bedf173b9b3ac130'
        )


def decorator(func):
    def inner(*args, **kwargs):
        start = time()
        try:
            func(*args, **kwargs)
        except Exception as e:
            check_data_logger.exception(e)
            Notify.send_noti("err_msg: 抛出异常")
            print e
        end = time()
        tc = end - start
        if tc > 120:
            Notify.send_noti("err_msg: 耗时有点长 tc=%s秒" % tc)
        check_data_logger.info('func_name:{} tc:{}'.format(func.__name__, end-start))
        return
    return inner


class App(object):

    @classmethod
    def manual_check(cls, old_db, old_table, from_time):
        config = Config.get_one_instance(old_db, old_table)
        if not config:
            msg = 'from_time:{} old_db:{} old_table:{} msg:找不到配置'.format(from_time, old_db, old_table)
            check_data_logger.error(msg)
            print msg
            return

        check = Checker(config, from_time)
        check.check_data()
        if check.err_msg_list:
            Notify.send_noti(check.noti_msg)

    @classmethod
    def auto_check(cls, from_time):
        for c in check_config:
            config = Config(c)
            check = Checker(config, from_time)
            check.check_data()
            if check.err_msg_list:
                Notify.send_noti(check.noti_msg)
            check_data_logger.info(check.noti_msg)

    @classmethod
    @decorator
    def total_check(cls, old_db, old_table):
        """
        全量检查
        :param old_db:
        :param old_table:
        :return:
        """
        check_data_logger.info('total_check old_db:{} old_table:{}'.format(old_db, old_table))
        now = datetime.now()
        hour = now.hour
        if 4 < hour < 23:
            msg = 'old_db:{} old_table:{} msg:全量检查请在夜里23点到第二天凌晨4点之间执行'.format(old_db, old_table)
            check_data_logger.error(msg)
            print msg
            return
        from_time = now - timedelta(days=20*365)
        cls.manual_check(old_db, old_table, from_time)

    @classmethod
    @decorator
    def day_check(cls):
        now = datetime.now()
        hour = now.hour
        if 4 < hour < 23:
            msg = 'msg:每日检查请在夜里23点到第二天凌晨4点之间执行'
            check_data_logger.error(msg)
            print msg
            return
        from_time = now - timedelta(days=1)
        cls.auto_check(from_time)

    @classmethod
    @decorator
    def minute_check(cls):
        now = datetime.now()
        from_time = now - timedelta(minutes=3)
        cls.auto_check(from_time)


if __name__ == '__main__':
    fire.Fire(App)
