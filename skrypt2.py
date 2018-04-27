# -*- coding: utf-8 -*- 

from random import randint
import sys
#from importlib import reload
#reload(sys)  # Reload does the trick!
#sys.setdefaultencoding('UTF8')
from time import localtime, strftime
import io
import re
import pysolr
import hashlib
import json
#from datetime import datetime


uri_pattern = "uri:(.+)\sl"


patterns = ["(?:\s[Dd]ata\swprowadzenia:\s)?[12][09][901][0-9]-[012][0-9]-[0123][0-9]\s[12]?[0-9]:[0-5][0-9](?::[0-5][0-9])?",  # "rok-miesiąc-dzień godzina:minuta"
            "(?:[123]?[0-9]\.[12]?[0-9]\.|[12]?[0-9]\.[123]?[0-9]\.)[12][09][901][0-9]\sr\.", # "dzień.miesiąc.rok " lub "miesiąc.dzień.rok "
            "(?:[Zz]|[Dd]o|[Ww])\s?(?:dni)?[au]?\s?[\s012][1-9]\.[\s01]?[1-9]\.[12][09][901][0-9]\sr\.",    # dzień.miesiąc.rok 
            "[123]?[0-9]\s(?:[sS]ty|[lL]ut|[mM]ar|[kK]wi|[mM]aj|[cC]ze|[lL]ip|[sS]ie|[wW]rz|[Pp]a[zź]|[Ll]is|[Gg]ru)\s\d{4}",   # "dzień miesiąc rok" 
            
            "\s?[0123][1-9]\.\s[0123][1-9]\.\s[12][09][901][0-9]",  # "dzień. miesiąc. rok" lub "miesiąc. dzień. rok"
            "(?:[Mm]iesi[aą]c:\s)?(?:1[0-2]|[1-9])(?:-[12][09][901][0-9])", # "miesiąc-rok"
            
            "(?:[123]?[0-9]?[\n\s](?:[Ss]tycz(?:e[nń]|nia|niu)|[Ll]ut(?:y|ego|ym)|[Mm]ar(?:zec|ca|cu)|[Kk]wie(?:cie[nń]|tnia|tniu)|[Mm]aj[au]?|[Cc]erw(?:iec|c[au])|[Ll]ip(?:iec|ca|cu)|[Ss]ierp(?:ie[nń]|ni[au])|[Ww]rze(?:sie[nń]|[sś]ni[au])|[Pp]a[zź]dziernik[au]?|[Ll]istopad(?:a|dzie)?|[Gg]rud(?:zie[nń]|nia|niu))\s[12][09][901][0-9])",  # "dzień miesiąc rok"
            "[Ww]?\s[12][09][901][0-9]\sroku",  # " rok "
            "[Ww]?\s?[12][09][901][0-9]\sr\.?", # "rok "
            "\s?\([12][09][901][0-9]\)",    # "(rok)"
            #"(?:[Zz]\sdnia\s)?[12]?[0-9]\s(?:[sS]tycznia|[lL]utego|[mM]arca|[Kk]wietnia|[Mm]aja|[Cc]zerwca|[Ll]ipca|[Ss]ierpnia|[Ww]rze[sś]nia|[Pp]a[zź]dziernika|[Ll]istopada|[Gg]rudnia)?\s[12][09][901][0-9]\sroku",
            #"(?:[Dd]o\sdnia|[Ww]\sdniu)?\s?[012][0-9]\s(?:[sS]tycznia|[lL]utego|[mM]arca|[Kk]wietnia|[Mm]aja|[Cc]zerwca|[Ll]ipca|[Ss]ierpnia|[Ww]rze[sś]nia|[Pp]a[zź]dziernika|[Ll]istopada|[Gg]rudnia)\s[12][09][901][0-9]\sr\.(?:\sdo\sgodz\.\s[012][0-9]:?[0-5][0-9](?:\.|\s)?)?",
            "\s-\s[12][09][901][0-9]",  # " - rok"
            "(?:[Nn]a)?\s[Rr]ok\s[12][09][901][0-9](?:\si\slata)?", # " rok"
            
            "(?:[Pp]ocz[aą]wszy\sod\s(?:I|II|III|IV)kwarta[lł]u\skalendarzowego\s)?[12][0-9][901][0-9]\sroku?", # "rok "
            "(?:[Ww]|[Zz])?\s[19\s][0-9]\sroku?",   # " rok" ale podany dwucyfrowo
            "[12][09][901][0-9]\s(?:rok|r\.)",  # "rok "
            #"(?:[Ww]\smiesi[aą]cu\s)?(?:[Ss]tyczniu|[Ll]utym|[Mm]arcu|[Kk]wietniu|[Mm]aju|[Cc]zerwcu|[Ll]ipcu|[Ss]ierpniu|[Ww]rze[sś]niu|[Pp]a[zź]dzierniku|[Ll]istopadzie|[Gg]rudniu)\s[12][09][901][0-9]",
            #"[1-31]\.(?:0?[1-9]|1[0-2])\.[12][09][901][0-9]\s?r\.",
            #"bytes:\d+\n.*(?:\n*|.*)+df6fa1abb58549287111ba8d776733e9"]
]

