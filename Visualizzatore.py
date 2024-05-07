# Versione 23-04-2024

# esportare in pickle l'agenda dal sw programmazione


import streamlit as st
from streamlit_folium import folium_static
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import time, timedelta, datetime, date
import math
import xlrd
import folium
import openrouteservice
import pickle
from utils import persistence_ab as pe
from io import BytesIO
import xlsxwriter
import random

st.set_page_config(page_title="Planner interventi", layout='wide')

client = openrouteservice.Client(key='5b3ce3597851110001cf6248d1d5a3c164ef475d8ae776eeb594fda6')
utente = st.sidebar.selectbox('User:',['Seleziona',
                                       'Valentina',
                                       'Giorgia',
                                       'Denise',
                                       'Simona Porro',
                                       'Simona Lavezzo'
                                       ])
if utente=='Seleziona':
    st.stop()

cred = st.sidebar.file_uploader('credenziali')
if not cred:
    st.stop()
credenziali=pd.read_excel(cred)


username = credenziali.Dati.iloc[0]
token = credenziali.Dati.iloc[1]
repository_name  = credenziali.Dati.iloc[2]
file_path  = credenziali.Dati.iloc[3]
file_path_note_valentina = credenziali.Dati.iloc[4]
file_path_note_giorgia = credenziali.Dati.iloc[5]
file_path_note_denise = credenziali.Dati.iloc[6]
file_path_note_simonap = credenziali.Dati.iloc[7]
file_path_note_simonal = credenziali.Dati.iloc[8]

path_note_git = {
    'Valentina':file_path_note_valentina,
    'Giorgia':file_path_note_giorgia,
    'Denise':file_path_note_denise,
    'Simona Porro':file_path_note_simonap,
    'Simona Lavezzo':file_path_note_simonal
}


coordinate_exera = (11.594276, 44.817830)

operatori = [
 'JOLLY',
 'SQUADRA1',
 'SQUADRA2',
 'SQUADRA3',
 'FURLATTI STEFANO',
 'SACCENTI FABRIZIO',
 'ALTIERI NICO',
 'FARINA MIRKO',
 'BERTAZZINI ALBIERI NICHOLAS',
 'BERGOSSI MATTIA',
 'BINELLI RICCARDO',
 'GOVONI ENRICO',
 'FABBRI MATTEO',
 'CESARI UMBERTO',
 'PASQUALI NICOLA',
 'OMEROVIC ESAD',
 'FRANCESCHINI ANDREA',
 'AGUIARI STEFANO',
 'MALAGUTTI FILIPPO',
 'BARALDI CLAUDIO'
 ]


headsx, headcx, headdx, headlogo = st.columns([1,1,1,6])
with headsx:
    placeholder = st.empty()
with headcx:
    placeholder2 = st.empty()
with headdx:
    placeholder3 =  st.empty()


col1, col2 = st.columns([4,1])
with col1:
    #st.title('Visualizzazione programma di lavoro')
    pass

with col2:
    #st.image('https://github.com/alebelluco/Test_EX/blob/main/exera_logo.png?raw=True')
    pass

layout  = {'Layout_select':['Check','Cliente','Sito','N_op','Op_vincolo','Indirizzo Sito','IstruzioniOperative','orari','Servizio','Periodicita','SitoTerritoriale','Citta',
                            'Durata_stimata','ID','lat','lng','date_range','Mensile'],

        'Layout_no_dup':['Cliente','Sito','N_op','Op_vincolo','Indirizzo Sito','IstruzioniOperative','orari','Servizio','Periodicita','SitoTerritoriale','Citta',
                            'Durata_stimata','ID','lat','lng','Target_range','Mensile'],


           'Layout_agenda':['Check','Cliente','Sito','N_op','Op_vincolo','Indirizzo Sito','IstruzioniOperative','orari','Servizio','Periodicita','SitoTerritoriale','Citta',
                            'Durata_stimata','ID','lat','lng','Operatore','date_range','Mensile'],

            'Layout_agenda_work':['Durata_stimata','Cliente','Sito','Servizio','Periodicita','Operatore','lat','lng','Data','Mensile'],

            'Agenda_edit' : ['IstruzioniOperative','Ordine_intervento','Durata_viaggio','Arrivo_da_precedente','Inizio','Durata_stimata','Fine','Cliente','Sito','Servizio','Periodicita','Operatore','lat','lng','Data','ID'],
                            
            'Agenda_esporta' : ['Data','Inizio','Fine','Durata_stimata','IstruzioniOperative','Cliente','Sito','Indirizzo Sito', 'Servizio','Operatore'] ,

            'Agenda_completa' : ['Operatore','Inizio','Fine','Durata_stimata','IstruzioniOperative','Cliente','Sito','Indirizzo Sito', 'Servizio'],

            'Scacchiera' : ['Durata_viaggio','Inizio','Fine','Durata_stimata','Cliente' ,'Indirizzo Sito' ,'IstruzioniOperative', 'Servizio'],

            'Refresh' : ['ID', 'Confronto','key']  ,   

            'Mappa'  : ['Check','Cliente','Durata_stimata', 'Servizio','Sito','N_op','Op_vincolo','Indirizzo Sito','IstruzioniOperative','orari','Periodicita','SitoTerritoriale','Citta',
                            'ID','lat','lng','Operatore','date_range','Mensile']      
                                                        
                            }

