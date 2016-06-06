# -*- coding: cp1250 -*-
import locale,urllib2,re
locale.setlocale(locale.LC_ALL, '')
import time


from HTMLParser import HTMLParser

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


class wordCounter:
    def __init__(self, word, counter):
        self.word = word
        self.counter=counter
    def __lt__(self, other):
         return self.counter > other.counter

page="http://wp.pl"
wybor=raw_input('Podaj link do strony (puste jeżeli domyslna): ')
if wybor != "":
    page = wybor

print "Wybrana strona to: "+page
print "Pobieranie strony..."
pageContent = urllib2.urlopen(page).read()
print "Strona Pobrana"
print "Parsowanie strony..."

print "Usuwam script"
pageContent = (re.subn(r'<(script).*?</\1>(?s)', '', pageContent)[0])
print "Usuwam style"
pageContent = (re.subn(r'<(style).*?</\1>(?s)', '', pageContent)[0])
print "Zmieniam kodowanie na utf-8 do regex'ow"
pageContent = pageContent.decode('utf-8', 'ignore')
print "Dodaje spację przed tagiem HTML aby nie połączyło słów pomiędzy nimi"
pageContent = pageContent.replace(u"<",u" <")
print "Usuwam tagi html"
pageContent = strip_tags(pageContent)
print "Zmieniam znaki na małe"
pageContent = pageContent.lower()
print "Usuwam znaki nie alfanumeryczne"
pageContent = re.sub(u'[^a-z0-9ąęśćżźłóćń\d\s]+', ' ', pageContent)
print "Usuwam zdublowane spacje i nowe linie"
pageContent = re.sub(u'[\t\r ]+', ' ', pageContent)
pageContent = re.sub(u'[\n]+', '\n', pageContent)
pageContent = re.sub(u'[\n ]+', '\n', pageContent)
pageContent = pageContent.replace("\n \n","\n")
print "Parsowanie ukończone"
print "Zmieniam kodowanie na ASCI aby zapisać do pliku"
print "Zapisywanie do pliku"
f = open('index.php', 'w')
f.write(pageContent.strip().encode("utf8"))
f.close()
print "Plik zapisany na dysk"


K=10#ilość najczęściej występujących słów
THRESH=4#minimalna ilość wystąpień słowa
content = open('index.php', 'r').read()

start = time.time()

contentList = content.split('\n')
contentList.sort(key=lambda x: locale.strxfrm(x))
wordCounterList = []

previous = ""
for p in contentList:
    if previous == p:
        wordCounterList[-1].counter+=1
    else:
        wordCounterList.append(wordCounter(p,1))
    previous = p;

wordCounterList.sort()
for i in range (0,K):
    #for w in wordCounterList:
    if wordCounterList[i].counter < THRESH:
        break
    print wordCounterList[i].word.decode('utf-8', 'ignore') + " <---> " + str(wordCounterList[i].counter)
    #print p.decode('utf-8', 'ignore')+"<<<"

end = time.time()

print "Czas wykonania: "+ str(end - start)+ " sekundy"



