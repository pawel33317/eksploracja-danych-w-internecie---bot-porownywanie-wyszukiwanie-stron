# -*- coding: cp1250 -*-
import locale,urllib2,re,sqlite3
from BeautifulSoup import BeautifulSoup
import sys
import json
import requests
sys.setrecursionlimit(100)
locale.setlocale(locale.LC_ALL, '')
from HTMLParser import HTMLParser
import numpy as np
DEBUG = True

STRONY_STARTOWE = ['https://www.facebook.com/groups/159446264116600/','http://www.bleepingcomputer.com/forums/t/616259/no-bsod-but-several-display-crashes-and-now-ctds-while-gaming-help-please/']
#STRONY_STARTOWE = []

ILOSC_STRON_DO_POBRANIA = 2
BUFFOR_BLEDNYCH_LINKOW = 0
LISTA_LINKOW = [] #lista linków korzysta się z niej w celu dodania nowych i w celu pobrania strony
DB_NAME = "bot3.db"
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
            print "."
            try:
                if wrzucDoBazy(iterator) == True:
                    iloscWrzuconychDoBazy +=1
                else:
                    #print "  mamy problem"
                    pass
            except: 
                pass
            iterator +=1
              
            #dodatkowy element z zadania 8 pobiera wypowiedzi użytkowników z kontentu strony 
            #i sprawdza wysyłając zapytanie do api jakiegoś tam czy są wesołe czy nie 
            
            
            if strona.startswith('http://www.bleepingcomputer'):
                try:
                    soup = BeautifulSoup(pobierzTrescStronyTimeout(iterator-1))
                    for akapit in soup.findAll('p'):
                        wypowiedz = akapit.getText()
                        if len(wypowiedz.strip()) < 8:
                            continue
                        print wypowiedz
                        podajCharakterZdania(wypowiedz)
                except:
                    pass 

            if strona.startswith('https://www.facebook.'):
                try:
                    soup = BeautifulSoup(pobierzTrescStronyTimeout(iterator-1).replace("<!--", "").replace("-->", ""))
                    for akapit in soup.findAll('p'):
                        try:
                            wypowiedz = akapit.getText()
                            if len(wypowiedz.strip()) < 3:
                                continue
                            print wypowiedz
                            podajCharakterZdania(wypowiedz)
                        except:
                            pass
                except:
                    pass


def podajCharakterZdania(dane):
    url = 'http://text-processing.com/api/sentiment/'
    data = dict(text=dane)
    r = requests.post(url, data=data, allow_redirects=True)
    if r.json()['probability']['neg'] >= r.json()['probability']['neutral'] and r.json()['probability']['neg'] >= r.json()['probability']['pos']:
        print "Negatywna: " + str(r.json()['probability']['neg'])
    if r.json()['probability']['pos'] >= r.json()['probability']['neutral'] and r.json()['probability']['pos'] >= r.json()['probability']['neg']:
        print "Pozytywna: " + str(r.json()['probability']['pos'])
    if r.json()['probability']['neutral'] >= r.json()['probability']['pos'] and r.json()['probability']['neutral'] >= r.json()['probability']['neg']:
        print "Neutralna: " + str(r.json()['probability']['neutral'])
    print " "

def userHandler2():
    userInput=""
    while userInput != "q":
        print 
        userInput=raw_input('Podaj słowo do sprawdzenia charakteru:')
        podajCharakterZdania(userInput);

      
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
    
    link_base = wyodrebnijLinkPodstawowy(LISTA_LINKOW[indexStronyzLinkami])
    robotsTXT = pobierzRobots(link_base)
    
    
    
    for linkl in soup.findAll('a'):
        link = linkl.get('href')
        if link is None or link.startswith('javascript:') or link.startswith('#') or link.startswith('android-app:')  or link.startswith('ios-app:') :
            continue;
        else:  
            result = True   
            link = link.replace(":80", "") #USUWA NUMER PORTU 80
            #print link_base
            ### JEŻELI LINKI ZACZYNAJĄ SIĘ OD PEŁNEGO LINKU CZYLI: //, HTTP, HTTPS
            if link.startswith('http://') or link.startswith('https://') or link.startswith('//') :
                if link.startswith('//'): # ZAMIANA // NA HTTP://
                    link = 'http:' + link
                sprawdzRobotsIdodajDoListy(robotsTXT, link);
     
            ### JEŻELI PODANO LINK WZGLĘDNY CZYLI BRAK POCZĄTKU I NA PEWNO TEN SAM SERWER
            else:
                if link_base.endswith("/") or link.startswith("/"):
                    sprawdzRobotsIdodajDoListy(robotsTXT, link_base+link)
                else:
                    sprawdzRobotsIdodajDoListy(robotsTXT, link_base+"/"+link)
    return result

