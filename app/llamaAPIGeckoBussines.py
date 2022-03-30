import pickle
import base64
import os
import pathlib
import matplotlib.pyplot as plt
plt.switch_backend('Agg') 

from datetime import date, datetime
from loguru import logger
from cryptopesosAPI.app.model.llamaAPIGeckoModel import obtener_lista_completa_ids_logos_activos
from cryptopesosAPI.app.model.llamaAPIGeckoModel import obtener_lista_completa_activos_model, obtener_grafica_historica
from cryptopesosAPI.app.model.llamaAPIGeckoModel import obtener_precios_activos,obtener_tendencias_actuales
from cryptopesosAPI.app.common.constantes import LISTA_ACTIVOS_PERMITIDOS, RUTA_ARCHIVO_LOG

logger.add(RUTA_ARCHIVO_LOG)

def actualiza_lista_logos_activos():
    aux_dict = {}
    data_id_map = obtener_lista_completa_ids_logos_activos()
    if not data_id_map:
        logger.error("No se pudo obtener la unformacion de CoinMarketCapAPI")

    try:
        for i in data_id_map:
            aux_dict[i.get("symbol")] = i.get("id")
        with open("lista_ids_coin_market_cap.pickle", 'wb') as f:
            logger.info("Escribiendo la lista de python con la info de marketcap en un archivo pickle")
            pickle.dump(aux_dict, f)
    except Exception as err:
        logger.error("Ocurrió un error al crear el archivo pickle: {}".format(str(err)))
    
    return aux_dict

def crea_grafica_b64(id_activo_gecko):
    a = obtener_grafica_historica(id_activo_gecko)
    x = []
    y = []
    for i in a.get("prices"):
        ts = i[0]
        ts /= 1000
        date = datetime.date(datetime.utcfromtimestamp(ts))
        x.append(date)
        y.append(i[1])
    
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(x, y,'#57D06E',linewidth=3)
    plt.axis('off')
    nombre_grafica = './{}.png'.format(str(datetime.now()))
    
    plt.savefig(nombre_grafica,bbox_inches='tight',dpi=100)
    
    with open(nombre_grafica, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())

    resultado = "data:image/png;base64," + encoded_string.decode("utf-8")

    os.remove(nombre_grafica)


    cambio_ultimo_dia = ((y[-1] - y[-2]) / y[-2]) * 100

    return resultado,cambio_ultimo_dia

def obtener_informacion_lista_completa_activos():
    resultado = []
    aux_dir = str(pathlib.Path().resolve())
    with open(aux_dir + "/app/business/lista_ids_coin_market_cap.pickle", "rb") as f:
        ids_activos_marketcap = pickle.load(f)

    aux_acrivos_permitidos = {}
    aux_ids_buscar = []
    lista_activos_gecko = obtener_lista_completa_activos_model()
    for i in lista_activos_gecko:
        if i.get("id") in LISTA_ACTIVOS_PERMITIDOS:
            aux_acrivos_permitidos[i.get("id")] = i.get("symbol").upper()
            aux_ids_buscar.append(i.get("id"))
    
    precios = obtener_precios_activos(aux_ids_buscar)

    for p in precios:
        dict_aux = {}
        id_activo_marketcap = ids_activos_marketcap.get(aux_acrivos_permitidos.get(p))
        dict_aux["name"] = p
        dict_aux["symbol"] = aux_acrivos_permitidos.get(p)
        dict_aux["id_activo_marketcap"] = id_activo_marketcap
        dict_aux["logo_link"] = 'https://s2.coinmarketcap.com/static/img/coins/64x64/{}.png'.format(str(id_activo_marketcap))
        dict_aux["mxn"] = "${:,.2f}".format(precios.get(p).get("mxn"))
        dict_aux["usd"] = "${:,.2f}".format(precios.get(p).get("usd"))
        graficab64,cambio_ultimo_dia = crea_grafica_b64(p)
        dict_aux["grafica"] = graficab64
        dict_aux["ult_dia"] = round(cambio_ultimo_dia,2)
        resultado.append(dict_aux)

    return resultado

def obtener_informacion_tendencias():
    resultado_tendencias = []
    dict_tendencias = obtener_tendencias_actuales()
    for i in dict_tendencias.get('coins'):
        precio = obtener_precios_activos([i.get('item').get("id")])

        aux_dict = {}
        aux_dict["id"] = i.get('item').get("id")
        aux_dict["name"] = i.get('item').get("name")
        aux_dict["symbol"] = i.get('item').get("symbol")
        aux_dict["img_link"] = i.get('item').get("large")

        resultado,cambio_ultimo_dia = crea_grafica_b64(i.get('item').get("id"))

        aux_dict["graficab64"] = resultado
        aux_dict["cambio_ultimo_dia"] = round(cambio_ultimo_dia,2)

        for j in precio:
            aux_dict["mxn"] = "${:,.2f}".format(precio.get(j).get("mxn"))
        
        resultado_tendencias.append(aux_dict)
        
    return resultado_tendencias[0:6]

if __name__ == "__main__":
    obtener_informacion_tendencias()
    
    