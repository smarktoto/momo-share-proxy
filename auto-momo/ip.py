# encoding:utf-8
from asyncio import create_task, wait, Semaphore, run
from random import choice
from aiohttp import ClientSession, ClientTimeout, TCPConnector
from re import findall, search

listIP = []  # 保存IP地址


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
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36"]
    headers = {'User-Agent': choice(headers_list)}
    return headers


# 生成任务列表
async def taskList(ss):
    task = [
        create_task(get_page('http://www.kxdaili.com/dailiip/2/1.html', session=ss)),
        create_task(get_page('https://proxy.seofangfa.com/', session=ss)),
        create_task(get_page('http://www.66ip.cn/areaindex_33/1.html', session=ss)),
        create_task(get_page('https://www.kuaidaili.com/free/inha/1/', mod=2, session=ss)),
        create_task(
            get_page('https://www.89ip.cn/tqdl.html?num=1000&address=&kill_address=&port=&kill_port=&isp=', mod=8,
                     session=ss)),
        create_task(get_page('https://cdn.jsdelivr.net/gh/parserpp/ip_ports/proxyinfo.txt', mod=-1, session=ss)),
        create_task(
            get_page('https://fastly.jsdelivr.net/gh/parserpp/ip_ports@main/proxyinfo.txt', mod=-1, session=ss)),
        create_task(get_page('https://www.kuaidaili.com/free/intr/2/', mod=2, session=ss)),
        create_task(get_page('https://www.proxy-list.download/api/v1/get?type=http', mod=3, session=ss)),
    ]

    for i in range(1, 4):
        task.append(create_task(get_page(f'http://www.nimadaili.com/http/{i}/', mod=4, session=ss)))
        task.append(create_task(get_page(f'https://www.89ip.cn/index_{i}.html', session=ss)))
        task.append(create_task(get_page(f'http://http.taiyangruanjian.com/free/page{i}/', mod=1, session=ss)))
        task.append(create_task(get_page(f'http://www.kxdaili.com/dailiip/1/{i}.html', session=ss)))
        task.append(create_task(get_page(f'http://www.ip3366.net/free/?stype=1&page={i}', session=ss)))
        task.append(create_task(get_page(f'https://www.dieniao.com/FreeProxy/{i}.html', mod=5, session=ss)))
    return task


# 实例化请求对象
async def create_aiohttp_ip():
    async with ClientSession(connector=TCPConnector(ssl=False)) as session:
        task = await taskList(session)
        await wait(task)


# 访问网页
async def get_page(url, session, mod=0):
    tout = ClientTimeout(total=5)
    hd = await getheaders()
    try:
        async with Semaphore(3):
            async with await session.get(url=url, headers=hd, timeout=tout) as response:
                page_source = await response.text()
                await soup_page(page_source, mod=mod)
    except Exception as e:
        print(f"['{url}']抓取失败:", e)


async def soup_page(source, mod):
    if mod == 0:
        # 通用
        ips = findall(r'<td>[\s]*?(\d+\.\d+\.\d+\.\d+)[\s]*?</td>', source)
        posts = findall(r'<td>[\s]*?(\d{1,5})[\s]*?</td>', source)
        for i in range(len(ips)):
            listIP.append(f"http://{ips[i]}:{posts[i]}")

    elif mod == -1:
        res = source.split('\n')
        for i in range(len(res) - 1):
            listIP.append(f'http://{res[i]}')

    elif mod == 1:
        # 太阳
        ips = findall(r'<div.*?">(\d+\.\d+\.\d+\.\d+)</div>', source)
        posts = findall(r'<div.*?">(\d{1,5})</div>', source)
        for i in range(len(ips)):
            listIP.append(f"http://{ips[i]}:{posts[i]}")

    elif mod == 2:
        # 快代理
        ips = findall(r'<td\s.*?="IP">(\d+\.\d+\.\d+\.\d+)</td>', source)
        posts = findall(r'<td\s.*?="PORT">(\d{1,5})</td>', source)
        for i in range(len(ips)):
            listIP.append(f"http://{ips[i]}:{posts[i]}")

    elif mod == 3:
        # www.proxy-list.download/api/v1/get?type=http
        ip_list = source.split('\r\n')[:-1]
        for i in ip_list:
            listIP.append(f"http://{i}")

    elif mod == 4:
        # 泥马代理
        ip_post = findall(r'<td>(.*?:\d+)</td>', source)
        for i in ip_post:
            listIP.append(f"http://{i}")

    elif mod == 5:
        # 蝶鸟
        ip_list = findall(r"<span\sclass='f-address'>(.*?)</span>", source)[1:]
        port_list = findall(r"<span class='f-port'>(\d+)</span>", source)
        for i in range(len(ip_list)):
            listIP.append(f'http://{ip_list[i]}:{port_list[i]}')

    elif mod == 6:
        # 站大爷
        pass
    elif mod == 7:
        ips = findall(r'<td>.*?(\d+\.\d+\.\d+\.\d+)</td>', source)
        posts = findall(r'<td>(\d{1,5})</td>', source)
        for i in range(len(ips)):
            listIP.append(f'http://{ips[i]}:{posts[i]}')
    elif mod == 8:
        temp = search(r'<div\sstyle=\"padding-left:20px;\">[\s]?(.*?)[\s]?</div>', source)
        pList = temp.group(1).strip().split('<br>')[:-2]
        for p in pList:
            print(f"http://{p}")


def ip_main():
    run(create_aiohttp_ip())
    global listIP
    listIP = list(set(listIP))  # 代理去重
    print(f"代理ip抓取完成,共{len(listIP)}个可用代理ip地址。")
