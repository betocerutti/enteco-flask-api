from sqlalchemy.orm import Session
from sqlalchemy.sql import text

from exceptions import EmpresaNoEncontradaError, ClienteNoEncontradoError


def cliente_exist(empresa_id: int, cliente_id: int, session: Session):
    """
    Comprueba si un cliente existe en la base de datos
    Un cliente puede existir en varias empresas, por lo
    que se debe especificar la empresa, de lo contrario
    la consulta devolvería mas de un resultado.
    Lanza una excepción si no se encuentra el cliente
    o la empresa
    """

    # Nota: de momento la empresa es siempre Enteco Pharma
    # por lo que se comprueba que el id sea 10
    # Cuando esta situación cambie, se deberá hacer la
    # consulta de otra manera
    if empresa_id != 10:
        raise EmpresaNoEncontradaError
    
    # Definimos nuestra consulta pura
    raw_query = text("""
                    SELECT EMPRESA, CLIENTE_ID 
                    FROM GENERAL.GNR_CLIENTES 
                    WHERE CLIENTE_ID=:cliente_id 
                    AND EMPRESA=:empresa_id""")

    # Ejecutamos la consulta con lo parametros pasados
    cursor = session.execute(raw_query, {"empresa_id": empresa_id, 
                                         "cliente_id": cliente_id})
    
    result: list = cursor.mappings().all()

    # Comprobamos que el cliente existe
    if len(result) == 0:
        raise ClienteNoEncontradoError


def get_requerido_vacios(empresa_id: int, cliente_id: int, session: Session) -> list:

    # Definimos nuestra consulta pura
    raw_query = text("""
        SELECT 
                C.DESCRIPC
            -- , C.REQUERID
            -- , DECODE(FC.VALOR, NULL, C.VALODEFE, FC.VALOR) VALOR
        FROM 
                GENERAL.GNR_LINEOBSE C 
        LEFT JOIN GENERAL.GNR_CABEOBSE CO ON C.TIPO = CO.TIPO 
            AND C.CODIGO = CO.CODIGO
        LEFT JOIN FICHTECN.FIC_LINEOBCL FC ON C.TIPO = FC.TIPO 
            AND C.CODIGO = FC.CODIGO 
            AND C.CODILINE = FC.CODILINE 
            AND :cliente_id = FC.CLIENTE_ID
        WHERE 
            C.TIPO = 'OBSERVACIONES CLIENTES(FICHAS TECNICAS COMERCIAL)'
            AND C.APLICOME = 'S'
            AND C.REQUERID = 'S' 
            AND (VALOR IS NULL OR RTRIM(LTRIM(VALOR)) = '')
    """)

    # Ejecutamos la consulta con lo parametros pasados
    result = session.execute(raw_query, {"cliente_id": cliente_id})

    # Metemos los resultados en una lista para que podamos serializarlos
    data = [row[0] for row in result]

    return data