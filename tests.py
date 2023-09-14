import unittest
from app import app, db

class TestApp(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        self.empresa_id = 10
        self.cliente_id = 1013
        self.api_url_ok = '/enteco/api-ora/observaciones-cliente/requerido-vacios/{empresa_id}/{cliente_id}'.format(
            empresa_id=self.empresa_id,
            cliente_id=self.cliente_id
        )
        self.api_url_wrong_client = '/enteco/api-ora/observaciones-cliente/requerido-vacios/{empresa_id}/{cliente_id}'.format(
            empresa_id=self.empresa_id,
            cliente_id=999999
        )
        self.api_url_wrong_empresa = '/enteco/api-ora/observaciones-cliente/requerido-vacios/{empresa_id}/{cliente_id}'.format(
            empresa_id=999999,
            cliente_id=self.cliente_id
        )

    def test_sample_route(self):
        response = self.app.get(self.api_url_ok)
        self.assertEqual(response.status_code, 200)
        # comprobamos que el resultado es una lista
        self.assertIsInstance(response.json, list)

    def test_cliente_no_encontrado(self):
        response = self.app.get(self.api_url_wrong_client)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json, {'error': 'Cliente no encontrado'})

    def test_empresa_no_encontrada(self):
        response = self.app.get(self.api_url_wrong_empresa)
        assert response.status_code == 404
        assert response.json == {'error': 'Empresa no encontrada'}

    def tearDown(self) -> None:
        return super().tearDown()
    
if __name__ == '__main__':
    unittest.main()
