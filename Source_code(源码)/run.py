"""
-------------------------------------------------------------------------------------------
* @Creation date: 2020-01-27 20:38:04
* @Last Modified by:   COLDRAIN_END
* @Version: 1.5(try)
* @Blog:  https://blog.csdn.net/COLDRAIN_END
* @Copyright (c) <Creation date>  COLDRAIN_END. All rights reserved.
-------------------------------------------------------------------------------------------
"""
from urllib import request, parse
import urllib
from bs4 import BeautifulSoup
import json
import time
"""出于性能原因，对长行跳过令牌化。长行的长度可通过 "editor.maxTokenizationLineLength" 进行配置。"""


class Run(object):
    """ 负责运行相关路径&数值集合，程序从这里开始"""
    def __init__(self):
        self.get_key_value = []
        self.url = "http://www.xiaotaokeji.com/magicform/query/result.php"      # 查询 API Interface
        self.filepath_json = "score_library.json"
        self.filepath_txt = "score_text.txt"
        self.ouput_txt_active = True        # 是否写入为 txt 文件
        self.count_loop = 0                 # 运行次数
        self.error_line = []                    # 记录出错
        # 设置程序运行速度时间间隔，防止宕机或者503错误， 0为最快，默认为1秒
        self.active_speed = 0

        # 用于构建各年级查询的表单数据列表 ， 列表索引 0和1 分别对应 form_id 和 media_id
        get_grade = input("请输入要查询抓取的年级为（如：2019） --->> ")
        if str(get_grade) == '2019':
            self.form_id = ['kS6rp1DbawZmiLyY', '1104371724']
        elif str(get_grade) == '2018':
            self.form_id = ['gUVzpdDRM7tCxEXu', '1104371724']
        elif str(get_grade) == '2017':
            self.form_id = ['4T9kM2I07JLEgYS3', '1104371724']
        else:
            self.form_id = ['kS6rp1DbawZmiLyY', '1104371724']  # 默认为生成查询19级的数据

        get_path = input("请输入 学号文件 的路径位置， 留空默认为 本程序根目录下的 xuehao.txt --->> ")
        if get_path:
            self.filepath_source = str(get_path)
        else:
            self.filepath_source = "xuehao.txt"

    def run_loop(self):
        try:
            filepath = open(self.filepath_source, "r+")
        except FileNotFoundError:
            print("\n程序错误！ 无法找到 xuehao.txt 文件。 程序已终止。")
            print("\n程序错误！ 无法找到 xuehao.txt 文件。 程序已终止。")
        try:
            get_str = filepath.readlines()
        except UnboundLocalError:
            pass
        for line in get_str:
            """ 使用断言方法排除错误 """
            self.count_loop = self.count_loop + 1
            while(True):
                try:
                    html = ObtainAndProcess.request_source(self, line)
                    break
                except IndexError:
                    print("\n\n* --出-现-错-误------出-现-错-误--------------------------------")
                    print("* ")
                    print("* “学号文件” 中的格式存在错误，请检查行中的信息是否是以4个空格分隔。")
                    print("* 程序：（已取消使用“学号文件”第" + str(self.count_loop) + "行的查询信息.")
                    print("* ---------------------------------------------------------------")
                    self.error_line.append(self.count_loop)
                    break
                except urllib.error.HTTPError:
                    print("\n\n* --伺-服-器-拒-绝-访-问---------------------------------------")
                    print("* HTTP Error 503: Service Temporarily Unavailable")
                    print("* 程序：（正在努力重新请求数据哦～    伺服器被玩坏了的说～ s）")
                    print("* 作者：等一下就可以了，服务器需要休息一下.")
                    print("\n* RE REQUESTING!  φ ( ≧ ω ≦ * ) ♪")
                    time.sleep(15)      # 等待15秒，等待服务器冷却
                    continue
            try:
                dict_info = ObtainAndProcess.extract(self, html)
            except IndexError:
                print("\n\n* --出-现-错-误------出-现-错-误--------------------------------")
                print("* ")
                print("* “学号文件”第 " + str(self.count_loop) + " 行出现错误，界面数据解析失败!")
                print("* 程序：( 放弃对该条目的字典构建，转为处理下一条目.)")
                print("* ---------------------------------------------------------------")
                self.error_line.append(self.count_loop)

            OuputFile.ouput_json(self, dict_info)
        Run.print_info(self)

    def run_speed(self):
        time.sleep(self.active_speed)   # 设置暂停，防止速度太快崩溃

    def print_info(self):
        effective = self.count_loop - len(self.error_line)
        percentage = ((self.count_loop - len(self.error_line)) / self.count_loop) * 100
        print("\n\n\n\n\n\n\n\n\n")
        print("* -运-行-结-束------------------------------------------------------")
        print("* 总计：  " + str(self.count_loop) + " 条数据.\t 有效数据：" + str(effective) + "条.\t" + "存在错误：" + str(len(self.error_line)) + "条.")
        print("* 本次数据抓取成功率为：　" + str('%.2f' % percentage) + " %")             # 计算成功率
        print("* ")

        for line in self.error_line:
            print("* \t错误： “学号文件”第 " + str(line) + " 行的学号或姓名信息存在问题，请检查.")
        print("* ")
        print("* 1. 请检查来源文件的错误行所对应的学号和姓名是否正确.")
        print("* 2. 请检查抓取的网页数据存储结构是否已经改变.")
        print("* 3. 请检查学号文件中行的数据是否是以4个空格分隔的.")
        print("* 4. 请检查 API 接口是否已经失效， 失效的话本程序寿命已尽，感谢使用！")
        print("* ")
        print("* -------------------------------------------------------------------\n")


