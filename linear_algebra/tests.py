from django.test import TestCase, Client
from django.urls import reverse
from . import math_engine

class MathEngineTests(TestCase):
    def test_gaussian_elimination(self):
        matrix = [[1, 2, 3], [4, 5, 6]]
        res = math_engine.solve_gaussian_elimination(matrix)
        self.assertIn('steps', res)
        self.assertGreater(len(res['steps']), 0)
        self.assertIn('solution_type', res)

    def test_gf2_arithmetic(self):
        add_res = math_engine.solve_gf2_arithmetic(1, 1, 'add')
        self.assertEqual(add_res['res'], 0)
        mul_res = math_engine.solve_gf2_arithmetic(1, 1, 'mul')
        self.assertEqual(mul_res['res'], 1)

    def test_vector_operations(self):
        v1 = [1, 0, 0]
        v2 = [0, 1, 0]
        res = math_engine.compute_vector_operations(v1, v2)
        self.assertEqual(res['dot_prod'], 0.0)
        self.assertTrue(res['is_orthogonal'])
        self.assertEqual(res['cross_prod'], [0.0, 0.0, 1.0])
        self.assertIn('step_dot_latex', res)

    def test_gram_schmidt(self):
        vectors = [[1, 0], [1, 1]]
        res = math_engine.solve_gram_schmidt(vectors)
        self.assertEqual(len(res['steps']), 2)

    def test_cofactor_expansion(self):
        matrix = [[1, 2], [3, 4]]
        res = math_engine.solve_cofactor_expansion(matrix, expand_by='row', idx=0)
        self.assertEqual(res['total_det_latex'], '-2')

    def test_diagonalization(self):
        matrix = [[2, 0], [0, 3]]
        res = math_engine.solve_diagonalization(matrix)
        self.assertTrue(res['is_diagonalizable'])

class PublicOpenAccessViewsTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_all_solver_urls_open_access(self):
        public_urls = [
            reverse('linear_algebra:index'),
            reverse('linear_algebra:gaussian'),
            reverse('linear_algebra:gf2'),
            reverse('linear_algebra:vectors'),
            reverse('linear_algebra:gram_schmidt'),
            reverse('linear_algebra:cofactor'),
            reverse('linear_algebra:diagonalization'),
        ]
        for url in public_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200, f"URL {url} failed with status {response.status_code}")
