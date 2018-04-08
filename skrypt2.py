# -*- coding: utf-8 -*- 

from random import randint
import sys
#from importlib import reload
reload(sys)  # Reload does the trick!
sys.setdefaultencoding('UTF8')
from time import localtime, strftime
import io
import re
import pysolr
import hashlib
import json
#from datetime import datetime


uri_pattern = "uri:(.+)\sl"

patterns = [
            "[123]?[0-9]\s(?:[sS]ty|[lL]ut|[mM]ar|[kK]wi|[mM]aj|[cC]ze|[lL]ip|[sS]ie|[wW]rz|[Pp]a[zź]|[Ll]is|[Gg]ru)\s\d{4}", 
            "[Ww]?\s[12][09][901][0-9]\sroku",
            "\s?[0123][1-9]\.\s[0123][1-9]\.\s[12][09][901][0-9]",
            "[Ww]?\s?[12][09][901][0-9]\sr\.?",
            "\s?\([12][09][901][0-9]\)",
            "(?:[Zz]|[Dd]o|[Ww])\s?(?:dni)?[au]?\s?[\s012][1-9]\.[\s01]?[1-9]\.[12][09][901][0-9]\sr\.", "(?:[Zz]\sdnia\s)?[12]?[0-9]\s(?:[sS]tycznia|[lL]utego|[mM]arca|[Kk]wietnia|[Mm]aja|[Cc]zerwca|[Ll]ipca|[Ss]ierpnia|[Ww]rze[sś]nia|[Pp]a[zź]dziernika|[Ll]istopada|[Gg]rudnia)?\s[12][09][901][0-9]\sroku","(?:[Dd]o\sdnia|[Ww]\sdniu)?\s?[012][0-9]\s(?:[sS]tycznia|[lL]utego|[mM]arca|[Kk]wietnia|[Mm]aja|[Cc]zerwca|[Ll]ipca|[Ss]ierpnia|[Ww]rze[sś]nia|[Pp]a[zź]dziernika|[Ll]istopada|[Gg]rudnia)\s[12][09][901][0-9]\sr\.(?:\sdo\sgodz\.\s[012][0-9]:?[0-5][0-9](?:\.|\s)?)?",
            "\s-\s[12][09][901][0-9]",
            "(?:[Nn]a)?\s[Rr]ok\s[12][09][901][0-9](?:\si\slata)?",
            "(?:\s[Dd]ata\swprowadzenia:\s)?[12][09][901][0-9]-[012][0-9]-[0123][0-9]\s[12]?[0-9]:[0-5][0-9](?::[0-5][0-9])?",
            "(?:[Pp]ocz[aą]wszy\sod\s(?:I|II|III|IV)kwarta[lł]u\skalendarzowego\s)?[12][0-9][901][0-9]\sroku?",
            "(?:[123]?[0-9]\.[12]?[0-9]\.|[12]?[0-9][123]?[0-9]\.)[12][09][901][0-9]\sr\.",
            "(?:[Ss]tycz(?:e[nń]|nia|niu)|[Ll]ut(?:y|ego|ym)|[Mm]ar(?:zec|ca|cu)|[Kk]wie(?:cie[nń]|tnia|tniu)|[Mm]aj[au]?|[Cc]erw(?:iec|c[au])|[Ll]ip(?:iec|ca|cu)|[Ss]ierp(?:ie[nń]|ni[au])|[Ww]rze(?:sie[nń]|[sś]ni[au])|[Pp]a[zź]dziernik[au]?|[Ll]istopad(?:a|dzie)?|[Gg]rud(?:zie[nń]|nia|niu))\s[12][09][901][0-9]",
            "(?:[Mm]iesi[aą]c:\s)?(?:1[0-2]|[1-9])(?:-[12][09][901][0-9])",
            "(?:[Ww]|[Zz])?\s[19\s][0-9]\sroku?",
            "[12][09][901][0-9]\s(?:rok|r\.)",
            "(?:[Ww]\smiesi[aą]cu\s)?(?:[Ss]tyczniu|[Ll]utym|[Mm]arcu|[Kk]wietniu|[Mm]aju|[Cc]zerwcu|[Ll]ipcu|[Ss]ierpniu|[Ww]rze[sś]niu|[Pp]a[zź]dzierniku|[Ll]istopadzie|[Gg]rudniu)\s[12][09][901][0-9]",
            "[1-31]\.(?:0?[1-9]|1[0-2])\.[12][09][901][0-9]\s?r\.",
            "bytes:\d+\n.*(?:\n*|.*)+df6fa1abb58549287111ba8d776733e9"]
            
#file = open("pl.2014_52.raw", encoding="utf8")            
file = io.open("teksty.txt", encoding="utf8")

text = ""
            
try:
    #for i in range(10000):
        #text += file.readline()
        #print (text.encode("utf8"))
    text = file.read()
finally:
    file.close()

