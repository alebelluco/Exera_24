# 25/03/2024
# 1. modificare il campo tgtrange in lista
# 2. inserire calcolatore di tempo tra due siti
# 3. editare campo orario
# 4. aggiungere la data
# 5. Copia agenda per 2 operatori

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

st.set_page_config(page_title="Planner interventi", layout='wide')

client = openrouteservice.Client(key='5b3ce3597851110001cf6248d1d5a3c164ef475d8ae776eeb594fda6')

file_path  = 'agenda.pickle'
username = "alebelluco"
repository_name  = 'storage_exera'
token = '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'

coordinate_exera = (11.594276, 44.817830)

#operatori = ['FARINA MIRKO','ALTIERI NICO','Op3','Op4','Op5']

operatori = [
    
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



col1, col2 = st.columns([4,1])
with col1:
    #st.title('Visualizzazione programma di lavoro')
    pass

with col2:
    #st.image('https://github.com/alebelluco/Test_EX/blob/main/exera_logo.png?raw=True')
    pass

#percorso = st.sidebar.file_uploader("Caricare il programma Ferrara")
#if not percorso:
#    st.stop()
#visualizzazione=pd.read_csv(percorso)

layout  = {'Layout_select':['Check','Cliente','Sito','N_op','Op_vincolo','Indirizzo Sito','IstruzioniOperative','orari','Servizio','Periodicita','SitoTerritoriale','Citta',
                            'Durata_stimata','ID','lat','lng','date_range','Mensile'],

        'Layout_no_dup':['Cliente','Sito','N_op','Op_vincolo','Indirizzo Sito','IstruzioniOperative','orari','Servizio','Periodicita','SitoTerritoriale','Citta',
                            'Durata_stimata','ID','lat','lng','Target_range','Mensile'],


           'Layout_agenda':['Check','Cliente','Sito','N_op','Op_vincolo','Indirizzo Sito','IstruzioniOperative','orari','Servizio','Periodicita','SitoTerritoriale','Citta',
                            'Durata_stimata','ID','lat','lng','Operatore','date_range','Mensile'],

            'Layout_agenda_work':['Durata_stimata','Cliente','Sito','Servizio','Periodicita','Operatore','lat','lng','Data','Mensile'],

            'Agenda_edit' : ['Ordine_intervento','Durata_viaggio','Arrivo_da_precedente','Inizio','Durata_stimata','Fine','Cliente','Sito','Servizio','Periodicita','Operatore','lat','lng','Data','ID']
                            }

tab4, tab5, tab6= st.tabs(['Assegna interventi','Agende', 'Calcolo distanze'])

with tab4:

    #vincolo_nop = visualizzazione[['ID','N_op','Op_vincolo']]
    #vincolo_nop = vincolo_nop.drop_duplicates()

    percorso_altri = st.sidebar.file_uploader("Caricare altri siti")
    if not percorso_altri:
        st.stop()
    altri_siti=pd.read_csv(percorso_altri)
    altri_siti = altri_siti.drop_duplicates()

    siti_unici = altri_siti['SitoTerritoriale'].unique()
    
    #scelta_giorno = st.date_input('Inserire data da pianificare').day

    if 'altri_siti' not in st.session_state:
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


    def refresh():
        #salva e recupera il file pickled dell'agenda da github
        pe.upload_file(username,token,st.session_state.agenda, repository_name, file_path)
        st.session_state.agenda = pe.retrieve_file(username, token,repository_name, file_path)
        

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
         st.stop()
    work = st.session_state.altri_siti.copy()
    work = work[[any(sito in word for sito in scelta_sito) for word in work['SitoTerritoriale'].astype(str)]]
    work = work[[str(scelta_giorno.day) in tgtrange for tgtrange in work.date_range]]

    if st.toggle(('2Operatori')):
        work = work[work['N_op']==' 2 OPERATORI']
    else:
        work = work[work['N_op']!=' 2 OPERATORI']

    work['Operatore'] = None

    try:
        coordinate_inizio = work[['Cliente','lat','lng']].copy()
    except:
         st.write(':orange[Nessun intervento sul sito disponibile nelle date selezionate]')
         st.stop()
    coordinate_inizio  = coordinate_inizio[(coordinate_inizio.lat != 0) & (coordinate_inizio.lat.astype(str) != 'nan')]
    if len(coordinate_inizio) != 0:
         inizio = (coordinate_inizio.lat.iloc[0],coordinate_inizio.lng.iloc[0])
    else:
         st.write(':orange[Nessun intervento nei siti selezionati]')
         st.stop()


    mensili = {'si':'red','no':'blue'}
    
    mappa=folium.Map(location=inizio,zoom_start=15)

    for i in range(len(work)):
        try:
            #folium.Marker(location=(work.lat.iloc[i],work.lng.iloc[i]),
              #            popup = work.Cliente.iloc[i]+'----------'+ work.Servizio.iloc[i]+'--------- Durata: '+
               #         str(work['Durata_stimata'].iloc[i]),color='red').add_to(mappa)
            
            #folium.CircleMarker(location=(work.lat.iloc[i],work.lng.iloc[i]),
               #                 popup = work.Cliente.iloc[i]+'----------'+ work.Servizio.iloc[i]+'--------- Durata: '+
                 #      str(work['Durata_stimata'].iloc[i]),fill=True, color='red', radius=4, stroke=False
                 #              )
            
             folium.CircleMarker(location=[work.lat.iloc[i], work.lng.iloc[i]],
                                 radius=4,
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
        
    folium_static(mappa,width=2500,height=800)

    work = st.data_editor(work[layout['Layout_select']])

    sx4, spazio1, cx4, dx4 =st.columns([4,1,3,2])

# view agenda    
    with sx4:
        nome_cognome = st.selectbox('Seleziona operatore',operatori)
        submit_button = st.button(label='Aggiungi interventi', on_click=callback3)
        work['Operatore'] = nome_cognome
        work['Data'] = scelta_giorno    
        agenda_work = st.session_state.agenda.copy()
        agenda_work = agenda_work[agenda_work.Operatore == nome_cognome]
        agenda_work = agenda_work[agenda_work.Data == scelta_giorno]
        #agenda_work['Data'] = scelta_giorno
        #st.data_editor(agenda_work[layout['Layout_agenda_work']],width=1500, column_config = {'Inizio':st.column_config.TimeColumn("Inizio",min_value=time(6, 0),max_value=time(20, 0),format="hh:mm "),
        #                                                                                      'Fine':st.column_config.TimeColumn("Fine",min_value=time(6, 0),max_value=time(20, 0),format="hh:mm ")})
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

with tab5:

    def callback_modifica_agenda():
        for i in range(len(st.session_state.agenda)):
            for j in range(len(agenda_edit)):
                if agenda_edit.ID.iloc[j] == st.session_state.agenda.ID.iloc[i]:
                    st.session_state.agenda.Inizio.iloc[i] = agenda_edit.Inizio.iloc[j]#.time()
                    st.session_state.agenda.Ordine_intervento.iloc[i] = agenda_edit.Ordine_intervento.iloc[j]
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

    #st.dataframe(st.session_state.agenda)

    sx5, cx5, dx5 = st.columns([3,6,1])
    with sx5:
        st.subheader('Modifica', divider='orange')
        op_modifica = st.selectbox("Seleziona operatore di cui modificare l'agenda", operatori)
        if not op_modifica:
            st.stop()
        data_agenda = st.date_input('Seleziona giornata da modificare')
        if not data_agenda:
            st.stop()
    
    calcola_distanze = st.toggle('abilita calcolo distanze')
    agenda_edit = st.session_state.agenda.copy()
    agenda_edit = agenda_edit[agenda_edit['Operatore'] == op_modifica]
    agenda_edit = agenda_edit[agenda_edit.Data == data_agenda]
    #agenda_edit = st.data_editor(agenda_edit[layout['Agenda_edit']],width=1500, column_config = {'Inizio':st.column_config.TimeColumn("Inizio",min_value=time(6, 0),max_value=time(20, 0),format="hh:mm "),
  #                                                                                            'Fine':st.column_config.TimeColumn("Fine",min_value=time(6, 0),max_value=time(20, 0),format="hh:mm ")})
    try:
        open_agenda = (agenda_edit.lat.iloc[0],  agenda_edit.lng.iloc[0])
    except:
        open_agenda = inizio

    mappa2=folium.Map(location=open_agenda,zoom_start=13)
    for i in range(len(agenda_edit)):
        try:
            folium.Marker(location=(agenda_edit.lat.iloc[i],agenda_edit.lng.iloc[i]),
                          popup = agenda_edit.Cliente.iloc[i]+'----------'+ agenda_edit.Servizio.iloc[i]+'--------- Durata: '+
                        str(agenda_edit['Durata_stimata'].iloc[i])).add_to(mappa2)
        except:
            st.write('Cliente {} non visibile sulla mappa per mancanza di coordinate su Byron'.format(agenda_edit.Cliente.iloc[i]))
            pass
    with cx5:    
        folium_static(mappa2,width=1200,height=500)

    agenda_edit = st.data_editor(agenda_edit[layout['Agenda_edit']], on_change=None)
    submit_button2 = st.button(label='Modifica agenda', on_click=callback_modifica_agenda)

    abilita_rimozione = st.toggle('Rimuovi interventi pianificati')
    if abilita_rimozione:
        modifica_agenda = st.session_state.agenda.copy()
        modifica_agenda = modifica_agenda[modifica_agenda.Data == data_agenda]
        modifica_agenda = modifica_agenda[modifica_agenda['Operatore']==op_modifica]
        modifica_agenda = st.data_editor(modifica_agenda[layout['Layout_select']])
        remove_button = st.button(label='Rimuovi interventi', on_click=callback4)


submit_button3 = st.sidebar.button('Refresh', on_click=refresh)


with tab6:

    pass