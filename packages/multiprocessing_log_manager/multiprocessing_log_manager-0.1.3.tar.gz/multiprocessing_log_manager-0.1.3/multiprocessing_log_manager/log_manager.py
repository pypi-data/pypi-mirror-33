"""
日志管理，支持日志打印到控制台或写入文件或mongodb
使用方式为  logger = LogManager('logger_name').get_and_add_handlers(log_level_int=1, is_add_stream_handler=True, log_path=None, log_filename=None, log_file_size=10,mongo_url=None,formatter_template=2)
或者 logger = LogManager('logger_name').get_without_handlers(),此种不立即记录日志，之后可以在单独统一的总闸处对所有日志根据loggerame进行get_and_add_handlers就能捕获到所有日志并记录了
"""

import os
import unittest
import time
import re
from collections import OrderedDict
import pymongo
import logging
# from logging.handlers import RotatingFileHandler
#
# # if os.name == 'posix':
# from cloghandler import ConcurrentRotatingFileHandler

from concurrent_log_handler import ConcurrentRotatingFileHandler

formatter_dict = {
    1: logging.Formatter('日志时间【%(asctime)s】 - 日志名称【%(name)s】 - 文件【%(filename)s】 - 第【%(lineno)d】行 - 日志等级【%(levelname)s】 - 日志信息【%(message)s】', "%Y-%m-%d %H:%M:%S"),
    2: logging.Formatter('%(asctime)s - %(name)s - %(filename)s - %(lineno)d - %(levelname)s - %(message)s', "%Y-%m-%d %H:%M:%S"),
}


class LogLevelException(Exception):
    def __init__(self, log_level):
        err = '设置的日志级别是 {0}， 设置错误，请设置为1 2 3 4 5 范围的数字'.format(log_level)
        Exception.__init__(self, err)


