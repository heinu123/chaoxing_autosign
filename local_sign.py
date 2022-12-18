# -*- coding: utf8 -*-
import os
import re
import time
import json
import random
import asyncio
from typing import Optional, List, Dict

from aiohttp import ClientSession
from aiohttp.cookiejar import SimpleCookie
from lxml import etree
from bs4 import BeautifulSoup

from config import *
from log import logger
from message import server_chan_send


class AutoSign(object):
    
    def __init__(self, username, password, schoolid=None, enc=None):
        """初始化就进行登录"""
        self.headers = {
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 11; M2007J3SC Build/RKQ1.200826.002) (device:M2007J3SC) Language/zh_CN com.chaoxing.mobile/ChaoXingStudy_3_5.1.3_android_phone_613_74',
        }
        self.session = ClientSession(headers=self.headers)
        self.username = username
        self.password = password
        self.schoolid = '' if schoolid is None else schoolid
        self.enc = '' if enc is None else enc
    
    async def check_login_status(self, status, text):
        """
        检查登录状态
        """
        if status == 403:
            return 1002
        data = json.loads(text)
        if data['result']:
            return 1000  # 登录成功
        else:
            return 1001  # 登录信息有误
    
    async def set_cookies(self):
        """设置cookies"""
        cookie = await self.check_cookies()
        if not cookie:
            # 无效则重新登录，并保存cookies
            status, text, cookie = await self.login()
            login_status = await self.check_login_status(status, text)
            
            if login_status == 1000:
                cookies = self.dict_from_simple_cookie(cookie)
                self.save_cookies(cookies)
            else:
                return 1001
        else:
            self.session.cookie_jar.update_cookies(cookie)
        return 1000
    
    def dict_from_simple_cookie(self, cookies) -> dict:
        """
        从响应对象中抽取cookies
        """
        result = {}
        for key, value in cookies.items():
            result[key] = value.value
        return result
    
    def save_cookies(self, cookies: dict):
        """保存cookies"""
        with open(COOKIES_FILE_PATH, "r") as f:
            data = json.load(f)
            data[self.username] = cookies
            with open(COOKIES_FILE_PATH, 'w') as f2:
                json.dump(data, f2)
    
    async def check_cookies(self) -> Optional[SimpleCookie]:
        """检测json文件内是否存有cookies,有则检测，无则登录"""
        if "cookies.json" not in os.listdir(COOKIES_PATH):
            with open(COOKIES_FILE_PATH, 'w+') as f:
                f.write("{}")
        
        with open(COOKIES_FILE_PATH, 'r') as f:
            # json文件有无账号cookies, 没有，则直接返回假
            try:
                data = json.load(f)
                cookies = data[self.username]
            except Exception as exc:
                logger.error(exc)
                return
        
        # 检测cookies是否有效
        async with self.session.request(
            method='GET',
            url='http://mooc1-1.chaoxing.com/api/workTestPendingNew',
            allow_redirects=False,
            cookies=cookies
        ) as resp:
            if resp.status != 200:
                print("cookie失效")
                return
            else:
                print("cookie有效!")
                return cookies
    
    async def login(self):
        """
        登录并返回响应
        """
        params = {
            'name': self.username,
            'pwd': self.password,
            'schoolid': self.schoolid,
            'verify': 0
        }
        async with self.session.request(
            method='GET',
            url='https://passport2.chaoxing.com/api/login',
            params=params
        ) as resp:
            status = resp.status
            text = await resp.text()
            cookies = resp.cookies
            return status, text, cookies
    
    def check_activeid(self, activeid):
        """检测activeid是否存在，不存在则添加"""
        activeid += self.username
        if "activeid.json" not in os.listdir(ACTIVEID_PATH):
            with open(ACTIVEID_FILE_PATH, 'w+') as f:
                f.write("{}")
        
        with open(ACTIVEID_FILE_PATH, 'r') as f:
            try:
                # 读取文件
                data = json.load(f)
                if data[activeid]:
                    return True
            except BaseException:
                # 如果出错，则表示没有此activeid
                return False
    
    def save_activeid(self, activeid):
        """保存已成功签到的activeid"""
        activeid += self.username
        if "activeid.json" not in os.listdir(ACTIVEID_PATH):
            with open(ACTIVEID_FILE_PATH, 'w+') as f:
                f.write("{}")
        with open(ACTIVEID_FILE_PATH, 'r') as f:
            data = json.load(f)
            with open(ACTIVEID_FILE_PATH, 'w') as f2:
                data[activeid] = True
                json.dump(data, f2)
    
    async def get_all_classid(self) -> List[Dict]:
        """
        获取课程主页中所有课程的classid和courseid
        """
        results = []
        extend_headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Referer': 'http://mooc1-2.chaoxing.com/visit/interaction',
            'Host': 'mooc1-2.chaoxing.com',
            'Origin': 'http://mooc1-2.chaoxing.com'
        }
        self.session.headers.update(extend_headers)
        async with self.session.request(
            method='POST',
            url='https://mooc1-2.chaoxing.com/visit/courselistdata',
            data="courseType=1&courseFolderId=0&courseFolderSize=0",
        ) as resp:
            text = await resp.text()
        
        for key in extend_headers:
            self.session.headers.pop(key)
        
        soup = BeautifulSoup(text, "lxml")
        course_li_nodes = soup.find_all('li', class_="course clearfix")
        print("所有有效课程：")
        for course_li in course_li_nodes:
            class_id = course_li.get('clazzid')
            if class_id == '0':
                continue
            course_id = course_li.get('courseid')
            class_name = course_li.find_next('span', class_="course-name").text
            # 如果有这个标签则说明，此课程已结束，不加入签到
            course_li.find('a', class_='not-open-tip')
            course = {
                'course_id': course_id,
                'class_id': class_id,
                'class_name': class_name
            }
            print(course)
            results.append(course)
        return results
    
    async def get_sign_type(self, class_id, course_id, active_id):
        """获取签到类型"""
        params = {
            'activeId': active_id,
            'classId': class_id,
            'courseId': course_id
        }
        async with self.session.request(
            method='GET',
            url='https://mobilelearn.chaoxing.com/widget/sign/pcStuSignController/preSign',
            params=params
        ) as resp:
            text = await resp.text()
        h = etree.HTML(text)
        sign_type = h.xpath('//div[@class="location"]/span/text()')
        return sign_type
    
    async def get_active_id(self, course: Dict):
        """访问任务面板获取课程的活动id"""
        res = []
        re_rule = r'([\d]+),2'
        params = {
            'courseId': course['course_id'],
            'jclassId': course['class_id']
        }
        # TODO： 此处使用的是老版本，后续计划将替换为新版本接口
        async with self.session.request(
            method='GET',
            url="https://mobilelearn.chaoxing.com/widget/pcpick/stu/index",
            verify_ssl=False,
            params=params,
        ) as resp:
            text = await resp.text()
        h = etree.HTML(text)
        activeid_list = h.xpath('//*[@id="startList"]/div/div/@onclick')
        
        for activeid in activeid_list:
            activeid = re.findall(re_rule, activeid)
            if not activeid:
                continue
            sign_type = await self.get_sign_type(course['course_id'], course['class_id'], activeid[0])
            res.append((activeid[0], sign_type[0]))
        n = len(res)
        if n:
            d = {'num': n, 'class': {}}
            for i in range(n):
                if not self.check_activeid(res[i][0]):
                    d['class'][i] = {
                        'classid': course['class_id'],
                        'courseid': course['course_id'],
                        'activeid': res[i][0],
                        'classname': course['class_name'],
                        'sign_type': res[i][1]
                    }
            return d
    
    async def general_sign(self, classid, courseid, activeid):
        """普通签到"""
        params = {
            'activeId': activeid,
            'classId': classid,
            'fid': '39037',
            'courseId': courseid
        }
        async with self.session.request(
            method='GET',
            url="https://mobilelearn.chaoxing.com/widget/sign/pcStuSignController/preSign",
            params=params,
            verify_ssl=False
        ) as resp:
            text = await resp.text()
        
        title = re.findall('<title>(.*)</title>', text)[0]
        if "签到成功" not in title:
            # 网页标题不含签到成功，则为拍照签到
            return self.tphoto_sign(activeid)
        else:
            s = {
                'date': time.strftime("%m-%d %H:%M", time.localtime()),
                'status': title
            }
            return s
    
    async def hand_sign(self, classid, courseid, activeid):
        """手势签到"""
        params = {
            'courseId': courseid,
            'classId': classid,
            'activeId': activeid
        }
        async with self.session.request(
            method='GET',
            url="https://mobilelearn.chaoxing.com/widget/sign/pcStuSignController/signIn",
            params=params,
            verify_ssl=False
        ) as resp:
            text = await resp.text()
        
        title = re.findall('<title>(.*)</title>', text)
        s = {
            'date': time.strftime("%m-%d %H:%M", time.localtime()),
            'status': title
        }
        return s
    

        """二维码签到"""
        params = {
            'enc': self.enc,
            'name': '',
            'activeId': activeid,
            'uid': '',
            'clientip': '',
            'useragent': '',
            'latitude': '-1',
            'longitude': '-1',
            'fid': '',
            'appType': '15'
        }
        
        async with self.session.request(
            'GET',
            url='https://mobilelearn.chaoxing.com/pptSign/stuSignajax',
            params=params,
            allow_redirects=False
        ) as resp:
            text = await resp.text()
            return {
                'date': time.strftime("%m-%d %H:%M", time.localtime()),
                'status': text
            }
    
    async def addr_sign(self, activeid):
        """位置签到"""
        params = {
            'name': '',
            'activeId': activeid,
            'address': '中国',
            'uid': '',
            'clientip': clientip,
            'latitude': str(latitude),
            'longitude': str(longitude),
            'fid': '',
            'appType': '15',
            'ifTiJiao': '1'
        }
        async with self.session.request(
            method="GET",
            url="https://mobilelearn.chaoxing.com/pptSign/stuSignajax",
            params=params
        ) as resp:
            text = await resp.text()
        
        if "不在可签到范围内" in text:
            text = "位置签到失败"
        
        return {
            'date': time.strftime("%m-%d %H:%M", time.localtime()),
            'status': text
        }
    
    async def tphoto_sign(self, activeid):
        """拍照签到"""
        objectId = await self.upload_img()
        params = {
            'name': '',
            'activeId': activeid,
            'address': '中国',
            'uid': '',
            'clientip': clientip,
            'latitude': latitude,
            'longitude': longitude,
            'fid': '',
            'appType': '15',
            'ifTiJiao': '1',
            'objectId': objectId
        }
        async with self.session.request(
            method="GET",
            url="https://mobilelearn.chaoxing.com/pptSign/stuSignajax",
            params=params
        ) as resp:
            text = await resp.text()
        
        return {
            'date': time.strftime("%m-%d %H:%M", time.localtime()),
            'status': text
        }
    
    async def get_token(self):
        """获取上传文件所需参数token"""
        url = 'https://pan-yz.chaoxing.com/api/token/uservalid'
        async with self.session.request(
            method='GET',
            url=url
        ) as resp:
            text = await resp.text()
        token_dict = json.loads(text)
        return token_dict['_token']
    
    async def upload_img(self):
        """上传图片"""
        # 从图片文件夹内随机选择一张图片
        try:
            all_img = os.listdir(IMAGE_PATH)
        except Exception as e:
            os.mkdir(IMAGE_PATH)
            all_img = 0
        
        if len(all_img) == 0:
            return "a5d588f7bce1994323c348982332e470"
        else:
            img = IMAGE_PATH + random.choice(all_img)
            # uid = self.session.cookies.get_dict()['UID']
            url = 'https://pan-yz.chaoxing.com/upload'
            files = {'file': open(img, 'rb')}
            uid = self.session.cookie_jar.filter_cookies('').get('UID').value
            token = await self.get_token()
            param = {
                'puid': uid,
                '_token': token
            }
            async with self.session.request(
                method='POST',
                url=url,
                params=param,
                data=files
            ) as resp:
                text = await resp.text()
            res_dict = json.loads(text)
            return res_dict['objectId']
    
    async def send_sign_request(self, classid, courseid, activeid, sign_type):
        """发送签到请求"""
        if "手势" in sign_type:
            return await self.hand_sign(classid, courseid, activeid)
        elif "二维码" in sign_type:
            return await self.qcode_sign(activeid)
        elif "位置" in sign_type:
            return await self.addr_sign(activeid)
        elif "拍照" in sign_type:
            return await self.tphoto_sign(activeid)
        else:
            return await self.general_sign(classid, courseid, activeid)
    
    async def start_sign_task(self):
        """开始所有签到任务"""
        tasks = []
        res = []
        await self.set_cookies()
        # 获取所有课程的classid和course_id
        course_list = await self.get_all_classid()
        
        # 获取所有课程activeid和签到类型
        for course in course_list:
            coroutine = self.get_active_id(course)
            tasks.append(coroutine)
        results: List[Dict] = await asyncio.gather(*tasks)
        
        for r in results:
            if r is None:
                continue
            
            for d in r['class'].values():
                resp = await self.send_sign_request(
                    d['classid'],
                    d['courseid'],
                    d['activeid'],
                    d['sign_type']
                )
                if resp:
                    # 签到课程， 签到时间， 签到状态
                    sign_msg = {
                        'name': d['classname'],
                        'date': resp['date'],
                        'status': resp['status']
                    }
                    res.append(sign_msg)
                    
                    if '失败' in resp['status']:
                        continue
                    # 签到成功后，新增activeid
                    self.save_activeid(d['activeid'])
        
        return res
    
    async def close_session(self):
        await self.session.close()
