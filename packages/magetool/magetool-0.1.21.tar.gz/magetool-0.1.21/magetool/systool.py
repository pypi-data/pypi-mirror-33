#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2017-12-09 22:36:40
# @Author  : mage
# @Link    : http://woodcol.com
# @market. : https://fengmm521.taobao.com
# @Version : $Id$

from sys import version_info  
def pythonVersion():
    return version_info.major,version_info.minor

if __name__ == '__main__':
    print(pythonVersion())