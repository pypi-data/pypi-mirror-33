# htmlLibrarian

## Installation

`sudo pip3 install htmlLibrarian`

## Introduction
The goal of this package is to almost be like a training wheels setup for web scraping.

A good example is recursively trying to visit all of the links on a site such as:

http://web.archive.org/web/20080827084856/http://www.nanowerk.com:80/nanotechnology/nanomaterial/commercial_all.php?page=2

If you mess up your scrape and you have done no preemptive measures, you lose all of your work done thus far. What `Librarian` aims to do is to save that html for later, so you don't have to redo scrapes that you have done before, letting you be much nicer to where you're requesting to and saving you time, letting you go through a much smoother scraping experience.

## Usage

Let's outline an example:

Take a look at the site above's html via Inspect Element; You will see that all of the names and links are under `<div class="divhead">`, and all of the blurbs are under `<div class="divline">`. Now, I would probably do this:

```python3
from urllib.request import urlopen
from bs4 import BeautifulSoup

alink = 'http://web.archive.org/web/20080827084856/http://www.nanowerk.com:80/nanotechnology/nanomaterial/commercial_all.php?page=2'
resp = urlopen(alink)
html = resp.read()
soup = BeautifulSoup(html, 'lxml')

for elem in soup.select('div.divhead'):
    print(elem.get_text())
```

To check if I was correct and there was nothing above that had the same css selector, to see if I had to change my headers using urllib.request.Request, or something else.
Then I'd probably check the same for `div.divline`, for the first reason above. Then for each of those sites, I'd have to recursively visit into them and grab their html.

If I screw anything up, or if some pages have different html, then it will take a long time to get back to where I was, making the process of scraping a site more painful than it has to be.

If we use `Librarian`, we can instead do this:

```python3
from htmlLibrarian import Librarian

lib = Librarian()

alink = 'http://web.archive.org/web/20080827084856/http://www.nanowerk.com:80/nanotechnology/nanomaterial/commercial_all.php?page=2'

html = lib.get(alink).get_html()
soup = BeautifulSoup(html, 'lxml')
```

Now, if I ever ask for that same website again (provided that `htmlLibrary` and the pickled files under `libarianTools` haven't been tampered with), the `Librarian` will find it and pull it out of your `htmlLibrary` so you can instantly use it.

If you need updated html, just
```python3
from htmlLibrarian import Librarian

lib = Librarian()

alink = 'http://web.archive.org/web/20080827084856/http://www.nanowerk.com:80/nanotechnology/nanomaterial/commercial_all.php?page=2'

newhtml = lib.fetch(alink).get_html()
```
`lib.fetch(alink)` will go and fetch the newest html and it will return a `dataLink` object.

If you want to see your older scrapes, just
```python3
from htmlLibrarian import Librarian

lib = Librarian()

alink = 'https://https://ca.indeed.com/jobs?q=data+scientist&l='
dataLinkList = lib.get_all(alink)
```

`lib.remove(alink)` will remove the dataLinks associated with `alink` from your `htmlLibrary` and `linkMap`.

To export your library as a csv file, do
```python3
from htmlLibrarian import librarianUtil

librarianUtil.make_csv('data.csv')
```
and all of your data will be exproted into `data.csv`.


This project is in it's infancy so if you want any features created, create an issue and I will get on it.


Thank you to `keithreitz` for creating `samplemod`, which I largely copied for the project structure.

