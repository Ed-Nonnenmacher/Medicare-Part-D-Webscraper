from selenium import webdriver
import bs4
import requests
import re
import sys,time

stime=time.asctime()

state_reg=re.compile(r'(Region \d{1,2})')
c1=re.compile(r'<b>(.*)</b>')#formulary plan name
c11=re.compile(r'<td align="center">(S\d{4}-\d{3})<br\/>')#plan name code
c2=re.compile(r'\$\d{0,}\.\d\d')#monthly premium
c3=re.compile(r'(\$[0-9]*)<\/td>')#deductible
c4=re.compile(r'(Yes|No)',re.I)#gap cover
c5=re.compile(r'(No Gap Coverage|Many Generics|Some Generics|All Generics)')#$0 prem. with full LIS
c6=re.compile(r'<td align="center">(Basic|Enhanced)</td>')
c7href=re.compile(r'<a href="(.*Reg=\d{2}\w{2}.*formulary=\d{8}.*contractId=S\d{4}.*planId=\d{3}.*)" target="_blank"')
href_build=re.compile(r'href=\"(https://q1medicare\.com/PartD-BrowseMedicare-2009PlanFormulary\.php\?letter=\w&formulary=\d{8}&contractId=S\d{4}&planId=\d{3}&segmentId=0&zipCountyCode=&ccountyName=Statewide&stateReg=\d{2}\w{2}&zip=&planType=&mode=state&prAuth=&stepTh=&qtyLmt=&tier1=&tier2=&tier3=&tier4=&tier5=&tier6=&sort=drugNameasc)')
regions=re.compile(r'href="(.*=1000)')

d_tier=re.compile(r'\d')
d_tier_descript=re.compile(r'<td align="left">(Tier? \d? ?-? ?)?(.*)<\/td>')
states=['AK', 'AL', 'AR', 'AS', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'GA',
        'GU', 'HI', 'IA', 'ID', 'IL', 'IN', 'IS', 'KS', 'KY', 'LA', 'MA', 'MD',
        'ME', 'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM',
        'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'PR', 'RI', 'SC', 'SD', 'TN', 'TX',
        'UT', 'VA', 'VI', 'VT', 'WA', 'WI', 'WV', 'WY']
alph_=list('qwertyuiopasdfghjklzxcvbnm')
alph_.sort()
alph=[x.capitalize() for x in alph_]
drugs=['Lipitor','Crestor']

arr=[]
intro=requests.get('https://q1medicare.com/PartD-Medicare-PartD-Overview-byRegion.php')
state_page=bs4.BeautifulSoup(intro.text)
state_rows=state_page.find_all('tr')