tab4, tab5, tab6, tab7= st.tabs(['Assegna interventi','Agende', 'Esporta agenda', 'Mappa pianificati'])

with tab4:

    #vincolo_nop = visualizzazione[['ID','N_op','Op_vincolo']]
    #vincolo_nop = vincolo_nop.drop_duplicates()

    percorso_altri = st.sidebar.file_uploader("Caricare altri siti")
    if not percorso_altri:
        st.stop()
    altri_siti=pd.read_csv(percorso_altri)
    altri_siti = altri_siti.drop_duplicates()

    altri_siti['SitoTerritoriale']=np.where(altri_siti['SitoTerritoriale'].astype(str)=='nan','ND',altri_siti['SitoTerritoriale'])

    siti_unici = altri_siti['SitoTerritoriale'].unique()
    
    
    #scelta_giorno = st.date_input('Inserire data da pianificare').day

    if 'altri_siti' not in st.session_state: 
        try:
            status_agenda = pe.retrieve_file(username, token,repository_name, file_path)
            altri_siti['Eliminare']=False
            for i in range(len(altri_siti)):
                id = str(altri_siti.ID.iloc[i])
                
                for k in range(len(status_agenda)):
                    id_agenda = str(status_agenda.ID.iloc[k])
                    if id == id_agenda:
                        altri_siti.Eliminare.iloc[i] = True       
            altri_siti = altri_siti[altri_siti.Eliminare == False]
            st.session_state.altri_siti = altri_siti.copy()
        
        except:
            st.session_state.altri_siti = altri_siti.copy()

        st.session_state.altri_siti['Durata_stimata'] = st.session_state.altri_siti['Durata_stimata'].str.replace(',','.')
        st.session_state.altri_siti['lat'] = st.session_state.altri_siti['lat'].str.replace(',','.')
        st.session_state.altri_siti['lng'] = st.session_state.altri_siti['lng'].str.replace(',','.')
        st.session_state.altri_siti['Durata_stimata'] = st.session_state.altri_siti['Durata_stimata'].astype(float)
        st.session_state.altri_siti['key_distanze'] = st.session_state.altri_siti['Cliente']+" | "+st.session_state.altri_siti['Indirizzo Sito']
        #st.session_state.siti_unici = st.session_state.altri_siti['SitoTerritoriale'].unique()
        st.session_state.altri_siti['no_spazi'] = [stringa.replace(' ','') for stringa in st.session_state.altri_siti['Target_range']]
        st.session_state.altri_siti['appoggio'] = [stringa.replace('[','') for stringa in st.session_state.altri_siti['no_spazi']]
        st.session_state.altri_siti['appoggio2'] = [stringa.replace(']','') for stringa in st.session_state.altri_siti['appoggio']]
        st.session_state.altri_siti['date_range'] = [str.split(stringa, ',') for stringa in st.session_state.altri_siti['appoggio2']]
        st.session_state.altri_siti['Check'] = False
        #st.session_state.altri_siti = st.session_state.altri_siti.rename(columns={'N_op_x':'N_op','Op_vincolo_x':'Op_vincolo'})
        #st.session_state.altri_siti = st.session_state.altri_siti.merge(vincolo_nop, how='left',left_on='ID',right_on='ID')   
        #st.session_state.altri_siti = st.session_state.altri_siti.rename(columns={'N_op_x':'N_op','Op_vincolo_x':'Op_vincolo'})
        #st.session_state.altri_siti = st.session_state.altri_siti.drop(columns=['Note','Target_range','no_spazi','appoggio','appoggio2','N_op_y','Op_vincolo_y'])


    if 'agenda' not in st.session_state:
        try:
            st.session_state.agenda = pe.retrieve_file(username, token,repository_name, file_path)
        except:
            st.session_state.agenda = st.session_state.altri_siti[st.session_state.altri_siti['Check'] == True]
            st.session_state.agenda['Operatore'] = None
            st.session_state.agenda['Data'] = None
            st.session_state.agenda['Inizio'] = None #np.datetime64('NaT')
            st.session_state.agenda['Fine'] = None #np.datetime64('NaT')
            st.session_state.agenda['Ordine_intervento'] = None
            st.session_state.agenda['Durata_viaggio'] = None
            st.session_state.agenda['Arrivo_da_precedente'] = None

    if 'note_valentina' not in st.session_state:
        try:
            st.session_state.note_valentina = pe.retrieve_file(username, token,repository_name, file_path_note_valentina)      
        except:
            st.session_state.note_valentina = {}

    if 'note_giorgia' not in st.session_state:
        try:
            st.session_state.note_giorgia = pe.retrieve_file(username, token,repository_name, file_path_note_giorgia)      
        except:
            st.session_state.note_giorgia = {}

    if 'note_denise' not in st.session_state:
        try:
            st.session_state.note_denise = pe.retrieve_file(username, token,repository_name, file_path_note_denise)      
        except:
            st.session_state.note_denise = {}

    if 'note_simonap' not in st.session_state:
        try:
            st.session_state.note_simonap = pe.retrieve_file(username, token,repository_name, file_path_note_simonap)      
        except:
            st.session_state.note_simonap = {}

    if 'note_simonal' not in st.session_state:
        try:
            st.session_state.note_simonal = pe.retrieve_file(username, token,repository_name, file_path_note_simonal)      
        except:
            st.session_state.note_simonal = {}
   
    dic_note = {
        'Valentina':st.session_state.note_valentina,
        'Giorgia':st.session_state.note_giorgia,
        'Denise':st.session_state.note_denise,
        'Simona Porro':st.session_state.note_simonap,
        'Simona Lavezzo':st.session_state.note_simonal
    }

    if 'last_up' not in st.session_state:
        # se non è già in cache segue lo stesso percorso di costruzione di agenda
        try:
            st.session_state.last_up = pe.retrieve_file(username, token,repository_name, file_path)

        except:
            st.session_state.last_up = st.session_state.altri_siti[st.session_state.altri_siti['Check'] == True]
            st.session_state.last_up['Operatore'] = None
            st.session_state.last_up['Data'] = None
            st.session_state.last_up['Inizio'] = None #np.datetime64('NaT')
            st.session_state.last_up['Fine'] = None #np.datetime64('NaT')
            st.session_state.last_up['Ordine_intervento'] = None
            st.session_state.last_up['Durata_viaggio'] = None
            st.session_state.last_up['Arrivo_da_precedente'] = None

    def refresh_new():
        check = st.session_state.agenda.copy()
        check['Confronto']=None
        for i in range(len(check)):
            check['Confronto'].iloc[i] = str(list([check.Operatore.iloc[i], check.Inizio.iloc[i], check.Fine.iloc[i]]))
        #check = check[layout['Refresh']]
        #check['data_string'] = [str(data) for data in check.Data]
        #check['key']= check['data_string']+check['Operatore']
        #st.write('check',check)
        try:
            last = st.session_state.last_up.copy()
            last['Confronto']=None
            for i in range(len(last)):
                last['Confronto'].iloc[i] = str(list([last.Operatore.iloc[i], last.Inizio.iloc[i], last.Fine.iloc[i]]))

            #st.write('last',last)#-------------------------------------------------------

            compare = last.merge(check, how='outer', left_on='ID',right_on='ID')
            compare['compare'] = compare['Confronto_x'] == compare['Confronto_y']
            compare = compare[compare['compare'] == False]
            compare['Azione'] = None

            for i in range(len(compare)):
                if compare.Operatore_x.astype(str).iloc[i] == 'nan':
                    compare['Azione'].iloc[i] = 'Aggiungi'

                elif compare.Operatore_y.astype(str).iloc[i]== 'nan':
                    compare['Azione'].iloc[i] = 'Rimuovi'

                else:
                    compare['Azione'].iloc[i] = 'Modifica'

            #st.write('compare',compare)#--------------------------------------------------

            add_ID = list(compare[compare.Azione == 'Aggiungi'].ID)
            change_ID = list(compare[compare.Azione == 'Modifica'].ID)
            delete = list(compare[compare.Azione == 'Rimuovi'].ID) 

            add = check[[any(id_check == id_add for id_add in add_ID) for id_check in check.ID ]]          
            change = check[[any(id_check == id_change for id_change in change_ID) for id_check in check.ID ]]

            #------------------------------------------
            #st.write('add', add)
            #st.write('change', change)
            #st.write('delete', delete)
            #------------------------------------------

            # Qui recupero l'agenda 
            try:
                agenda_git = pe.retrieve_file(username, token,repository_name, file_path)
            except:
                agenda_git = st.session_state.agenda

            agenda_git['Elimina'] = None

            # elimino le righe da eliminare
            if delete != []: #se ci sono righe  da eliminare
                for i in range(len(agenda_git)):
                    id_git = agenda_git.ID.iloc[i]
                    for id_del in delete:
                        if id_git == id_del:
                            agenda_git['Elimina'].iloc[i] = 'x'
                
                agenda_git = agenda_git[agenda_git.Elimina != 'x']
            
            # modifico le righe cambiate
            if change_ID != []:
                for i in range(len(agenda_git)):
                    id_git = agenda_git.ID.iloc[i]
                    for j in range(len(change)):
                        id_chg = change.ID.iloc[j]
                        if id_git == id_chg:
                            agenda_git.iloc[i] = change.iloc[j]
            
            # aggiungo le righe nuove
            if add_ID != []:
                add = add.drop(columns=['Confronto'])
                agenda_git = pd.concat([agenda_git,add])

            
            # elimino colonne create per fare i confronti 
            agenda_git = agenda_git.drop(columns=['Elimina'])        
            #st.write('agenda_git', agenda_git)

            pe.upload_file(username,token,agenda_git, repository_name, file_path)
            st.session_state.agenda = agenda_git
            st.session_state.last_up = agenda_git

        except Exception as e:
            st.write(f'eccezione: {e}')
            pass

    def refresh_note():
        # aggiornamento note
        to_upload = dic_note[utente]
        try:
            pe.upload_dict(username,token,to_upload, repository_name, path_note_git[utente])
        except Exception as e:
            st.write(f'eccezione nel caricamento della nota aggiornata: {e}')
            
        try:
            st.session_state.note_valentina = pe.retrieve_file(username, token,repository_name, file_path_note_valentina)
        except:
            pass
        
        try:
            st.session_state.note_giorgia = pe.retrieve_file(username, token,repository_name, file_path_note_giorgia)
        except:
            pass

        try:
            st.session_state.note_denise = pe.retrieve_file(username, token,repository_name, file_path_note_denise)
        except:
            pass

        try:
            st.session_state.note_simonap = pe.retrieve_file(username, token,repository_name, file_path_note_simonap)
        except:
            pass

        try:
            st.session_state.note_simonal = pe.retrieve_file(username, token,repository_name, file_path_note_simonal)
        except:
            pass
        
    def callback3():    
            #st.session_state.agenda = pd.concat([st.session_state.agenda,st.session_state.altri_siti[st.session_state.altri_siti['Check']==True]])
            st.session_state.agenda = pd.concat([st.session_state.agenda, work[work['Check']==True]])
            for i in range (len(st.session_state.altri_siti)):
                 id = st.session_state.altri_siti.ID.iloc[i]
                 for k in range(len(work)):
                      id_work = work.ID.iloc[k]
                      if id == id_work:
                           st.session_state.altri_siti.Check.iloc[i] = work.Check.iloc[k]
            st.session_state.altri_siti = st.session_state.altri_siti[st.session_state.altri_siti['Check'] == False]

    def callback4(): #togli intervento da agenda  e rendi nuovamente pianificabile
        st.session_state.altri_siti = pd.concat([st.session_state.altri_siti, modifica_agenda[modifica_agenda['Check']==False]])
        for i in range (len(st.session_state.agenda)):
            id = st.session_state.agenda.ID.iloc[i]
            for k in range(len(modifica_agenda)):
                id_modifica = modifica_agenda.ID.iloc[k]
                if id == id_modifica:
                    st.session_state.agenda.Check.iloc[i] = modifica_agenda.Check.iloc[k]
        st.session_state.agenda = st.session_state.agenda[st.session_state.agenda.Check == True]
        #st.session_state.agenda = st.session_state.agenda.drop_duplicates

    #st.subheader('{:0.2f} ore totali di intervento sul sito territoriale'.format(st.session_state.altri_siti['Durata_stimata'].sum()/60)) 

    scelta_giorno = st.date_input('Inserire data da pianificare')
    scelta_sito = st.multiselect('Selezionare Sito', siti_unici)
    if not scelta_sito:
         #st.stop()
         scelta_sito=siti_unici
    work = st.session_state.altri_siti.copy()

    work = work[[any(sito in word for sito in scelta_sito) for word in work['SitoTerritoriale'].astype(str)]]
    
    if st.toggle('Mostra tutti gli interventi del mese'):
        work = work
        improrogabili = list(work.ID[[len(date)==1 for date in work.date_range ]])
        st.write(f'{len(improrogabili)} interventi improrogabili nel sito nel mese')

    else:
        work = work[[str(scelta_giorno.day) in tgtrange for tgtrange in work.date_range]]
        #st.write('work',work)

        improrogabili = list(work.ID[[len(date)==1 for date in work.date_range ]])
        st.write(f'{len(improrogabili)} interventi improrogabili nel sito nella data selezionata')


    if st.toggle('Mostra improrogabili'):
        try:            
            work = work[[len(date)==1 for date in work.date_range ]]
        except:
            st.write('nessun intervento')
    else:       
        work = work


    if st.toggle('Mostra interventi con disponibilità ristretta'):
        try:            
            work = work[[len(date)<=5 for date in work.date_range ]]
        except:
            st.write('nessun intervento')
    else:       
        work = work


    if st.toggle(('2Operatori')):
        try:
            work = work[work['N_op']==' 2 OPERATORI']
        except:
            st.write('Nessun intervento')
    else:
        try:
            work = work[work['N_op']!=' 2 OPERATORI']
        except:
            st.write('Nessun intervento')

    work['Operatore'] = None
    
    try:
        coordinate_inizio = work[['Cliente','lat','lng']].copy()
    except:
         st.write(':orange[Nessun intervento sul sito disponibile nelle date selezionate]')

    coordinate_inizio  = coordinate_inizio[(coordinate_inizio.lat != 0) & (coordinate_inizio.lat.astype(str) != 'nan')]

    if len(coordinate_inizio) != 0:
         inizio = (coordinate_inizio.lat.iloc[0],coordinate_inizio.lng.iloc[0])
    else:
         st.write(':orange[Nessun intervento nei siti selezionati]')
         inizio = (coordinate_exera[1],coordinate_exera[0])

    try:
        mensili = {'si':'red','no':'blue'}
        centro_mappa = st.session_state.agenda.copy()
        #st.write(centro_mappa)
        #st.write(scelta_giorno)
        #st.write(centro_mappa.Data.iloc[-1])
        #st.stop()
        #centro_mappa = centro_mappa[centro_mappa.Operatore == nome_cognome]
        #centro_mappa = centro_mappa[centro_mappa.Data == scelta_giorno]
        #st.write(centro_mappa)
        #st.stop()



        try:
            lat_inizio = centro_mappa.lat.iloc[-1]
            lng_inizio = centro_mappa.lng.iloc[-1]
            if not lat_inizio:
                lat_inizio = work.lat.iloc[1]
                lng_inizio = work.lng.iloc[0]
                if not lat_inizio:
                    lat_inizio = coordinate_exera[1]
                    lng_inizio = coordinate_exera[0]

     
        except:
            lat_inizio = work.lat.iloc[1]
            lng_inizio = work.lng.iloc[0]


        #mappa=folium.Map(location=inizio,zoom_start=15)
        mappa=folium.Map(location=(lat_inizio,lng_inizio),zoom_start=15)
        
        #stampo il punto dell'ultimo intervento

        folium.CircleMarker(location=(lat_inizio,lng_inizio),
                                    radius=30,
                                    color='red',
                                    stroke=False,
                    fill=True,
                    fill_opacity=0.8,
                    opacity=1,
                    ).add_to(mappa)
        
        for i in range(len(work)):
            try:
                folium.CircleMarker(location=[work.lat.iloc[i], work.lng.iloc[i]],
                                    radius=7,
                                    color=mensili[work.Mensile.iloc[i]],
                                    stroke=False,
                    fill=True,
                    fill_opacity=1,
                    opacity=1,
                    popup=work.Cliente.iloc[i]+'----------'+ work.Servizio.iloc[i]+'--------- Durata: '+
                        str(work['Durata_stimata'].iloc[i]),
                    #tooltip=cluster,
                    ).add_to(mappa)
            except:
                st.write('Cliente {} non visibile sulla mappa per mancanza di coordinate su Byron'.format(work.Cliente.iloc[i]))
                pass
            
        sxmappa, dxmappa = st.columns([2,1])    
        with sxmappa:
            folium_static(mappa,width=1300,height=800)

        with dxmappa:
            work = st.data_editor(work[layout['Mappa']],height=800)

        sx4, spazio1, cx4, dx4 =st.columns([4,1,3,2])

    # view agenda    
        with sx4:
            nome_cognome = st.selectbox('Seleziona operatore',operatori)
            data_pianificazione = st.date_input('Seleziona data assegnazione', value=scelta_giorno)
            submit_button = st.button(label='Aggiungi interventi', on_click=callback3)
            work['Operatore'] = nome_cognome
            work['Data'] = data_pianificazione  
            agenda_work = st.session_state.agenda.copy()
            agenda_work = agenda_work[agenda_work.Operatore == nome_cognome]
            agenda_work = agenda_work[agenda_work.Data == data_pianificazione]
            agenda_work[layout['Layout_agenda_work']]
            
    # Cruscotto dati giornata
        with cx4:
            distanze = st.toggle('Abilita calcolo distanze')         
            tempo = agenda_work.Durata_stimata.sum()         
            st.subheader('Indicatori giornata', divider='orange')
            st.subheader('Operatore: :orange[{}]'.format(nome_cognome))
            st.subheader('Ore di intervento: :orange[{:0.2f}]'.format(tempo/60))

            viaggio = 0

            if distanze:

                if len(agenda_work)==0:
                    st.stop()
                else:
                    primo_intervento = (agenda_work.lng.iloc[0],agenda_work.lat.iloc[0])

                try:
                    res = client.directions((coordinate_exera, primo_intervento))
                    durata = res['routes'][0]['summary']['duration']
                    viaggio+=(durata/3600)
                except:
                    viaggio += 0.25
                    st.write('coordinate non presenti, stimato 15 minuti primo viaggio della giornata')

                for i in range(1,len(agenda_work)):
                    part = (agenda_work.lng.iloc[i-1],agenda_work.lat.iloc[i-1])
                    arr = (agenda_work.lng.iloc[i],agenda_work.lat.iloc[i])
                
                    try:
                        res = client.directions((part , arr))
                        durata = res['routes'][0]['summary']['duration']/3600
                        viaggio+=durata

                    except:
                        if part == arr:
                            durata = 0
                        else:
                            durata = 0.25
                            st.write('coordinate non presenti')
                        viaggio+=durata
            
                ultimo_intervento = (agenda_work.lng.iloc[-1],agenda_work.lat.iloc[-1])
                try:
                    res = client.directions((ultimo_intervento,coordinate_exera))
                    durata = res['routes'][0]['summary']['duration']
                    viaggio+=(durata/3600)
                except:
                    viaggio += 0.25
                    st.write('coordinate non presenti, stimato 15 minuti ultimo viaggio della giornata')        
            else:
                viaggio = 15*len(agenda_work)/60

            st.subheader('Ore di viaggio stimate: :orange[{:0.2f}]'.format(viaggio))
            st.subheader('Ore totali agenda: {:0.2f}'.format(viaggio + tempo/60))
    except:
        pass

