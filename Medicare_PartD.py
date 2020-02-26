import bs4
import requests
import re
import sys,time

##Pulls all Medicare Part D drug plans and formularies from https://q1medicare\.com
##Please set timers between iterations.

stime=time.asctime()

c1=re.compile(r'<b>(.*)</b>')#formulary plan name
c2=re.compile(r'\$\d{0,}\.\d\d')#monthly premium
c3=re.compile(r'\$\d*')#deductible
c4=re.compile(r'(Yes|No)',re.I)#gap cover
c5=re.compile(r'(Yes|No)',re.I)#$0 prem. with full LIS
c6=re.compile(r'(Preferred Generic: \$\d{0,}\.\d{0,}|Preferred Generic: \d{0,3}\%)(<br/>)?(Generic: \$\d{0,}\.\d{0,}|Preferred Brand: \$\d{0,}\.\d{0,})?(<br/>)?(Preferred Brand: \$\d{0,}\.\d{0,}|Preferred Brand: \d{0,3}\%)?<br/>(Non-Preferred Drug: \d{0,}\%|Non-Preferred Brand: \d{0,}\%|Non-Preferred Drug: \$\d{0,}\.\d{0,}|Non-Preferred Brand: \$\d{0,}\.\d{0,})(<br/>)?(Injectable Drugs: \d{0,3}\%)?<br/>(Specialty Tier: \d{0,3}\%)')
c7href=re.compile(r'href="(.*=fbtextlink?)')
href_build=re.compile(r'href=\"(https://q1medicare\.com/PartD-BrowseMedicare-2018PlanFormulary\.php\?.{0,}?sort=drugNameasc)\">.')

d_tier=re.compile(r'\d')
d_tier_descript=re.compile(r'^<td align="left">(.*)<\/td>?')
states=['AK', 'AL', 'AR', 'AS', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'GA',
        'GU', 'HI', 'IA', 'ID', 'IL', 'IN', 'IS', 'KS', 'KY', 'LA', 'MA', 'MD',
        'ME', 'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM',
        'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'PR', 'RI', 'SC', 'SD', 'TN', 'TX',
        'UT', 'VA', 'VI', 'VT', 'WA', 'WI', 'WV', 'WY']
alph_=list('qwertyuiopasdfghjklzxcvbnm')
alph_.sort()
alph=[x.capitalize() for x in alph_]
drugs=['Candesartan','Losartan','Valsartan']

arr=[]
for url_extension in states:
    print('\n\n'+url_extension+'\n\n')
    wp=requests.get('https://q1medicare.com/PartD-SearchPDPMedicare-2018PlanFinder.php?state='+url_extension+'#results')
    page=bs4.BeautifulSoup(wp.text)
    
    result=page.find_all('tr',{'valign':'middle'})#all formularys are in valign=middle
    for r_iter in result:  #begins iteration over each formulary on the page
        r=[]
        for i in range(len(r_iter.select('td'))):   #iterates over each column of each formulary (2nd for loop)
            if i == 0:
                mo1=c1.search(str(r_iter.select('td')[i]))
                formul_title=str(mo1.group(1))
                r.append(formul_title)
                print(formul_title)
            if i==1:
                mo2=c2.search(str(r_iter.select('td')[i]))
                premium=str(mo2.group())
                r.append(premium)
                print(premium)
            if i==2:
                mo3=c3.search(str(r_iter.select('td')[i]))
                deductible=str(mo3.group())
                r.append(deductible)
                print(deductible)
            if i==3:
                mo4=c4.search(str(r_iter.select('td')[i]))
                g_coverage=str(mo4.group())
                r.append(g_coverage)
                print(g_coverage)
            if i==4:
                mo5=c5.search(str(r_iter.select('td')[i]))
                F_LIS=str(mo5.group())
                r.append(F_LIS)
                print(F_LIS)
            if i==5:
                mo6=c6.search(str(r_iter.select('td')[i]))
                cp_ci=str(mo6.groups())
                r.append(cp_ci)
                print(cp_ci)
            if i==6:                                    #on the 7th iteration (counter=6) we begin the drug listing process
                mo7=c7href.search(str(r_iter.select('td')[i]))
                mo7_refined=re.sub('amp;','',mo7.group(1))

                drug_wp=requests.get(mo7_refined)     #loads drug page within row of formulary (usually 3k-5k) for the purpose of parsing all drug pages (A-Z)
                drug_page=bs4.BeautifulSoup(drug_wp.text)    #loads new drug page into html text

                
                div_href=drug_page.find_all(class_='formattoolpagerow')  #establish all letter hrefs
                hrefs=div_href[3]
                cleaned_hrefs=re.sub('amp;','',str(hrefs))

                print('building href list to scan for plan ' + formul_title)

                
                all_pages=list(href_build.findall(cleaned_hrefs))
                all_letter_pages=all_pages.copy()
                A=list(all_pages[1])
                A[73]='A'
                a=''.join(A)
                all_letter_pages.insert(0,a)

                for drug in drugs:
                    for url in all_letter_pages:
                        if url[73]!=drug[0]:   #filters redundency of searching for drugs in wrong alphabetical URL
                            continue
                            #print function if nothing found
                        #print function here if found
                        drug_wp=requests.get(url)     #loads drug page within row of formulary (usually 3k-5k)
                        drug_page=bs4.BeautifulSoup(drug_wp.text)                    
                
                        drug_result=drug_page.find_all('tr',{'valign':'middle'})  #gets table rows on new drug page
                        for row in drug_result:   #begin iteration over all drug results for drug plan
                            drug_name=row.select('td')[0]
                            tier=row.select('td')[1]
                            tier_description=row.select('td')[2]
                        
                            d_search=re.compile(r'style="text-align:left;">(%s[^\-]{0,})<a class='%drug,re.I)  #CURRENT REGEX ONLY ELIMINATES DUPLICATES THAT CONTAIN A (-) DASH IN THEM
                            if d_search.search(str(drug_name)):          #IT WILL NOT REMOVE DUPLICATES FOR DRUGS OF DIFFERENT APPLICATION (ie. ointment vs tablets)
                                print('found ' +d_search.search(str(row)).group(1) + ' in ' + url)
                                r.append(d_search.search(str(row)).group(1))                                      # example 1:  ACYCLOVIR 200 MG/5 ML SUSP (tier4)  vs  ACYCLOVIR 200 MG CAPSULE (tier1)
                                r.append(d_tier.search(str(tier)).group())
                                r.append(d_tier_descript.search(str(tier_description)).group(1))
                            else:
                                continue
                
        arr.append(r)

ftime=time.asctime()
print('All done! =)  Start time is ' + stime + '\nFinish time is ' + ftime)