for state in state_rows:
    print('\n\n\n'+str(state)+'\n\n\n')
    state1=state.select('td')
    state_row=regions.findall(str(state1))
    for st in state_row:
        st_refined=re.sub('amp;','',st)
        print(st_refined)
        wp=requests.get(st_refined)
        page=bs4.BeautifulSoup(wp.text)
        years=page.find_all(class_='textred')
        for year in years:
            if year.text=='2014':  #this decides what year will be selected
                wp1=requests.get(year.get('href'))
                page1=bs4.BeautifulSoup(wp1.text)
                print('in ' + year.text)
                med_plans=page1.find_all(class_='tbllight')
                for plan in med_plans:
                    r=[]
                    cells=list(plan)
                    r.append(c1.search(str(plan)).group(1)+' '+cells[6].text)
                    print(c1.search(str(plan)).group(1))
                    r.append(state_reg.search(str(state)).group(1))
                    r.append(c2.search(str(plan)).group())
                    print(c2.search(str(plan)).group())
                    r.append(c3.search(str(plan)).group(1))
                    print(c3.search(str(plan)).group(1))
                    r.append(c4.search(str(plan)).group())
                    print(c4.search(str(plan)).group())
                    r.append(c5.search(str(plan)).group(1))
                    print(c5.search(str(plan)).group(1))
                    r.append(c6.search(str(plan)).group(1))
                    print(c6.search(str(plan)).group(1))
                    links=plan.find_all('a',{'target':'_blank'})[6]
                    drug_wp=requests.get(re.sub('amp;','',c7href.search(str(links)).group(1)))
                    drug_page=bs4.BeautifulSoup(drug_wp.text)
                    
                    div_href=drug_page.find_all(class_='formattoolpagerow')  #establish all letter hrefs
                    hrefs=div_href[3]
                    cleaned_hrefs=re.sub('amp;','',str(hrefs))
                    print('building href list to scan formulary for drugs')
                    all_pages=list(href_build.findall(cleaned_hrefs))
                    all_letter_pages=all_pages.copy()
                    A=list(all_pages[1])
                    A[73]='A'
                    a=''.join(A)
                    all_letter_pages.insert(0,a)

                    for drug in drugs:
                        for url in all_letter_pages:
                            if url[73]!=drug[0]:   #filters redundency of searching for drugs in wrong alphabetical URL
                                print('scanning...')
                                continue
                            print('match!')
                            drug_wp1=requests.get(url)     #loads drug page within row of formulary (usually 3k-5k)
                            drug_page1=bs4.BeautifulSoup(drug_wp1.text)
                            drug_result=drug_page1.find_all('tr',{'valign':'middle'})  #gets table rows on new drug page
                            for row in drug_result:   #begin iteration over all drug results for drug plan
                                drug_name=row.select('td')[0]
                                tier=row.select('td')[1]
                                tier_description=row.select('td')[2]
                                d_search=re.compile(r'style=\"text-align:left;\">(%s[^\-]{0,})<a class='%drug,re.I) #CURRENT REGEX ONLY ELIMINATES DUPLICATES THAT CONTAIN A (-) DASH IN THEM
                                if d_search.search(str(drug_name)): #IT WILL NOT REMOVE DUPLICATES FOR DRUGS OF DIFFERENT APPLICATION (ie. ointment vs tablets)
                                    print('found ' +d_search.search(str(row)).group(1) + ' in ' + url)
                                    r.append(d_search.search(str(row)).group(1))
                                    r.append(d_tier.search(str(tier)).group())
                                    if d_tier_descript.search(str(tier_description)).group(2):
                                        r.append(d_tier_descript.search(str(tier_description)).group(2))
                                        print(tier_description)
                                        print('group 2 tier desc')
                                        continue
                                    r.append(d_tier_descript.search(str(tier_description)).group(1))
                                    print('group 1 tier desc')
                                    print(tier_description)
                                else:
                                    continue
                    arr.append(r)
    


                '''             
                        drug_result=drug_page.find_all('tr',{'valign':'middle'})  #gets table rows on new drug page
                        for row in drug_result:   #begin iteration over all drug results for drug plan
                            drug_name=row.select('td')[0]
                            tier=row.select('td')[1]
                            tier_description=row.select('td')[2]
                        
                            d_search=re.compile(r'style=\"text-align:left;\">(%s[^\-]{0,})<a class='%drug,re.I)  #CURRENT REGEX ONLY ELIMINATES DUPLICATES THAT CONTAIN A (-) DASH IN THEM
                            if d_search.search(str(drug_name)):          #IT WILL NOT REMOVE DUPLICATES FOR DRUGS OF DIFFERENT APPLICATION (ie. ointment vs tablets)
                                print('found ' +d_search.search(str(row)).group(1) + ' in ' + url)
                                r.append(d_search.search(str(row)).group(1))                                      # example 1:  ACYCLOVIR 200 MG/5 ML SUSP (tier4)  vs  ACYCLOVIR 200 MG CAPSULE (tier1)
                                r.append(d_tier.search(str(tier)).group())
                                r.append(d_tier_descript.search(str(tier_description)).group(1))
                            else:
                                continue
                
        arr.append(r)

ftime=time.asctime()
print('All done! =)  Start time is ' + stime + '\nFinish time is ' + ftime)'''
