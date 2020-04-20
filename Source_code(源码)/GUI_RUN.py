"""
-------------------------------------------------------------------------------------------
* @Creation date: 2020-01-30 14:00:40
* @Last Modified by:   COLDRAIN_END
* @Version: default
* @Blog:  https://blog.csdn.net/COLDRAIN_END
* @Copyright (c) <Creation date>  COLDRAIN_END. All rights reserved.
-------------------------------------------------------------------------------------------
"""
# -*- coding: utf-8 -*-
# Form implementation generated from reading ui file 'connect_me.ui'
# Created by: PyQt5 UI code generator 5.11.3
# WARNING! All changes made in this file will be lost!

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from GUI_01 import Ui_MainWindow
from GUI_02 import Ui_ABOUT
from GUI_03 import Ui_Advanced
from urllib import request, parse
import urllib
from bs4 import BeautifulSoup
import time
import os
import base64
import memory_pyfile

""" PYQT5 资料参考： https://doc.qt.io/qt-5/gettingstarted.html """


class MyMainForm(QMainWindow, Ui_MainWindow):
    """ 这里是主窗口，程序从这里开始，负责主要的运行和调用各种选项 """
    def __init__(self, parent=None):
        super(MyMainForm, self).__init__(parent)
        self.setupUi(self)

        # 触发“关于”按钮
        about = AboutForm()
        self.pushButton_about.clicked.connect(lambda: about.show())
        # 触发“高级功能”按钮
        advanced = AdvancedForm()
        self.pushButton_advanced.clicked.connect(lambda: advanced.show())
        # 触发“查询成绩”按钮
        self.pushButton_start.clicked.connect(self.main)

        # 构建年级相应查询表单
        self.form_id = []
        self.key_courses = []
        self.value_scores = []
        self.college_get = []
        self.class_get = []
        self.name_get = []
        self.build_dict = {}    # 建造保存 课程与成绩的键值对字典
        self.API_url = "http://www.xiaotaokeji.com/magicform/query/result.php"

    def main(self):
        """ 主要的函数， 用于调用各个功能作用和处理错误的发生 """
        OuputGUI.initialization_display(self)
        input_id = self.lineEdit_id.text()
        input_name = self.lineEdit_name.text()

        try:
            self.form_id = MyMainForm.grade_count(self, input_id)
            html = ObtainAndProcess.request_source(self, input_id, input_name)
            ObtainAndProcess.extract(self, html, input_id, input_name)
        except IndexError:
            pass
        except urllib.error.URLError:
            self.textBrowser_main.append(
                "\n 程序：发生 urllib.error.URLError 错误！\n"
                + "     1. 请检查网络连接是否稳定或正常。\n" + "     2. 请检查API 查询接口是否已经失效。\n"
                + "      3. 网络不稳定，可以等一下再试一次。\n" + "      4. 连接丢包中断，建议再点一次查询。"
                )
        except urllib.error.HTTPError:
            self.textBrowser_main.append(
                "\n 程序：发生 503 访问错误！ \n"
                + "      操作频繁，服务器拒绝访问，等一下再尝试查询吧。"
                )

        try:
            OuputGUI.display_info(self)
            OuputGUI.display_main(self)
            OuputGUI.display_vice(self)
            OuputGUI.display_more(self, input_id)
        except IndexError:
            QMessageBox.warning(
                self, '! ERROR', '输入信息可能存在错误，无法获取该同学的成绩'
                + '\n1. 请检查 学号和姓名是否有误. '
                + '\n2. 另外这个程序只能查询17～19级的成绩信息。', QMessageBox.Yes
                )
        except ZeroDivisionError:
            pass

    def grade_count(self, input_id):
        """ 这里计算判断出输入的年级，返回计算出相应的表单查询构建方法 """
        num_list = []
        for x in input_id:
            num_list.append(x)
        grade = str(num_list[0]) + str(num_list[1])
        if grade == '19':
            form_id = ['kS6rp1DbawZmiLyY', '1104371724']
        elif grade == '18':
            form_id = ['gUVzpdDRM7tCxEXu', '1104371724']
        elif grade == '17':
            form_id = ['4T9kM2I07JLEgYS3', '1104371724']
        else:
            form_id = ['kS6rp1DbawZmiLyY', '1104371724']    # 缺省设置为 19级
        return form_id


class AboutForm(QMainWindow, Ui_ABOUT):
    """ “关于”窗口，里面包含一些作者写入的文本信息 """
    def __init__(self, parent=None):
        super(AboutForm, self).__init__(parent)
        self.setupUi(self)


class AdvancedForm(QMainWindow, Ui_Advanced):
    """ “高级功能”窗口，包含两个按钮触发，和调用打开命令行处理 """
    def __init__(self, parent=None):
        super(AdvancedForm, self).__init__(parent)
        self.setupUi(self)
        self.pushButton_run.clicked.connect(self.open_run)
        self.pushButton_sc.clicked.connect(self.open_sortout)

    def open_run(self):
        """ 这里直接弄WINDOWS的了 """
        path = os.getcwd()
        # os.system("python3 " + path + " run.py")
        os.system("start cmd /k python run.py")

    def open_sortout(self):
        os.system("start cmd /k python sort_out.py")