#updated_patterns = ["([0-3]?[0-9][\.\-\s/][012]?[0-9][\.\-\s/][12][0-9]{3}|[012]?[0-9][\.\-\s/][0-3]?[0-9][\.\-\s/][12][0-9]{3})\s[012][0-9]:[0-5][0-9]:[0-5][0-9]"]
            
#file = open("pl.2014_52.raw", encoding="utf8")            
file = io.open("teksty.txt", encoding="utf8")
#file = io.open("tekst.txt", encoding="utf8")

text = ""
            
try:
    #for i in range(1000):
        #text += file.readline()
        #print (text.encode("utf8"))
    text = file.read()
finally:
    file.close()

#print (text)    
#sys.exit()    
text_without_whitespaces = text[33:]

texts = re.split(r"\ndf6fa1abb58549287111ba8d776733e9\s", text_without_whitespaces)

#sys.exit()
dates = [[]] * len(texts)
#print (dates)
#sys.exit()
#dates = [[]]

#dates = []
k = 0
uris = []

#print (dates)
#print (dates[0])
#dates[0] = "TEST"
#print (dates[0].append("TEST"))
#print (dates[2])
#print (dates)
#sys.exit()
#dates.append("TEST2")
#dates[0] = ["pierwsza data", "druga data"]
#print (dates[0])
#print (dates[1])
#print (dates)
#print (len(texts))
#print (len(dates))
#print (texts)
#sys.exit()

for text in texts:  # text drugi 
    text_index = texts.index(text)  # 1
    #print (text_index)
    #print (text_index)
    for pattern in patterns:    # pierwszy pattern
        #print (patterns.index(pattern))
        temp = re.findall(pattern, text)        # 
        #print (temp)
        if len(temp) != 0 and len(dates[text_index]) == 0: #and len(temp) > len(dates[text_index]):
            dates[text_index] = temp
            #print (text_index)
            #print (temp)
            #print (pattern)
            #for t in temp:
                #print (t)
                #dates[text_index].append(t)
            #print (dates[text_index])
        #else:
        #    dates[text_index].append(temp)
    #print (dates[0])
    #sys.exit()
#print (dates)
#print (len(texts))
#print (texts[0].encode("utf-8"))
#print (dates[1])
#print (dates[8])
#sys.exit()
'''
for x in range(len(patterns) - 1):
    for y in range(len(texts)):
        temp = re.findall(patterns[x], texts[y])
        #print temp
        #print type(temp)
        #sys.exit()
        if len(temp) != 0:
            for t in range(len(temp)):
                dates[y].append(temp[t])
'''
#print (len(dates))
#sys.exit()
'''        
        if dates[y] == "":
            temp = re.findall(patterns[x], texts[y])
            #print temp
            if len(temp) == 0:
                dates[y] = ""
            else:
                dates[y] = temp
'''
#print patterns[12]
#temp_one = re.findall(patterns[16], texts[0])
#print (temp_one)
#print (dates)
#sys.exit()