class ObtainAndProcess(object):
    """ 抓取网页上的信息并进行界面解析、分离整理与合成 """
    def __init__(self, url, ouput_txt_active,  error_line, count_loop):
        self.url = url
        self.ouput_txt_active = ouput_txt_active
        self.error_line = error_line
        self.count_loop = count_loop
        self.form_id = []           # 预留表单提交接口

    def request_source(self, line):
        # self.count_loop = self.count_loop + 1
        line = line.strip("\n")
        self.get_key_value = line.split("    ")  # 文件中使用4个空格分隔信息
        form_data = {
            'data_1': self.get_key_value[0],             # 学号
            'data_2': self.get_key_value[1],             # 姓名
            'form_id': self.form_id[0],                 # 输入用于构建表单的相关数据
            'media_id': self.form_id[1]               # （见Run类， __init__初始化处）
        }
        data = parse.urlencode(form_data).encode('utf-8')
        req = request.Request(self.url, data)
        responce = request.urlopen(req)
        html = responce.read().decode()     # 得到网页
        return html

    def extract(self, html):
        """
        界面解析参照:
        https://beautifulsoup.readthedocs.io/zh_CN/latest/
        """
        soup = BeautifulSoup(html, 'html.parser')   # print(soup.prettify())
        result_score = []       # 课程，成绩，班级
        result_info = []          # 学号，姓名，学院
        keys = []
        values = []
        name_get = []
        class_get = []
        erorr_get = []
        # 抓取到的数据顺序： 学号，姓名，课程，成绩，学院，班级
        # exclude = ['1938050122', '彭成新', '机电与信息工程学院', '19计算机网络技术1']
        for link in soup.find_all("span"):
            text = "".join(link.string.split())   # 强制去除字符串中的空白符
            if (text != self.get_key_value[0] and text != self.get_key_value[1] and text != '机电与信息工程学院'):        # 这里分离出 课程，成绩，班级（变动信息）
                result_score.append("".join(link.string.split()))
            else:
                result_info.append("".join(link.string.split()))

        # 课程<index>是3的倍数    成绩<index -1>是3的倍数   班级<index -2>或者<index +1>是3的倍数
        for sep in range(len(result_score)):
            if sep % 3 == 0:
                keys.append(result_score[sep])
            elif (sep-1) % 3 == 0:
                values.append(result_score[sep])
            elif (sep+1) % 3 == 0:
                class_get.append(result_score[sep])
            else:
                erorr_get.append(result_score[sep])

        # 获得 从网页中抓取的姓名
        for sep in range(len(result_info)):
            if (sep-1) % 3 == 0:
                name_get.append(result_info[sep])

        # 生成待写入的字典
        dict_json = {'name': name_get[0], 'class': class_get[0], }
        for x in range(len(keys)):
            dict_json[keys[x]] = values[x]

        # 判断是否调用写入为 txt 文件
        if self.ouput_txt_active:
            OuputFile.ouput_txt(self, result_info, keys, values)

        print("\n\n第 " + str(self.count_loop) + " 个数据集正在存储  ο(=•ω＜=)ρ⌒☆ ")
        print("--->>  " + str(result_info[1]) + "的: " + str(keys) + " 成绩信息")

        return dict_json


class OuputFile(object):
    """ 输出文件为 json 或者是 txt """
    def __inti__(self, filepath_json, filepath_txt):
        self.filepath_json = filepath_json
        self.filepath_txt = filepath_txt

    # 将数据集输出到 json 文件
    def ouput_json(self, dict_json):
        with open(self.filepath_json, "a", encoding='utf-8') as f_object:
            json.dump(dict_json, f_object, ensure_ascii=False)
            f_object.write(",")

    # 将数据集输出到 txt 文件
    def ouput_txt(self,  result_info, keys, values):
        ouput = open(self.filepath_txt, "a")
        ouput.write(result_info[1])

        for x in range(len(keys)):
            ouput.write("\t" + keys[x])
        ouput.write("\n")
        for x in range(len(values)):
            ouput.write("\t" + values[x])
        ouput.write("\n\n")


run = Run()
run.run_loop()