class ObtainAndProcess(object):
    """ 负责抓取网页上的信息并进行界面解析、分离整理与合成 """
    def __init__(self, url, ouput_txt_active,  error_line, count_loop):
        self.API_url = url
        self.ouput_txt_active = ouput_txt_active
        self.error_line = error_line
        self.count_loop = count_loop
        self.form_id = []           # 预留表单提交接口，以下大多数都为缺省无用的。

        self.key_courses = []
        self.value_scores = []
        self.college_get = []
        self.class_get = []
        self.name_get = []
        self.build_dict = {}    # 用于构建课程和分数的键值对字典

    def request_source(self, input_id, input_name):
        # self.count_loop = self.count_loop + 1

        form_data = {
            'data_1': input_id,             # 学号
            'data_2': input_name,                 # 姓名
            'form_id': self.form_id[0],                 # 输入用于构建表单的相关数据
            'media_id': self.form_id[1]               # （见Run类， __init__初始化处）
        }
        data = parse.urlencode(form_data).encode('utf-8')
        req = request.Request(self.API_url, data)
        responce = request.urlopen(req)
        html = responce.read().decode()     # 得到网页
        return html

    def extract(self, html, input_id, input_name):
        """ 界面解析参照: https://beautifulsoup.readthedocs.io/zh_CN/latest/ """

        soup = BeautifulSoup(html, 'html.parser')   # print(soup.prettify())
        result_score = []       # 课程，成绩，班级
        result_info = []          # 学号，姓名，学院

        # （分析）抓取到的数据顺序为： 学号，姓名，课程，成绩，学院，班级
        for link in soup.find_all("span"):
            text = "".join(link.string.split())   # 强制去除字符串中的空白符

            # 这里过滤出 课程，成绩，学院，班级         | 学号，姓名
            if (text != input_id and text != input_name):
                result_score.append("".join(link.string.split()))
            else:
                result_info.append("".join(link.string.split()))

        """ 表单数据样本，用于分析如何进行解析提取 """
        # ['计算机数学', '87', '机电与信息工程学院', '19计算机网络技术1',
        # '思想道德修养与法律基础', '96', '机电与信息工程学院', '19计算机网络技术1',
        # '大学生军事课及入学教育', '90', '机电与信息工程学院', '19计算机网络技术1',
    

        for sep in range(len(result_score)):
            if sep % 4 == 0:
                self.key_courses.append(result_score[sep])
            elif (sep-1) % 4 == 0:
                self.value_scores.append(result_score[sep])
            elif (sep-2) % 4 == 0:
                self.college_get.append(result_score[sep])
            elif (sep-3) % 4 == 0:
                self.class_get.append(result_score[sep])
            else:
                print(" Error detaching list content! ")

        # 获得 从网页中抓取的姓名
        for sep in range(len(result_info)):
            if (sep+1) % 2 == 0:
                self.name_get.append(result_info[sep])

        # 构建字典
        for x in range(len(self.value_scores)):
            self.build_dict[self.key_courses[x]] = self.value_scores[x]


