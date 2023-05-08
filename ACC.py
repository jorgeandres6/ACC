##Libraries
import time
import copy
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
import csv
import pandas as pd
import openai
from openpyxl import load_workbook

##----------------FUNCIONES-----------------

##---------------RECIVIR OPENAI K-----------

def getOK ():
    with open("") as tsv:
        print ('') ##-------------------CAMBIAR AQUI!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

##----------------AGREGA DATOS DE RAZON SOCIAL A LA BBDD
def agregarDatos (data, archivo):

    workbook_name = archivo
    wb = load_workbook(workbook_name)
    page = wb.active
    page.append(data)
    wb.save(filename=workbook_name)

    """ with open(archivo, mode='a') as file:
        wr = csv.writer(file)
        wr.writerow(data)
    file.close() """

##-----------FUNCION PARA CONSULTAR LA ACTIVIDAD PRINCIPAL DE LA RAZON SOCIAL
def busquedaRS (driver, rs):
    newTab = "window.open('about:blank','secondtab');"
    driver.execute_script(newTab)
    driver.switch_to.window("secondtab")
    driver.get('https://srienlinea.sri.gob.ec/sri-en-linea/SriRucWeb/ConsultaRuc/Consultas/consultaRuc')
    time.sleep(5) ##ESPERA CARGA DE PAGINA
    razSocb = driver.find_element(By.XPATH, '//*[@id="sribody"]/sri-root/div/div[2]/div/div/sri-consulta-ruc-web-app/div/sri-ruta-ruc/div[2]/div[1]/div[1]/div[2]/div/div[2]/button') ##BOTON SELECCIONAR RAZON SOCIAL
    razSocb.click() ##CLICK SELECCION RAOZN SOCIAL

    razSocI = driver.find_element(By.XPATH, '//*[@id="busquedaRazonSocialId"]') ##INPUT RAZON SOCIAL
    razSocI.send_keys(rs) ##INSERTAR LA RAZON SOCIAL
    time.sleep(5) ##ESPERA VERIFICACION RAZON SOCIAL

    verRS = driver.find_element(By.XPATH, '//*[@id="sribody"]/sri-root/div/div[2]/div/div/sri-consulta-ruc-web-app/div/sri-ruta-ruc/div[2]/div[1]/div[6]/div[2]/div/div[2]/div/button') ##BOTON CONSULTAR RAZON SOCIAL
    verRS.click() ##CLICK PARA CONSULTAR RAZON SOCIAL
    time.sleep(4) ##ESPERA CARGA DE PAGINA

    actPrin = driver.find_elements(By.XPATH, '//*[@id="sribody"]/sri-root/div/div[2]/div/div/sri-consulta-ruc-web-app/div/sri-ruta-ruc/div[2]/div[1]/sri-mostrar-contribuyente/div[1]/div[4]/div/div[2]/span/div/div/table/thead/tr[2]/td') ##ACTIVIDAD PRINCIPAL

    if len(actPrin) < 1:
        actPrin = driver.find_elements(By.XPATH, '//*[@id="sribody"]/sri-root/div/div[2]/div/div/sri-consulta-ruc-web-app/div/sri-ruta-ruc/div[2]/div[1]/sri-mostrar-contribuyente/div[4]/div/div[1]/div[2]/table/tbody/tr/td') ##ACTIVIDAD PRINCIPAL
        if len(actPrin) < 1:
            input("ReChaptcha...")
            actPrin = driver.find_elements(By.XPATH, '//*[@id="sribody"]/sri-root/div/div[2]/div/div/sri-consulta-ruc-web-app/div/sri-ruta-ruc/div[2]/div[1]/sri-mostrar-contribuyente/div[1]/div[4]/div/div[2]/span/div/div/table/thead/tr[2]/td') ##ACTIVIDAD PRINCIPAL
            if len(actPrin) < 1:  
                actPrin = driver.find_elements(By.XPATH, '//*[@id="sribody"]/sri-root/div/div[2]/div/div/sri-consulta-ruc-web-app/div/sri-ruta-ruc/div[2]/div[1]/sri-mostrar-contribuyente/div[4]/div/div[1]/div[2]/table/tbody/tr/td') ##ACTIVIDAD PRINCIPAL
                    
    query = rs+' '+actPrin[0].text

    driver.close()
    driver.switch_to.window("firsttab")
    
    return(query)
    ##print (rs)

