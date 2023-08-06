from bs4 import BeautifulSoup
import requests


def toplink(search):
    SearchUrl=str('https://www.youtube.com/results?search_query='+search)
    page=requests.get(SearchUrl)
    soup = BeautifulSoup(page.text, "lxml")
    print(page)
    link=soup.findAll(attrs={'class':'yt-uix-tile-link'})
    links=link[0]
    return ('https://www.youtube.com' + links['href'])

def toplinks(search):
    SearchUrl=str('https://www.youtube.com/results?search_query='+search)
    page=requests.get(SearchUrl)
    soup = BeautifulSoup(page.text, "lxml")
    print(page)
    link=soup.findAll(attrs={'class':'yt-uix-tile-link'})
    links=link[0]
    ret=[]
    for vid in link:
        ret.append('https://www.youtube.com' + vid['href'])

    return ret
