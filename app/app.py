from loguru import logger
from flask import Flask, jsonify
from flask_restful import Resource, Api


app = Flask(__name__)
api = Api(app)

class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}

api.add_resource(HelloWorld, '/')

if __name__ == '__main__':
    app.run(debug=True)

'''
from cryptopesosAPI.app.common.constantes import RUTA_ARCHIVO_LOG
from cryptopesosAPI.app.business.llamaAPIGeckoBussines import obtener_informacion_lista_completa_activos
from cryptopesosAPI.app.business.llamaAPIGeckoBussines import obtener_informacion_tendencias
'''
#app = Flask(__name__)

#logger.add(RUTA_ARCHIVO_LOG)

'''
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



@app.route('/hola/', methods=['GET'])
def hola_flask():
   return "<p>Hola</p>"

'''