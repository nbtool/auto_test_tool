#!/usr/bin/env python3
# coding=utf-8


def bsp_string_check_in_str(str,list):
    for sub_str in list:
        if sub_str in str:
            return 1

    return 0

