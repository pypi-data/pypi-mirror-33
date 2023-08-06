# -*- coding: utf-8 -*-
import re
import json
from ..lib.CommonLogger import debug, info, warn, error


class RouteInfoGenerator:
    """
    用于生成需要的对接数据结构
    """

    @classmethod
    def generate_route_info(cls, url, func):
        the_doc = func.__doc__
        if the_doc is None:
            warn("url:{url}没有函数doc".format(url=url))
            return None
        debug("获取url:{url},doc:{doc}".format(url=url, doc=the_doc))
        doc_lines = the_doc.splitlines()
        if len(doc_lines) < 1:
            warn("不支持doc的解析[行数过少]:{d}".format(d=the_doc))
            return None
        else:
            handler = cls.get_doc_generate_handler(doc_lines[0])
            debug("获取到的doc生成函数是:{func}".format(func=handler))
            the_route_info = handler(doc_lines)
            return the_route_info

    @classmethod
    def get_doc_generate_handler(cls, first_line):
        first_line = first_line.strip().lower()
        debug("检查doc类型:{li}".format(li=first_line))
        match_dict = {
            'att_doc': cls.parse_doc_as_att_annotation
        }
        return match_dict.get(first_line, cls.parse_doc_as_att_annotation)

    @classmethod
    def parse_doc_as_att_annotation(cls, the_doc_lines):
        debug("对doc生成路由信息 {doc}".format(doc='\n'.join(the_doc_lines)))
        route_info = {'params': [], 'example': []}
        route_match_regexp = {
            'name': r'\s*@name\s+(.*)\s*$',
            'description': r'\s*@description\s+(.*)\s*$',
            'author': r'\s*@author\s+(.*)\s*$',
            'params': r'\s*@params\s*$',
            'example': r'\s*@example[s]*\s*$',
            'expect': r'\s*@expect\s+(.*)\s*$',
            'toolable': r'\s*@toolable\s*(.*)\s*$',
            'long_description': r'\s*@long_description\s*$',
        }
        is_get_params = False
        is_get_example = False
        is_long_description = False
        for one_line in the_doc_lines:
            if is_get_params:
                if one_line.find('name:') != -1 and one_line.find('type:') != -1 and one_line.find('desc:') != -1:
                    debug("这是一个参数行:{}".format(one_line))
                    route_info['params'].append(cls.parse_att_params(one_line))
                else:
                    debug("这已经不是一个参数行:{}".format(one_line))
                    is_get_params = False
            if is_get_example:
                if one_line.find('usage:') != -1 and one_line.find('desc:') != -1:
                    debug("这是一个例子行:{}".format(one_line))
                    route_info['example'].append(cls.parse_att_example(one_line))
                else:
                    debug("这已经不是一个例子行:{}".format(one_line))
                    is_get_example = False
            if is_long_description:
                if re.match("^\s*@", one_line):
                    debug("这不是一个 long_description {}".format(one_line))
                    is_long_description = False
                else:
                    route_info['long_description'] = '\n'.join([route_info['long_description'], one_line])

            for one_key in route_match_regexp.keys():
                match_data = re.match(route_match_regexp[one_key], one_line)
                if match_data:
                    if one_key == 'params':
                        is_get_params = True
                        continue
                    if one_key == 'example':
                        is_get_example = True
                        continue
                    if one_key == 'long_description':
                        is_long_description = True
                        route_info[one_key] = ''
                        continue
                    if one_key == 'toolable':
                        route_info[one_key] = 'true'
                        continue
                    route_info[one_key] = match_data.group(1).strip()
        debug('最后得到的一个路由信息是:{}'.format(json.dumps(route_info)))
        if route_info.get('name', None) is None:
            info("无法解析到name,认为这个解析是失败的")
            return None
        return route_info

    @classmethod
    def parse_att_params(cls, params_line):
        desc_arr = params_line.split('desc:')
        the_desc = desc_arr.pop().strip()
        params_arr = desc_arr[0].split(',')
        param_info = {'id': params_arr[0].strip(), 'desc': the_desc}
        for one_param_opt_str in params_arr[1:]:
            debug("需要处理 {}".format(one_param_opt_str))
            one_param_opt_str = one_param_opt_str.strip()
            if len(one_param_opt_str) == 0:
                debug('有","分割的空行,容错处理 {}'.format(one_param_opt_str))
                continue
            param_opt_arr = one_param_opt_str.split(':')
            if len(param_opt_arr) != 2:
                debug('没有":"的一个参数项,容错处理 {}'.format(params_arr))
                continue
            param_key = param_opt_arr[0].strip()
            param_value = param_opt_arr[1].strip()
            param_info[param_key] = param_value
        debug("获取到的参数解析信息:{}".format(json.dumps(param_info)))
        return param_info

    @classmethod
    def parse_att_example(cls, params_line):
        desc_arr = params_line.split('desc:')
        the_desc = desc_arr.pop().strip()
        params_arr = desc_arr[0].split('usage:')
        param_info = {
            'desc': the_desc,
            'usage': params_arr.pop().strip()
        }
        debug("获取到的example解析信息:{}".format(json.dumps(param_info)))
        return param_info
