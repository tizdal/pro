# encoding=utf8
import os, sys
reload(sys)
sys.setdefaultencoding('utf8')

import mysql.connector
import requests
import csv
import textwrap3
import re
from  bs4 import BeautifulSoup
from termcolor import colored
from playsound import playsound
from dateutil import parser




headers = {
    'User-Agent':	"Mozilla/5.0 (X11; Ubuntu; Linu…) Gecko/20100101 Firefox/69.0"
}

login_data = {
    'op': '1',
    'login': 'contact@alhayat-tenders.com',
    'pass_w': 'benya644'
}


with requests.Session() as s:
    subscribe = s.post("http://www.baosem.com/v4/fr/index.php",data=login_data, headers=headers)
print("connection established")

# open files
Log = open ('Log.txt','a')   
Tout_file = open ('Tout.csv','a') 
Appel_offre_file = open ('Appel_offre.csv','a')
Prorogation_file = open ('Prorogation.csv','a')
Resultats_file = open ('Resultats.csv','a')
Resiliation_file = open ('Resiliation.csv','a')
Rectification_file = open ('Rectification.csv','a')
Prequalification_file = open ('Prequalification.csv','a')
Addendum_file = open ('Addendum.csv','a')
Annulation_file = open ('Annulation.csv','a')
Infructueux_file = open ('Infructueux.csv','a')
information_file = open ('information.csv','a')
preselection_file = open ('preselection.csv','a')
Consultation_restreinte_file = open ('Consultation_restreinte.csv','a')
Appel_manifestation_interet_file = open ('Appel_manifestation_interet.csv','a')
Invitation_soumissionner_file = open ('Invitation_soumissionner.csv','a')
Resultat_relance_file = open ('Resultat_relance.csv','a')
Avenant_file = open ('Avenant.csv','a')
GRE_A_GRE_APRES_CONSULTATION_file = open ('GRE_A_GRE_APRES_CONSULTATION.csv','a')

#  connect to my database
connection = mysql.connector.connect(
    host = "127.0.0.1",
    user = "root",
    passwd = "AlhayatManager",
    database="testdb"
)

cursor = connection.cursor()