for text in texts:
    uri = re.findall(uri_pattern, text)
    uris.append(uri[0])
    text = text.replace("\n\n", "\n")
    text = text.replace("  ", ' ')
#print (uris)
'''
for u in uris:
    if "zlotowskie" in u:
        index_zlotowskie = uris.index(u)
        print ("SĄ ZŁOTOWSKIE!")
        print (index_zlotowskie)
        print (dates[index_zlotowskie])

count = 0        
print (len(texts))      # teksty.txt mają 1 milion linijek tekstu, znalezionych tekstów = 49423
for m in dates:
    if len(m) != 0:
        count += 1
print (count)           # znalezionych dat = 8118 (lepszy wynik o ok. 600 dat, niż wcześniej) 
'''              
#if "zlotowskie" in uris[0]:
    #print ("JEST")
#print (len(texts))
#sys.exit()    
'''    
for m in range(len(dates)):
    if len(dates[m]) > 0:
        dates[m] = dates[m][0]
'''                

formatted_dates = [[]]  * len(dates)
#print (dates)
#print (dates[0])
#print (len(texts[0]))
#sys.exit()

for date in dates:
    index = dates.index(date)
    #print (date)
    #print (index)
    for d in date:
        #print (d)
        index_date = date.index(d)
        #print (index_date)
        if d != "":
            #print (d)
            temp_d = re.sub(r"([Ss]tycz(e[nń]|nia|niu))", '1', d)
            temp_d = re.sub(r"([Ll]ut(y|ego|ym))", '2', d)
            temp_d = re.sub(r"([Mm]ar(zec|ca|cu))", '3', d)
            temp_d = re.sub(r"([Kk]wie(cie[nń]|tnia|tniu))", '4', d)
            temp_d = re.sub(r"([Mm]aj(|a|u))", '5', d)
            temp_d = re.sub(r"([Cc]erw(iec|ca|cu))", '6', d)
            temp_d = re.sub(r"([Ll]ip(iec|ca|cu))", '7', d)
            temp_d = re.sub(r"([Ss]ierp(ie[nń]|nia|niu))", '8', d)
            temp_d = re.sub(r"([Ww]rze(sie[nń]|[sś]nia|[sś]niu))", '9', d)
            temp_d = re.sub(r"([Pp]a[zź]dziernik(|a|u))", "10", d)
            temp_d = re.sub(r"([Ll]istopad(|a|zie))", "11", d)
            temp_d = re.sub(r"([Gg]rud(zie[nń]|nia|niu))", "12", d)
            
            temp_d = temp_d.replace("Sty", "1")
            temp_d = temp_d.replace("sty", "1")
            temp_d = temp_d.replace("Lut", "2")
            temp_d = temp_d.replace("lut", "2")
            temp_d = temp_d.replace("Mar", "3")
            temp_d = temp_d.replace("mar", "3")
            temp_d = temp_d.replace("Kwi", "4")
            temp_d = temp_d.replace("kwi", "4")
            temp_d = temp_d.replace("Maj", "5")
            temp_d = temp_d.replace("maj", "5")
            temp_d = temp_d.replace("Cze", "6")
            #print (temp_d)
            temp_d = temp_d.replace("cze", "6")
            temp_d = temp_d.replace("Lip", "7")
            temp_d = temp_d.replace("lip", "7")
            temp_d = temp_d.replace("Sie", "8")
            temp_d = temp_d.replace("sie", "8")
            temp_d = temp_d.replace("Wrz", "9")
            temp_d = temp_d.replace("wrz", "9")
            temp_d = temp_d.replace("Paz", "10")
            #temp_d = temp_d.replace(u"Paź", "10")
            temp_d = temp_d.replace("Paź", "10")
            temp_d = temp_d.replace("paz", "10")
            #temp_d = temp_d.replace(u"paź", "10")
            temp_d = temp_d.replace("paź", "10")
            temp_d = temp_d.replace("Lis", "11")
            temp_d = temp_d.replace("lis", "11")
            temp_d = temp_d.replace("Gru", "12")
            temp_d = temp_d.replace("gru", "12")
            #print (temp_d)
            #print (dates[0][0])
            #formatted_dates[index].append(d) #.append(re.findall(r"[\d]+", d))
            #print (index)
            #print (index_date)
            #print (dates[1][0])
            #print (temp_d)
            dates[index][index_date] = temp_d
            