with tab5:

    def callback_modifica_agenda():
        for i in range(len(st.session_state.agenda)):
            for j in range(len(agenda_edit)):
                if agenda_edit.ID.iloc[j] == st.session_state.agenda.ID.iloc[i]:
                    st.session_state.agenda.Inizio.iloc[i] = agenda_edit.Inizio.iloc[j]#.time()
                    st.session_state.agenda.Ordine_intervento.iloc[i] = agenda_edit.Ordine_intervento.iloc[j]
                    st.session_state.agenda.Operatore.iloc[i] = agenda_edit.Operatore.iloc[j]
                    st.session_state.agenda.Durata_stimata.iloc[i] = agenda_edit.Durata_stimata.iloc[j]
                    st.session_state.agenda.Data.iloc[i] = agenda_edit.Data.iloc[j]
                    st.session_state.agenda.IstruzioniOperative.iloc[i] = agenda_edit.IstruzioniOperative.iloc[j]



                    
                    #calcolo ora di fine + viaggio

                    if calcola_distanze:
                        try:
                            start = datetime.strptime(str(agenda_edit.Inizio.iloc[j]),'%H:%M')
                        except:
                            pass
                        durata = agenda_edit.Durata_stimata.iloc[j]
                        try:
                            st.session_state.agenda.Fine.iloc[i] = str((start + timedelta(minutes=durata)).time())
                        except:
                            pass #se non è stato inserito un orario faccio stop
                        
                        arrivo_agenda = (agenda_edit.lng.iloc[j],agenda_edit.lat.iloc[j])
                        if j == 0:
                            partenza_agenda = coordinate_exera
                        else:
                            partenza_agenda = (agenda_edit.lng.iloc[j-1],agenda_edit.lat.iloc[j-1])

                        try:
                            res_agenda = client.directions((partenza_agenda , arrivo_agenda))
                            last_viaggio = res_agenda['routes'][0]['summary']['duration']/60
                        except:
                            last_viaggio = 0

                        st.session_state.agenda.Durata_viaggio.iloc[i] = last_viaggio
                        try:
                            if j != 0:
                                st.session_state.agenda.Arrivo_da_precedente.iloc[i] = str((datetime.strptime(str(agenda_edit.Fine.iloc[j-1]), '%H:%M:%S')+timedelta(minutes=last_viaggio)).time())[0:8]
                            else:
                                st.session_state.agenda.Arrivo_da_precedente.iloc[i] = None
                        except:
                            #st.write('problema')
                            pass
                                    
                    st.session_state.agenda = st.session_state.agenda.sort_values(by=['Data','Operatore','Ordine_intervento'])

    def callback_nota():
        dic_note[utente][str(data_agenda)] = dic_campi_note[utente]
        to_upload = dic_note[utente]
        pe.upload_dict(username, token, to_upload,repository_name, path_note_git[utente])


    h_note =  300
    h_note2 = 125
    h_noted = 300
    h_mappa = 660
    w_mappa = 1000

    st.subheader('Modifica', divider='orange')
    op_modifica = st.selectbox("Seleziona operatore di cui modificare l'agenda", operatori)
    if not op_modifica:
        st.stop()
    data_agenda = st.date_input('Seleziona giornata da modificare')
    if not data_agenda:
        st.stop()

    sx5, cx5, dx5 = st.columns([2,1,1])

    with cx5:
        try:
            nota_valentina = st.text_area('Note Valentina', value = st.session_state.note_valentina[str(data_agenda)], height=h_note)
        except:
            nota_valentina = st.text_area('Note Valentina', height=h_note)

        try:
            nota_giorgia = st.text_area('Note Giorgia', value = st.session_state.note_giorgia[str(data_agenda)], height=h_note)
        except:
            nota_giorgia = st.text_area('Note Giorgia',height=h_note)

    with dx5:
        try:
            nota_denise = st.text_area('Note Denise', value = st.session_state.note_denise[str(data_agenda)], height=h_noted)
        except:
            nota_denise = st.text_area('Note Denise',height=h_noted)

        try:
            nota_simonap = st.text_area('Note Simona Porro', value = st.session_state.note_simonap[str(data_agenda)], height=h_note2)
        except:
            nota_simonap = st.text_area('Note Simona Porro', height=h_note2)

        try:
            nota_simonal = st.text_area('Note Simona Lavezzo', value = st.session_state.note_simonal[str(data_agenda)], height=h_note2)
        except:
            nota_simonal = st.text_area('Note Simona Lavezzo',height=h_note2)
        
    
        dic_campi_note = {
            'Valentina':nota_valentina,
            'Giorgia':nota_giorgia,
            'Denise':nota_denise,
            'Simona Porro':nota_simonap,
            'Simona Lavezzo':nota_simonal
        }

    sx_butt,dx_butt = st.columns([13,1])

    with dx_butt:
        submit_button_nota = st.button(label='Aggiorna nota', on_click=callback_nota)
        #st.write("Rende pubblica l'ultima modifica" )    

    with placeholder2:
        refresh_button  = st.button(label=':orange[Refresh note]', on_click=refresh_note)
        #st.write(":orange[Vedi ultimo aggiornamento note degli altri utenti]")
    

    calcola_distanze = st.toggle('abilita calcolo distanze')
    agenda_edit = st.session_state.agenda.copy()
    agenda_edit = agenda_edit[agenda_edit['Operatore'] == op_modifica]
    agenda_edit = agenda_edit[agenda_edit.Data == data_agenda]
    
    try:
        open_agenda = (agenda_edit.lat.iloc[0],  agenda_edit.lng.iloc[0])
    except:
        open_agenda = inizio

    try:
        mappa2=folium.Map(location=open_agenda,zoom_start=13)
        for i in range(len(agenda_edit)):
                try:
                    folium.Marker(location=(agenda_edit.lat.iloc[i],agenda_edit.lng.iloc[i]),
                                popup = agenda_edit.Cliente.iloc[i]+'----------'+ agenda_edit.Servizio.iloc[i]+'--------- Durata: '+
                                str(agenda_edit['Durata_stimata'].iloc[i])).add_to(mappa2)
                except:
                    st.write('Cliente {} non visibile sulla mappa per mancanza di coordinate su Byron :orange[(potrebbe essere inserito urgente)]'.format(agenda_edit.Cliente.iloc[i]))
                    pass
        with sx5:    
                folium_static(mappa2,width=w_mappa,height=h_mappa)
    except:
        st.write('Mappa non disponibile per assenza di coordinate | :orange[(verifica interventi urgenti)]')

    def callback_urgente():
        st.session_state.agenda = pd.concat([st.session_state.agenda, to_add])

    def callback_cambia_op():
        op_check = op_modifica
        op_new = operatore_new
        data_check = str(data_agenda)
        for i in range(len(st.session_state.agenda)):
            op = st.session_state.agenda.Operatore.iloc[i]
            data = str(st.session_state.agenda.Data.iloc[i])
            if op == op_check and data == data_check:
                st.session_state.agenda.Operatore.iloc[i] = op_new
    

    agenda_edit['Ordine_intervento'] =  agenda_edit['Ordine_intervento'].astype(float)
    agenda_edit = st.data_editor(agenda_edit[layout['Agenda_edit']],column_config={'Operatore':st.column_config.SelectboxColumn(options=operatori),
                                                                                   'Data':st.column_config.DateColumn()} ,on_change=None)

    submit_button2 = st.button(label='Modifica agenda', on_click=callback_modifica_agenda)

    urgente = st.toggle(':red[Aggiungi urgente]')
    if urgente:

        cliente = st.text_input('Cliente')
        servizio = st.text_input('Servizio')
        durata = st.number_input('Durata stimata')

        if not (cliente and servizio and durata):
            st.stop()

        to_add = pd.DataFrame(columns=['ID','Cliente','Servizio','Data','Operatore','IstruzioniOperative','lat','lng', 'Check', 'Durata_stimata'])
        to_add.loc[0]=''
        to_add.Cliente.loc[0]=cliente
        to_add.Servizio.loc[0]=servizio
        to_add.Durata_stimata.loc[0]=durata
        to_add.Data.loc[0] = data_agenda
        to_add.Operatore.loc[0] = 'JOLLY'
        to_add.ID.loc[0]=random.randint(1000000000,3000000000)
        to_add.Check.loc[0]=True
        #to_add.lat.loc[0] = coordinate_exera[1]
        #to_add.lng.loc[0] = coordinate_exera[0]
       # to_add = st.data_editor(to_add, width=1500)
        submit_button_urgente = st.button(label='Aggiungi urgente',on_click=callback_urgente)

    if st.toggle('Trasferisci agenda'):
        operatore_new = st.selectbox("Selezionare operatore a cui trasferire l'agenda",operatori)
        submit_button_trasferisci = st.button(label='Trasferisci',on_click=callback_cambia_op)
        
    

    abilita_rimozione = st.toggle('Rimuovi interventi pianificati')
    if abilita_rimozione:
        try:
            modifica_agenda = st.session_state.agenda.copy()
            modifica_agenda = modifica_agenda[modifica_agenda.Data == data_agenda]
            modifica_agenda = modifica_agenda[modifica_agenda['Operatore']==op_modifica]
            modifica_agenda = st.data_editor(modifica_agenda[layout['Layout_select']])
            remove_button = st.button(label='Rimuovi interventi', on_click=callback4)
        except:
            pass

