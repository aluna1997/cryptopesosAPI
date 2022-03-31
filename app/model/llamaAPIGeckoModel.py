import coinmarketcapapi
import requests
import base64

from flask import request
from loguru import logger
from pycoingecko import CoinGeckoAPI
from app.common.constantes import IMG_LOGO_DEFAULT, RUTA_ARCHIVO_LOG

logger.add(RUTA_ARCHIVO_LOG)

def obtener_lista_completa_activos_model():
    """
    Función que obtiene la lita completa de activos soportados por 
    CoinGecko
    """
    coins = []
   
    # Instancia de objeto coin gecko que nos ayuda a llamar al API oficial
    # a través de funciones de Python
    cg = CoinGeckoAPI()
    logger.info("Obteniendo lista completa de activos")
   
    try:
        # Función que ontiene la lista completa de los activos soportados por
        # CoinGecko
        coins = cg.get_coins_list()
    except Exception as err:
        logger.error("Ocurrio un error al obtener la lista completa de activos {}".format(str(err)))
    
    return coins

def obtener_lista_completa_ids_logos_activos():
    """
    Función que obtiene la lista completa de ids de las monedas de CoinMarketCapAPI
    """
    data_id_map = []
    cmc = coinmarketcapapi.CoinMarketCapAPI()
    logger.info("Coinsultando al API oficial de coin marketcap")
    try:
        data_id_map = cmc.cryptocurrency_map().data
    except Exception as err:
        logger.error("Ocurrió un error al consultar al API de marketcap: {}".format(str(err)))
    
    return data_id_map

def obtener_precios_activos(ids,moneda=['usd', 'mxn']):
    cg = CoinGeckoAPI()
    resultado = {}
    logger.info("Obteniendo precio de activos")
    try:
        resultado = cg.get_price(ids,vs_currencies=moneda)
    except Exception as err:
        logger.error("Ocurrió un error al consultar al API de CoinGeckoAPI: {}".format(str(err)))
    return resultado

def obtener_grafica_historica(id):
    try:
        cg = CoinGeckoAPI()
        return cg.get_coin_market_chart_by_id(id,"mxn",300)
    except Exception as err:
        logger.error("Ocurrió un error al obtener la info del historico del activo: {}".format(str(err)))

def obtener_tendencias_actuales():
    try:
        cg = CoinGeckoAPI()
        return cg.get_search_trending()
    except Exception as err:
        logger.error("Ocurrió un error al obtener la info de tendencias: {}".format(str(err)))

if __name__ == "__main__":
    cg = CoinGeckoAPI()
    a = cg.get_search_trending()
    for i in a.get('coins'):
        print(i.get('item'))
        print('')

