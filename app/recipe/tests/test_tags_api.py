"""
Test for Tags API.
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag, Recipe
from recipe.serializers import TagSerializer


TAGS_URL = reverse('recipe:tag-list')


def detail_url(tag_id):
    """create and return a tag detail url"""
    return reverse('recipe:tag-detail', args=[tag_id])

def create_user(email='test@example.com', password='testpassword123!'):
    """Create and returns a user """
    return get_user_model().objects.create_user(email=email, password=password)


class PublicTagsApiTests(TestCase):
    """ Test unauthenticated api requests"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required for retrieving tags"""

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)



class PrivateTagsApiTests(TestCase):
    """Test authenticated api requests"""

    def setUp(self):

        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrieving tags"""
        Tag.objects.create(user=self.user, name='Vegen')
        Tag.objects.create(user=self.user, name='spice')
        res = self.client.get(TAGS_URL)
        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test list of tags limited to authenticated users"""
        user2 = create_user(email='user2@example.com', password='tespassword123!')
        Tag.objects.create(user=user2, name='vegan')
        tag = Tag.objects.create(user=self.user, name='comfort food')
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)


        #tags = Tag.objects.filter(user=self.user).order_by('-name')
        #serializer = TagSerializer(tags, many=True)
        #self.assertEqual(res.data[0], serializer.data[0])
        self.assertEqual(res.data[0]['name'], tag.name)
        self.assertEqual(res.data[0]['id'], tag.id)
    
    def test_update_tag(self):
        """Test updating a tag"""
        tag = Tag.objects.create(user=self.user, name='After Dinner')
        payload = {'name': 'Desert'}
        url = detail_url(tag.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])

    def test_delete_tag(self):
        """Test deleting tag"""
        tag = Tag.objects.create(user=self.user, name='Breakfast')
        url = detail_url(tag.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        tags = Tag.objects.filter(user=self.user)
        self.assertFalse(tags.exists())

    def test_filter_tags_assigned_to_reciep(self):
        """TEst listing tags to those assigned to recipe"""
        tag1 = Tag.objects.create(user=self.user, name='Breakfast')
        tag2 = Tag.objects.create(user=self.user, name='Lunch')
        recipe = Recipe.objects.create(
            title='malaai kofta',
            time_minutes=60,
            price=Decimal('5.55'),
            user=self.user,
        )
        recipe.tags.add(tag1)
        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        s1 = TagSerializer(tag1)
        s2 = TagSerializer(tag2)
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filter_tags_unique(self):
        """Test filter tags return a unique list"""
        tag = Tag.objects.create(user=self.user, name='Breakfast')
        Tag.objects.create(user=self.user, name='dinner')
        recipe1 = Recipe.objects.create(
            title='pan cake',
            time_minutes=23,
            price=Decimal('5.55'),
            user=self.user,
        )
        recipe2 = Recipe.objects.create(
            title='paneer',
            time_minutes=5,
            price=Decimal('3.33'),
            user=self.user,
        )

        recipe1.tags.add(tag)
        recipe2.tags.add(tag)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})
        self.assertEqual(len(res.data), 1)