#print (dates)
#sys.exit()
            
for date_string in dates:#formatted_dates:
    numbers_only = []
    #print (date_string)
    max_len = 0
    for d_s in date_string:
        #print (d_s)
        numbers_only.append(re.findall(r"[\d]+", d_s))
        #date_string[date_string.index()]
        #print (numbers_only)
        #sys.exit()
    for number_only in numbers_only:
        #print (number_only)
        #print (len(number_only))
        #sys.exit()
        if len(number_only) > max_len:
            max_len = len(number_only)
            index_numbers_only = numbers_only.index(number_only)
            #print (index_numbers_only)
            #sys.exit()
    #print (numbers_only)
    if len(date_string) > 0:
        temp_date_string = numbers_only[index_numbers_only]
        #print (temp_date_string)
        #sys.exit()
        #print (date_string)
        index_formatted_dates = dates.index(date_string)
        #formatted_dates[index_formatted_dates] = date_string
        dates[index_formatted_dates] = temp_date_string
#print (date_string)
#print (formatted_dates)
        

            
#print (dates)
#sys.exit()
#print (dates[0])
#print (dates[1])
#for test in dates:
#    for ji in dates:
#        if ji != test:
#            print ("NIE WSZYSTKIE SĄ RÓWNE!")
    
#print (len(dates[0]))
#print (type(dates[0]))
#print (dates[0])
#dates = dates[0]
#print (len(dates))
#print (type(dates))
#sys.exit()

#print (formatted_dates)
'''
max = 0
ind = 0
for f_d in formatted_dates:
    #print (f_d)
    for f in f_d:
        #print (f)
        if len(f) > 1:
            for elements in f:
                #print (elements)
                if len(elements) == 4:
                    if max < int(elements):
                        max = int(elements)
                        ind = f_d.index(f)
#print (ind)
formatted_dates[0] = formatted_dates[0][ind]
#print (formatted_dates[0])                    
'''
#print (dates)
#sys.exit()    
    
i = 0
indexes_to_remove = []
for formatted_date in dates:#formatted_dates:
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
    if temp_day == "" or int(temp_day) > 31 or int(temp_day) == 0:
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
    
    #formatted_dates[i] = formatted_date
    dates[i] = formatted_date
    i += 1

#print (len(dates))
#print (dates)
#sys.exit()    
#print (uris)  
#sys.exit()
for index_to_remove in indexes_to_remove:
    #formatted_dates[index_to_remove] = ""
    dates[index_to_remove] = ""
    texts[index_to_remove] = ""
    uris[index_to_remove] = ""
#print (dates)
#print (uris)
#print (uris[0])
#print (uris[0][0]) 
#print (type(uris[0]))   
#sys.exit()    
    
final_texts, final_formatted_dates, final_uris = [], [], []
size_of_texts = len(texts)
for x in range(size_of_texts):
    if texts[x] != "":
        final_texts.append(texts[x])
    if dates[x] != "":#formatted_dates[x] != "":
        final_formatted_dates.append(dates[x])#formatted_dates[x])
    if uris[x] != "":
        final_uris.append(uris[x])#[0])