def sprawdzRobotsIdodajDoListy(robotsTXT, linkStrony):
    #http://www.elektroda.pl/robots.txt
    if linkStrony not in LISTA_LINKOW:
        if robotsTXT == False:    
            LISTA_LINKOW.append(linkStrony)  
            return True
        else:
            listaNiedozwolonych = parsujRobots(robotsTXT)
            adresBezLinkuBazowego=linkStrony[len(wyodrebnijLinkPodstawowy(linkStrony)):]
            for niedozwolony in listaNiedozwolonych:
                if adresBezLinkuBazowego.startswith(niedozwolony):
                    print "   INFO: ROBOTS.TXT nie pobrano pliku: "+linkStrony
                    return False
            LISTA_LINKOW.append(linkStrony)  
            return True
              
def parsujRobots(robotsTXT):
    lista = robotsTXT.split("\n")
    #lista2 = [l for l in lista if l.startswith("Disallow")]
    listaZakazanych = []
    for l in lista:
        if l.startswith("Disallow") and len(l)>10:
            listaZakazanych.append(l[10:])
    return listaZakazanych
           
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

def pobierzRobots(linkBazowy):
    html_url = linkBazowy+"/robots.txt"
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
        
def znajdzStronyPodobne(idStrony):
    print "Szukam stron podobnych do strony o ID: "+str(idStrony)
    stronaGlownaTresc = DB_HANDLER.execute('SELECT CONTENT from PAGES WHERE ID = '+str(idStrony)).fetchone()[0]
    result = DB_HANDLER.execute('SELECT ID, LINK, CONTENT from PAGES LIMIT 100')

    listaWynikow = []
    #żeby nie iterowało z każdym razem w pętli
    stronaGlownaLista = generujListe(stronaGlownaTresc)
    
    #stronaGlownaLista = ['mama','tata','siostra','brat','dziecko']
    #aaa = ['mama','tata','blabla','oooo']
    #listaWynikow.append(podobienstwoWynik(4, 4, 4, porownajStrony(stronaGlownaLista, aaa)))
    
    #print listaWynikow[0].result
    for row in result:
        if idStrony != row[0]:
            listaWynikow.append(podobienstwoWynik(row[0], row[1], row[2][:40], porownajStrony(stronaGlownaLista, generujListe(row[2]))))
    
    listaWynikow.sort()
    limiter = 0
    for w in listaWynikow:
        print u"  ID: "+str(w.idd) + u", WSKAŹNIK: "+ str(w.result)+", LINK: "+ w.adres + ", TRESC: " + w.tresc
        limiter +=1
        if limiter > 4:
            break

    #for w in listaWynikow:
    #    print str(w.result)
    
    
def porownajStrony(listaA, listaB):
    slownik = generujSlownik(listaA, listaB)
    vectorA, vectorB = generujWektor(listaA, listaB, slownik)
    wynik = obliczWskaznikPodobienstwa(vectorA, vectorB)
    return wynik
  
def obliczWskaznikPodobienstwa(vectorA, vectorB):
    result = np.dot(vectorA,vectorB)/(np.linalg.norm(np.array(vectorA))*np.linalg.norm(np.array(vectorB)))
    #print np.linalg.norm(np.array(vectorA))
    #print np.linalg.norm(np.array(vectorB))
    #print np.dot(vectorA,vectorB)
    #print "---------"#print str(np.dot(vectorA,vectorB)) + "/////" + str(np.linalg.norm(np.array(vectorA))*np.linalg.norm(np.array(vectorB)))
    return result

def generujWektor(listaA, listaB, slownik):
    vectorA = [0.0]*len(slownik)
    ilosc_wyrazow = len(listaA)
    for word in listaA:
        if len(word) > 3:
            vectorA[slownik.index(word)] += 1.0/ilosc_wyrazow
    #print vectorA
    
    vectorB = [0.0]*len(slownik)
    ilosc_wyrazow = len(listaB)
    for word in listaB:
        if len(word) > 3:
            vectorB[slownik.index(word)] += 1.0/ilosc_wyrazow   
    #print vectorB
    return [vectorA, vectorB]


def generujListe(strona):
    lista = strona.strip().split(' ')
    #dodać wywalenie słów  len < 3
    return lista  
        
def generujSlownik(listaA, listaB):
    slownik = []
    for word in listaA:
        if len(word) > 3:
            if word not in slownik:
                slownik.append(word)
    for word in listaB:
        if len(word) > 3:
            if word not in slownik:
                slownik.append(word)
    #print slownik
    return slownik
        
class podobienstwoWynik:
    def __init__(self, idd, adres, tresc, result):
        self.idd = idd
        self.adres = adres
        self.result=result
        self.tresc=tresc
    def __lt__(self, other):
        return self.result > other.result
         
def initDebug():
    global STRONY_STARTOWE
    global ILOSC_STRON_DO_POBRANIA
    global DB_NAME
    if DEBUG:
        STRONY_STARTOWE = ['http://wykop.pl','http://www.elektroda.pl',
               'http://www.wp.pl','http://weeia.p.lodz.pl',
               'http://haks.pl/?a=5']
        ILOSC_STRON_DO_POBRANIA = 25
        DB_NAME = "bot2.db"
        
if __name__ == '__main__':
    #initDebug()
    initDB()
    if DEBUG:
        createDB()
        main()
    userHandler2()
