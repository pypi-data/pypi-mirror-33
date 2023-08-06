#coding=utf-8
import logging
import sys

__logger_record = {}

def get_logger(logger_name='moelog',logging_level=logging.INFO,both_to_file_path=None):
    '''
    example:
    l = get_logger()
    l.info('foo')
    l.i('foo')
    '''

    if logger_name in __logger_record:
        result = __logger_record[logger_name]
    else:
        result = logging.getLogger(logger_name)
        __logger_record[logger_name] = result

    assert isinstance(result,logging.Logger)

    result.setLevel(logging_level)

    foramter = logging.Formatter('%(asctime)s [%(levelname)s]\t:%(message)s')

    t = logging.StreamHandler(sys.stdout)
    t.setFormatter(foramter)
    result.addHandler(t)

    if both_to_file_path:
        t = logging.FileHandler(both_to_file_path)
        t.setFormatter(foramter)
        result.addHandler(t)

    setattr(result,'d',result.debug)
    setattr(result,'i',result.info)
    setattr(result,'w',result.warning)
    setattr(result,'e',result.error)
    setattr(result,'c',result.critical)

    return result