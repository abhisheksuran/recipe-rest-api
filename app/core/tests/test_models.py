"""
Tests for Models
"""
from unittest.mock import patch
from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from core import models


def create_user(email='user@example.com', password='testpassword123'):
    """Create and return an new user"""
    return get_user_model().objects.create_user(email, password)


class ModelTest(TestCase):
    """Test Models"""

    def test_user_with_email_successful(self):
        """Test creating a user with email successful"""
        email = 'test@exmaple.com'
        password = 'testpassword@123!'
        user = get_user_model().objects.create_user(email=email, password=password)
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test for email normalization for new user"""
        sample_email = [['Test1@Example.com', 'Test1@example.com'],
                        ['TEST2@EXAMPLE.COM', 'TEST2@example.com'],
                        ['Test3@example.COM', 'Test3@example.com'],
                        ['test4@Example.com', 'test4@example.com']]

        for email, expected in sample_email:
            user = get_user_model().objects.create_user(email=email, password='testpassword123!')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_errie(self):
        """Test that creating user without email raises error."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'passwordtest123!')

    def test_create_superuser(self):
        """Test creating a super user"""
        user = get_user_model().objects.create_superuser('test1@example.com', 'testpassword123!')
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)


    def test_creating_recipe(self):
        """Test creating a recipe is  successful"""
        user = get_user_model().objects.create_user(
            'test@example.com', 'testpasswod123!'
        )
        recipe = models.Recipe.objects.create(
            user=user,
            title='Sample recipe name',
            time_minutes=5,
            price=Decimal('5.50'),
            description='Sample recipe description.',
        )
        self.assertEqual(str(recipe), recipe.title)


    def test_create_tag(self):
        """Test creating a tag is successful"""
        user = create_user()
        tag = models.Tag.objects.create(user=user, name='Tag1')

        self.assertEqual(str(tag), tag.name)

    def test_create_ingredient(self):
        """Test creating an ingredient is successfull"""
        user = create_user()
        ingredient = models.Ingredient.objects.create(user=user, name='ingredient')
        self.assertEqual(str(ingredient), ingredient.name)

    @patch('core.models.uuid.uuid4')
    def test_recipe_file_name_uuid(self, mock_uuid):
        """Test generating image path"""
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None, 'example.jpg')

        self.assertEqual(file_path, f'uploads/recipe/{uuid}.jpg')

