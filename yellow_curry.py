import requests
import subprocess
import logging
import os
from datetime import datetime
import json
import urllib3
urllib3.disable_warnings()

TOKEN = "xoxb-309750004087-2405092575238-VoPgu3gS5Crb6HHj29H3VVID"
LIB_VER = '1.0.0' # 삐약이 데몬버전
LIB_DATE = '2022-01-12' # 삐약이 업데이트 일자
LIB_NAME = 'yellow_curry'
    
CUR_D = os.path.dirname(__file__)
JOIN = os.path.join

class yellow_curry:
    def __init__(self, channel, demon_name, demon_ver, demon_date, write_log=True, show_demon_info=True, show_lib_info=False):
        self.token = TOKEN
        self.channel = channel
        self.lib_name = LIB_NAME
        self.lib_ver = LIB_VER
        self.lib_date = LIB_DATE
        self.demon_name = demon_name
        self.demon_ver = demon_ver
        self.demon_date = demon_date
        if write_log:
            self.logger = logging.getLogger(self.lib_name)
            self.logInit()
        self.show_lib_info = show_lib_info
        self.show_demon_info = show_demon_info
        
    def logInit(self):
        formatter = logging.Formatter('%(filename)s:] %(asctime)s > %(message)s')
        self.logger.setLevel(logging.INFO)
        logFilePath = JOIN(CUR_D, self.lib_name + '.log')
        fileHandler = logging.FileHandler(logFilePath)
        fileHandler.setFormatter(formatter)
        self.logger.addHandler(fileHandler)
    def writeLogFile(self, msg):
        self.logger.info(msg)
    def get_serverinfo(self):
        hostname = subprocess.check_output('hostname', shell=True, universal_newlines=True).strip()
        ip = subprocess.check_output('hostname -I', shell=True, universal_newlines=True).split()[0]
        return hostname, ip
    
    def send(self, text):
    
        hostname, ip = self.get_serverinfo()
        t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if self.show_lib_info:
            text = 'Library {} build v{} ({}) from ({}, {}) [{}]\n{}'.format(self.lib_name, self.lib_ver, self.lib_date, ip, hostname, t, text)
        
        if self.show_demon_info:
            text = '{}\n[{} ({}, {}), v{}, BuildDate:{}, AlertTime:{}]'.format(text, self.demon_name, ip, hostname, self.demon_ver, self.demon_date, t)
        
        try:
            self.writeLogFile(text)
            response = requests.post("https://slack.com/api/chat.postMessage",
                headers={"Authorization": "Bearer "+ self.token},
                data={
                    "channel": self.channel,
                    "text": text
                    # "attachments": [{
                    #     "image_url": "https://newsimg.hankookilbo.com/cms/articlerelease/2019/04/29/201904291390027161_3.jpg",
                    #                 "text": "text-world",
                    #                 "pretext": "pre-hello"
                    #             }]
                },
                verify=False
            )
            if response.status_code == 200:
                result = json.loads(response.text)
                if 'error' in result:
                    error_message = 'Failed to send! {}'.format(result['error'])
                    self.writeLogFile(error_message)
            else:
                error_message = 'error_code={}, Failed to send! {}'.format(response.status_code, response.text)
                self.writeLogFile(error_message)
        except ConnectionError:
            command = "reboot"
            error_message = 'ConnectionError!'
            self.writeLogFile(error_message)
            # subprocess.run(command, shell=True)
        except Exception as ex:
            msg = error_message = 'Unexpected Error {}!'.format(ex)
            self.writeLogFile(msg)
        