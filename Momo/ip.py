# encoding:utf-8
import re
import chardet
from random import choice
import asyncio
import requests
from pyppeteer import launch
from aiohttp import ClientSession, ClientTimeout, TCPConnector
# import encodings.idna

listIP = []  # 保存IP地址
cnt_findNewIp = 0 # 每次新增50个有效ip
path = '/var/www/tools/momo-share/momo-share-proxy/Momo/ip.txt'  # 文件保存地址


# 随机返回请求头
async def getheaders():
    headers_list = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
        "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36", ]
    headers = {'User-Agent': choice(headers_list)}
    return headers


# 清空文档
def clear_file():
    with open(path, 'r') as f_in:
        lines = f_in.readlines()
        listIP = lines[:100]
        f_in.close()
        if len(lines)>200:
            print('ip数量大于200，开始清除')
            with open(path, 'w', encoding='utf-8') as f:
                f.truncate()
                f.writelines(listIP)


# 写入文档
async def record(text):
    global listIP
    with open(path, 'a', encoding='utf-8') as f:
        if text not in listIP:
            f.write(f'{text}\n')

async def getHtmlWithRunJs(url):
    print('启动浏览器')
    browser = await launch(executablePath='/opt/google/chrome/google-chrome',headless=True,args=['--no-sandbox'])
    # 打开一个新页面
    page = await browser.newPage()
    # 开启js
    await page.setJavaScriptEnabled(enabled=True)
    # 设置请求头
    await page.setUserAgent(
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299'
    )
    # 开启 隐藏 是selenium 让网站检测不到
    await page.evaluate('''() =>{ Object.defineProperties(navigator,{ webdriver:{ get: () => false } }) }''')
    await page.setViewport(viewport={"width": 1920, "height": 1080})
    # 访问指定URL
    await page.goto(url)
    # 等待页面加载完毕，示例中等待了2秒
    await asyncio.sleep(2)
    # 获取页面内容
    content = await page.content()
    # 关闭浏览器
    await browser.close()
    return content


async def check_proxy(proxy,session):
    hd = await getheaders()  # 设置请求头
    sem = asyncio.Semaphore(50)  # 设置限制并发次数.
    tout = ClientTimeout(total=5)  # 设置请求超时
    global cnt_findNewIp
    async with sem:
        try:
            async with await session.get(url='https://www.baidu.com', headers=hd, proxy=proxy, timeout=tout) as response:
                # 如果状态码为200，则代理可用
                if response.status_code == 200:
                    print(f"代理 {proxy} 可用")
                    await record(proxy)
                    cnt_findNewIp += 1
                    if cnt_findNewIp>50:
                        print('本次新增有效ip',cnt_findNewIp)
                        exit(0)
                else:
                    print(f"代理 {proxy} 返回状态码 {response.status_code}")
        except Exception as e:
            print(f"代理 {proxy} 请求失败")

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            # 'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            # 'Cookie': 'BAIDUID=99C9E0BB02F9B2785867606169DC3B5E:FG=1; BIDUPSID=10718E3AD78C242F341870B1F3600FA0; PSTM=1697958277; BDUSS=NmYm11aWpCOS04UjF3LXdXMmh2OTBhYS1xclhkMm1BUEIwOUxIV0R5alN4V1ZsSVFBQUFBJCQAAAAAAAAAAAEAAAD1h7lexOa54tbQtcTOonhpYW8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAANI4PmXSOD5lZH; H_PS_PSSID=40206_40217_40223_40283_40295_40287_40284_40318_40080_40364_40352_40302_40366_40377_40410_40416_40011; MCITY=-%3A; COOKIE_SESSION=0_0_0_0_0_0_0_0_0_0_0_0_0_1706876179%7C1%230_0_0_0_0_0_0_0_1706876179%7C1; H_WISE_SIDS=110085_281879_282466_292505_290994_293754_292166_294108_287701_287174_292123_292246_294359_294755_294743_294749_269892_295129_295083_289026_295396_295412_295772_291191; MSA_WH=1586_804; BAIDU_WISE_UID=wapp_1707828950783_758; newlogin=1',
            'Upgrade-Insecure-Requests': '1',
        }
        # 使用代理发起请求，timeout参数设置超时时间
        response = requests.get("http://www.baidu.com/", headers=headers, proxies={"http": proxy, "https": proxy}, timeout=1)
        # 如果状态码为200，则代理可用
        if response.status_code == 200:
            print(f"代理 {proxy} 可用")
            await record(proxy)
            return True
        else:
            print(f"代理 {proxy} 返回状态码 {response.status_code}")
            return False
    except Exception as e:
        print(f"代理 {proxy} 请求失败")
        return False


async def check_proxtList(proxy_list):
    async with ClientSession(connector=TCPConnector(ssl=False)) as session:
        # 生成任务列表
        task = [asyncio.create_task(check_proxy(proxy=proxy, session=session))
                for proxy in proxy_list]
        await asyncio.wait(task)


