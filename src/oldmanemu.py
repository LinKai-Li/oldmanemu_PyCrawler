import sys
import time
import requests
from lxml import etree
import csv
import random


class OldmanSpider:
    def get_html(self, url):
        # 获取HTML
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
        }
        html = requests.get(url=url, headers=headers).text
        return html

    def get_all_console_type1(self):
        # 获取掌机类别
        all_type_url = "https://www.oldmanemu.net/"
        all_type_html = self.get_html(url=all_type_url)
        eboj = etree.HTML(all_type_html)
        console_type1_list = eboj.xpath('//li[@id="menu-item-21"]/a/text()')
        for i in range(1, 12):
            console = eboj.xpath('//li[@id="menu-item-21"]/ul[@class ="sub-menu"]/li[{}]//text()'.format(i))
            console_type1_list.extend(console)
            href = eboj.xpath('//li[@id="menu-item-21"]/ul[@class ="sub-menu"]/li[{}]//@href'.format(i))
            console_type1_list.extend(href)
        return console_type1_list

    def get_all_console_type2(self):
        # 获取家用机类别
        all_type_url = "https://www.oldmanemu.net/"
        all_type_html = self.get_html(url=all_type_url)
        eboj = etree.HTML(all_type_html)
        console_type2_list = eboj.xpath('//li[@id="menu-item-84"]/a/text()')
        for i in range(1, 17):
            console = eboj.xpath('//li[@id="menu-item-84"]/ul[@class ="sub-menu"]/li[{}]//text()'.format(i))
            console_type2_list.extend(console)
            href = eboj.xpath('//li[@id="menu-item-84"]/ul[@class ="sub-menu"]/li[{}]//@href'.format(i))
            console_type2_list.extend(href)
        return console_type2_list

    def get_menu_links(self, url):
        # 获取游戏机类别下的链接
        games_menu_url = self.get_html(url=url)
        eboj = etree.HTML(games_menu_url)
        games_content_list = []
        for i in range(2, 5):
            games_content = eboj.xpath("//div[@class ='entry-content']/p[{}]//text()".format(i))
            if len(games_content) > 1:
                games_content = [''.join(games_content[:])]
            if not games_content:
                continue
            games_content = [x for x in games_content if "配" not in x]
            games_content_list.extend(games_content)
            href = eboj.xpath("//div[@class='entry-content']/p[{}]//@href".format(i))
            href = [x for x in href if "bbs" not in x]
            games_content_list.extend(href)
        return games_content_list

    def get_arcade_links(self,url):
        # 获取街机类别下的链接
        games_menu_url = self.get_html(url=url)
        eboj = etree.HTML(games_menu_url)
        games_content_list = []
        for i in range(2, 10):
            games_content = eboj.xpath("//div[@class ='entry-content']/p[{}]/a//text()".format(i))
            if not games_content:
                continue
            games_content_list.extend(games_content)
            href = eboj.xpath("//div[@class='entry-content']/p[{}]/a//@href".format(i))
            games_content_list.extend(href)
        return games_content_list

    def get_menu(self, url, csv_name):
        # 获取游戏目录
        self.f = open("{}.csv".format(csv_name), 'w', newline='', encoding='utf8')
        self.writer = csv.writer(self.f)
        menu_url = self.get_html(url=url)
        eboj = etree.HTML(menu_url)
        menu = eboj.xpath('//div[@class="entry-content"]//text()')
        for i in range(1, len(menu)):
            menu = eboj.xpath('//div[@class="entry-content"]/p[{}]//text()'.format(i))
            href = eboj.xpath('//div[@class="entry-content"]/p[{}]//@href'.format(i))
            k = []
            for i in menu:
                j = i.replace(' ', '')
                k.append(j)
            k = [i.replace('\xa0', '') for i in k]
            k = [i.replace('\u3000', '') for i in k]
            if '\n' in k:
                k.remove('\n')
            if '' in k:
                k.remove('')
            if len(k) > 1:
                k = [''.join(k[:])]
            if not k:
                continue
            else:
                print(k)  # 可以去除保持美观
                self.writer.writerow(k)
            href = [i.replace('\n', '') for i in href]
            if not href:
                continue
            elif '/wp-login.php' in href:
                continue
            else:
                print(href)  # 可以去除保持美观
                self.writer.writerow(href)

    def get_others_menu(self, url, csv_name):
        # 获取其它游戏机类别下的目录
        self.f = open("{}.csv".format(csv_name), 'w', newline='', encoding='utf8')
        self.writer = csv.writer(self.f)
        self.writer.writerow(['掌机名称', '发行厂商', '发售年份', '全集类型', '游戏数量', '下载地址', '访问码'])
        menu = self.get_html(url=url)
        eboj = etree.HTML(menu)
        for i in range(1, 21):
            menu_table_list = []
            for a in range(1, 6):
                menu_table = eboj.xpath("//div[@class='entry-content']/table[{}]/tbody/tr/td[{}]//text()".format(i, a))
                menu_table_list.extend(menu_table)
            href = eboj.xpath("//div[@class='entry-content']/table[{}]/tbody/tr/td[6]//@href".format(i))
            menu_table_list.extend(href)
            menu_table_list.extend(['oldman'])
            if menu_table_list[0] == 'oldman':
                break
            print(menu_table_list)
            self.writer.writerow(menu_table_list)

    def choose_crawl(self):
        # 获取游戏机类型列表
        all_console_type1_list = self.get_all_console_type1()
        all_console_type2_list = self.get_all_console_type2()
        # 生成游戏机类型提示菜单
        console_type_dict = {'1': all_console_type1_list[0], '2': all_console_type2_list[0]}
        for key in console_type_dict:
            print('[' + key + ']' + console_type_dict[key])
        flag = 1
        console_type = []
        # 获取用户输入并判断是否为非法输入
        while flag == 1:
            console_type = input("请输入游戏机类型：")
            if console_type == '1':
                console_type = all_console_type1_list[1:]
                flag = 0
            elif console_type == '2':
                console_type = all_console_type2_list[1:]
                flag = 0
            else:
                print("输入错误！请输入数字选择游戏机类型！")
                flag = 1
        print('-' * 100)
        # 生成游戏机列表提示菜单
        console_dict = {}
        for i in range(1, int(len(console_type)/2)+1):
            console_dict['{}'.format(i)] = console_type[2*i-2]
        for key in console_dict:
            print('[' + key + ']' + console_dict[key])
        menu_links_list = []
        # 获取用户输入并判断是否为非法输入
        while flag == 0:
            console_name = input("请输入游戏机名称：")
            if console_name.isdigit() and not(console_name.isspace()):
                if int(console_name) <= int(len(console_type) / 2):
                    url = console_type[2*int(console_name)-1]
                    flag = 1
                    menu_links_list = self.get_menu_links(url=url)
                    if not menu_links_list:
                        self.get_others_menu(url=url,csv_name=console_type[-2])
                        print('-' * 100)
                        print('"{}.csv"获取成功！'.format(console_type[-2]))
                        print('-' * 100)
                        sys.exit()
                    if console_type[2*int(console_name)-2] == '街机':
                        menu_links_list = self.get_arcade_links(url=url)
                else:
                    print("输入错误！请输入数字选择游戏机！")
            else:
                print("输入错误！请输入数字选择游戏机！")
        print('-' * 100)
        menu_links_dict = {}
        # 生成游戏列表提示菜单
        for i in range(1, int(len(menu_links_list) / 2) + 1):
            menu_links_dict['{}'.format(i)] = menu_links_list[2 * i - 1]
            menu = '[' + str(i) + ']' + menu_links_list[2 * i - 2]
            menu = menu.replace(u'\xa0', u' ')
            print(menu)
        # 获取用户输入并判断是否为非法输入
        while flag == 1:
            games_menu = input("请输入游戏目录：")
            # print('-'*100)
            if games_menu.isdigit() and not(games_menu.isspace()):
                if int(games_menu) <= int(len(menu_links_list) / 2):
                    menu_name = menu_links_list[2 * int(games_menu) - 2]
                    menu_url = menu_links_dict[games_menu]
                    self.get_menu(url=menu_url, csv_name=menu_name)
                    print('-' * 100)
                    print('获取成功！请到文件夹中查看"{}.csv"！'.format(menu_name))
                    flag = 0
                else:
                    print("输入错误！请输入数字选择游戏目录！")
            else:
                print("输入错误！请输入数字选择游戏目录！")
                flag = 1

    def all_crawl_type1(self):
        all_console_type1_list = self.get_all_console_type1()
        console_type1 = all_console_type1_list[1:]
        try:
            for i in range(1, len(console_type1), 2):
                url = console_type1[i]
                menu_links_list = self.get_menu_links(url=url)
                time.sleep(random.randint(1, 3))
                for a in range(0, int((len(menu_links_list)) / 2 + 1), 2):
                    self.get_menu(url=menu_links_list[a + 1], csv_name=menu_links_list[a])
                    time.sleep(random.randint(1, 3))
                    print('-' * 100)
                    print('"{}.csv"获取成功！'.format(menu_links_list[a]))
                    print('-' * 100)
        except IndexError:
            url = console_type1[-1]
            time.sleep(random.randint(1, 3))
            self.get_others_menu(url=url, csv_name=console_type1[-2])
            print('-' * 100)
            print('"{}.csv"获取成功！'.format(console_type1[-2]))
            print('-' * 100)
            print('掌机游戏数据获取成功！')
            print('-' * 100)

    def all_crawl_type2(self):
        all_console_type2_list = self.get_all_console_type2()
        console_type2 = all_console_type2_list[1:]
        for i in range(1, len(console_type2), 2):
            url = console_type2[i]
            menu_links_list = self.get_menu_links(url=url)
            time.sleep(random.randint(1, 3))
            for a in range(0, int((len(menu_links_list)) / 2 + 1), 2):
                try:
                    self.get_menu(url=menu_links_list[a + 1], csv_name=menu_links_list[a])
                    time.sleep(random.randint(1, 3))
                    print('-' * 100)
                    print('"{}.csv"获取成功！'.format(menu_links_list[a]))
                    print('-' * 100)
                except requests.exceptions.MissingSchema:
                    url = console_type2[-3]
                    menu_links_list = self.get_arcade_links(url=url)
                    for a in range(0, int((len(menu_links_list)) / 2 + 1), 2):
                        self.get_menu(url=menu_links_list[a + 1], csv_name=menu_links_list[a])
                        time.sleep(random.randint(1, 3))
                        print('-' * 100)
                        print('"{}.csv"获取成功！'.format(menu_links_list[a]))
                        print('-' * 100)
                except IndexError:
                    url = console_type2[-1]
                    time.sleep(random.randint(1, 3))
                    self.get_others_menu(url=url, csv_name=console_type2[-2])
                    print('-' * 100)
                    print('"{}.csv"获取成功！'.format(console_type2[-2]))
                    print('-' * 100)
                    print('家机游戏数据获取成功！')
                    print('-' * 100)
        print('全部数据获取成功！请到文件夹中查看CSV格式文件！')

    def run(self):
        # 询问用户选择爬取模式：
        flag = 0
        choose_list = ['1', '选择爬取', '2', '全部爬取']
        for i in range(0, 4, 2):
            menu = '[' + choose_list[i] + ']' + choose_list[i + 1]
            print(menu)
        while flag == 0:
            mode = input("请输入爬取模式：")
            if mode == '1':
                print('-' * 100)
                self.choose_crawl()
                flag = 1
            elif mode == '2':
                print('-' * 100)
                self.all_crawl_type1()
                self.all_crawl_type2()
                flag = 1
            else:
                print("输入错误！请输入数字选择模式！")
                flag = 0
        self.f.close()


if __name__ == '__main__':
    spider = OldmanSpider()
    spider.run()
