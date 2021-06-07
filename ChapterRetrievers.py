from bs4 import BeautifulSoup
import requests

class RoyalRoadRetriever:

    def get_web_data(self, url):
        return BeautifulSoup(requests.get(url).text, 'html.parser')

    def get_RR_cover_image(self, soup):
        return soup.find("img", class_="img-offset thumbnail inline-block").attrs.get('src')

    def get_RR_ChapterList(self, soup):
        # <table class="table no-border" data-chapters="196" id="chapters">
        # <tr data-url="/fiction/36049/the-primal-hunter/chapter/557051/chapter-1-another-monday-morning" style="cursor: pointer">
        chaptersTable = soup.find_all(id="chapters").pop()
        chapterSoupList = chaptersTable.contents[3].contents

        #Grab the website title, then reformat the string to be only the fiction title
        fictionTitle = ''.join(soup.find('title').contents[0].split('|')[0]).strip()
        chapterList = []
        for index, x in enumerate(chapterSoupList):
            # Odd numbers hold the chapter urls
            if index % 2 == 1:
                chapterTitle = x.find('a').text.strip()
                chapter = {'title': chapterTitle,
                           'url': "https://www.royalroad.com" + x.attrs.get('data-url'),
                           'fiction':fictionTitle
                            }
                chapterList.append(chapter)
        return chapterList