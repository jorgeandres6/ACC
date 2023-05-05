##Libraries
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
import csv

init = 0 ##Auxiliar para ignorar la cabecera "RAZON SOCIAL"

comercios = []
actPrinL = [['ACTIVIDAD PRINCIPAL']]

with open('DataCom.csv', mode='r') as file:
    reader = csv.reader(file)
    for row in reader:
        if init > 0:
            comercios.append(row[0])
        init = 1
file.close()
init = 0

driverCom = webdriver.Chrome() ##Elegir el browser

firstTab = "window.open('about:blank','firsttab');"
driverCom.execute_script(firstTab)
driverCom.switch_to.window("firsttab")
driverCom.get('https://srienlinea.sri.gob.ec/sri-en-linea/SriRucWeb/ConsultaRuc/Consultas/consultaRuc')
time.sleep(5) ##ESPERAR A QUE CARGA LA PAGINA INICIAL

for rz in comercios:
    razSocb = driverCom.find_element(By.XPATH, '//*[@id="sribody"]/sri-root/div/div[2]/div/div/sri-consulta-ruc-web-app/div/sri-ruta-ruc/div[2]/div[1]/div[1]/div[2]/div/div[2]/button') ##BOTON SELECCIONAR RAZON SOCIAL
    razSocb.click() ##CLICK SELECCION RAOZN SOCIAL

    razSocI = driverCom.find_element(By.XPATH, '//*[@id="busquedaRazonSocialId"]') ##INPUT RAZON SOCIAL
    razSocI.send_keys(rz) ##INSERTAR LA RAZON SOCIAL
    time.sleep(5) ##ESPERA VERIFICACION RAZON SOCIAL

    verRS = driverCom.find_element(By.XPATH, '//*[@id="sribody"]/sri-root/div/div[2]/div/div/sri-consulta-ruc-web-app/div/sri-ruta-ruc/div[2]/div[1]/div[6]/div[2]/div/div[2]/div/button') ##BOTON CONSULTAR RAZON SOCIAL
    verRS.click() ##CLICK PARA CONSULTAR RAZON SOCIAL
    time.sleep(4) ##ESPERA CARGA DE PAGINA

    """ dataRZ = driverCom.find_element(By.XPATH, '//*[@id="sribody"]/sri-root/div/div[2]/div/div/sri-consulta-ruc-web-app/div/sri-ruta-ruc/div[2]/div[1]/sri-mostrar-contribuyente/div[4]') ##ACTIVIDAD PRINCIPAL

    dataRZin = dataRZ.find_element(By.TAG_NAME,"div")

    dataRZin2 = dataRZin.find_elements(By.TAG_NAME,"div")

    dataRZin3 = dataRZin2[1].find_elements(By.TAG_NAME,"table") """

    actPrin = driverCom.find_elements(By.XPATH, '//*[@id="sribody"]/sri-root/div/div[2]/div/div/sri-consulta-ruc-web-app/div/sri-ruta-ruc/div[2]/div[1]/sri-mostrar-contribuyente/div[1]/div[4]/div/div[2]/span/div/div/table/thead/tr[2]/td') ##ACTIVIDAD PRINCIPAL

    if len(actPrin) < 1:
        actPrin = driverCom.find_elements(By.XPATH, '//*[@id="sribody"]/sri-root/div/div[2]/div/div/sri-consulta-ruc-web-app/div/sri-ruta-ruc/div[2]/div[1]/sri-mostrar-contribuyente/div[4]/div/div[1]/div[2]/table/tbody/tr/td') ##ACTIVIDAD PRINCIPAL
        if len(actPrin) < 1:
            input("ReChaptcha...")
            actPrin = driverCom.find_elements(By.XPATH, '//*[@id="sribody"]/sri-root/div/div[2]/div/div/sri-consulta-ruc-web-app/div/sri-ruta-ruc/div[2]/div[1]/sri-mostrar-contribuyente/div[1]/div[4]/div/div[2]/span/div/div/table/thead/tr[2]/td') ##ACTIVIDAD PRINCIPAL
            if len(actPrin) < 1:  
                actPrin = driverCom.find_elements(By.XPATH, '//*[@id="sribody"]/sri-root/div/div[2]/div/div/sri-consulta-ruc-web-app/div/sri-ruta-ruc/div[2]/div[1]/sri-mostrar-contribuyente/div[4]/div/div[1]/div[2]/table/tbody/tr/td') ##ACTIVIDAD PRINCIPAL
                    
    print(actPrin[0].text)
    actPrinL.append(actPrin[0].text.split()) ##AGREGAR ACTIVIDAD PRINCIPAL

    nuevaConsulta = driverCom.find_element(By.XPATH, '//*[@id="sribody"]/sri-root/div/div[2]/div/div/sri-consulta-ruc-web-app/div/sri-ruta-ruc/div[3]/div/div[4]/div/button') ##BOTON NUEVA CONSULTA
    nuevaConsulta.click() ##CLICK PARA NUEVA CONSULTA
    time.sleep(2) ##ESPERA CARGA DE PAGINA

""" with open('DataCom.csv', mode='a', newline='') as file:
    writer = csv.writer(file)
    for i in actPrinL:
        writer.writerow(i) """

with open('DataCom.csv', 'a') as myfile:
    wr = csv.writer(myfile)
    wr.writerows(actPrinL)

file.close()

time.sleep(5) ##ESPERA PARA REVISION FINAL

##print(comercios[5])