##--------------------CLASIFICAR LA ACTIVIDAD PRINCIPAL
def clasificarActividad (actividad): 
    clase = ''
    if actividad.find("ALIMENTACIÓN") != -1:
        clase = "ALIMENTACIÓN"
    elif actividad.find("VIVIENDA") != -1:
        clase = "VIVIENDA"
    elif actividad.find("SALUD") != -1:
        clase = "SALUD"
    elif actividad.find("EDUCACIÓN") != -1:
        clase = "EDUCACIÓN"
    elif actividad.find("CULTURA") != -1:
        clase = "CULTURA"
    elif actividad.find("DEPORTE") != -1:
        clase = "DEPORTE"
    elif actividad.find("COMUNICACIÓN") != -1:
        clase = "COMUNICACIÓN"
    elif actividad.find("VESTIMENTA") != -1:
        clase = "VESTIMENTA"
    elif actividad.find("TRANSPORTE") != -1 or actividad.find("MOVILIDAD") != -1 or actividad.find("TRANSPORTE Y MOVILIDAD") != -1:
        clase = "TRANSPORTE Y MOVILIDAD"
    else:
        input ("Verificar clase")
    return clase

##----------------OBTENCIÓN DE DATOS DEL USUARIO
def dataUs ():
    df = pd.read_excel('DECLARACIONES.xlsx', sheet_name='Sheet1')
    for index in range(len(df['DECLARACION'])):
        if  (df['DECLARACION'][index] == 'P'):
            df['DECLARACION'][index] = principal (str(df['CEDULA'][index]), df['PSW'][index], str(df['ANO'][index]), df['MES'][index])
            with pd.ExcelWriter("DECLARACIONES.xlsx",mode="a",engine="openpyxl",if_sheet_exists="replace") as writer:
                ##pd.write_excel(writer,df)
                df.to_excel(writer, sheet_name="Sheet1")

##-------------------MAX DE DEVOLUCION POR AÑO
def maxDev (yy):
    if (yy == '2023'):
        return 108
    elif (yy == '2022'):
        return 102

