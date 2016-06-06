# -*- coding: cp1250 -*-
import locale,urllib2,re,sqlite3
import time,socket
from BeautifulSoup import BeautifulSoup
import sys
sys.setrecursionlimit(100)
locale.setlocale(locale.LC_ALL, '')
from HTMLParser import HTMLParser

STRONY_STARTOWE = ['http://wykop.pl','http://www.elektroda.pl',
               'http://www.wp.pl','http://weeia.p.lodz.pl',
               'http://www.forumpc.pl'] 
ILOSC_STRON_DO_POBRANIA = 10000
BUFFOR_BLEDNYCH_LINKOW = 0
LISTA_LINKOW = [] #lista linków korzysta się z niej w celu dodania nowych i w celu pobrania strony
DB_NAME = "bot.db"
DB_HANDLER = None
 
def main():
    global LISTA_LINKOW
    global ILOSC_LINKOW_DO_POBRANIA_NA_1_LINK
    global BUFFOR_BLEDNYCH_LINKOW
    BUFFOR_BLEDNYCH_LINKOW = ILOSC_STRON_DO_POBRANIA/len(STRONY_STARTOWE)/2
    ILOSC_LINKOW_DO_POBRANIA_NA_1_LINK = ILOSC_STRON_DO_POBRANIA/len(STRONY_STARTOWE)+BUFFOR_BLEDNYCH_LINKOW
    
    #dla każdego linku wejściowego
    for strona in STRONY_STARTOWE:
        
        #wypełniamy listę linkami
        print "\nINFO: operacja dla strony: " + strona
        print "  INFO: tworzę listę z linkami"
        LISTA_LINKOW = []#czyścimy żeby była pusta dla kolejnej strony
        LISTA_LINKOW.append(strona)#wstawiamy do listy linków pierwszy link
        wypelnijListeLinkami()#false jak za mało linków
        #print "INFO: rozmiar listy linków: "+str(len(LISTA_LINKOW))
        
        #pobieramy treść i wrzucamy do bazy
        iterator = 0
        iloscWrzuconychDoBazy = 0;
        #print "iterator: "+str(iterator)+" len(LISTA_LINKOW)"+str(len(LISTA_LINKOW))+" iloscWrzuconychDoBazy"+str(iloscWrzuconychDoBazy)+ " ILOSC_LINKOW_DO_POBRANIA_NA_1_LINK: "+str(ILOSC_LINKOW_DO_POBRANIA_NA_1_LINK)
        print "  INFO: pobieram strony i wrzucam do bazy"
        while iterator < len(LISTA_LINKOW) and iloscWrzuconychDoBazy < ILOSC_STRON_DO_POBRANIA/len(STRONY_STARTOWE):
            print ".",
            try:
                if wrzucDoBazy(iterator) == True:
                    iloscWrzuconychDoBazy +=1
                else:
                    #print "  mamy problem"
                    pass
            except: 
                pass
            iterator +=1
            
def wrzucDoBazy(indexwLiscie):
    global DB_HANDLER
    global LISTA_LINKOW
    trescStrony = pobierzTrescStronyTimeout(indexwLiscie)
    if trescStrony == False or len(trescStrony)<100: 
        return False
    trescPoParsingu = usunNoweLinie(usunZnakiPrzestankowe(usunZnacznikiHTML(trescStrony)))
    if len(trescPoParsingu)<50:
        return False
     
    try:
        "Wrzucam do bazy"
        #if "prazubr.pl" in str(LISTA_LINKOW[indexwLiscie]):
        #    print LISTA_LINKOW[indexwLiscie]+" >>>>>>>>>"+trescPoParsingu + "<<<<<<<<<<<<"
        DB_HANDLER.execute('''INSERT INTO PAGES (LINK, CONTENT) VALUES ("'''+LISTA_LINKOW[indexwLiscie]+'''", "'''+trescPoParsingu+'''")''')
        DB_CONNECTION.commit()
    except:
        print "ERROR: nie udało się wrzucić danych do bazy"
        return False
    return True


def wypelnijListeLinkami():
    global LISTA_LINKOW
    global ILOSC_LINKOW_DO_POBRANIA_NA_1_LINK
    INDEX_STRONY_Z_KTOREJ_POBIERAM_LINKI = 0
    while len(LISTA_LINKOW) < ILOSC_LINKOW_DO_POBRANIA_NA_1_LINK:
        #print LISTA_LINKOW
        #print "INFO: rozmiar listy linków: "+str(len(LISTA_LINKOW))
        if INDEX_STRONY_Z_KTOREJ_POBIERAM_LINKI > len(LISTA_LINKOW)-1:
            print "WARNING: brak wystarczająco linków"
            return False
        dodajLinkiDoListy(INDEX_STRONY_Z_KTOREJ_POBIERAM_LINKI)
        INDEX_STRONY_Z_KTOREJ_POBIERAM_LINKI +=1
    return True
        