#print (len(final_texts))        
#print (final_formatted_dates)
#print (final_uris)
#sys.exit()
#print (len(final_texts))
#print (len(final_formatted_dates))
#print (len(final_uris))


solr = pysolr.Solr("http://150.254.78.133:8983/solr/isi")
#sys.exit()
#data = [{}]
data = []
hashes = []
#print (len(final_texts))
#sys.exit()
final_texts_length = len(final_texts)

for f in range(final_texts_length):
    #print (final_formatted_dates[f][0:4])
    #print (final_formatted_dates[f][5:7])
    #print (final_formatted_dates[f][8:10])
    #print (final_formatted_dates[f][17:19])
    duration_start = final_formatted_dates[f][0:11] + "00:00:00Z"
    if duration_start[6:7] == "4" and  duration_start[8:10] == "31":
        f += 1
        duration_start = final_formatted_dates[f][0:11] + "00:00:00Z"
    #duration_start = ""
    #print (len(final_uris))
    #print (len(final_texts))
    #sys.exit()
    #temp_hash = hashlib.md5(final_uris[f].encode() + str(len(final_texts[f]) + len(final_uris[f]) + randint(0, 100000)).encode()).hexdigest()
    temp_hash = hashlib.md5(final_uris[f].encode() + str(len(final_texts[f]) + len(final_uris[f])).encode()).hexdigest()
    

    #print (temp_hash)
    hashes.append(temp_hash)
    hash_length = int(len(temp_hash) / 2.5)

    #iid = str(int(temp_hash[:hash_length], 16))
    iid = int(temp_hash[:hash_length], 36)
    print (iid)
    #sys.exit()
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
    
    #print (duration_start)
    #print (duration_end)
    
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
    #sys.exit()
    #formatted_dates[f][:11] + "00:00:00Z" #final_formatted_dates[f]
        #print formatted_dates[f][0:11]
        #print duration_start
        #sys.exit()
        
    #final_texts[f] = re.findall(r"", final_texts[f])
    #final_texts[f] = list(re.findall(r"bytes:\d+\n((.|\n)*)", final_texts[f]))
    if iid == 424552607074071657:
        print (final_texts[f])
        #print ("\n")
        #print (re.findall(r"bytes:\d+\n((.|\n)*)", final_texts[f]))
        #sys.exit()
        #final_texts[f] = str(re.findall(r"bytes:\d+\n((.|\n)*)", final_texts[f]))#[0])#[0]
    else:
        final_texts[f] = list(re.findall(r"bytes:\d+\n((.|\n)*)", final_texts[f])[0])[0]
    #print (final_texts[f])
    #sys.exit()
    #print (final_texts[f])
    #sys.exit()
    content = final_texts[f]
    url = final_uris[f]
    #print (final_uris)
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
    print (str((f/final_texts_length) * 100) + '%') 
    
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
    #print (content)
    #print (lang)
    #print (iid)
    #print (url)
    #print (added)
    #sys.exit()
    #solr.add(data)
    #sys.exit()
    #print (data[0])
    #sys.exit()
#print (len(hashes))         # 7608
#print (len(set(hashes)))    # 7547
#sys.exit()    
#print (len(data))
#sys.exit()   

#txt = re.findall(r"bytes:[\d]+\n((.|\n)+)", content)
#print (type(txt))

'''
new_file = io.open("one_text.txt", "w+", encoding="utf8")
new_file.write(list(txt[0])[0])
new_file.close()
'''
#sys.exit()
#print (re.findall(r"bytes:[\d]+\n((.|\n)+)", content))
#print (duration_start)
#print (duration_end)
#sys.exit()

if len(hashes) == len(set(hashes)): 
    print ("Nie ma powtórek iid.")
    #sys.exit()
    solr.add(data)
else:
    print ("Są powtórki iid! Przerwano dodawanie")
    print (len(hashes))
    print (len(set(hashes)))
    solr.add(data)
