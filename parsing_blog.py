# -*- coding: utf-8 -*- 

import subprocess
# import sys   
# !{sys.executable} -m pip install requests

import requests
import urllib.request
from bs4 import BeautifulSoup

import utils

class Parser(object):
    def __init__(self, _path='out', _markdown_mdoe=True, skip_sticker=True):
        self.counter = 0
        self.stkcounter = 0
        self.markdown_mdoe = _markdown_mdoe
        self.folder_path = _path
        if self.markdown_mdoe:
            self.endline = '\n\n'
        else:
            self.endline = '\n'
        self.title = '#'
        self.subtitle1 = '##'
        self.subtitle2 = '###'
        self.subtitle3 = '####'
        self.skip_sticker = skip_sticker
        # 파싱 리스트
        self.parsing_func_list = [self.img_group, self.link, self.text, self.code, self.img, self.sticker, self.hr, self.textarea, self.video, self.script, self.anniversary, self.unreliable_text, self.hashtags]


    def is_exist_item(self):
        pass

    @staticmethod
    def redirect_url(blog_url): #href 자체를 받음
        redirect_link = ''

        #티스토리 등 외부 블로그(www 붙어있음): iframe 관련 태그 없음. url 그 자체를 사용하면 됨
        no_need_redirect_url = ['PostView.nhn', 'PostList.nhn','www']

        for no_need in no_need_redirect_url:
            if no_need in blog_url:
                print('no need redirect url: ' + blog_url)
                return blog_url

        try:
            #print('리다이렉트 주소를 가져옵니다 : ', end = '')
            blog_soup = BeautifulSoup(requests.get(blog_url).text, 'lxml')
            #print(blog_soup)

            # iframe 관련 태그를 선택한 리스트를 만든다
            mainframelist=blog_soup.select('iframe#mainFrame')
            screenframelist=blog_soup.select('iframe#screenFrame')

            # 네이버 블로그: iframe#mainFrame 태그가 존재
            if not screenframelist:
                for link in blog_soup.select('iframe#mainFrame'):
                    #print("link.get('src') :", link.get('src')) #link.get으로 src를 갖고와서 조합해 쓸 수 있음
                    redirect_link = "http://blog.naver.com" + link.get('src')
                print("redirect_link :",redirect_link)
                return redirect_link

            # 네이버 블로그로 리디렉션: iframe#screenFrame 태그가 존재
            if not mainframelist:
                for link in blog_soup.select('iframe#screenFrame'):
                    #print("link.get('src') :", link.get('src'))
                    redirect_link =link.get('src') #src 가져와서 그대로 쓰면 됨
                print("redirect_link :",redirect_link)
                return redirect_link

        except Exception as e:
            print(e)
            return ''

    # 링크
    def link(self, content):
        txt = ''
        if 'se_og_box' in str(content):
            for sub_content in content.select('.se_og_box'):
                if self.markdown_mdoe:
                    txt += '[' + str(sub_content['href']) + ']('
                    txt += str(sub_content['href'])
                    txt += ')'
                    txt += self.endline
                else:
                    txt += str(sub_content['href'])
                    txt += self.endline
            return txt
        elif 'se-module-oglink' in str(content):
            for sub_content in content.select('.se-oglink-info'):
                if self.markdown_mdoe:
                    txt += '[' + str(sub_content['href']) + ']('
                    txt += str(sub_content['href'])
                    txt += ')'
                    txt += self.endline
                else:
                    txt += str(sub_content['href'])
                    txt += self.endline
            return txt
        return None


    def wrapping_text(self, header, txt, tail=''):
        return header + ' ' + txt.strip() + '' + tail

    # 텍스트
    def text(self, content):
        txt = ''
        if 'se-title-text' in str(content):
            for sub_content in content.select('.se-title-text'):
                txt += self.wrapping_text(self.title, sub_content.text, self.endline)
            return txt
        elif 'se-section-sectionTitle' in str(content):
            #for sub_content in content.select('.se-section-sectionTitle'):
            for i, sub_content in enumerate( content.select('.se-section-sectionTitle') ):
                #print(str(i) + ' ' + sub_content.text.strip())
                if sub_content.text.strip() == '':
                    continue
                if 'se-l-default' in str(content):  # sectiontitle 1
                    txt += self.wrapping_text(self.subtitle1, sub_content.text)
                elif 'se-2-default' in str(content):  # sectiontitle 2
                    txt += self.wrapping_text(self.subtitle2, sub_content.text)
                elif 'se-3-default' in str(content):  # sectiontitle 3
                    txt += self.wrapping_text(self.subtitle3, sub_content.text)
                else:
                    txt += sub_content.text

                txt += self.endline
            return txt
        elif 'se-module-text' in str(content):
            for sub_content in content.select('.se-module-text'):
                for p_tag in sub_content.select('p'):
                    txt += p_tag.text
                    txt += self.endline
                if txt == '':
                    txt += sub_content.text
                    txt += self.endline
            return txt
        return None

    # 텍스트
    def unreliable_text(self, content):
        '''
        txt = ''
        if 'se-module-text' in str(content):
            for sub_content in content.select('.se-module-text'):
                txt += sub_content.text
                txt += self.endline
            return txt
        '''
        return None

    # 태그 존재 여부
    def hashtags(self, content):
        tags ='0'
        if 'se-hash-tag' in str(content):
            ## 태그 존재 한다
            tags = '1'
            # for tag in content.select('se-hash-tag'):
            #     print("*"*50,tag)
            #     # tags = tag.text
            #     # tags += self.endline
            # return tags
        return tags

    # 코드
    def code(self, content):
        txt = ''
        if 'se-code-source' in str(content):
            txt += '```'
            txt += self.endline
            for sub_content in content.select('.se-code-source'):
                for line in sub_content.text.split('\n'):
                    txt += line + '\n'
                txt += self.endline
                #print(str(sub_content))
            txt += '```'
            txt += self.endline
            return txt
        return None

    # 이미지 그룹
    def img_group(self,content):
        txt = ''
        str_content = str(content)
        if 'se-imageGroup' in str_content or 'se-imageStrip' in str_content:
            img_txt = self.img(content)
            if not (img_txt == '' or img_txt is None):
                txt += img_txt
            text_txt = self.text(content)
            if not (text_txt == '' or text_txt is None):
                txt += text_txt
            return txt
        return None

    # 이미지
    def img(self,content):
        txt = ''
        if 'se-image' in str(content) or 'se_image' in str(content):
            for sub_content in content.select('img'):
                url = sub_content['data-lazy-src']
                # if self.markdown_mdoe:
                #     txt += '![' + './img/' + str(self.counter)+'.png' + ']('
                #     txt += './img/' + str(self.counter)+'.png' + ')'
                #     txt += '\n'
                # else:
                #     txt += '['+ str(self.counter) +']'
                #     txt += url
                #     txt += '\n'

                # if not utils.saveImage(url, self.folder_path + '/img/' + str(self.counter)+'.png'):
                #     print('\t' + str(content) + ' 를 저장합니다.')
                # else:
                self.counter += 1
            txt += self.endline
            return txt
        return None

    def imgCount(self):
        return self.counter

    # 스티커 이미지 링크
    def sticker(self, content):
        txt = ''
        cont_text = str(content).replace('se_sticker', 'se-sticker')
        if 'se-sticker' in str(cont_text):
            if self.skip_sticker:
                self.stkcounter += 1
                # return '[sticker]' + self.endline
            # for sub_content in content.select('img'):
                # #fp.write(sub_content['src'])
                # txt += sub_content['src']
                # txt += self.endline
            # return txt
        return None

    def stickerCnt(self):
        return self.stkcounter

    # # 공감
    # def like(self, content):
    #     txt = ''
    #     result = re.search('<em class="u_cnt _count">(.*)</em>', content)
    #     txt += result.group(1)
    #     return txt

    # 구분선
    def hr(self, content):
        txt = ''
        if 'se-hr' in str(content):
            for sub_content in content.select('.se-hr'):
                #fp.write(str(sub_content))
                #fp.write(str('<hr /> \n')) #hr 테그
                if self.markdown_mdoe:
                    txt += '---'
                else:
                    txt += '<hr />'
                txt += self.endline
            return txt
        return None

    # 텍스트 영역
    def textarea(self, content):
        txt = ''
        if 'se_textarea' in str(content):
            for sub_content in content.select('.se_textarea'):
                #fp.write(str(sub_content))
                txt += str(sub_content)
                txt += self.endline
            return txt
        return None

    # 비디오 영역
    def video(self, content):
        txt = ''
        # if 'se_video' in str(content) or 'se-video' in str(content):
        #     for sub_content in content.select('iframe'):
        #         #fp.write(sub_content['src'])
        #         txt += sub_content['src']
        #         txt += self.endline
        #     return txt
        return None

    # 비디오 개수세기
    def videoCnt(self, content):
        videoCnt = 0
        if 'se_video' in str(content) or 'se-video' in str(content):
            for sub_content in content.select('iframe'):
                #fp.write(sub_content['src'])
                videoCnt += 1
        return videoCnt

    # 스크립트 영역
    def script(self, content):
        txt = ''
        if 'se-section-material' in str(content):
            for sub_content in content.select('.se-material-title'):
                txt += '\t'+sub_content.text
                txt += self.endline
            for sub_content in content.select('.se-section-material'):
                for sub_content in content.select('a'):
                    txt += '\t'+sub_content['href']
                    txt += self.endline
            return txt
        if 'se-oembed' in str(content):
            for sub_content in content.select('script'):
                #fp.write(sub_content['data-module'])
                script_txt = sub_content['data-module']
                '''
                '''
                script_txt = script_txt[script_txt.find('<iframe'):]
                script_txt = script_txt[:script_txt.find('/iframe')+len('/iframe')+1]
                txt += script_txt
                txt += self.endline
            return txt
        return None

    def anniversary(self, content):
        txt = ''
        if 'se-anniversarySection' in str(content):
            for sub_content in content.select('.se-anniversary-date'):
                txt += '\t'+sub_content.text
                txt += self.endline
            for sub_content in content.select('.se-anniversary-date-text'):
                txt += '\t'+sub_content.text
                txt += self.endline
            for sub_content in content.select('.se-anniversary-title'):
                txt += '\t'+sub_content.text
                txt += self.endline
            for sub_content in content.select('.se-anniversary-summary'):
                txt += '\t'+sub_content.text
                txt += self.endline
            for sub_content in content.select('a'):
                txt += '\t'+sub_content['href']
                txt += self.endline

            return txt
        return None
        '''
        unkown tag: <div class="se-component se-anniversarySection se-l-anniversary_winter" id="SE-de85199c-41be-4717-9a3d-2a4b138b86fb">
        <div class="se-component-content">
        <div class="se-section se-section-anniversarySection se-l-anniversary_winter se-section-align-">
        <a class="se-module se-module-anniversarySection" href="http://blog.naver.com/chandong83/40180614296" target="_blank">
        <div class="se-anniversary-date-info">
        <span class="se-anniversary-date">2013.2.15.</span>
        <span class="se-anniversary-date-text">7년 전 오늘</span>
        </div>
        <div class="se-anniversary-info">
        <strong class="se-anniversary-title">끝없는 고수의 등장....</strong>
        <p class="se-anniversary-summary">RPG 게임을 할때나.... 만화 시리즈를 볼때 보면... 주인공이 강해지면 그 보다 강한 상대가 나타난다.... 근데..... 일하면서도 똑같은 것 같다.... 공부를 해서 내가 강해졌다고 생각하면 더 강한 고수가 
        나타나고.... 흠.... 이 세상에 넘사벽 고수가 어마어마 하다...</p>
        <p class="se-anniversary-blog">하이! 제니스</p>
        </div>
        </a>
        </div>
        </div>
        </div>
        '''

    # 위젯 개수
    def widget(self, content):
        if 'aWidget.push' in str(content):
            widgets = str(content).count('aWidget.push')
        # widgets = len(content.select('aWidget.push')) 
        return widgets


    def parsing(self, content):
        txt = ''
        for func in self.parsing_func_list:
            item = func(content)
            if item is not None:
                txt += item
                break

        if txt == '':
            print('unkown tag: ' + str(content))
        return txt