with placeholder:
    submit_button3 = st.button('Refresh', on_click=refresh_new)

with tab6:

    st.subheader('Esporta agenda', divider='orange')
    data_agenda_exp = st.date_input('Selezionare giornata')
    if not data_agenda_exp:
        st.stop()

    if not st.toggle('Visualizza tutti gli operatori'):

        op_modifica_exp = st.selectbox("Selezionare operatore", operatori)
        if not op_modifica_exp:
            st.stop()
        agenda_edit_exp = st.session_state.agenda.copy()
        agenda_edit_exp = agenda_edit_exp[agenda_edit_exp['Operatore'] == op_modifica_exp]
        agenda_edit_exp = agenda_edit_exp[agenda_edit_exp.Data == data_agenda_exp]
        filename_agenda = f'Agenda_{data_agenda_exp} | {op_modifica_exp}'
        download = st.data_editor(agenda_edit_exp[layout['Agenda_esporta']])

    else:
        agenda_edit_exp = st.session_state.agenda.copy()
        
        
        agenda_edit_exp = agenda_edit_exp[agenda_edit_exp.Data == data_agenda_exp]

        op_unici = list(agenda_edit_exp.Operatore.unique())
        #st.write(op_unici)
        
        ganttsx, ganttdx = st.columns([10,6])
        #fig, ax = plt.subplots(figsize=(10,10))
        #n=0
        for op in op_unici:
            #n+=1
           
            plot = agenda_edit_exp[agenda_edit_exp.Operatore == op][layout['Scacchiera']]

            with ganttsx:
                st.subheader(op)
                st.dataframe(plot, width=1000)
                
            gantt = plot.copy()
            
            try:
                gantt['Start']= [datetime.strptime(str(inizio),'%H:%M').time() for inizio in gantt.Inizio] 
                gantt['Start_gantt'] = [(datetime.strptime(str(inizio),'%H:%M').time().hour * 60 + datetime.strptime(str(inizio),'%H:%M').time().minute) for inizio in gantt.Inizio]
                gantt['pos_text'] = gantt['Start_gantt']+1#gantt['Durata_stimata']/2 - 3

            except Exception as e:
                st.write(f'Operatore {op} | Grafico non disponibile, compilare orari')


            try:
                #fig, ax = plt.subplots(figsize=(15,1))
                #ax.barh(1.3, gantt['Durata_stimata'], left=gantt['Start_gantt'], color='orange') 

            
                #for i in range (len(gantt)):
                #    ax.text(gantt['pos_text'].iloc[i]-22,0.2, str(gantt.Start.iloc[i]),rotation=45)
                 #   ax.text(gantt['pos_text'].iloc[i]+gantt['Durata_stimata'].iloc[i]-24,0.2,str(gantt.Fine.iloc[i] ), rotation=45)
                  #  ax.text(gantt['pos_text'].iloc[i],2,gantt.Cliente.iloc[i], rotation=90)
                   # pass
                
                fig, ax = plt.subplots(figsize=(10,10))
                
                ax.bar(0.5,gantt['Durata_stimata'], bottom=gantt['Start_gantt'], color='orange', width=2)
                for i in range (len(gantt)):
                    pass

                for i in range (len(gantt)):
                    
                    ax.text(1.52,gantt['pos_text'].iloc[i]-5, str(gantt.Start.iloc[i]),rotation=0)
                    ax.text(1.7,gantt['pos_text'].iloc[i]+gantt['Durata_stimata'].iloc[i]-5,str(gantt.Fine.iloc[i] ), rotation=0)
                    ax.text(0.12,gantt['pos_text'].iloc[i]+gantt['Durata_stimata'].iloc[i]/2-5,gantt.Cliente.iloc[i], rotation=0)






                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['bottom'].set_visible(False)
                ax.spines['left'].set_visible(False)
                

                

                with ganttdx:

                    st.subheader(op)
                    #st.write(op)
                    plt.ylim(480,1080)
                    #plt.xlim(480,1020)
                    plt.xlim(0,2)
                    plt.yticks([])
                    plt.xticks([])

                    st.pyplot(fig)
                    st.divider()

            except Exception as e:
                with ganttdx:
                    #st.write(e)
                    pass
                    #st.write('Grafico non disponibile')
                
                pass

       # with ganttdx:
         #   st.pyplot(fig)
           

        #agenda_edit_exp = agenda_edit_exp[agenda_edit_exp.Data == data_agenda_exp]
        filename_agenda = f'Agenda_{data_agenda_exp} | tutti gli operatori'
        #download = st.data_editor(agenda_edit_exp[layout['Agenda_completa']])


    def scarica_excel(df, filename):
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        df.to_excel(writer, sheet_name='Sheet1', index=False)
        writer.close()
        st.download_button(
            label="Download Excel workbook",
            data=output.getvalue(),
            file_name=filename,
            mime="application/vnd.ms-excel"
        )

    #scarica_excel(download, filename_agenda)
    

with tab7:

    data_planned  = st.date_input('selezionare data')
    try:
        planned = st.session_state.agenda.copy()
        planned = planned[[data == data_planned for data in planned.Data]]


        #mensili = {'si':'red','no':'blue'}
        
        mappa_planned=folium.Map(location=(coordinate_exera[1],coordinate_exera[0]),zoom_start=10)

        for i in range(len(work)):
            try:
                folium.CircleMarker(location=[planned.lat.iloc[i], planned.lng.iloc[i]],
                                    radius=5,
                                    color='blue',#mensili[work.Mensile.iloc[i]],
                                    stroke=False,
                    fill=True,
                    fill_opacity=1,
                    opacity=1,
                    popup=planned.Operatore.iloc[i] +' - '+ planned.Cliente.iloc[i]
                    #tooltip=cluster,
                    ).add_to(mappa_planned)
            except:
                #st.write('Cliente {} non visibile sulla mappa per mancanza di coordinate su Byron'.format(work.Cliente.iloc[i]))
                pass
            
        folium_static(mappa_planned,width=2000,height=800)

    except:
        pass