# regulaire expression seting up
re_price = re.compile(r"(( |\()*([\d])+( |,|\.|\))*)+(( |\()*(\$|€|(DA)|(Da)|(EUROS)|(dinars)|(Dinars)|(Dinars Algériens)|USD|DZD)( |\))*)+")
re_phone = re.compile(r"(\d|\(|\)| |\.|-|\+){9,20}")
re_NCahier = re.compile(r"[Nn°º]+[ 0-9A-Z.\-+_]+(\/[A-Z °0-9\-+_.]+){1,}\/[a-zA-Z°0-9\-+_.]*")
re_email = re.compile(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+")
re_nember = re.compile(r"(([\d])+( |,|\.)*)+")



for p_id in range (15843, 15844):
    p_id = str(p_id)
    page_url = 'http://www.baosem.com/v4/baosem2/appels/consulter.php?id='+p_id
    page = s.get(page_url)
    soup = BeautifulSoup(page.content, 'html5lib')

    
    Titre = soup.find('h1', class_='titre').text
    if not Titre.strip() :
        print colored("{}".format(p_id)),colored(' not fond','red')
    
    else:
        paragraphs = []
        price_liste = [0]
        phone = []
        NCahier = []
        email = []
        restreint = ''
        national = ''
        international =''
        ouvert = ''
        var = '1'
        info = soup.find("div", {"id": "descriptif-ao"}).p

        for x in info:
            paragraphs.append(str(x))
        while '<br/>' in paragraphs:
            paragraphs.remove('<br/>')
            # finde type d'offre
        for line in paragraphs:     
            if re.search('national', line, re.IGNORECASE) and var == '1': 
                national = 'national'
                if re.search('international', line, re.IGNORECASE):
                    international = 'international'
                if re.search('ouvert', line, re.IGNORECASE):
                    ouvert = 'ouvert'
                if re.search('restreint', line, re.IGNORECASE):
                    restreint = 'restreint'
                var = '0'
            
            if re_price.search(line):
                number = re_nember.search(re_price.search(line).group(0)).group(0)
                number = number.replace(" ", "")
                number = number.replace(",", ".")
                if "." not in number:
                    number = number + ".00"
                number = number.replace(".", "")
                number = number [:-2]           #delet two lettres to write the price in DA
                if number =='':
                    number = 0
                number = int(number)
                if "€" in re_price.search(line).group(0):  #convert euro to DA
                    number = number * 135 
                elif "EUROS" in re_price.search(line).group(0):  #convert euro to DA
                    number = number * 135 
                elif "$" in re_price.search(line).group(0):  #convert dollar to DA
                    number = number * 120
                elif "USD" in re_price.search(line).group(0):  #convert dollar to DA
                    number = number * 120
                if 999999999 < number :
                    number = 0
                price_liste.append(number) 

            if re_phone.search(line):
                a = re_phone.search(line).group(0)
                numbers = sum(c.isdigit() for c in a)
                if 9 <= numbers <=  12:
                    phone.append(a)  

            if re_NCahier.search(line):
                NCahier.append(re_NCahier.search(line).group(0)) 

            if re_email.search(line):
                email.append(re_email.search(line).group(0))   

        price = max(price_liste)
        price_liste = [0]
        email = ";   ".join(str(x) for x in email)
        phone = ";   ".join(str(x) for x in phone)
        NCahier = ";   ".join(str(x) for x in NCahier)
        Contenu = soup.find("div", {"id": "descriptif-ao"}).p.text
        detail = soup.find('dl', class_='details')
        lign = detail.find_all('dd')
        Reference = lign[1].text
        Type = lign[2].text
        Annonceur = lign[3].text
        Categorie = lign[4].text
        Date = parser.parse(lign[0].text.split(':')[1]) 

                
        if restreint and international and national: 
            offre = 'national et internationl restreint'
        elif international =='' and restreint and national:
            offre = 'national restreint'
        elif international and national and ouvert:
            offre = 'national et internationl ouvert'
        elif national and restreint == ''and ouvert and international == '':
            offre = 'national ouvert'
        else:
            offre = ''  


#	save data
    	
        record_to_insert = (p_id,Date,offre, NCahier, textwrap3.dedent(Annonceur).strip(), textwrap3.dedent(Categorie).strip(), textwrap3.dedent(Titre).strip(), textwrap3.dedent(Contenu).strip(),phone ,email ,price,page_url)
    	
        csv.writer(Tout_file).writerow(record_to_insert)
        insert_query= """ INSERT INTO Tout (p_id,Dat, type_offre, n_cahier, annonceur, categorie, titre, contenu, telephone, email, prix, link) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""  
        cursor.execute(insert_query, record_to_insert)
        connection.commit()


        if textwrap3.dedent(Type).strip() == "Avis d'appel d'offres":
            csv.writer(Appel_offre_file).writerow(record_to_insert)
            insert_query= """ INSERT INTO Appel_Offer (p_id,Dat, type_offre, n_cahier, annonceur, categorie, titre, contenu, telephone, email, prix, link) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""  
            cursor.execute(insert_query, record_to_insert) 
            print ("page add successfully Avis d'appel d'offres")
            connection.commit()

        elif textwrap3.dedent(Type).strip() == "Avis de prorogation de délai":
            csv.writer(Prorogation_file).writerow(record_to_insert)
            insert_query= """ INSERT INTO Prorogation (p_id,Dat, type_offre, n_cahier, annonceur, categorie, titre, contenu, telephone, email, prix, link) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""    
            cursor.execute(insert_query, record_to_insert) 
            print ('page add successfully Avis de prorogation de délai')
            connection.commit()

        elif textwrap3.dedent(Type).strip() == "Résultats":
            csv.writer(Resultats_file).writerow(record_to_insert)
            insert_query= """ INSERT INTO Resultats (p_id,Dat, type_offre, n_cahier, annonceur, categorie, titre, contenu, telephone, email, prix, link) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""     
            cursor.execute(insert_query, record_to_insert) 
            print ('page add successfully Resultats')
            connection.commit()

        elif textwrap3.dedent(Type).strip() == "Avis de résiliation":
            csv.writer(Resiliation_file).writerow(record_to_insert)
            insert_query= """ INSERT INTO Resiliation (p_id,Dat, type_offre, n_cahier, annonceur, categorie, titre, contenu, telephone, email, prix, link) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""     
            cursor.execute(insert_query, record_to_insert) 
            print ('page add successfully Avis de Resiliation')
            connection.commit()

        elif textwrap3.dedent(Type).strip() == "Réctificatif":
            csv.writer(Rectification_file).writerow(record_to_insert)
            insert_query= """ INSERT INTO Rectification (p_id,Dat, type_offre, n_cahier, annonceur, categorie, titre, contenu, telephone, email, prix, link) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""     
            cursor.execute(insert_query, record_to_insert) 
            print ('page add successfully Réctificatif')
            connection.commit()

        elif textwrap3.dedent(Type).strip() == "Avis de préqualification":
            csv.writer(Prequalification_file).writerow(record_to_insert)
            insert_query= """ INSERT INTO Prequalification (p_id,Dat, type_offre, n_cahier, annonceur, categorie, titre, contenu, telephone, email, prix, link) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""     
            cursor.execute(insert_query, record_to_insert) 
            print ('page add successfully Avis de Prequalification')
            connection.commit()

        elif textwrap3.dedent(Type).strip() == "Addendum":
            csv.writer(Addendum_file).writerow(record_to_insert)
            insert_query= """ INSERT INTO Addendum (p_id,Dat, type_offre, n_cahier, annonceur, categorie, titre, contenu, telephone, email, prix, link) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""     
            cursor.execute(insert_query, record_to_insert) 
            print ('page add successfully Addendum')
            connection.commit()

        elif textwrap3.dedent(Type).strip() == "Annulation":
            csv.writer(Annulation_file).writerow(record_to_insert)
            insert_query= """ INSERT INTO Annulation (p_id,Dat, type_offre, n_cahier, annonceur, categorie, titre, contenu, telephone, email, prix, link) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""     
            cursor.execute(insert_query, record_to_insert) 
            print ('page add successfully Annulation')
            connection.commit()

        elif textwrap3.dedent(Type).strip() == "Infructueux":
            csv.writer(Infructueux_file).writerow(record_to_insert)
            insert_query= """ INSERT INTO Infructueux (p_id,Dat, type_offre, n_cahier, annonceur, categorie, titre, contenu, telephone, email, prix, link) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""     
            cursor.execute(insert_query, record_to_insert) 
            print ('page add successfully Infructueux')
            connection.commit()

        elif textwrap3.dedent(Type).strip() == "Avis d'information":
            csv.writer(information_file).writerow(record_to_insert)
            insert_query= """ INSERT INTO information (p_id,Dat, type_offre, n_cahier, annonceur, categorie, titre, contenu, telephone, email, prix, link) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""     
            cursor.execute(insert_query, record_to_insert) 
            print ("page add successfully Avis d'information")
            connection.commit()

        elif textwrap3.dedent(Type).strip() == "Avis de présélection":
            csv.writer(preselection_file).writerow(record_to_insert)
            insert_query= """ INSERT INTO preselection (p_id,Dat, type_offre, n_cahier, annonceur, categorie, titre, contenu, telephone, email, prix, link) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""     
            cursor.execute(insert_query, record_to_insert) 
            print ("page add successfully Avis de présélection")
            connection.commit()

        elif textwrap3.dedent(Type).strip() == "Consultation restreinte":
            csv.writer(Consultation_restreinte_file).writerow(record_to_insert)
            insert_query= """ INSERT INTO Consultation_restreinte (p_id,Dat, type_offre, n_cahier, annonceur, categorie, titre, contenu, telephone, email, prix, link) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""     
            cursor.execute(insert_query, record_to_insert) 
            print ("page add successfully Consultation restreinte")
            connection.commit()

        elif textwrap3.dedent(Type).strip() == "Appel à manifestation d'interet":
            csv.writer(Appel_manifestation_interet_file).writerow(record_to_insert)
            insert_query= """ INSERT INTO Appel_manifestation_interet (p_id,Dat, type_offre, n_cahier, annonceur, categorie, titre, contenu, telephone, email, prix, link) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""     
            cursor.execute(insert_query, record_to_insert) 
            print ("page add successfully Appel à manifestation d'interet")
            connection.commit()

        elif textwrap3.dedent(Type).strip() == "Invitation a soumissionner":
            csv.writer(Invitation_soumissionner_file).writerow(record_to_insert)
            insert_query= """ INSERT INTO Invitation_soumissionner (p_id,Dat, type_offre, n_cahier, annonceur, categorie, titre, contenu, telephone, email, prix, link) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""     
            cursor.execute(insert_query, record_to_insert) 
            print ("page add successfully Invitation a soumissionner")
            connection.commit()

        elif textwrap3.dedent(Type).strip() == "Résultats et relance":
            csv.writer(Resultat_relance_file).writerow(record_to_insert)
            insert_query= """ INSERT INTO Resultat_relance (p_id,Dat, type_offre, n_cahier, annonceur, categorie, titre, contenu, telephone, email, prix, link) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""     
            cursor.execute(insert_query, record_to_insert) 
            print ("page add successfully Résultats et relance")
            connection.commit()

        elif textwrap3.dedent(Type).strip() == "Avenant":
            csv.writer(Avenant_file).writerow(record_to_insert)
            insert_query= """ INSERT INTO Avenant (p_id,Dat, type_offre, n_cahier, annonceur, categorie, titre, contenu, telephone, email, prix, link) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""     
            cursor.execute(insert_query, record_to_insert) 
            print ("page add successfully Avenant")
            connection.commit()

        elif textwrap3.dedent(Type).strip() == "GRE A GRE APRES CONSULTATION ":
            csv.writer(GRE_A_GRE_APRES_CONSULTATION_file).writerow(record_to_insert)
            insert_query= """ INSERT INTO GRE_A_GRE_APRES_CONSULTATION (p_id,Dat, type_offre, n_cahier, annonceur, categorie, titre, contenu, telephone, email, prix, link) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""     
            cursor.execute(insert_query, record_to_insert) 
            print ("page add successfully GRE_A_GRE_APRES_CONSULTATION")
            connection.commit()

        else :
            Log.write(p_id)
            Log.write(" no existing table for this page \n")            
            playsound('audio.mp3')
        
        print(p_id)
N_page_vide = 1
print colored("Nember of missed pages is : {}".format(N_page_vide),'red')



if(connection):
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")

Log.close()
Tout_file.close()
Appel_offre_file.close()
Prorogation_file.close()
Resultats_file.close()
Resiliation_file.close()
Rectification_file.close()
Prequalification_file.close()
Addendum_file.close()
Annulation_file.close()
Infructueux_file.close()
information_file.close()
preselection_file.close()
Consultation_restreinte_file.close()
Appel_manifestation_interet_file.close()
Invitation_soumissionner_file.close()
Resultat_relance_file.close()
Avenant_file.close()
GRE_A_GRE_APRES_CONSULTATION_file.close()

