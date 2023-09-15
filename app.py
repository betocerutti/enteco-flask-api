from flask import Flask, jsonify, Blueprint, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import logging

from exceptions import EmpresaNoEncontradaError, ClienteNoEncontradoError
from queries import cliente_exist, get_requerido_vacios


app = Flask(__name__)
api = Api(app, version='0.1', 
          title='Enteco API', 
          description='API para Enteco Pharma',
          doc='/enteco/api-ora/docs',
          default='Enteco API',
          default_label='Enteco API',
          validate=True,
          ordered=True,
          catch_all_404s=True,
          errors={
              'EmpresaNoEncontradaError': {
                  'status': 404,
                  'message': 'Empresa no encontrada'
                  },
                  'ClienteNoEncontradoError': {
                      'status': 404,
                      'message': 'Cliente no encontrado'
                      },
                      'Exception': {
                          'status': 500,
                          'message': 'Fallo en el servidor'
                          }
            }
)


# Definimos la ruta de la API
bp = Blueprint('common', __name__, url_prefix='/enteco/api-ora')

# Configuramos la conexión a la base de datos
username = 'alfredo'
password = '9'
hostname = '192.168.106.59'
port = 1521
service_name = 'ENTECO'
app.config['SQLALCHEMY_DATABASE_URI'] = 'oracle://{username}:{password}@{hostname}:{port}/{service_name}'.format(
    username=username, password=password, hostname=hostname, port=port, service_name=service_name
)
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])

# Configuramos el log de SQLAlchemy
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Configuramos el log de Flask
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
logging.FileHandler('error.log')
app.logger.addHandler(log)

# Iniciamos SQLAlchemy
db = SQLAlchemy(app)

# Definimos la base para todas las URLs
API_URL = '/enteco/api-ora'
    

@api.route('/enteco/api-ora/observaciones-cliente/requerido-vacios/<int:empresa_id>/<cliente_id>')
class ObservacionesClienteVacias(Resource):

    def get(self, empresa_id: int, cliente_id: int):
        """
        Devuelve los campos que faltan por rellenar en las observaciones
        de un cliente nuevo.
        """
        session = Session(engine)

        try:
            # Comprobamos que el cliente existe
            cliente_exist(empresa_id, cliente_id, session)
            result = get_requerido_vacios(empresa_id, cliente_id, session)
        except EmpresaNoEncontradaError:
            return {'error': 'Empresa no encontrada'}, 404
        except ClienteNoEncontradoError:
            return {'error': 'Cliente no encontrado'}, 404
        except Exception as e:
            # Guardamos el error en un log
            log.error(e)
            return {'error': 'Fallo en el servidor'}, 500
        finally:
            # Cerramos la sesión
            session.close()

        # Devolvemos los datos y el estado de la solicitud
        return result, 200
    


# Registramos el blueprint
app.register_blueprint(bp)

if __name__== '__main__':
    app.run()

