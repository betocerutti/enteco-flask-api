from flask import Flask, jsonify, Blueprint
from flask_restx import Api
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import logging

from exceptions import EmpresaNoEncontradaError, ClienteNoEncontradoError
from queries import cliente_exist, get_requerido_vacios


app = Flask(__name__)
api = Api(app, version='1.0', title='Enteco API')


# Definimos la ruta de la API
common_bp = Blueprint('common', __name__, url_prefix='/enteco/api-ora')

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
    

@common_bp.route('/observaciones-cliente/requerido-vacios/<int:empresa_id>/<cliente_id>',
                 methods=['GET'])
def get_observaciones(empresa_id: int, cliente_id: int):
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
        return jsonify({'error': 'Empresa no encontrada'}), 404
    except ClienteNoEncontradoError:
        return jsonify({'error': 'Cliente no encontrado'}), 404
    except Exception as e:
        # Guardamos el error en un log
        log.error(e)
        return jsonify({'error': 'Fallo en el servidor'}), 500
    finally:
        # Cerramos la sesión
        session.close()

    # Devolvemos los datos y el estado de la solicitud
    return jsonify(result), 200


# Registramos el blueprint
app.register_blueprint(common_bp)

if __name__== '__main__':
    app.run()

