# # test_app.py
# import unittest
# from unittest.mock import MagicMock
#
# from fastapi.testclient import TestClient
#
# from app import app, get_database
#
#
# class TestApp(unittest.TestCase):
#     def setUp(self):
#         self.client = TestClient(app)
#         self.mock_db = MagicMock()
#         app.dependency_overrides[get_database] = lambda: self.mock_db
#
#     def test_create_simulation_empty_lights(self):
#         response = self.client.post('/simulation/create', json={
#             'population': 100,
#             'mutationRate': 0.1,
#             'selecteds': 2,
#             'lights': []
#         })
#         self.assertEqual(response.status_code, 400)
#         self.assertEqual(response.json()['detail'], 'A lista de semáforos não pode estar vazia')
#
#     def test_create_simulation_db_exception(self):
#         self.mock_db.get_session.side_effect = Exception('DB Error')
#         response = self.client.post('/simulation/create', json={
#             'population': 100,
#             'mutationRate': 0.1,
#             'selecteds': 2,
#             'lights': [{'redDuration': 30, 'greenDuration': 30, 'cycleStartTime': 0}]
#         })
#         self.assertEqual(response.status_code, 500)
#         self.assertIn('Erro ao criar simulação', response.json()['detail'])
#
#     def test_create_simulation_success(self):
#         self.mock_db.get_session.return_value = MagicMock()
#         response = self.client.post('/simulation/create', json={
#             'population': 100,
#             'mutationRate': 0.1,
#             'selecteds': 2,
#             'lights': [{'redDuration': 30, 'greenDuration': 30, 'cycleStartTime': 0}]
#         })
#         self.assertEqual(response.status_code, 200)
#         self.assertIn('id', response.json())
#
#
# if __name__ == '__main__':
#     unittest.main()
