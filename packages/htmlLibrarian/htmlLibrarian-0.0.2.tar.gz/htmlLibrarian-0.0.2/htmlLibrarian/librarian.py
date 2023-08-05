import pickle as pkl
import os
import time
import urllib
from urllib.request import urlopen

class Librarian:
    def __init__(self, rateLimitVal=2):
        if not os.path.isdir('librarianTools'):
            print('creating librarianTools dir...')
            os.mkdir('librarianTools')

        if not os.path.isdir('htmlLibrary'):
            print('creating htmlLibrary dir...')
            os.mkdir('htmlLibrary')

        try:
            self.linkMap = pkl.load(open('./librarianTools/linkMap.pkl', 'rb'))
        except:
            self.linkMap = {}

        self.rateLimitVal = rateLimitVal

    def rateLimit(Librarian):
        try:
            lastTime = pkl.load(open('./librarianTools/lastTime.pkl', 'rb'))
        except:
            lastTime = 0
        currentTime = time.time()
        timeToWait = Librarian.rateLimitVal - (currentTime - lastTime)
        if timeToWait > 0:
            print('sleeping', timeToWait, 'seconds...')
            time.sleep(timeToWait)
        pkl.dump(time.time(), open('./librarianTools/lastTime.pkl', 'wb'))

    def get(Librarian, link):
        if link in Librarian.linkMap:
            mapval = Librarian.linkMap[link]
        else:
            Librarian.linkMap[link] = len(Librarian.linkMap.keys())
            mapval = Librarian.linkMap[link]

        pkl.dump(Librarian.linkMap, open('./librarianTools/linkMap.pkl', 'wb'))
        fileName = './htmlLibrary/html_'+str(mapval)

        try:
            f = pkl.load(open(fileName, 'rb'))
            print('found file; loading and returning right now...')
            return f

        except:
            print('could not find html for that link in the html store. getting...')
            Librarian.rateLimit()
            try:
                res = urlopen(link)
                html = res.read()
                print('found site html!')
                pkl.dump(html, open(fileName, 'wb'))
                return html
            except urllib.error.HTTPError as e:
                print('ran into an HTTPError scraping the site...')
                print('HTTPError: ', e.code)
                print('setting this site to empty bytes...')
                html = bytes('', 'utf-8')

                if e.code == '404':
                    return html
                pkl.dump(html, open(fileName, 'wb'))
                return html

    def remove(Librarian, link):

        if link in Librarian.linkMap:
            fileName = './htmlLibrary/html_'+str(Librarian.linkMap[link])
            del Librarian.linkMap[link]
            os.remove(fileName)
            print('removed', link, 'from my library!')
            return True

        print("couldn't find that link in my library!")
        return False
