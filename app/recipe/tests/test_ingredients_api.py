"""
Tests for the ingrediets api.
"""

from decimal  import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient, Recipe

from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')

def detail_url(ingredient_id):
    """returns the detailed url for the ingredient"""
    return reverse('recipe:ingredient-detail', args=[ingredient_id])


def create_user(email='test@example.com', password='testpassword@123'):
    """Create user"""
    return get_user_model().objects.create_user(email=email, password=password)


class PublicIngredientApiTests(TestCase):
    """Test unathenticated api requests"""

    def setUp(self):

        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required for retriving ingridients"""
        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngridientApiTests(TestCase):
    """Test authenticated api requests"""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients(self):
        """Test retriving ingredients"""
        Ingredient.objects.create(user=self.user, name='kale')
        Ingredient.objects.create(user=self.user, name='salt')

        res = self.client.get(INGREDIENTS_URL)
        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test retriving ingredients limited to the users"""
        user2 = create_user(email='user2@example.com')
        Ingredient.objects.create(user=user2, name='Salt')
        ingredient = Ingredient.objects.create(user=self.user, name='papper')

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)
        self.assertEqual(res.data[0]['id'], ingredient.id)

    def test_update_ingredient(self):
        """Test updating ingredient"""
        ingredient = Ingredient.objects.create(user=self.user, name='mirchi')
        payload = {'name': 'chinni'}
        url = detail_url(ingredient.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name, payload['name'])

    def test_delete_ingredient(self):
        """Test delete ingredient"""
        ingredient = Ingredient.objects.create(user=self.user, name='nimmboo')
        url = detail_url(ingredient.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        ingredients = Ingredient.objects.filter(user=self.user)
        self.assertFalse(ingredients.exists())

    def test_filter_ingredients_assigned_to_recipes(self):
        """Listing ingredients those assigned to the recipes"""
        in1 = Ingredient.objects.create(user=self.user, name='Apple')
        in2 = Ingredient.objects.create(user=self.user, name='Orange')

        recipe = Recipe.objects.create(user=self.user, title='apple cruble', time_minutes=25, price=Decimal('4.50'),)
        recipe.ingredients.add(in1)
        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        s1 = IngredientSerializer(in1)
        s2 = IngredientSerializer(in2)
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtered_ingredients_unique(self):
        """Test filter ingredients returns a unique list"""
        ing = Ingredient.objects.create(user=self.user, name='Banana')
        Ingredient.objects.create(user=self.user, name='Podheena')
        recipe1 = Recipe.objects.create(title='Banana shake', time_minutes=5, price=Decimal('5.44'), user=self.user)
        recipe2 = Recipe.objects.create(title='Banana icecream', time_minutes=33, price=Decimal('4.44'), user=self.user)
        recipe1.ingredients.add(ing)
        recipe2.ingredients.add(ing)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)