# 实例化请求对象
async def create_aiohttp():
    # 实例化对象
    async with ClientSession() as session:
        task = [
        #    asyncio.create_task(get_page('http://www.kxdaili.com/dailiip/2/1.html',mod=2, session=session)),
            asyncio.create_task(get_page('https://www.zdaye.com/free/?ip=&adr=&checktime=3&sleep=2',mod=2, session=session)),
        #    asyncio.create_task(get_page('https://www.kuaidaili.com/free', mod=2, session=session,isUseJs = 1)),
        #    asyncio.create_task(get_page('https://www.kuaidaili.com/free/fps/', mod=2, session=session,isUseJs = 1)),
        #    asyncio.create_task(get_page('http://www.66ip.cn/mo.php?sxb=&tqsl=50',mod=0, session=session)),
        #    asyncio.create_task(get_page('https://www.89ip.cn',mod=1, session=session)),
        #    asyncio.create_task(get_page('https://cdn.jsdelivr.net/gh/parserpp/ip_ports@master/proxyinfo.txt',mod=0, session=session)),
        #    asyncio.create_task(get_page('https://fastly.jsdelivr.net/gh/parserpp/ip_ports@main/proxyinfo.txt',mod=0, session=session)),
        #    asyncio.create_task(get_page('https://www.proxy-list.download/api/v1/get?type=http', mod=3, session=session)),
        ]

        #for i in range(1, 4):
            #task.append(asyncio.create_task(get_page(f'https://proxy.ip3366.net/free/?action=china&page={i}',mod = 2, session=session)))
            #task.append(asyncio.create_task(get_page(f'http://www.kxdaili.com/dailiip/1/{i}.html',mod=2, session=session)))
            #task.append(asyncio.create_task(get_page(f'http://ip.tyhttp.com/{i}/',mod=2, session=session)))
        await asyncio.gather(*task)


# 访问网页
async def get_page(url, session, mod=0 ,isUseJs = 0):
    hd = await getheaders()  # 请求头
    tout = ClientTimeout(total=30)  # 超时时间
    try:
        if isUseJs:
            page_source = await getHtmlWithRunJs(url)
            ip_lists = await soup_page(page_source, mod=mod)
            await check_proxtList(ip_lists)
            print(f"['{url}']抓取成功{len(ip_lists)}个")
            return
        async with await session.get(url=url, headers=hd, timeout=tout) as response:
            data = await response.read()  # 返回字符串形式的相应数据
            encoding = chardet.detect(data)['encoding']
            print(f'page detected  possible encoding:{encoding}')
            encodings = [encoding ,'utf-8', 'gbk', 'GB2312', 'windows-1252']  # 常见编码列表
            for encoding in encodings:
                try:
                    page_source = data.decode(encoding)
                    print(page_source)
                    ip_lists = await soup_page(page_source, mod=mod)
                    await check_proxtList(ip_lists)
                    print(f"['{url}']成功解码：{encoding}")
                    print(f"['{url}']抓取成功{len(ip_lists)}个")
                    break
                except UnicodeDecodeError:
                    print(f"['{url}']解码失败：{encoding}")
                    continue
    except Exception as e:
        print(f"['{url}']抓取失败:", e)


# 清洗页面 提取IP
# 生成代理链接格式: http://ip:port
async def soup_page(source, mod):
    ip_list = []
    if mod == 0:
        # 通用
        # 正则表达式匹配IP地址及端口号
        # \d{1,3} 匹配1到3位数字，\.:匹配点号。
        # :\d{1,5} 匹配冒号和其后的1到5位数字（端口号范围）。
        ip_port = re.findall(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}\b', source)
        for i in ip_port:
            ip_list.append(f"http://{i}")
        return ip_list

    elif mod == 1:
        # 89ip.cn
        ips = re.findall(r'(\d+\.\d+\.\d+\.\d+)', source)
        posts = re.findall(r'\s(\d{1,5})\s', source)
        for i in range(len(ips)):
            ip_list.append(f"http://{ips[i]}:{posts[i]}")
        return ip_list

    elif mod == 2:
        # 快代理 || kxdaili.com || proxy.ip3366.net || http://ip.tyhttp.com/3/
        ips = re.findall(r'>(\d+\.\d+\.\d+\.\d+)</td>', source)
        posts = re.findall(r'>(\d{1,5})</td>', source)
        for i in range(len(ips)):
            ip_list.append(f"http://{ips[i]}:{posts[i]}")
        return ip_list

    elif mod == 3:
        # www.proxy-list.download/api/v1/get?type=http
        ip_port = source.split('\r\n')[:-1]
        for i in ip_port:
            ip_list.append(f"http://{i}")
        return ip_list



def ip_main():
    clear_file()  # 清空存放代理文件
    print('正在抓取代理ip。。。')
    # 所有任务完成后关闭客户端会话和事件循环
    loop = asyncio.get_event_loop()
    loop.run_until_complete(create_aiohttp())
    print("代理抓取完成!!!")