#print (text)    
#sys.exit()    
text_without_whitespaces = text[33:]

texts = re.split(r"\ndf6fa1abb58549287111ba8d776733e9\s", text_without_whitespaces)


dates = [""] * len(texts)

k = 0
uris = []

for x in range(len(patterns) - 1):
    for y in range(len(texts)):
        if dates[y] == "":
            temp = re.findall(patterns[x], texts[y])
            if len(temp) == 0:
                dates[y] = ""
            else:
                dates[y] = temp

for text in texts:
    uri = re.findall(uri_pattern, text)
    uris.append(uri)
    text = text.replace("\n\n", "\n")
    text = text.replace("  ", ' ')

for m in range(len(dates)):
    if len(dates[m]) > 0:
        dates[m] = dates[m][0]
                

formatted_dates = []


for date in dates:
    if date != "":
        date = re.sub(r"([Ss]tycz(e[nń]|nia|niu))", '1', date)
        date = re.sub(r"([Ll]ut(y|ego|ym))", '2', date)
        date = re.sub(r"([Mm]ar(zec|ca|cu))", '3', date)
        date = re.sub(r"([Kk]wie(cie[nń]|tnia|tniu))", '4', date)
        date = re.sub(r"([Mm]aj(|a|u))", '5', date)
        date = re.sub(r"([Cc]erw(iec|ca|cu))", '6', date)
        date = re.sub(r"([Ll]ip(iec|ca|cu))", '7', date)
        date = re.sub(r"([Ss]ierp(ie[nń]|nia|niu))", '8', date)
        date = re.sub(r"([Ww]rze(sie[nń]|[sś]nia|[sś]niu))", '9', date)
        date = re.sub(r"([Pp]a[zź]dziernik(|a|u))", "10", date)
        date = re.sub(r"([Ll]istopad(|a|zie))", "11", date)
        date = re.sub(r"([Gg]rud(zie[nń]|nia|niu))", "12", date)
        
        date = date.replace("Sty", "1")
        date = date.replace("sty", "1")
        date = date.replace("Lut", "2")
        date = date.replace("lut", "2")
        date = date.replace("Mar", "3")
        date = date.replace("mar", "3")
        date = date.replace("Kwi", "4")
        date = date.replace("kwi", "4")
        date = date.replace("Maj", "5")
        date = date.replace("maj", "5")
        date = date.replace("Cze", "6")
        date = date.replace("cze", "6")
        date = date.replace("Lip", "7")
        date = date.replace("lip", "7")
        date = date.replace("Sie", "8")
        date = date.replace("sie", "8")
        date = date.replace("Wrz", "9")
        date = date.replace("wrz", "9")
        date = date.replace("Paz", "10")
        date = date.replace(u"Paź", "10")
        date = date.replace("paz", "10")
        date = date.replace(u"paź", "10")
        date = date.replace("Lis", "11")
        date = date.replace("lis", "11")
        date = date.replace("Gru", "12")
        date = date.replace("gru", "12")
        
        formatted_dates.append(re.findall(r"[\d]+", date))
    else:
        formatted_dates.append(date)
    

i = 0
indexes_to_remove = []
for formatted_date in formatted_dates:
    temp_year, temp_month, temp_day, temp_hour, temp_minute, temp_second = "", "", "", "", "", ""
    if len(formatted_date) > 0:
        if len(formatted_date[0]) == 4:
            temp_year = formatted_date[0]
            for d in range(len(formatted_date)):
                if d == 1:
                    temp_month = formatted_date[1]
                elif d == 2:
                    temp_day = formatted_date[2]
                elif d == 3:
                    temp_hour = formatted_date[3]
                elif d == 4:
                    temp_minute = formatted_date[4]
                elif d == 5:
                    temp_second = formatted_date[5]
        elif len(formatted_date[-1]) == 4:
            temp_year = formatted_date[-1]
            for d in range(len(formatted_date)):
                if d == len(formatted_date) - 2:
                    temp_month = formatted_date[-2]
                elif d == len(formatted_date) - 3:
                    temp_day = formatted_date[-3]
                elif d == len(formatted_date) - 4:
                    temp_second = formatted_date[-4]
                elif d == len(formatted_date) - 5:
                    temp_minute = formatted_date[-5]
                elif d == len(formatted_date) - 6:
                    temp_hour = formatted_date[-6]
    if temp_year == "" or int(temp_year) < 1997 or int(temp_year) > 2018:
        indexes_to_remove.append(i)
    if temp_month == "" or int(temp_month) > 12:
        temp_month = "01"
    if temp_day == "" or int(temp_day) > 31:
        temp_day = "01"
    if temp_hour == "" or int(temp_hour) > 23:
        temp_hour = "23"
    if temp_minute == "" or int(temp_minute) > 59:
        temp_minute = "59"
    if temp_second == "" or int(temp_second) > 59:
        temp_second = "59"
    
    if len(temp_month) == 1:
        temp_month = '0' + temp_month
    if len(temp_day) == 1:
        temp_day = '0' + temp_day
        
    formatted_date = "{0}-{1}-{2}T{3}:{4}:{5}Z".format(temp_year, temp_month, temp_day, temp_hour, temp_minute, temp_second)
    
    formatted_dates[i] = formatted_date
    i += 1
  
