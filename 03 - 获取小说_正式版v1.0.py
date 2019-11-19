import os
import re
import requests
import threading
import time

# url = 'https://www.77nt.com/50750/'
# url = 'https://www.77nt.com/50750/12068063.html'
# url = 'https://www.77nt.com/107094/34439391.html'

text_index_list = []
lock = threading.Lock()


def get_date(url):
    html = requests.get(url)
    html_bytes = html.content
    html_str = html_bytes.decode()
    text_index_list.append(url)
    return html_str  # 返回值为从服务器获得的数据，字符串类型


#
#
def get_topic(index_url, index_html):
    topic_url_list = []
    topic_block = re.findall(r'<dl>(.*?)</dl>', index_html, re.S)[0]  # tips: 加个括号框起来，只返回括号里的数据
    topic_url = re.findall(r'href="(.*?)"', topic_block, re.S)
    for u in topic_url:
        topic_url_list.append(index_url + u)
    return topic_url_list  # 得到小说的目录地址（URL)


# pycharm 遇到 \r 会回到开头，若是没有\n配合，会覆盖前面的内容
def get_article(article_html, index):
    chapter_name = re.search(r'<h1>(.*)</h1>', article_html, re.S).group(1)
    chapter_name = re.sub(r'[/\\:*?"<>|《》7nt.com]', '', chapter_name)
    chapter_name = re.search(r'[\u4e00-\u9fa5]+\s(.*)', chapter_name, re.S).group(1)
    # print(chapter_name)

    chapter_name = str(index + 1) + '-' + chapter_name

    try:
        text_block = re.findall(r'<div class="con_show_l"><script type="text/javascript">show_d\(\);</script></div>('
                                r'.*?)<div', article_html, re.S)[0]
        text_block = text_block.replace('\r<br />', "")
        text_block = text_block.replace('<br />', '')
        text_block = text_block.replace('&nbsp;&nbsp;&nbsp;&nbsp;', '\r\n')
        return chapter_name, text_block  # 得到小说章节名称和内容
    except Exception as e:
        print(chapter_name + '----出错----')
        text_block = '无内容'
        return chapter_name, text_block


def save(chapter, article, name, i):
    if not os.path.exists(f"../小说/{name}"):
        os.mkdir(f"../小说/{name}")
    # print(chapter)
    if not os.path.exists(os.path.join(f"../小说/{name}", chapter + '.txt')):
        with open(os.path.join(f"../小说/{name}", chapter + '.txt'), 'w+', encoding='utf-8') as f:
            f.write(chapter)
            f.write('\r\n')
            f.write(article)


def control(name, url):
    index_html = get_date(url)
    top_list = get_topic(url, index_html)
    for i in top_list:
        index = top_list.index(i)   # 获得页面列表的索引，方便排序
        if i not in text_index_list:   # 判断网页是否已经读取过，防止线程重复进行
            lock.acquire()
            text_index_list.append(i)
            lock.release()
            article_html = get_date(i)
            chapter_name, text_block = get_article(article_html, index)
            save(chapter_name, text_block, name, i)


if __name__ == '__main__':
    Aim = ('轮回乐园', 'https://www.77nt.com/98380/')

    sub_t1 = threading.Thread(target=control, args=Aim, daemon=True)
    sub_t2 = threading.Thread(target=control, args=Aim, daemon=True)
    sub_t3 = threading.Thread(target=control, args=Aim, daemon=True)
    sub_t4 = threading.Thread(target=control, args=Aim, daemon=True)
    sub_t5 = threading.Thread(target=control, args=Aim, daemon=True)

    print("采集开始")

    sub_t1.start()
    sub_t2.start() 
    sub_t3.start()
    sub_t4.start()
    sub_t5.start()

    sub_t1.join()
    sub_t2.join()
    sub_t3.join()
    sub_t4.join()
    sub_t5.join()

    print("采集完成")