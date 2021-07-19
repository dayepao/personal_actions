import re
import time

from bs4 import BeautifulSoup
from selenium.webdriver import Edge

# pip install -U requests[security]

driver = Edge(executable_path='C:\\Users\\ll057\\Desktop\\edgedriver_win64\\msedgedriver.exe')
url = "https://search.cctv.com/search.php?qtext=%E5%8D%A7%E5%BA%95%20%E6%99%AE%E6%B3%95%E6%A0%8F%E7%9B%AE%E5%89%A7&type=video"
resoult = {}
res = driver.get(url)
html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')
items = soup.find_all(class_='jvedio')
for item in items:
    if '普法栏目剧' in item.a['title']:
        if '卧底' in item.a['title']:
            resoult[item.a["title"]] = re.findall(r"targetpage=(.+?)&point=", item.a['href'])
for page in range(1, 4):
    time.sleep(10)
    page = driver.find_element_by_partial_link_text('下一页')
    page.click()
    time.sleep(10)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all(class_='jvedio')
    for item in items:
        if '普法栏目剧' in item.a['title']:
            if '卧底' in item.a['title']:
                resoult[item.a["title"]] = re.findall(r"targetpage=(.+?)&point=", item.a['href'])
new_resoult = sorted(resoult.items(), reverse=False)
new_resoult = dict(new_resoult)
print("下面是结果：\n")
for key, value in new_resoult.items():
    print(key, value)