for index_to_remove in indexes_to_remove:
    formatted_dates[index_to_remove] = ""
    texts[index_to_remove] = ""
    uris[index_to_remove] = ""

final_texts, final_formatted_dates, final_uris = [], [], []
size_of_texts = len(texts)
for x in range(size_of_texts):
    if texts[x] != "":
        final_texts.append(texts[x])
    if formatted_dates[x] != "":
        final_formatted_dates.append(formatted_dates[x])
    if uris[x] != "":
        final_uris.append(uris[x][0])
    
#print (final_formatted_dates)
#print (len(final_texts))
#print (len(final_formatted_dates))
#print (len(final_uris))


solr = pysolr.Solr("http://150.254.78.133:8983/solr/isi")

#data = [{}]
data = []
hashes = []
for f in range(len(final_texts)):
    duration_start = final_formatted_dates[f][0:11] + "00:00:00Z"
    if duration_start[6:7] == "4" and  duration_start[8:10] == "31":
        f += 1
        duration_start = final_formatted_dates[f][0:11] + "00:00:00Z"
    #duration_start = ""
    #print (len(final_uris))
    #print (len(final_texts))
    #sys.exit()
    temp_hash = hashlib.md5(final_uris[f].encode() + str(len(final_texts[f]) + len(final_uris[f]) + randint(0, 100000)).encode()).hexdigest()
    print (temp_hash)
    hashes.append(temp_hash)
    hash_length = int(len(temp_hash) / 3)

    #iid = str(int(temp_hash[:hash_length], 16))
    iid = int(temp_hash[:hash_length], 36)
    #print (iid)
    #iid = int(temp_hash[:hash_length], 36)[:len(iid)]
    #print (iid)
    #iid = int(temp_hash, 36)
    #print (type(iid))
    #print (type(1<<31))
    #sys.exit()
    id = str(iid) + "-1"
    #print (iid)
    #print (id)
    #sys.exit()
    #id = iid
    lang = "pl"
    lname = "commoncrawl"
    duration_end = final_formatted_dates[f]
    print (duration_end)
    
    #if final_formatted_dates[f][11] == '2' and final_formatted_dates[f][12] == '3' and final_formatted_dates[f][14] == '5' and final_formatted_dates[f][15] == '9' and final_formatted_dates[f][17] == '5' and final_formatted_dates[f][18] == '9':
    
        #final_formatted_dates[f][11] = '0'
        #final_formatted_dates[f][12] = '0'
        #final_formatted_dates[f][14] = '0'
        #final_formatted_dates[f][15] = '0'
        #final_formatted_dates[f][17] = '0'
        #final_formatted_dates[f][18] = '0'
        #print final_formatted_dates[f]
    #print (final_formatted_dates[0][0:11] + "00:00:00Z")
    
        
    #print (duration_start[5:7])
    #print (duration_start)
    #sys.exit()
    #formatted_dates[f][:11] + "00:00:00Z" #final_formatted_dates[f]
        #print formatted_dates[f][0:11]
        #print duration_start
        #sys.exit()
    content = final_texts[f]
    url = final_uris[f]
    #added = datetime.now().isoformat(timespec="seconds")
    #added = str(added) + 'Z'
    added = strftime("%Y-%m-%dT%H:%M:%S", localtime()) 
    added = str(added) + 'Z'
    
    data.append({
        "id": id,
        "iid": iid,
        "content": content,
        "duration_start": duration_start,
        "duration_end": duration_end,
        "url": url,
        "lname": lname,
        "lang": lang,
        "added": added
        })
    '''
    data[0] = {
        "iid": iid,
        "id": id,
        "lname": lname,
        "duration_start": duration_start,
        "duration_end": duration_end,
        "content": content,
        "lang": lang,
        "url": url,
        "added": added
        }
    '''
    #print (len(hashes))
    #print (len(set(hashes)))
    #print (type(data[0]))
    #print (iid)
    #print (id)
    #print (lname)
    #print (duration_start)
    #print (duration_end)
    #if f != 0:
    #if f < 100:
        #print (content.encode('utf8'))
    #break
    #print (lang)
    #print (iid)
    #print (url)
    #print (added)
    #sys.exit()
    #solr.add(data)
    #sys.exit()
    #print (data[0])
    #sys.exit()
print (len(hashes))         # 7608
print (len(set(hashes)))    # 7547
#sys.exit()    
#print (len(data))
#sys.exit()   
if len(hashes) == len(set(hashes)): 
    print ("TUTAJ")
    solr.add(data)
else:
    print ("Są powtórki iid! Przerwano dodawanie")
