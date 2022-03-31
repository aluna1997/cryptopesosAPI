import pickle
import base64
import os
import pathlib
import matplotlib.pyplot as plt
plt.switch_backend('Agg') 

from datetime import date, datetime
from loguru import logger
from app.model.llamaAPIGeckoModel import obtener_lista_completa_ids_logos_activos
from app.model.llamaAPIGeckoModel import obtener_lista_completa_activos_model, obtener_grafica_historica
from app.model.llamaAPIGeckoModel import obtener_precios_activos,obtener_tendencias_actuales
from app.common.constantes import LISTA_ACTIVOS_PERMITIDOS, RUTA_ARCHIVO_LOG

logger.add(RUTA_ARCHIVO_LOG)

def actualiza_lista_logos_activos():
    """
    Función que llama al modelo que a su vez nos regresa la lista completa de los activos
    soportados por el API de CoinMarketCap, nos sirve para saber el id de cada activo y asi
    usarlo posteriormente para obtener los logos de manera gratuita
    """
    aux_dict = {}
    # Llamamos a la función del modelo que obtiene la información
    data_id_map = obtener_lista_completa_ids_logos_activos()
    if not data_id_map:
        logger.error("No se pudo obtener la unformacion de CoinMarketCapAPI")
    try:
        # Guardamos la información en un diccionario para obtener información
        # en tiempo constante
        for i in data_id_map:
            aux_dict[i.get("symbol")] = i.get("id")
        # Dado que el API de CoinMarketCap no es gratuita y tiene un límite muy pequeño de
        # consultas, guardamos el diccionario en un archivo pickle asi sólo gastamos una consulta
        # cada que sea realmente necesario
        with open("lista_ids_coin_market_cap.pickle", 'wb') as f:
            logger.info("Escribiendo la lista de python con la info de marketcap en un archivo pickle")
            pickle.dump(aux_dict, f)
    except Exception as err:
        logger.error("Ocurrió un error al crear el archivo pickle: {}".format(str(err)))
    
    return aux_dict

def crea_grafica_b64(id_activo_gecko):
    """
    Función que a partir de la información de fecha vs precio de un activo que nos proporciona 
    CoinGecko genera una gráfica en png
    """
    # Obtenemos la información para la gráfica
    a = obtener_grafica_historica(id_activo_gecko)
    x = []
    y = []
    for i in a.get("prices"):
        # Convertimos los milisegindos a segundos
        ts = i[0]
        ts /= 1000
        # Convertimos la fecha en un objeto de Python
        date = datetime.date(datetime.utcfromtimestamp(ts))
        x.append(date)
        y.append(i[1])
    
    # Creamos un objeto gráfica de Mathplotlib
    fig, ax = plt.subplots(figsize=(8, 6))
    # Generamos la gráfica
    ax.plot(x, y,'#57D06E',linewidth=3)
    # Quitamos los ejes
    plt.axis('off')

    # Exportamos la gráfica a un archivo png
    nombre_grafica = './{}.png'.format(str(datetime.now()))
    plt.savefig(nombre_grafica,bbox_inches='tight',dpi=100)
    
    # Convertimos la imagen a base64
    with open(nombre_grafica, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())

    resultado = "data:image/png;base64," + encoded_string.decode("utf-8")

    # Eliminamos la imagen que ya no se ocupa
    os.remove(nombre_grafica)

    # Obtenemos el porcentaje de cambio del precio de el día de ayer 
    # vs el día de hoy
    cambio_ultimo_dia = ((y[-1] - y[-2]) / y[-2]) * 100

    return resultado,cambio_ultimo_dia

def obtener_informacion_lista_completa_activos():
    """
    Función que obtiene la información de los precios actuales de los activos
    """
    resultado = []
    # Obtenemos los ids de los activos de CoinMarketCap
    aux_dir = str(pathlib.Path().resolve())
    with open(aux_dir + "/app/business/lista_ids_coin_market_cap.pickle", "rb") as f:
        ids_activos_marketcap = pickle.load(f)

    # Filtramos de todos los activos sólo los que tenemos permitidos en nuestra lista
    # esto con fines de sólo mostrar información básica de ejemplo y no saturar las peticiones
    aux_acrivos_permitidos = {}
    aux_ids_buscar = []
    lista_activos_gecko = obtener_lista_completa_activos_model()
    for i in lista_activos_gecko:
        if i.get("id") in LISTA_ACTIVOS_PERMITIDOS:
            aux_acrivos_permitidos[i.get("id")] = i.get("symbol").upper()
            aux_ids_buscar.append(i.get("id"))
    
    # Obtenemos la información de los precios de los activos que nos proporciona el 
    # API de CoinGecko
    precios = obtener_precios_activos(aux_ids_buscar)

    # Para que el front-end pueda interprear facilmente la información la encapsulamos
    # en un diccionario (json)
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
    """
    Función que ontiene la información de los activos que estan en el top de tendecia
    según el API de CoinGecko (la tendencia puede ir a la alta o a la baja)
    """
    resultado_tendencias = []
    # Llamamos al modelo para obtener la información
    dict_tendencias = obtener_tendencias_actuales()

    # Iteramos cada activo en tendencia
    for i in dict_tendencias.get('coins'):
        # Dado que ese endpoint no nos regresa el precio actual debemos
        # de llamar a otro endpoint que lo haga
        precio = obtener_precios_activos([i.get('item').get("id")])
        aux_dict = {}
        aux_dict["id"] = i.get('item').get("id")
        aux_dict["name"] = i.get('item').get("name")
        aux_dict["symbol"] = i.get('item').get("symbol")
        aux_dict["img_link"] = i.get('item').get("large")

        # Obtenemos la gráfica y el porcentaje de cambio del precio del último día
        resultado,cambio_ultimo_dia = crea_grafica_b64(i.get('item').get("id"))

        aux_dict["graficab64"] = resultado
        aux_dict["cambio_ultimo_dia"] = round(cambio_ultimo_dia,2)

        for j in precio:
            aux_dict["mxn"] = "${:,.2f}".format(precio.get(j).get("mxn"))
        
        resultado_tendencias.append(aux_dict)
        
    return resultado_tendencias[0:6]

if __name__ == "__main__":
    obtener_informacion_tendencias()
    
    