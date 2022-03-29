from loguru import logger
from flask import Flask
from cryptopesosAPI.common.constantes import RUTA_ARCHIVO_LOG
from flask import jsonify
from cryptopesosAPI.business.llamaAPIGeckoBussines import obtener_informacion_lista_completa_activos
from cryptopesosAPI.business.llamaAPIGeckoBussines import obtener_informacion_tendencias
app = Flask(__name__)

logger.add(RUTA_ARCHIVO_LOG)

@app.route('/precios/', methods=['GET'])
def obtener_info_precios():
    logger.debug("Obteniendo la información completa de los precios")
    resultado = obtener_informacion_lista_completa_activos()
    resultado = jsonify(resultado)
    resultado.headers.add('Access-Control-Allow-Origin', '*')
    return resultado

@app.route('/tendencias/', methods=['GET'])
def obtener_info_tendencias():
    logger.debug("Obteniendo la información completa de las tendencias")
    resultado = obtener_informacion_tendencias()
    resultado = jsonify(resultado)
    resultado.headers.add('Access-Control-Allow-Origin', '*')
    return resultado
    
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)