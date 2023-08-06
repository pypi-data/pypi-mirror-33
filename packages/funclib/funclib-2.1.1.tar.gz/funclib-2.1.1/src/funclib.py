# -*- coding:utf-8 -*-
import sys
import re
import os
import time
import copy
import json
import platform
from .config.config import *
from .helper.helper import Helper

if sys.version[0] != '2':
    from functools import reduce
    raw_input = input

class FuncLib(object):
    @staticmethod
    def info():
        docs_vars = vars(Helper)
        keys = FuncLib.each(lambda x: FuncLib.replace(r'\n|\s|=', '', x[:8]), Helper._info.split('fn.')[1:])
        docs_keys = FuncLib.each(lambda x: '_' + x, keys)
        docs = {}
        for key in keys:
            docs[key] = docs_vars[docs_keys[keys.index(key)]]
        return {'keys': keys, 'docs': docs}

    @staticmethod
    def index(predicate, _list):
        if _list and FuncLib.typeof(_list, list, map, tuple):
            if predicate in _list:
                return _list.index(predicate)
            elif isinstance(predicate, dict):
                for i in range(0, len(_list)):
                    tmp_bool = True
                    for key in predicate:
                        if key not in _list[i] or predicate[key] != _list[i][key]:
                            tmp_bool = False
                            break
                    if tmp_bool:
                        return i
                return -1
            elif FuncLib.typeof(predicate, 'func'):
                for i in range(0, len(_list)):
                    if predicate(_list[i]):
                        return i
            return -1
        return -1

    @staticmethod
    def find(predicate, _list):
        idx = FuncLib.index(predicate, _list)
        if idx != -1:
            return _list[idx]
        return None

    @staticmethod
    def filter(predicate, _list):
        tmp_list = FuncLib.clone(_list)
        ret_list = []
        while True:
            index = FuncLib.index(predicate, tmp_list)
            if index == -1:
                break
            else:
                ret_list.append(tmp_list[index])
                if index < len(tmp_list) - 1:
                    tmp_list = tmp_list[index + 1:]
                else:
                    break
        return ret_list

    @staticmethod
    def reject(predicate, _list):
        index = FuncLib.index(predicate, _list)
        if index != -1:
            tmp_list = FuncLib.clone(_list)
            del tmp_list[index]
            return FuncLib.reject(predicate, tmp_list)
        return _list

    @staticmethod
    def reduce(*args):
        return reduce(*args)

    @staticmethod
    def contains(predicate, _list):
        index = FuncLib.index(predicate, _list)
        return index != -1

    @staticmethod
    def flatten(_list, is_deep=False):
        if _list and FuncLib.typeof(_list, list, map):
            tmp_list = []
            for item in _list:
                if isinstance(item, list):
                    if is_deep:
                        tmp_list += FuncLib.flatten(item, True)
                    else:
                        tmp_list += item
                else:
                    tmp_list.append(item)
            return tmp_list
        return _list

    @staticmethod
    def each(*args):
        return list(map(*args))

    @staticmethod
    def uniq(_list, *args):
        tmp_list = FuncLib.clone(_list)
        if FuncLib.typeof(tmp_list, tuple, map):
            tmp_list = list(tmp_list)
        if tmp_list and FuncLib.typeof(tmp_list, list):
            if len(args) == 0:
                for i in range(0, len(tmp_list)):
                    if len(tmp_list) <= i + 1:
                        break
                    tmp_list = tmp_list[:i + 1] + FuncLib.reject(
						lambda x: x == tmp_list[i], tmp_list[i + 1:])
            else:
                for i in range(0, len(tmp_list)):
                    if len(tmp_list) <= i + 1:
                        break
                    tmp_list = tmp_list[:i + 1] + FuncLib.reject(
                        lambda x: FuncLib.__cpr_val(args, x, tmp_list[i]), tmp_list[i + 1:])
        return tmp_list
    
    @staticmethod
    def __cpr_val(args, dict1, dict2):
        v1 = FuncLib.__get_val(args, dict1)
        v2 = FuncLib.__get_val(args, dict2)
        return  v1[0] and v2[0] and v1[1] == v2[1]
    
    @staticmethod
    def __get_val(args, _dict):
        tmp_val = _dict
        for i in range(0, len(args)):
            if FuncLib.typeof(tmp_val, dict) and tmp_val.has_key(args[i]):
                tmp_val = tmp_val[args[i]]
            else:
                return False, None
        return True, tmp_val


    @staticmethod
    def pluck(body, *key, **opt):
        if isinstance(body, dict):
            tmp_body = [body]
        else:
            tmp_body = body
        if FuncLib.typeof(tmp_body, list, map, tuple):
            for k in key:
                field_k = FuncLib.each(lambda x: x[k], tmp_body)
                if len(field_k) > 0:
                    tmp_body = reduce(FuncLib.list, FuncLib.each(lambda x: x[k], tmp_body))
                tmp_body = FuncLib.list(tmp_body)
            if bool(opt) and "uniq" in opt and opt['uniq']:
                tmp_body = FuncLib.uniq(tmp_body)
        return tmp_body

    @staticmethod
    def pick(origin, *layers, **kwargs):
        if 'new_layers' in kwargs:
            layers = kwargs['new_layers']
        if origin and layers:
            layer = layers[0]
            if isinstance(origin, dict) and layer in origin:
                if len(layers) == 1:
                    return origin[layer]
                elif len(layers) > 1:
                    return FuncLib.pick(origin[layer], new_layers=layers[1:])
            if FuncLib.typeof(origin, list, map, tuple):
                if isinstance(layer, list) and len(layer) == 1 \
                        and isinstance(layer[0], int) and -len(origin) <= layer[0] < len(origin):
                    if len(layers) == 1:
                        return origin[layer[0]]
                    elif len(layers) > 1:
                        return FuncLib.pick(origin[layer[0]], new_layers=layers[1:])
                else:
                    layer_val = FuncLib.find(layer, origin)
                    if layer_val:
                        if len(layers) == 1:
                            return layer_val
                        elif len(layers) > 1:
                            return FuncLib.pick(layer_val, new_layers=layers[1:])
        if 'default' in kwargs:
            return kwargs['default']
        else:
            return None

    @staticmethod
    def every(predicate, _list):
        if _list and FuncLib.typeof(_list, list, map, tuple):
            for item in _list:
                if predicate != item:
                    if isinstance(predicate, dict):
                        for key in predicate:
                            if key not in item or predicate[key] != item[key]:
                                return False
                    elif FuncLib.typeof(predicate, 'func'):
                        if not bool(predicate(item)):
                            return False
                    else:
                        return False
            return True
        return False

    @staticmethod
    def some(predicate, _list):
        if _list and FuncLib.typeof(_list, list, map, tuple):
            for item in _list:
                if predicate != item:
                    if isinstance(predicate, dict):
                        tmp_bool = True
                        for key in predicate:
                            if key not in item or predicate[key] != item[key]:
                                tmp_bool = False
                        if tmp_bool:
                            return True
                    elif FuncLib.typeof(predicate, 'func'):
                        if bool(predicate(item)):
                            return True
                else:
                    return True
            return False
        return False

    @staticmethod
    def list(*values):
        def list_handler(val):
            if isinstance(val, list):
                return val
            return [val]

        if len(values) == 0:
            return []
        elif len(values) == 1:
            return list_handler(values[0])
        else:
            return reduce(lambda a, b: list_handler(a) + list_handler(b), values)

    @staticmethod
    def drop(_list, is_without_0=False):
        if bool(_list):
            if isinstance(_list, tuple):
                _list = list(_list)
            if isinstance(_list, list):
                tmp_list = []
                for item in _list:
                    if bool(item) or (is_without_0 and item == 0):
                        tmp_list.append(item)
                return tmp_list
        return _list

    @staticmethod
    def dump(_json):
        if isinstance(_json, list) or isinstance(_json, dict) or isinstance(_json, tuple):
            return json.dumps(_json, sort_keys=True, indent=2)
        return _json

    @staticmethod
    def clone(obj):
        return copy.deepcopy(obj)

    @staticmethod
    def test(pattern, origin):
        return re.search(pattern, origin) is not None

    @staticmethod
    def replace(*args):
        return re.sub(*args)

    @staticmethod
    def iscan(exp):
        if isinstance(exp, str):
            try:
                exec (exp)
                return True
            except:
                return False
        return False

    @staticmethod
    def log(*msgs, **conf):
        line_len = 87
        title = log_title
        if 'title' in conf and str(conf['title']):
            tt = str(conf['title'])
            title = len(tt) <= 35 and tt or tt[:35]
        if 'len' in conf and FuncLib.typeof(conf['len'], int) and conf['len'] > 40:
            line_len = conf['len']
        line_b = '=' * line_len
        line_m = '-' * line_len
        line_s = '- ' * int((line_len / 2))
        title = ' ' * int((line_len - len(title)) / 2) + title
        print('%s\n%s\n%s' % (line_b, title, line_m))
        if len(msgs) > 0:
            for i in range(0, len(msgs)):
                if i > 0:
                    print(line_s)
                print(FuncLib.dump(msgs[i]))
        else:
            print('Have no Message!')
        print(line_b)

    @staticmethod
    def timer(fn, times=60, interval=1):
        if not FuncLib.typeof(fn, 'func') or not isinstance(times, int) or not isinstance(interval, int) \
                or times < 1 or interval < 0:
            return
        is_time_out = False
        count = 0
        while True:
            count += 1
            if count == times:
                fn()
                is_time_out = True
                break
            elif fn():
                break
            time.sleep(interval)
        return is_time_out

    @staticmethod
    def now():
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

    @staticmethod
    def help(*args, **kwargs):
        row_cols = 6
        docs_info = FuncLib.info()
        keys = docs_info['keys']
        docs = docs_info['docs']
        max_key_len = max(FuncLib.each(lambda x: len(x), keys)) + 6
        if len(args) > 0:
            is_show_hint = False
            if args[0] in keys:
                FuncLib.clear()
                if args[0] == 'info':
                    print(docs['info'])
                else:
                    is_show_hint = True
                    FuncLib.log(docs[args[0]], title=log_title_fix + args[0])
            if 'keep' in kwargs and kwargs['keep']:
                FuncLib.help(hint=is_show_hint, **kwargs)
        else:
            if not ('keep' in kwargs and kwargs['keep']):
                FuncLib.clear()
                print(docs['info'])
            elif 'hint' in kwargs and kwargs['hint']:
                print('')
                hints = FuncLib.each(lambda x: FuncLib.__fix_str(
                    FuncLib.__fix_str(str(keys.index(x))) + x, keys.index(x) % row_cols + 1, max_key_len
                ), keys)
                end = 0
                while True:
                    sta = end
                    end += row_cols
                    if end > len(hints):
                        hints.append(' ' * (end - len(hints)) * max_key_len + ' ')
                        end = len(hints)
                    print('[ ' + reduce(lambda a, b: a + ' ' + b, hints[sta:end]) + ']')
                    if end == len(hints):
                        break
                print('')
            idx = raw_input('Input a method or it\'s index (Nothing input will Return!): ')
            if idx:
                if FuncLib.iscan('int(%s)' % idx) and int(idx) in range(0, len(keys)):
                    FuncLib.clear()
                    is_show_hint = False
                    key = keys[int(idx)]
                    if idx == '0':
                        print(docs[key])
                    else:
                        is_show_hint = True
                        FuncLib.log(docs[key], title=log_title_fix + key)
                    FuncLib.help(keep=True, hint=is_show_hint)
                else:
                    FuncLib.help(idx, keep=True)

    @staticmethod
    def __fix_str(string, column=0, max_len=14):
        str_len = len(string)
        tmp_str = string
        if column == 0:
            tmp_str = string + ': fn.'
            if str_len == 1:
                tmp_str = '0' + tmp_str
        elif str_len < max_len:
            tmp_str = string + ' ' * (max_len - str_len - 1)
            if column == 1 or column == 2:
                tmp_str += ' '
            elif column == 3:
                tmp_str = tmp_str[:-1]
        return tmp_str

    @staticmethod
    def clear():
        if platform.system() == "Windows":
            os.system('cls')
        else:
            os.system('clear')

    @staticmethod
    def typeof(var, *types):
        if len(types) > 0:
            for _type in types:
                if (isinstance(_type, type) and isinstance(var, _type)) \
                        or (_type == 'func' and 'function' in str(type(var))):
                    return True
        return False
