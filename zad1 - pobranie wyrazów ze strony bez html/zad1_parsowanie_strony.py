                                                                     
                                                                     
                                                                     
                                             
# -*- coding: cp1250 -*-
import locale,urllib2,re
locale.setlocale(locale.LC_ALL, '')

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




page="http://kis.p.lodz.pl"
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
#print pageContent


    


