import io
from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from . import math_engine
from .context_processors import user_display

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

class SolverViewsTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_public_index_view(self):
        response = self.client.get(reverse('linear_algebra:index'))
        self.assertEqual(response.status_code, 200)

    def test_protected_routes_redirect_unauthenticated(self):
        protected_urls = [
            reverse('linear_algebra:gaussian'),
            reverse('linear_algebra:gf2'),
            reverse('linear_algebra:vectors'),
            reverse('linear_algebra:gram_schmidt'),
            reverse('linear_algebra:cofactor'),
            reverse('linear_algebra:diagonalization'),
            reverse('linear_algebra:profile'),
        ]
        for url in protected_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)

    def test_protected_routes_authenticated(self):
        # Authenticate via login
        login_res = self.client.post(reverse('linear_algebra:login'), {
            'email': 'parthsalunke2306@gmail.com',
            'password': 'password123'
        })
        self.assertEqual(login_res.status_code, 302)

        protected_urls = [
            reverse('linear_algebra:gaussian'),
            reverse('linear_algebra:gf2'),
            reverse('linear_algebra:vectors'),
            reverse('linear_algebra:gram_schmidt'),
            reverse('linear_algebra:cofactor'),
            reverse('linear_algebra:diagonalization'),
            reverse('linear_algebra:profile'),
        ]
        for url in protected_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

class ProfileAvatarTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.client.post(reverse('linear_algebra:login'), {
            'email': 'parthsalunke2306@gmail.com',
            'password': 'password123'
        })

    def test_profile_get_view(self):
        response = self.client.get(reverse('linear_algebra:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Account & Profile Picture')

    def test_profile_update_name(self):
        response = self.client.post(reverse('linear_algebra:profile'), {
            'full_name': 'Parth S. Advanced',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.session.get('user_name'), 'Parth S. Advanced')

    def test_profile_update_preset_avatar(self):
        preset_url = '/static/linear_algebra/img/avatars/avatar-1.svg'
        response = self.client.post(reverse('linear_algebra:profile'), {
            'full_name': 'Parth Salunke',
            'avatar_preset': preset_url,
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.session.get('user_avatar'), preset_url)

    def test_profile_upload_avatar_file(self):
        # 1x1 pixel PNG bytes
        png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
        avatar_file = SimpleUploadedFile("my_avatar.png", png_data, content_type="image/png")

        response = self.client.post(reverse('linear_algebra:profile'), {
            'full_name': 'Parth Salunke',
            'avatar_file': avatar_file,
        })
        self.assertEqual(response.status_code, 200)
        saved_avatar_url = self.client.session.get('user_avatar')
        self.assertTrue(saved_avatar_url.startswith('/media/avatars/avatar_'))
        self.assertTrue(saved_avatar_url.endswith('.png'))

    def test_profile_remove_avatar(self):
        # First set an avatar
        self.client.post(reverse('linear_algebra:profile'), {
            'full_name': 'Parth Salunke',
            'avatar_preset': '/static/linear_algebra/img/avatars/avatar-1.svg',
        })
        self.assertTrue(bool(self.client.session.get('user_avatar')))

        # Now remove it
        response = self.client.post(reverse('linear_algebra:profile'), {
            'full_name': 'Parth Salunke',
            'remove_avatar': 'true',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.session.get('user_avatar'), '')

    def test_context_processor_user_display(self):
        class MockRequest:
            def __init__(self, name, email, avatar):
                self.session = {
                    'user_name': name,
                    'user_email': email,
                    'user_avatar': avatar
                }
                self.supabase_user = None

        req = MockRequest('Hariom', 'hariom@gmail.com', '/media/avatars/avatar_123.png')
        data = user_display(req)
        self.assertEqual(data['session_user_name'], 'Hariom')
        self.assertEqual(data['session_user_email'], 'hariom@gmail.com')
        self.assertEqual(data['session_user_avatar'], '/media/avatars/avatar_123.png')


