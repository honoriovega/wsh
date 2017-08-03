import urllib
import re
import sys
from bs4 import BeautifulSoup
import json
import os


from flask import Flask

app = Flask(__name__)


#  builds a disqus link for comments
def buildLink(html):

    video_name = re.findall('<meta content="(.*)" name="title"',html)[0].replace(' ','%20')

    video_id = re.findall("var disqus_identifier = '(\d+)';",html)[0]

    stuff = { ':' : '%3A', '/' : '%2F', '?' : '%3F' , '=' : '%3D'}
    url = 'www.worldstarhiphop.com/videos/video.php?v=wshh63xS1M20QU5JzsWd'

    for key in stuff.keys():
        url = url.replace(key,stuff[key])
        if(key in url):
            url = url.replace(key,stuff[key])

    temp = ["https://disqus.com/embed/comments/?base=default",
     "f=worldstar",
     "t_i=" + video_id,
     "t_u="  +  url,
     "t_d=" + video_name,
     "t_t=" + video_name,
     "s_o=default"]

    return '&'.join(temp)

#  finds all the links to worldstar videos from a page
def getLinks(mainLink):

    html = urllib.urlopen(mainLink).read()
    base = 'http://www.worldstarhiphop.com'
    pattern = '/videos/video\.php\?v=[A-z0-9]+'

    return [ base + link for link in set(re.findall(pattern,html) )]

def getRawVideoLink(html):

    patterns = [ r'http://hw-videos.*\.mp4', 'http://www.youtube.com.*autoplay=1',
                'http://hw-videos.*\\.flv' ]

    for pattern in patterns:
        video_link = re.findall(pattern, html)
        if(video_link):
            return video_link[0]

    return ''

# scrape info from video and deliver in json format
def getJson(videoLink):

    videoInfo = {'title' : '', 'views' : '', 'date' : '', 'videolink' : '',
                 'imgUrl' : '', 'disqusLink' : '', 'link' : videoLink, 'about' : ''}
 
    try:
        data = urllib.urlopen(videoLink).read()
        disqusLink = buildLink(data)
        soup = BeautifulSoup(data,'html.parser')
        
        title = soup.find('h1').text
        views = soup.find('strong', attrs={'class': 'watch-view-count'}).text
        date = soup.find('time', attrs={'class': 'date'})['datetime']
        imgUrl = soup.find('meta',attrs={"itemprop" : "thumbnailUrl"})['content']
        about = soup.find('div', attrs={'class':'text-holder'}).text

        videoInfo['title']  =  title.encode('utf-8')
        videoInfo['views'] =  views.encode('utf-8')
        videoInfo['date']  =  date.encode('utf-8')
        videoInfo['videolink']  =  getRawVideoLink(data).encode('utf-8')
        videoInfo['imgUrl']  =  imgUrl.encode('utf-8')
        videoInfo['disqusLink'] =  disqusLink.encode('utf-8')
        videoInfo['about']  =  about.encode('utf-8')

    except:
		# handle errors here
		return videoInfo

        
    return videoInfo

# find all videos from a page and return json data for each video
def getAllJson():
    
    mainLink = 'http://www.worldstarhiphop.com/videos/search.php?s=' + 'strip club'.replace(' ','+')
    
    datajson = [getJson(link) for link in getLinks(mainLink) ]

    # sort the video by upload date
    datajson = sorted(datajson, key=lambda k: k['date'],reverse=True)

    return json.dumps(datajson)    





@app.route('/')
def hello():
    return getAllJson()


app.run(host=os.getenv('IP', '0.0.0.0'),port=int(os.getenv('PORT', 8080)))

