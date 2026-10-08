from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Category, Product


class CategoryTestCase(TestCase):
    """Pruebas para el endpoint de Categorias"""

    def setUp(self):
        """Se ejecuta antes de cada prueba"""
        self.client = APIClient()
        # Crear categoria de prueba
        self.category = Category.objects.create(name='Electronica')

    def test_create_category(self):
        """Prueba 1: Crear una nueva categoria"""
        response = self.client.post('/api/categories/', {'name': 'Ropa'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Category.objects.count(), 2)

    def test_list_categories(self):
        """Prueba 2: Listar todas las categorias"""
        response = self.client.get('/api/categories/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)


class ProductTestCase(TestCase):
    """Pruebas para el endpoint de Productos (requiere JWT)"""

    def setUp(self):
        """Se ejecuta antes de cada prueba"""
        self.client = APIClient()

        # Crear usuario y obtener token JWT
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}'
        )

        # Crear datos de prueba
        self.category = Category.objects.create(name='Electronica')
        self.product = Product.objects.create(
            name='Laptop',
            category=self.category,
            description='Laptop HP',
            price=15000.00
        )

    def test_create_product(self):
        """Prueba 3: Crear un nuevo producto"""
        response = self.client.post('/api/products/', {
            'name': 'Mouse',
            'category': self.category.id,
            'description': 'Mouse inalambrico',
            'price': 500.00
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Product.objects.count(), 2)

    def test_list_products(self):
        """Prueba 4: Listar todos los productos"""
        response = self.client.get('/api/products/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_update_product(self):
        """Prueba 5: Actualizar un producto existente"""
        response = self.client.put(f'/api/products/{self.product.id}/', {
            'name': 'Laptop Pro',
            'category': self.category.id,
            'description': 'Laptop HP actualizada',
            'price': 18000.00
        })
        self.assertEqual(response.status_code, 200)
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, 'Laptop Pro')

    def test_delete_product(self):
        """Prueba 6: Eliminar un producto"""
        response = self.client.delete(f'/api/products/{self.product.id}/')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Product.objects.count(), 0)

    def test_precio_final_autenticado(self):
        """Prueba 7: Obtener precio final con descuento (autenticado)"""
        response = self.client.get(f'/api/products/{self.product.id}/precio-final/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('precio_final', response.data)
        # Electronica tiene 10% de descuento (15000 * 0.90 = 13500)
        self.assertEqual(response.data['precio_final'], 13500.00)

    def test_precio_final_sin_autenticar(self):
        """Prueba 8: Intentar obtener precio final sin token JWT (debe fallar 401)"""
        self.client.credentials()  # Quita el token de las cabeceras
        response = self.client.get(f'/api/products/{self.product.id}/precio-final/')
        self.assertEqual(response.status_code, 401)

    def test_factory_method_categoria_default(self):
        """Prueba 9: Verificar que Factory Method crea producto con categoria default"""
        prod = Product.crear_con_categoria_default(
            name='Teclado',
            description='Teclado mecanico',
            price=1200.00
        )
        self.assertEqual(prod.category.name, 'Sin categoría')


