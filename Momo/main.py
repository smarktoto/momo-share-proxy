# encoding:utf-8
import asyncio
from aiohttp import ClientSession, ClientTimeout, TCPConnector
from ip import ip_main, getheaders

# 可根据自己电脑更改位置
link_path = "momo_link.txt"


# 读取文件获取文件内容
def readfile():
    with open('ip.txt', 'r', encoding='utf-8') as file:
        ips = file.readlines()
    return ips


# 读取文件获取momo链接
def share_Link():
    import sys
    import os

    # 判断文件是否存在，不存在则创建
    if os.path.isfile(link_path):
        fileopen = open(link_path, 'r', encoding='utf-8')
        momo_share_link = fileopen.readline().strip()
        # 判断是否有链接 无则终止程序
        if momo_share_link == '':
            fileopen.close()
            sys.exit()
        fileopen.close()
        return momo_share_link.strip()
    else:
        os.close(os.open(link_path, os.O_CREAT))  # 创建文件
        sys.exit()  # 终止程序


# 设置代理抓取https页面报错问题解决
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def create_aiohttp(url, proxy_list):
    global n
    n = 0

    async with ClientSession(connector=TCPConnector(ssl=False)) as session:
        # 生成任务列表
        task = [asyncio.create_task(web_request(url=url, proxy=proxy, session=session))
                for proxy in proxy_list]
        await asyncio.wait(task)


# 网页访问
async def web_request(url, proxy, session):
    hd = await getheaders()  # 设置请求头
    sem = asyncio.Semaphore(50)  # 设置限制并发次数.
    tout = ClientTimeout(total=20)  # 设置请求超时
    async with sem:
        try:
            async with await session.get(url=url, headers=hd, proxy=proxy, timeout=tout) as response:
                # 返回字符串形式的相应数据
                page_source = await response.text()
                await page(page_source)
        except Exception as e:
            print("网页请求失败! ", e)


global n  # 记录访问成功次数


# 判断访问是否成功
async def page(page_source):
    global n
    if "学习天数" in page_source:
        n += 1
        print('访问成功!!!')
    else:
        print('访问失败! 页面无此元素。')


def main():
    link = share_Link()  # 读取文件里的墨墨分享链接
    print("访问链接:", link)
    ip_main()  # 抓取代理
    proxies = [i.strip() for i in readfile()]  # 生成代理列表
    asyncio.run(create_aiohttp(link, proxies))
    print("任务完成!!!")

    # 呈现程序运行结果。可根据自己电脑更改位置
    reminder_path = f'访问成功{n}次.txt'
    # 创建运行结果提示文件
    with open(reminder_path, 'w', encoding='utf-8') as f:
        f.close()


if __name__ == '__main__':
    main()