def dodajLinkiDoListy(indexStronyzLinkami):
    global LISTA_LINKOW
    trescStrony = pobierzTrescStronyTimeout(indexStronyzLinkami)
    if trescStrony == False:
        return False
    try:
        try:
            soup = BeautifulSoup(trescStrony.decode("utf-8"))
        except:
            soup = BeautifulSoup(trescStrony.decode("cp1250"))
    except:
        print "WARNING: strony nie udało się rozkodować"
        return False
    result = False
    for linkl in soup.findAll('a'):
        link = linkl.get('href')
        if link is None or link.startswith('javascript:') or link.startswith('#') or link.startswith('android-app:')  or link.startswith('ios-app:') :
            continue;
        else:  
            result = True   
            link = link.replace(":80", "") #USUWA NUMER PORTU 80
            link_base = wyodrebnijLinkPodstawowy(LISTA_LINKOW[indexStronyzLinkami])
            ### JEŻELI LINKI ZACZYNAJĄ SIĘ OD PEŁNEGO LINKU CZYLI: //, HTTP, HTTPS
            if link.startswith('http://') or link.startswith('https://') or link.startswith('//') :
                if link.startswith('//'): # ZAMIANA // NA HTTP://
                    link = 'http:' + link
                if link not in LISTA_LINKOW:
                    LISTA_LINKOW.append(link)        
            ### JEŻELI PODANO LINK WZGLĘDNY CZYLI BRAK POCZĄTKU I NA PEWNO TEN SAM SERWER
            else:
                if link_base.endswith("/") or link.startswith("/"):
                    if link_base+link not in LISTA_LINKOW:
                        LISTA_LINKOW.append(link_base+link)
                else:
                    if link_base+"/"+link not in LISTA_LINKOW:
                        LISTA_LINKOW.append(link_base+"/"+link)
    return result
     
def wyodrebnijLinkPodstawowy(link):
    #pobieramy link bazowy w celu połączenia z nim stron lokalnych
    link_base = link[7:] # PARSOWANIE LINKU BAZOWEGO
    if link_base.count('/') > 0: # USUWA KOŃCOWE /blabla
        link_base = link_base[0:link_base.find("/")]
    if link_base.count('?') > 0: # USUWA ? I TO CO JEST ZA NIM
        link_base = link_base[0:link_base.find("?")]
    link_base = link[:7] + link_base
    return link_base 
     
def pobierzTrescStronyTimeout(indexStronyzLinkami):
    global LISTA_LINKOW
    html_url = LISTA_LINKOW[indexStronyzLinkami]
    try:
        opener = urllib2.build_opener()
        request = urllib2.Request(html_url)
        response = opener.open(request,timeout=3)
        html_content = response.read()
        return html_content
    except urllib2.HTTPError:
        #print "\n  WARNING: Podana strona nie istnieje"#+html_url
        return False      
    except:
        #print "\n  WARNING: Przekroczono czas: strona pominieta"#+html_url
        return False

def initDB():
    global DB_HANDLER
    global DB_CONNECTION
    DB_CONNECTION = sqlite3.connect(DB_NAME)
    DB_HANDLER = DB_CONNECTION.cursor()
    
def createDB():
    DB_HANDLER.execute('''DROP TABLE IF EXISTS PAGES''')
    DB_HANDLER.execute('''CREATE TABLE PAGES (ID INTEGER PRIMARY KEY AUTOINCREMENT, LINK TEXT, CONTENT TEXT)''')
    print "INFO: utworzono bazę"
class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)
def strip_tags(html):
    try:
        s = MLStripper()
        s.feed(html)
        return s.get_data()
    except: 
        return ""
def usunZnacznikiHTML(text):
    try:
        #print "Usuwam script"
        text = (re.subn(r'<(script).*?</\1>(?s)', '', text)[0])
        #print "Usuwam style"
        text = (re.subn(r'<(style).*?</\1>(?s)', '', text)[0])
        #print "Zmieniam kodowanie na utf-8 do regex'ow"
        text = text.decode('utf-8', 'ignore')
        #print "Dodaje spację przed tagiem HTML aby nie połączyło słów pomiędzy nimi"
        text = text.replace(u"<",u" <")
        #print "Usuwam tagi html"
        text = strip_tags(text)
        return text
    except: 
        return ""   
def usunZnakiPrzestankowe(text):
    try: 
        #print "Usuwanie znakow przestankowych"
        text = text.lower()
        text = re.sub(u'[^a-z0-9ąęśćżźłóćń\d\s]+', ' ', text)
        return text
    except: 
        return ""
def usunNoweLinie(text):
    try:
        #print "Usuwanie nowych linii"
        text = re.sub(u'[\t\r\n ]+', ' ', text)
        return text
    except: 
        return ""
def usunPojedynczeZnaki(text):
    try:
        #print "Usuwanie pojedynczych znakow"
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
    except: 
        return ""
    
def userHandler():
    userInput=""
    while userInput != "q":
        userInput=raw_input('Input:')
        userInput=usunNoweLinie(usunZnakiPrzestankowe(userInput.lower()))
        result = DB_HANDLER.execute('SELECT ID, LINK, CONTENT from PAGES WHERE LINK LIKE "%'+userInput+'%" OR CONTENT LIKE "%'+userInput+'%"')
        for row in result:
            print "ID: "+str(row[0])+" LINK: "+row[1]+" TREŚĆ: "+ row[2].decode("cp1250")
        print "Słowo/fraza wystąpiła w tekście " +str(len(DB_HANDLER.fetchall()))+ "razy."
    
if __name__ == '__main__':
    initDB()
    #createDB()
    #main()
    userHandler()