class OuputGUI(object):
    """ 这里是输出类，大多数的窗体 Text 信息都将经过这个类处理输出  """
    def __init__(self, default):
        self.class_get = []
        self.name_get = []
        # 程序预留接口，默认值为default，目前是没有用处的
        self.textBrowser_more = default
        self.textBrowser_main = default
        self.textBrowser_vice = default
        self.textBrowser_name = default
        self.textBrowser_class = default
        self.API_url = default

    # 字符串拆分参考： https://blog.csdn.net/qq_29750277/article/details/82023347
    def display_main(self):
        """ 显示主文本输出框的内容 """
        self.textBrowser_main.append("    " + "分数" + "\t\t" + "课程科目" + "\n")
        for course, score in self.build_dict.items():
            self.textBrowser_main.append(
                "      " + str(score) + "\t\t" + str(course))

    # 总分， 平均分 ， 优秀率(>85分)， 合格率(>60)
    def display_vice(self):
        """ 显示副文本输出框的内容 """
        count_get = OuputGUI.dispaly_vice_of_count(self)
        text_info = OuputGUI.dispaly_vice_of_text(self, count_get)
        text = "总分： " + str(count_get[0]) + "    \t平均分： " + str('%.2f' % count_get[1]) + "\t"
        text += "优秀率(>85)： " + str('%.2f' % count_get[2]) + " %    \t不及格率：" + str('%.2f' % count_get[3]) + " %"
        self.textBrowser_vice.append(text)
        self.textBrowser_vice.append("\n程序评语： " + text_info)

    def dispaly_vice_of_text(self, count_get):
        """ 根据平均分分值返回相应信息 """
        if count_get[1] <= 30:
            text_info = "这个成绩.... 读书不如去打工."
        elif count_get[1] <= 40:
            text_info = "未来的路还很长远...  感觉这个成绩不行诶.."
        elif count_get[1] <= 50:
            text_info = "读书，就像一场永无休止的苦役，希望不要放弃自己，而是要相信自己"
        elif count_get[1] <= 60:
            text_info = "成绩感觉总体比较差，希望不要放弃学习，加油吧"
        elif count_get[1] <= 70:
            text_info = "平均分没过70，希望能够继续努力学习，认真上课，加油！"
        elif count_get[1] <= 80:
            text_info = "成绩一般般，希望能继续努力学习，不断提高自己，加油！"
        elif count_get[1] <= 85:
            text_info = "成绩总体来说挺不错的，希望能继续保持，努力加油超越自己。"
        elif count_get[1] <= 90:
            text_info = "成绩总体来说很优秀喔，莫非... 就是传说中的学霸！？ 希望继续保持好成绩。"
        elif count_get[1] <= 100:
            text_info = "無情的學習機器？！ 成绩总体来说非常优异，平均分可以达到奖学金标准了（>85分）"
        else:
            text_info = "Program Error! (Line --->> def dispaly_vice_of_text)"
        return text_info

    def dispaly_vice_of_count(self):
        """ 这里是计算出副文本输出框所需的数值数据，并以列表形式返回 """
        scores_list = []
        excellent = 0
        unqualified = 0
        for score in self.build_dict.values():
            try:
                score = int(score)
            except ValueError:
                continue
            scores_list.append(score)
            if score >= 85:
                excellent = excellent + 1
            elif score <= 60:
                unqualified = unqualified + 1

        sum_score = 0           # 求总分
        for num in scores_list:
            num = int(num)
            sum_score = sum_score + num

        age_score = sum_score / len(scores_list)    # 求平均分
        rate_excellent = (excellent / len(scores_list)) * 100   # 优秀率
        rate_unqualified = (unqualified / len(scores_list)) * 100   # 不及格率

        count_info = [sum_score, age_score, rate_excellent, rate_unqualified]
        return count_info

    # 年级  学院 | 班级 姓名 | 学号
    def display_more(self, input_id):
        """ 这里是第二个主要的文本输出框，位于Tab2 """
        grade = OuputGUI.dispaly_more_of_count(self, input_id)

        self.textBrowser_more.append("   年级： " + grade + "\t\t学院：" + self.college_get[0])
        self.textBrowser_more.append("   班级： " + self.class_get[0] + "\t\t姓名：" + self.name_get[0])
        self.textBrowser_more.append("   学号： " + input_id + "\n")
        self.textBrowser_more.append("   查询时间：" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        self.textBrowser_more.append("   本机公网IP地址： " + str(request.urlopen('http://ip.42.pl/short').read()))
        self.textBrowser_more.append("   当前API查询接口：" + self.API_url)
        # 本来想弄个最高分与，最低分，还有折线图的，后来懒得弄了

    def dispaly_more_of_count(self, input_id):
        """ 根据学号求出年级 """
        num_list = []
        for x in input_id:
            num_list.append(x)
        grade = "20" + str(num_list[0]) + str(num_list[1]) + " 级"
        return grade

    def initialization_display(self):
        """ 查询按钮点击时进行界面初始化，清空所有的界面文本和列表信息
               但是有个奇怪的 bug 就是 查完19级再查18级的 文本输出窗口的信息会乱掉，很奇怪"""
        self.class_get = []
        self.name_get = []
        self.college_get = []
        self.build_dict = {}
        self.textBrowser_vice.clear()
        self.textBrowser_main.clear()
        self.textBrowser_more.clear()
        self.textBrowser_name.clear()
        self.textBrowser_class.clear()

    def initialization_display_simply(self):
        self.textBrowser_main.clear()

    def display_info(self):
        """ 显示横批下面的那个班级姓名信息 """
        self.textBrowser_class.setText(self.class_get[0])
        self.textBrowser_name.setText(self.name_get[0])


class FilesWrite(object):
    """ 这里负责文件的写入，目前主要用于高级功能中的.py文件解压 """
    def __init__(self):
        pass

    def get_pyfile(self, py_code, py_name):
        """ BASE64 解码 解压 get Python .py files """
        py = open(py_name, 'wb')
        py.write(base64.b64decode(py_code))
        py.close()
        print(" writer running.... ")

    def open_pyfile(self):
        FilesWrite.get_pyfile(self, memory_pyfile.run, 'run.py')
        FilesWrite.get_pyfile(self, memory_pyfile.sort_out, 'sort_out.py')


FW = FilesWrite()
FW.open_pyfile()    # 解压高级功能中要用到的 .py文件

if __name__ == "__main__":
    # 固定的，PyQt5程序都需要QApplication对象。sys.argv是命令行参数列表，确保程序可以双击运行
    app = QApplication(sys.argv)
    myWin = MyMainForm()    # 初始化
    myWin.show()        # 将窗口控件显示在屏幕上
    sys.exit(app.exec_())  # 程序运行，sys.exit方法确保程序完整退出。
