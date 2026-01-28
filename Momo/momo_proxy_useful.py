#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random
import tkinter
from tkinter import *
import hashlib
import time
from tkinter.ttk import Progressbar

import requests
import threading
LOG_LINE_NUM = 0


class MyThread(threading.Thread):
    def __init__(self, func, *args):
        super().__init__()

        self.func = func
        self.args = args

        self.setDaemon(True)
        self.start()  # 在这里开始

    def run(self):
        # print('self.func', self.func)
        self.func(*self.args)

class MY_GUI():
    def __init__(self,init_window_name):
        self.init_window_name = init_window_name


    #设置窗口
    def set_init_window(self):
        self.init_window_name.title("单词脚本_v1")           #窗口名
        #self.init_window_name.geometry('320x160+10+10')                         #290 160为窗口大小，+10 +10 定义窗口弹出时的默认展示位置
        self.init_window_name.geometry('500x240+10+10')
        # self.init_window_name["bg"] = "white"                                    #窗口背景色，其他背景色见：blog.csdn.net/chl0000/article/details/7657887
        #self.init_window_name.attributes("-alpha",0.9)                          #虚化，值越小虚化程度越高
        #标签
        self.init_data_label = Label(self.init_window_name, text="↓请在下方输入分享链接↓", width=70, anchor='center')
        self.init_data_label.grid(row=0, column=0)
        #文本框
        self.init_data_Text = Text(self.init_window_name, width=70, height=3)  #原始数据录入框
        self.init_data_Text.grid(row=1, column=0, rowspan=10, columnspan=10)
        #按钮
        self.str_trans_to_md5_button = Button(self.init_window_name, text="点击开始运行", bg="lightblue", width=10,
                                              command=lambda: MyThread(self.str_trans_to_md5))  # 调用内部方法  加()为直接调用
        self.str_trans_to_md5_button.grid(row=20, column=0)
        #进度条
        self.progressbarOne = Progressbar(self.init_window_name, length=400)
        self.progressbarOne.grid(row=29, column=0)
        self.progressbarOne['maximum'] = 35
        self.progressbarOne['value'] = 0
        # 进度标签
        # self.progress_label = Label(self.init_window_name, anchor='center', width=5)
        # self.progress_label.grid(row=29, column=0)
        #日志
        self.log_data_Text = Text(self.init_window_name, width=70, height=9)  # 日志框
        self.log_data_Text.grid(row=31, column=0, columnspan=10)
        self.log_data_Text.insert(END, '输出日志'+"\n")
    #功能函数
    def str_trans_to_md5(self):
        share_url = self.init_data_Text.get(0.0, END).strip().replace("\n", "")
        # print("src =", share_url, '\n', share_url[0:23])
        momo_url = 'https://www.maimemo.com'
        suc_num = 0
        if share_url[0:23] == momo_url:
            self.progressbarOne['value'] = 0
            self.write_log_to_Text("正在运行")
            try:
                for i in range(35):
                    if i != 0:
                        time.sleep(random.randint(60, 120))
                    #换成自己的代理
                    proxies = self.jl_api('https://www.maimemo.com/share/page?uid=35103585&pid=2cfaa018e3403c2daadb212e3a941b49&tid=644081403e4b66455cede638db606ecf')
                    suc_num = self.run(share_url, suc_num, proxies)

                    self.progressbarOne['value'] += 1
                    self.init_window_name.update()
                    self.write_log_to_Text("正在运行,已成功{}次".format(suc_num))
                    if i == 34:
                        self.write_log_to_Text("任务完成，成功{}次".format(suc_num))
                #输出到界面
                # self.result_data_Text.delete(1.0,END)
                # self.result_data_Text.insert(1.0,myMd5_Digest)
                # self.write_log_to_Text("INFO:str_trans_to_md5 success")
            except:
                self.write_log_to_Text("无效")
        else:
            self.write_log_to_Text("无效的分享链接")

    #获取当前时间
    def get_current_time(self):
        current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        return current_time
    def write_log_to_Text(self,logmsg):
        global LOG_LINE_NUM
        current_time = self.get_current_time()
        logmsg_in = str(current_time) +" " + str(logmsg) + "\n"      #换行
        if LOG_LINE_NUM <= 7:
            self.log_data_Text.insert(END, logmsg_in)
            LOG_LINE_NUM = LOG_LINE_NUM + 1
        else:
            self.log_data_Text.delete(1.0,2.0)
            self.log_data_Text.insert(END, logmsg_in)

    # def jl_api(self, api_url):
    #     # 获取API接口返回的代理IP
    #     proxy_ip = requests.get(api_url).text
    #     print(proxy_ip)
    #     # 用户名密码认证(动态代理/独享代理)
    #     username = ""
    #     password = ""
    #     proxies = {
    #         "http": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": proxy_ip},
    #         "https": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": proxy_ip},
    #     }
    #     # print(proxies)
    #     return proxies
    def jl_api(self, api_url):
        # 获取API接口返回的代理IP
        proxy_ip = requests.get(api_url).text
        # 代理服务器
        proxyHost = proxy_ip.split(":")[0]
        proxyPort = proxy_ip.split(":")[1]

        print(proxy_ip)
        # 用户名密码认证(动态代理/独享代理)
        proxyMeta = "http://%(host)s:%(port)s" % {
            "host": proxyHost,
            "port": proxyPort,
        }
        proxies = {
            "http": proxyMeta,
        }
        # print(proxies)
        return proxies

    def run(self, url_ls, suc_num, proxies):

        headers = {
            'authority': 'www.maimemo.com',
            'Proxy-Authorization': 'Basic ZDI0MjkxNjczNzU6bGM1ZjJ4cDQ=',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        }
        num = 1
        requests.DEFAULT_RETRIES = 10
        try:
            response = requests.get(url=url_ls, headers=headers, proxies=proxies)
        except Exception as e:
            print("http exception:", e)
            suc_num += 0
            return suc_num
        else:
            content = response.text
            if (str(content).find("学习天数")) != -1:
                suc_num += 1
                return suc_num
def gui_start():
    init_window = Tk()              #实例化出一个父窗口
    ZMJ_PORTAL = MY_GUI(init_window)
    # 设置根窗口默认属性
    ZMJ_PORTAL.set_init_window()

    init_window.mainloop()          #父窗口进入事件循环，可以理解为保持窗口运行，否则界面不展示


gui_start()