class MongoHandler(logging.Handler):
    """
    一个mongodb的log handler,支持日志按loggername创建不同的集合写入mongodb中
    """
    msg_pattern = re.compile('(\d+-\d+-\d+ \d+:\d+:\d+) - (\S*?) - (\S*?) - (\d+) - (\S*?) - ([\s\S]*)')

    def __init__(self, mongo_url, mongo_database='logs'):
        """
        :param mongo_url:  mongo连接
        :param mongo_database: 保存日志ide数据库，默认使用logs数据库
        """
        logging.Handler.__init__(self)
        mongo_client = pymongo.MongoClient(mongo_url)
        self.mongo_db = mongo_client.get_database(mongo_database)

    def emit(self, record):
        try:
            """以下使用解析日志模板的方式提取出字段"""
            # msg = self.format(record)
            # logging.LogRecord
            # msg_match = self.msg_pattern.search(msg)
            # log_info_dict = {'time': msg_match.group(1),
            #                  'name': msg_match.group(2),
            #                  'file_name': msg_match.group(3),
            #                  'line_no': msg_match.group(4),
            #                  'log_level': msg_match.group(5),
            #                  'detail_msg': msg_match.group(6),
            #                  }
            level_str = None
            if record.levelno == 10:
                level_str = 'DEBUG'
            elif record.levelno == 20:
                level_str = 'INFO'
            elif record.levelno == 30:
                level_str = 'WARNING'
            elif record.levelno == 40:
                level_str = 'ERROR'
            elif record.levelno == 50:
                level_str = 'CRITICAL'
            log_info_dict = OrderedDict()
            log_info_dict['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
            log_info_dict['name'] = record.name
            log_info_dict['file_path'] = record.pathname
            log_info_dict['file_name'] = record.filename
            log_info_dict['func_name'] = record.funcName
            log_info_dict['line_no'] = record.lineno
            log_info_dict['log_level'] = level_str
            log_info_dict['detail_msg'] = record.msg
            col = self.mongo_db.get_collection(record.name)
            col.insert_one(log_info_dict)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:  # NOQA
            self.handleError(record)


class ColorHandler(logging.StreamHandler):
    """彩色日志，根据不同级别的日志显示不同颜色"""

    def emit(self, record):
        """
        0    40    黑色
        31    41    红色
        32    42    绿色
        33    43    黃色
        34    44    蓝色
        35    45    紫红色
        36    46    青蓝色
        37    47    白色
        :param record:
        :return:
        """
        # print(record.name)
        # print(self.filter_logger_name_list)
        # if record.name in self.filter_logger_name_list:
        #     return
        try:
            # logging.LogRecord.levelno
            msg = self.format(record)
            if record.levelno == 10:
                print('\033[0;32m%s\033[0m' % msg)  # 绿色
            elif record.levelno == 20:
                print('\033[0;36m%s\033[0m' % msg)  # 青蓝色
            elif record.levelno == 30:
                print('\033[0;34m%s\033[0m' % msg)  # 蓝色
            elif record.levelno == 40:
                print('\033[0;35m%s\033[0m' % msg)  # 紫红色
            elif record.levelno == 50:
                print('\033[0;31m%s\033[0m' % msg)  # 血红色
        except (KeyboardInterrupt, SystemExit):
            raise
        except:  # NOQA
            self.handleError(record)


def get_logs_dir_by_folder_name(folder_name='/app/'):
    """获取app文件夹的路径,如得到这个路径
    D:/coding/hotel_fares/app
    如果没有app文件夹，就在当前文件夹新建
    """
    three_parts_str_tuple = (os.path.dirname(__file__).replace('\\', '/').partition(folder_name))
    # print(three_parts_str_tuple)
    if three_parts_str_tuple[1]:
        return three_parts_str_tuple[0] + three_parts_str_tuple[1] + 'logs/'  # noqa
    else:
        return three_parts_str_tuple[0] + '/logs/'  # NOQA


class LogManager(object):
    """
    一个日志类，用于创建和记录日志，支持将日志打印到控制台打印和写入日志文件。
    """
    logger_name_list = []
    logger_list = []

    def __init__(self, logger_name=None):
        """
        :param logger_name: 日志名称，当为None时候打印所有日志
        """
        self._logger_name = logger_name
        self.logger = logging.getLogger(logger_name)
        self._logger_level = None
        self._is_add_stream_handler = None
        self._log_path = None
        self._log_filename = None
        self._log_file_size = None
        self._mongo_url = None
        self._formatter = None

    def get_logger_and_add_handlers(self, log_level_int=1, is_add_stream_handler=True, log_path=get_logs_dir_by_folder_name(), log_filename=None, log_file_size=100, mongo_url=None,
                                    formatter_template=2):
        """
       :param log_level_int: 日志输出级别，设置为 1 2 3 4 5，分别对应输出DEBUG，INFO，WARNING，ERROR,CRITICAL日志
       :param is_add_stream_handler: 是否打印日志到控制台
       :param log_path: 设置存放日志的文件夹路径
       :param log_filename: 日志的名字，仅当log_path和log_filename都不为None时候才写入到日志文件。
       :param log_file_size :日志大小，单位M，默认10M
       :param mongo_url : mongodb的连接，为None时候不添加mongohandler
       :param formatter_template :日志模板，1为formatter_dict的详细模板，2为简要模板
       :type log_level_int :int
       :type is_add_stream_handler :bool
       :type log_path :str
       :type log_filename :str
       :type mongo_url :str
       :type log_file_size :int
       """
        self.__check_log_level(log_level_int)
        self._logger_level = self.__transform_logger_level(log_level_int)
        self._is_add_stream_handler = is_add_stream_handler
        self._log_path = log_path
        self._log_filename = log_filename
        self._log_file_size = log_file_size
        self._mongo_url = mongo_url
        self._formatter = formatter_dict[formatter_template]
        self.__set_logger_level()
        self.__add_handlers()
        self.logger_name_list.append(self._logger_name)
        self.logger_list.append(self.logger)
        return self.logger

    def get_logger_without_handlers(self):
        """返回一个不带hanlers的logger"""
        return self.logger

    def __set_logger_level(self):
        self.logger.setLevel(self._logger_level)

    @staticmethod
    def __check_log_level(log_level_int):
        if log_level_int not in [1, 2, 3, 4, 5]:
            raise LogLevelException(log_level_int)

    @staticmethod
    def __transform_logger_level(log_level_int):
        logger_level = None
        if log_level_int == 1:
            logger_level = logging.DEBUG
        elif log_level_int == 2:
            logger_level = logging.INFO
        elif log_level_int == 3:
            logger_level = logging.WARNING
        elif log_level_int == 4:
            logger_level = logging.ERROR
        elif log_level_int == 5:
            logger_level = logging.CRITICAL
        return logger_level

    def __remove_handlers_from_other_logger(self, handler_class):
        """
        当logger name为None时候需要移出其他logger的handler，否则可能重复记录日志
        :param handler_class: handler类型
        :return:
        """
        if self._logger_name is None:
            for logger in self.logger_list:
                for hdlr in logger.handlers:
                    if isinstance(hdlr, handler_class):
                        logger.removeHandler(hdlr)

    def __add_handlers(self):
        if self._is_add_stream_handler:
            for h in self.logger.handlers + logging.getLogger(None).handlers:
                if isinstance(h, ColorHandler):  # 使用colorhandler
                    break
            else:
                self.__add_stream_handler()
                self.__remove_handlers_from_other_logger(ColorHandler)
        if all([self._log_path, self._log_filename]):
            for h in self.logger.handlers + logging.getLogger(None).handlers:
                if os.name == 'nt':
                    if isinstance(h, ConcurrentRotatingFileHandler):
                        break
                if os.name == 'posix':
                    if isinstance(h, ConcurrentRotatingFileHandler):
                        break
            else:
                self.__add_file_handler()
                self.__remove_handlers_from_other_logger(ConcurrentRotatingFileHandler)
        if self._mongo_url:
            for h in self.logger.handlers + logging.getLogger(None).handlers:
                if isinstance(h, MongoHandler):
                    break
            else:
                self.__add_mongo_handler()
                self.__remove_handlers_from_other_logger(MongoHandler)

    def __add_mongo_handler(self):
        """写入日志到mongodb"""
        mongo_handler = MongoHandler(self._mongo_url)
        mongo_handler.setLevel(logging.DEBUG)
        mongo_handler.setFormatter(self._logger_level)
        self.logger.addHandler(mongo_handler)

    def __add_stream_handler(self):
        """
        日志显示到控制台
        """
        # stream_handler = logging.StreamHandler()
        stream_handler = ColorHandler(self.logger_name_list)  # 不使用streamhandler，使用自定义的彩色日志
        stream_handler.setLevel(self._logger_level)
        stream_handler.setFormatter(self._formatter)
        self.logger.addHandler(stream_handler)

    def __add_file_handler(self):
        """
        日志写入日志文件
        """
        if not os.path.exists(self._log_path):
            os.makedirs(self._log_path)
        log_file = os.path.join(self._log_path, self._log_filename)
        os_name = os.name
        rotate_file_handler = None
        if os_name == 'nt':
            # windows下用这个，非进程安全
            rotate_file_handler = ConcurrentRotatingFileHandler(log_file, maxBytes=self._log_file_size * 1024 * 1024, backupCount=10,
                                                                encoding="utf-8")
        if os_name == 'posix':
            # linux下可以使用ConcurrentRotatingFileHandler，进程安全的日志方式
            rotate_file_handler = ConcurrentRotatingFileHandler(log_file, maxBytes=self._log_file_size * 1024 * 1024,
                                                                backupCount=10, encoding="utf-8")
        rotate_file_handler.setLevel(self._logger_level)
        rotate_file_handler.setFormatter(self._formatter)
        self.logger.addHandler(rotate_file_handler)


class _Test(unittest.TestCase):
    @unittest.skip
    def test_repeat_add_handlers_(self):
        """测试重复添加handlers"""
        LogManager('test').get_logger_and_add_handlers(log_path='../logs', log_filename='test.log')
        LogManager('test').get_logger_and_add_handlers(log_path='../logs', log_filename='test.log')
        LogManager('test').get_logger_and_add_handlers(log_path='../logs', log_filename='test.log')
        test_log = LogManager('test').get_logger_and_add_handlers(1, log_path='../logs', log_filename='test.log')
        print('下面这一句不会重复打印四次和写入日志四次')
        time.sleep(1)
        test_log.debug('这一句不会重复打印四次和写入日志四次')

    @unittest.skip
    def test_get_logger_without_hanlders(self):
        """测试没有handlers的日志"""
        log = LogManager('test2').get_logger_without_handlers()
        print('下面这一句不会被打印')
        time.sleep(1)
        log.info('这一句不会被打印')

    @unittest.skip
    @staticmethod
    def test_add_handlers(self):
        """这样可以在具体的地方任意写debug和info级别日志，只需要在总闸处规定级别就能过滤，很方便"""
        LogManager('test3').get_logger_and_add_handlers(2)
        log1 = LogManager('test3').get_logger_without_handlers()
        print('下面这一句是info级别，可以被打印出来')
        time.sleep(1)
        log1.info('这一句是info级别，可以被打印出来')
        print('下面这一句是debug级别，不能被打印出来')
        time.sleep(1)
        log1.debug('这一句是debug级别，不能被打印出来')

    @unittest.skip
    def test_only_write_log_to_file(self):  # NOQA
        """只写入日志文件"""
        log5 = LogManager('test5').get_logger_and_add_handlers(is_add_stream_handler=False, log_filename='test5.log')
        print('下面这句话只写入文件')
        log5.debug('这句话只写入文件')

    @unittest.skip
    def test_color_and_mongo_hanlder(self):
        """测试彩色日志和日志写入mongodb"""
        connect_url = 'mongodb://myUserAdmin:8mwTdy1klnxxxx@112.25.53.14:27017/admin'
        logger = LogManager('helloMongo').get_logger_and_add_handlers(mongo_url=connect_url)
        logger.debug('一个debug级别的日志')
        logger.info('一个info级别的日志')
        logger.warning('一个warning级别的日志')
        logger.error('一个error级别的日志')
        logger.critical('一个critical级别的日志')

    @unittest.skip
    @staticmethod
    def test_get_app_logs_dir():  # NOQA
        print(get_logs_dir_by_folder_name())

    @staticmethod
    def test_none():
        log1 = LogManager('log1').get_logger_and_add_handlers()
        LogManager().get_logger_and_add_handlers()
        LogManager().get_logger_and_add_handlers()
        LogManager('log1').get_logger_and_add_handlers()
        LogManager().get_logger_and_add_handlers()
        log1.debug('打印几次？')


if __name__ == "__main__":
    unittest.main()

