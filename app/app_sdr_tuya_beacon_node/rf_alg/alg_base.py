#!/usr/bin/env python
# coding=utf-8
# 基础算法
import math
import shutil
import os


class alg_base:
    @staticmethod
    def to_hexstr(int_array,sgm=''):
        return sgm.join(format(num, '02x') for num in int_array).upper()

    @staticmethod
    def to_hexs(hex_string):
        return [int(hex_string[i:i+2], 16) for i in range(0, len(hex_string), 2)]

    # 将数组files中的所有文件复制到目标目录中
    # 如果目录不存在，则创建目录
    @staticmethod
    def my_file_copy_files_to(files,dst_path):
        # 清空一个文件夹（如果已经存在，则删除）
        def my_file_clear_folder(path):
            my_file_rm_dir(path)

            time.sleep(1)
            os.makedirs(path)

        # 删除一个文件夹
        def my_file_rm_dir(path):
            if os.path.exists(path):
                shutil.rmtree(path, onerror=readonly_handler)

        def readonly_handler(func, path, execinfo):
            os.chmod(path, stat.S_IWRITE)
            func(path)

        if os.path.exists(dst_path) == False:
            my_file_clear_folder(dst_path)

        for file in files:
            if os.path.exists(file):
                shutil.copy(file,dst_path)

    @staticmethod
    def get_distance(position1,position2):
        x = position1[0] - position2[0]
        y = position1[1] - position2[1]
        z = position1[2] - position2[2]

        return math.sqrt(x*x+y*y+z*z)
