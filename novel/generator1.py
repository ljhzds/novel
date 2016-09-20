# coding = utf-8
import asyncio
# import async_timeout
import aiohttp
import time


def consumer():
    r = ''
    while True:
        n = yield r 
        if not n:
            return
        print('[CONSUMER] Consuming %s ...' % n)
        r = '[%s returns]' % n


def produce(c):
    c.send(None)
    n = 0
    while n < 5:
        n += 1
        print('[PRODUCER] Producing %s ...' % n)
        r = c.send(n)
        print('[PRODUCER] Consumer returns : %s ' % r)
    c.close()

async def test():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.github.com/events') as resp:
            return resp.status, str(await resp.text())[:10]


async def test2(n):
    await asyncio.sleep(1)
    return n

async def n_times_test2(n):
    tasks = []
    for i in range(n):
        task = asyncio.ensure_future(test2(i))
        tasks.append(task)
    result = await asyncio.gather(*tasks)
    return result


async def get_content(url):
    pass


urls = ['http://www.1xiaoshuo.com//yongyejunwang/6853993/', 'http://www.1xiaoshuo.com//yongyejunwang/6847388/', '   http://www.1xiaoshuo.com//yongyejunwang/6842648/']


if __name__ == '__main__':
    # c = consumer()
    # produce(c)
    import async_timeout
    start = time.time()
    loop = asyncio.get_event_loop()
    # ss = loop.run_until_complete(asyncio.wait(tasks))
    ss = loop.run_until_complete(n_times_test2(5))
    end = time.time()
    print(end-start)
    print(ss)