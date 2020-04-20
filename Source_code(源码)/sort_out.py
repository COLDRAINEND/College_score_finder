"""
-------------------------------------------------------------------------------------------
* @Creation date: 2020-01-27 23:59:23
* @Last Modified by:   COLDRAIN_END
* @Version: 0.5a
* @Blog:  https://blog.csdn.net/COLDRAIN_END
* @Copyright (c) <Creation date>  COLDRAIN_END. All rights reserved.
-------------------------------------------------------------------------------------------
"""
import json
import os


class Main(object):
    def __init__(self):
        self.filepath_input = "/home/coldrain-end/CODE_Projects/Python/get_loop/score_library.json"
        self.filepath_ouput = "/home/coldrain-end/CODE_Projects/Python/get_loop/builds.txt"
        self.name_get = []
        self.class_get = []
        self.count_loop = 0         # 统计错误信息数量
        self.count_class = 0

    def run(self):
        with open(self.filepath_input, "r") as f_object:
            load_dict = json.load(f_object)
        for single in load_dict:
            get_list = sorted(single.items(), key=lambda x: x[0])
            ProcessAndWrite.structure(self, get_list)
        Main.print_info(self)

    def print_info(self):
        print("\n\n* ------------------------------------------------------\n")
        print("* 运行结束 ：程序总共处理了 " + str(self.count_loop) + " 条数据. \n")
        basedir = os.path.abspath("builds.txt")
        print("* 生成文件已保存到" + str(basedir))
        print("\n* ------------------------------------------------------\n")


class ProcessAndWrite(object):
    def __init__(self, filepath_ouput):
        self.filepath_ouput = filepath_ouput
        self.name_get = []
        self.class_get = []

    def structure(self, get_list):
        for line in get_list:
            line = str(line)
            line = line.lstrip("'(").rstrip("')").replace(" '", "").replace("'", "").split(',')   # 去除括号，单引号，再分割为列表
            if line[0] == 'name':
                self.name_get = line[1]
            if line[0] == 'class':
                self.class_get = line[1]

        filepath = open(self.filepath_ouput, "a")
        filepath.write(self.class_get + "\t" + self.name_get)
        print(str(self.class_get) + "  " + str(self.name_get) + " 的分数信息已整理写入文件.")

        for line in get_list:
            line = str(line)
            line = line.lstrip("'(").rstrip("')").replace(" '", "").replace("'", "").split(',')   # 去除括号，单引号，再分割为列表
            if line[0] != 'class' and line[0] != 'name':
                filepath.write("\t" + line[0]+"\t" + line[1])
                # print(str(line[0]) + str(line[1]))

        filepath.write("\n")
        self.count_loop = self.count_loop + 1


r = Main()
r.run()