##-------------------CORE
def principal (ced, pas, yy, mm):

    ##----------------VARIABLES

    driver = webdriver.Chrome() ##Elegir el browser

    cont = 0 ##Contador para elegir solo la extraccion de facturas

    cont2 = 0 ##Contador ubicacion barra navegacion paginas de facturas

    num_pags = 1 ##Numero de paginas de facturas total

    individuo = [] ##Datos de cada factura

    data = [] ##Cojunto de individuos

    total_dev=0 ##Devolucion total

    aux_tot_dev=0 ##Control valor a devolverse

    pagina_actual=1 ##Numero de pagina actual.

    tipo_gasto="OTROS" ##Tipo de gasto

    encuentro = 0 ##VARIABLE PARA SABER SI SE ENCONTRO EL COMERCIO

    userID = ced ##CEDULA DEL USUARIO

    pascode = pas ##PASSWORD

    ano = yy ##AÑO A SOLICITAR

    mes = mm ##MES A SOLICITAR

    prompt = "" ##PROMP PARA CHATGPT

    quer1='' ##RAZON SOCIAL Y ACTIVIDAD PRINCIPAL

    quer2 = ' clasificalo de acuerdo a las siguientes clases: ALIMENTACIÓN, VIVIENDA, SALUD, EDUCACIÓN, CULTURA, DEPORTE, COMUNICACIÓN, VESTIMENTA o TRANSPORTE Y MOVILIDAD' ##CONSULTA PARA CHATGPT

    max_dev = 108 ##DEVOLUCION MAXIMA POR AÑO

    ##---------PROGRAMA PRINCIPAL-------------------

    max_dev =  maxDev (yy) ##Calculo del maximo a devolver en ese año

    ##Login
    firstTab = "window.open('about:blank','firsttab');"
    driver.execute_script(firstTab)
    driver.switch_to.window("firsttab")
    driver.get('https://srienlinea.sri.gob.ec/auth/realms/Internet/protocol/openid-connect/auth?client_id=app-sri-claves-angular&redirect_uri=https%3A%2F%2Fsrienlinea.sri.gob.ec%2Fsri-en-linea%2F%2Fcontribuyente%2Fperfil&state=50eea84b-44db-4fb0-8adc-6330da3dfa04&nonce=2bb86d5d-5cae-4bfe-8cc9-6ba12524d708&response_mode=fragment&response_type=code&scope=openid')
    time.sleep(1)
    try:
        cedula = driver.find_element(By.XPATH, '//*[@id="usuario"]')
        psw = driver.find_element(By.XPATH, '//*[@id="password"]')
    except:
        print ("La pagina no carga")
    cedula.send_keys(userID)
    psw.send_keys(pascode)
    time.sleep(1)
    submit = driver.find_element(By.XPATH,'//*[@id="kc-login"]')
    submit.click()
    time.sleep(20)
    try:
        devol = driver.find_element(By.XPATH,'//*[@id="mySidebar2"]/div[11]/div/button')
        devol.click()
    except:
        print ("no se pudo acceder a la plataforma")
    time.sleep(1)
    devol_sub = driver.find_element(By.XPATH,'//*[@id="mySidebar"]/p-panelmenu/div/div[10]/div[2]/div/p-panelmenusub/ul/li[2]/a')
    devol_sub.click()
    time.sleep(1)
    init_proc = driver.find_element(By.XPATH,'//*[@id="j_id436:j_id445"]')
    init_proc.click()
    time.sleep(2)
    init_proc_acc = driver.find_element(By.XPATH,'//*[@id="frmConfirmacionCiudadDevolucion:j_id342"]')
    init_proc_acc.click()
    time.sleep(2)
    init_proc_cuenta = driver.find_element(By.XPATH,'//*[@id="frmConvenioDebito:tblConvenios:0:j_id373"]')
    init_proc_cuenta.click()
    time.sleep(5)
    init_proc_fin = driver.find_element(By.XPATH,'//*[@id="j_id320:j_id325"]')
    init_proc_fin.click()
    time.sleep(8)
    select_y_elem=driver.find_element(By.XPATH,'//*[@id="j_id142:cmbAnio"]')
    select_y = Select(select_y_elem)
    select_y.select_by_visible_text(ano)
    time.sleep(1)
    select_m_elem=driver.find_element(By.XPATH,'//*[@id="j_id142:cmbPeriodo"]')
    select_m = Select(select_m_elem)
    select_m.select_by_visible_text(mes)
    sub_date = driver.find_element(By.XPATH,'//*[@id="j_id142:btnBuscarComprobantesElectronicos"]')
    sub_date.click()
    time.sleep(10)

    ##ENCONTRAR LA BARRA INFERIOR DE NAVEGACION

    ##tabla_factura = driver.find_element(By.XPATH,'//*[@id="j_id142:tblFacturas:paginadorFactura_table"]') ##Elemento tabla que contiene datos de las facturas
    tabla_factura = driver.find_element(By.XPATH,'//*[@id="j_id142:tblFacturas:paginadorFactura_table"]/tbody/tr') ##Elemento tabla que contiene datos de las facturas
    tabla_factura2 = driver.find_element(By.XPATH,'//*[@id="j_id142:tblFacturas:tb"]') ##Elemento tabla que contiene datos de las facturas

    ##contenido = tabla_factura.find_elements(By.TAG_NAME,'tr') ##Elementos individuales de la tabla
    contenido2 = tabla_factura2.find_elements(By.TAG_NAME,'tr') ##Elementos individuales de la tabla
    """ for tr in contenido: ##Loop para las filas de la tabla
        if (cont >= 0): ##Solo obtener datos de las facturas
            print ('--------------------cont',cont)
            for td in tr.find_elements(By.TAG_NAME,'td'): ##Loop datos de cada fila
                print (td.text)
                cont2+=1
        cont+=1
    cont=0 """
    for td in tabla_factura.find_elements(By.TAG_NAME,'td'): ##Loop datos de cada fila
        ##print (td.text)
        cont2+=1
    ##cont2 == len(contenido)
    print ('cont2------',cont2)
    pos_btn_next = cont2-1 ##Posicion del boton next facturas
    if(cont2 < 7):
        cont2 = 7
    num_pags = cont2-6 ##Numero de pags de facturas
    ##print ("NP",num_pags)
    ##btn_next = driver.find_element(By.XPATH,'//*[@id="j_id142:tblFacturas:paginadorFactura_table"]/tbody/tr/td['+str(pos_btn_next)+']/a')  ##Boton siguiente pagina facturas

    ##IMPORTAR DATOS DE LOS COMERCIOS

    df = pd.read_excel('DATA_ENTRENAMIENTO.xlsx', sheet_name='Sheet1')

    ##LECTURA DE DATOS DE LAS FACTURAS

    for i in range(num_pags):

        for tr in contenido2:
            if (cont >= 0):
                ##print ("--------------------")
                pos = 0
                for td in tr.find_elements(By.TAG_NAME,'td'):
                    print(td.text)
                    if pos <= 6:
                        individuo.append(td.text)
                    pos+=1

                    if pos == 3:
                        ##BUSCAR RAZON SOCIAL EN BBDD
                        for razon in range(len(df['RAZON'])):
                            if df['RAZON'][razon].find(individuo[2]) != -1:
                                tipo_gasto = df['CLASE'][razon]
                                encuentro = 1
                                break
                        if encuentro < 1: ##SI NO SE ENCUENTRA LA RAZON SOCIAL
                            ##print (individuo[2])
                            quer1 = busquedaRS (driver, individuo[2])
                            prompt='"'+quer1+'"'+quer2
                            print ("prompt",prompt)
                            openai.api_key="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"
                            comp = openai.Completion.create(engine="text-davinci-003",prompt=prompt, max_tokens=2048)
                            print (comp.choices[0].text)
                            ##time.sleep(2)
                            clase = clasificarActividad (comp.choices[0].text.upper())
                            print (clase)
                            data_salv=[quer1,clase]
                            agregarDatos (data_salv, 'DATA_ENTRENAMIENTO.xlsx')
                            tipo_gasto = clase
                            df = pd.read_excel('DATA_ENTRENAMIENTO.xlsx', sheet_name='Sheet1')
                            ##input("NO ESTA EN LA BBDD")

                        encuentro = 0

                    if pos == 6:
                        aux_tot_dev += float(individuo[5])

                    if aux_tot_dev <= max_dev:
                        ##COMPLETAR DATOS PARA LA DEVOLUCION
                        if pos == 7: ##VALOR DEL IVA
                            td.find_element(By.TAG_NAME,'input').send_keys(individuo[5])
                        if pos == 8: ##TIPO DE GASTO
                            td.find_element(By.TAG_NAME,'select').send_keys(tipo_gasto)
                        if pos == 9: ##SELECCIONAR FACTURA
                            td.find_element(By.TAG_NAME,'input').click()
                ##print ("--------------------",cont)
                ##print ("individuo--------------",individuo)
                if aux_tot_dev <= max_dev:
                    data.append(copy.deepcopy(individuo))
                else:
                    if (len(individuo)>0):
                        aux_tot_dev -= float(individuo[5])
                print ("TOTAL ACTUAL",aux_tot_dev)
                individuo.clear()
            cont+=1
        cont=0 ##Reiniciar contador despues del proceso de lectura
        ##print ("data-------------------------------",data)

        ##SUMATORIA TOTAL DE LOS VALORES

        ##NAVEGACION A LA SIGUIENTE PAGINA DE LAS FACTURAS

        btn_next = driver.find_element(By.XPATH,'//*[@id="j_id142:tblFacturas:paginadorFactura_table"]/tbody/tr/td['+str(pos_btn_next)+']/a')  ##Boton siguiente pagina facturas

        btn_next.click() ##Boton siguiente pagina facturas

        time.sleep(2)

        ##----------------------------
        ##tabla_factura = driver.find_element(By.XPATH,'//*[@id="j_id142:tblFacturas"]') ##Elemento tabla que contiene datos de las facturas
        ##contenido = tabla_factura.find_elements(By.TAG_NAME,'tr') ##Elementos individuales de la tabla
        
        tabla_factura2 = driver.find_element(By.XPATH,'//*[@id="j_id142:tblFacturas:tb"]') ##Elemento tabla que contiene datos de las facturas
        contenido2 = tabla_factura2.find_elements(By.TAG_NAME,'tr') ##Elementos individuales de la tabla
      
        """for tr in contenido: ##Loop para las filas de la tabla
            if (cont == 3): ##Solo obtener datos de las facturas
                print ('--------------------cont',cont)
                for td in tr.find_elements(By.TAG_NAME,'td'): ##Loop datos de cada fila
                    print (td.text)
            cont+=1
        cont=0"""
        ##----------------------------

        ##print ('cont2', cont2)

    for ind in data:
        total_dev+=float(ind[5])

    print ('total',round(total_dev,2))

    btn_proc = driver.find_element(By.XPATH,'//*[@id="j_id142:btnGuardarFacturasSeleccionadas"]')  ##Boton procesamiento de facturas

    btn_proc.click() ##Boton procesar facturas

    input("Revisar")

    time.sleep(2) ##ESPERAR A QUE APARESCA RESUMEN DE FACTURAS PROCESADAS

    btn_guardar_proc = driver.find_element(By.XPATH,'//*[@id="j_id142:btnFinalizarCargaComprobantesElectronicos"]')  ##Boton GUARDAR FACTURAS PROCESADAS

    btn_guardar_proc.click() ##Boton GUARDAR FACTURAS PROCESADAS

    time.sleep(3) ##ESPERAR A CARGA DE PAGINA

    btn_enviar_sol = driver.find_element(By.XPATH,'//*[@id="j_id320:j_id333"]')  ##Boton ENVIAR SOLICITUD

    btn_enviar_sol.click() ##Boton ENVIAR SOLICITUD

    time.sleep(3) ##ESPERAR A CARGA DE PAGINA

    btn_cargar_sol = driver.find_element(By.XPATH,'//*[@id="j_id12:btnCargarInformacion"]')  ##Boton CARGAR SOLICITUD

    btn_cargar_sol.click() ##Boton CARGAR SOLICITUD

    with open(userID+'_'+ano+'_'+mes+'.csv', 'w') as myfile:
        wr = csv.writer(myfile)
        wr.writerows(data)


    ##ESPERA FINAL
    input("FIN DEL PROCESO")
    return ("F")

##----------------FLUJO PRINCIPAL----------------------
##principal('1704464575','minas1135')
dataUs ()