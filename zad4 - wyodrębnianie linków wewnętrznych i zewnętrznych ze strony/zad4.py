# -*- coding: cp1250 -*-

#################################################################################################
#####REKURENCYJNE WYSZUKIWANIE LINKÓW NA STRONIE Z PODZIAŁEM NA LINKI LOKALNE I ZEWNĘTRZNE#######
#################################################################################################


import locale,urllib2,re,urllib
import numpy as np
locale.setlocale(locale.LC_ALL, '')
import time,socket
from BeautifulSoup import BeautifulSoup

###STRONA STARTOWA
html_url_start = "http://weeia.p.lodz.pl"
### RZĄD REKURENCJI POSZUKIWAŃ
N = 2;


def getPageContentWithTimeout(html_url):
    try:
        opener = urllib2.build_opener()
        request = urllib2.Request(html_url)
        response = opener.open(request,timeout=3)
        html_content = response.read()
        return html_content
    except urllib2.HTTPError:
        print "  !!! Podana strona nie istnieje: "+html_url
        return False      
    except:
        #print "  !!! Przekroczono czas -> strona pominieta: "+html_url
        return False

### DOSTAJE 2 LISTY Z LINKAMI WEWNĘTRZNE I ZEWNĘTRZNE
### POBIERA Z DANEJ LISTY LKNKÓW WSZYSTKIE LINKI KTÓRE SĄ NA STRONIE
def getLinksFromHtml(currentInternal, currentExternal):
    newInternal = [] # LISTA Z LNIKAMI WEWNĘTRZNYMI BĘDĄ ONE WYCIĄGNIĘTE ZE STRON DO KTÓRYCH LINKI OTRZYMAŁĄ FUNKCJA
    newExternal = [] # LISTA Z LNIKAMI ZEWNĘTRZNYMI BĘDĄ ONE WYCIĄGNIĘTE ZE STRON DO KTÓRYCH LINKI OTRZYMAŁĄ FUNKCJA
    currentAll  = [] # WSZYSTKIE LINKI KTÓRE OTRZYMAŁA FUNKCJA, NIE MA POTRZEBY ABY BYŁ TU PODZIAŁ NA ZEWNĘTRZNE I WEWNĘTRZNE BO TO NASTĄPI PÓŹNIEJ

    ### ŁĄCZENIE LIST W JEDNĄ NA POTRZEBY PRZETWARZANIA
    currentAll.extend(currentInternal)
    currentAll.extend(currentExternal)

    ### DLA KAŻDEGO OTRZYMANGEO LINKU POBIERA STRONĘ I WYCIĄGA Z NIEJ LINKI
    for html_url in currentAll:
        print "  Parsowanie linku: " + html_url

        ### POBRANIE CONTENTU STRONY Z TIMEOUTEM JAK COŚ NIE TAK TO OLEWA DANĄ STRONĘ
        html_content = getPageContentWithTimeout(html_url)
        if html_content == False:
            continue

        ### ROZBIJA CONTENT STRONY NA STRUKTURE HTML
        soup = BeautifulSoup(html_content)

        ### ZNAJDUJE HREF ZE ZNACZNIKÓW A
        for linkl in soup.findAll('a'):
            link = linkl.get('href')
            if link is None or link.startswith('javascript:') or link.startswith('#') or link.startswith('android-app:')  or link.startswith('ios-app:') :
                continue;
            else:
                link = link.replace(":80", "") #USUWA NUMER PORTU 80
           
                ### JEŻELI ZACZYNAJĄ SIĘ OD PEŁNEGO LINKU CZYLI: //, HTTP, HTTPS
                if link.startswith('http://') or link.startswith('https://') or link.startswith('//') :
                    if link.startswith('//'): # ZAMIANA // NA HTTP://
                        link = 'http:' + link
                    link_to_ip = link[7:] # PARSOWANIE LINKU DO SPRAWDZENIA IP
                    
                    if link_to_ip.count('/') > 0: # USUWA KOŃCOWE /
                        link_to_ip = link_to_ip[0:link_to_ip.find("/")]
                    if link_to_ip.count('?') > 0: # USUWA ? I TO CO JEST ZA NIM
                        link_to_ip = link_to_ip[0:link_to_ip.find("?")]

                    try: ### DODAJE DO ODPOWIEDNIEJ LISTY LINK
                        if current_server_ip == socket.gethostbyname(link_to_ip.strip()):
                            if link not in newInternal:
                                newInternal.append(link)
                        else:
                            if link not in newExternal:
                                newExternal.append(link)
                    except:
                        print "  !!! Nie mozna pobrac IP dla strony: "+link_to_ip.strip()

                        
                ### JEŻELI PODANO LINK WZGLĘDNY CZYLI BRAK POCZĄTKU I NA PEWNO TEN SAM SERWER
                else:
                    try:
                        if html_url_start.startswith(html_url):
                            if html_url.endswith("/") or link.startswith("/"):
                                if html_url+link not in newInternal:
                                    newInternal.append(html_url+link)
                            else:
                                if html_url+"/"+link not in newInternal:
                                    newInternal.append(html_url+"/"+link)
                        else:
                            if html_url.endswith("/") or link.startswith("/"):
                                if html_url+link not in newExternal:
                                    newExternal.append(html_url+link)
                            else:
                                if html_url+"/"+link not in newExternal:
                                    newExternal.append(html_url+"/"+link)
                    except:
                        print "  !!! Nie mozna pobrac IP dla strony: "+link_to_ip.strip()
    return (newInternal, newExternal)


### IP SERWERA
current_server_ip = socket.gethostbyname(html_url_start[7:].strip())
print "IP serwera strony: ", current_server_ip
### LISTY Z LINKAMI WEWNĘTRZNYMI I ZEWNĘTRZNYMI
wewList = []
zewList = []
### INICJACJA PUSTYCH LIST STARTOWYCH Z LINKAMI JEDNA MA PIERWSZY LINK DO STRONY OD KTÓREJ SIĘ WSZYSTKO ZACZNYA
wewList.append([])
zewList.append([])
wewList[0].append(html_url_start)


### WYKONUJE REKURENCYJNE POBIERANIA
for i in range(N):
    print "Parsowanie strony rzedu: "+str(i+1)
    ### LISTA 2 WYMIAROWA ZARIERA W KAŻDYM INDEKSIE LINKI Z POSZUKIWAAŃ DANEGO RZĄDU NP zewList[1][5] ZAWIERA 6-STY LINK Z DRUGIEGO RZĘDU POSZUKIWAŃ
    wewList.append([])
    zewList.append([])
    wewList[i+1], zewList[i+1] = getLinksFromHtml(wewList[i], zewList[i])


### ŁĄCZENIE NA 1 LISTĘ WEWNĘTRZNĄ I JEDNĄ ZEWNĘTRZNĄ WSZYSTKICH RZĘDÓW POSZUKIWAŃ
commonWewList = []
commonZewList = []
for lista in wewList:
    commonWewList.extend(lista)
for lista in zewList:
    commonZewList.extend(lista)


### ZAPIS DO PLIKU
f = open('wew.txt', 'w')
f.write("\n".join(commonWewList).encode("utf8"))
f.close()
f = open('zew.txt', 'w')
f.write("\n".join(commonZewList).encode("utf8"))
f.close()
