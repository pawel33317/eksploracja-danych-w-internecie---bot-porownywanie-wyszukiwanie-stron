# -*- coding: cp1250 -*-
import locale,urllib2,re
import numpy as np
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
class podobienstwoWynik:
    def __init__(self, file1, file2, result):
        self.file1 = file1
        self.file2 = file2
        self.result=result
    def __lt__(self, other):
         return self.result < other.result
def usunZnacznikiHTML(text):
    print "Usuwam script"
    text = (re.subn(r'<(script).*?</\1>(?s)', '', text)[0])
    print "Usuwam style"
    text = (re.subn(r'<(style).*?</\1>(?s)', '', text)[0])
    print "Zmieniam kodowanie na utf-8 do regex'ow"
    text = text.decode('utf-8', 'ignore')
    print "Dodaje spację przed tagiem HTML aby nie połączyło słów pomiędzy nimi"
    text = text.replace(u"<",u" <")
    print "Usuwam tagi html"
    text = strip_tags(text)
    return text   
def usunZnakiPrzestankowe(text):
    print "Usuwanie znakow przestankowych"
    text = text.lower()
    text = re.sub(u'[^a-z0-9ąęśćżźłóćń\d\s]+', ' ', text)
    return text
def usunNoweLinie(text):
    print "Usuwanie nowych linii"
    text = re.sub(u'[\t\r\n ]+', '\n', text)
    return text
def usunPojedynczeZnaki(text):
    print "Usuwanie pojedynczych znakow"
    listaWyrazow = text.strip().split('\n')
    i = 0
    iloscWyrazow = len(listaWyrazow)
    while i < iloscWyrazow:
        if len(listaWyrazow[i]) < 2:
            del(listaWyrazow[i])
            iloscWyrazow -= 1
        else:
            i +=1
    text = "\n".join(listaWyrazow)
    return text

listaLinkow = [ 'https://pl.wikipedia.org/wiki/Zoologia', 'https://pl.wikipedia.org/wiki/Zwierz%C4%99ta',
'https://pl.wikipedia.org/wiki/Systematyka_organizm%C3%B3w', 'https://pl.wikipedia.org/wiki/Ornitologia',
'https://pl.wikipedia.org/wiki/Biologia',
'https://pl.wikipedia.org/wiki/Muzyka_powa%C5%BCna', 'https://pl.wikipedia.org/wiki/Muzyka_romantyczna',
'https://pl.wikipedia.org/wiki/Sonata', 'https://pl.wikipedia.org/wiki/Opera',
'https://pl.wikipedia.org/wiki/Symfonia',
'https://pl.wikipedia.org/wiki/Informatyka', 'https://pl.wikipedia.org/wiki/System_operacyjny',
'https://pl.wikipedia.org/wiki/Programowanie_komputer%C3%B3w', 'https://pl.wikipedia.org/wiki/J%C4%99zyk_programowania',
'https://pl.wikipedia.org/wiki/Oprogramowanie' ]
listaOpisowLinkow = [ 'zoologia1', 'zoologia2', 'zoologia3', 'zoologia4', 'zoologia5',
                      'muzyka__1', 'muzyka__2', 'muzyka__3', 'muzyka__4', 'muzyka__5',
                      'informat1', 'informat2', 'informat3', 'informat4', 'informat5']

for i in range(len(listaLinkow)):
    print "####################\n###Przetwarzam stronę: "+listaLinkow[i]
    print "Pobieranie strony..."
    pageContent = urllib2.urlopen(listaLinkow[i]).read()
    print "Parsowanie strony..."
    pageContent = usunNoweLinie(usunZnakiPrzestankowe(usunZnacznikiHTML(pageContent)))
    pageContent = usunPojedynczeZnaki(pageContent)
    print "Zmieniam kodowanie na ASCI aby zapisać do pliku i zapisuje"
    f = open(listaOpisowLinkow[i]+'.txt', 'w')
    f.write(pageContent.strip().encode("utf8"))
    f.close()

SLOWNIK = []
print "Tworzenie słownika"
for i in range(len(listaLinkow)):
    fileContent = open(listaOpisowLinkow[i]+'.txt', 'r').read().strip().split('\n')
    for word in fileContent:
        if word not in SLOWNIK:
            SLOWNIK.append(word)
    print "Rozmiar słownika: "+str(len(SLOWNIK))

vectorList = []
print "Generowanie listy wektorów..."
for i in range(len(listaLinkow)):
    vector = [0.0]*len(SLOWNIK)
    fileContent = open(listaOpisowLinkow[i]+'.txt', 'r').read().strip().split('\n')
    ilosc_wyrazow = len(fileContent)
    for word in fileContent:
        vector[SLOWNIK.index(word)] += 1.0/ilosc_wyrazow
    vectorList.append(vector)

listaWynikow = []
print "Obliczanie podobieństw..."
for i in range(len(listaLinkow)):
    for j in range(len(listaLinkow)):
        if j > i:
            print vectorList[i][1]
            result = np.dot(vectorList[i],vectorList[j])/(np.linalg.norm(np.array(vectorList[i]))*np.linalg.norm(np.array(vectorList[j])))
            listaWynikow.append(podobienstwoWynik(listaOpisowLinkow[i],listaOpisowLinkow[j],result))

print "Sortowanie i wypisywanie wyników"
listaWynikow.sort()
for wynik in listaWynikow:
    helper = ""
    if wynik.file1[0:7] == wynik.file2[0:7]:
        helper = "# "
    else:
        helper = "- "
    print helper + wynik.file1+" <-> "+wynik.file2+" => "+str(wynik.result)





























