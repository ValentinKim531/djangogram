from django.core.exceptions import ValidationError

from django.test import TestCase

from django.contrib.auth.models import User

from django.urls import reverse

from accounts.models import InstaUser
from insta.views.post import CreatePostView


class PostCreateTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="test_user", password="1@abcTest",
                                             email="test@email.com")
        self.profile = InstaUser.objects.create(user=self.user)
        self.user.save()

    def test_create_post_when_not_signed_up(self):
        response = self.client.get(reverse('insta:add'), follow=True)
        status_code = self.client.get(reverse('insta:add')).status_code
        self.assertEqual('/accounts/login/', response.request['PATH_INFO'])
        self.assertEqual(302, status_code)

    def test_create_post_when_signed_up(self):
        self.client.login(username='test_user', password="1@abcTest")
        with open('insta/tests/fixtures/test_image.jpg', 'rb') as fp:
            response = self.client.post(reverse('insta:add'), {'title': 'test_title',
                                                               'description': 'test_description',
                                                               'image': fp,
                                                               'creator': self.user}, follow=True)
        post = response.context_data['post']

        self.assertEqual('/posts/1', response.request['PATH_INFO'])
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, post.pk)
        self.assertTrue(response.is_rendered)
        self.assertTrue(response.charset == 'utf-8')
        self.assertEqual('test_title', post.title)
        self.assertEqual('test_description', post.description)
        self.assertIsNotNone(post.image)
        self.assertEqual(self.user, post.creator)
        post.delete()

    def test_get_error_messages(self):
        self.client.login(username='test_user', password="1@abcTest")
        with open('insta/tests/fixtures/test.txt', 'rb') as fp:
            response = self.client.post(reverse('insta:add'), {'title': 'q',
                                                               'description': 'q',
                                                               'image': fp,
                                                               'creator': self.user}, follow=True)

        self.assertEqual(200, response.status_code)
        self.assertIn('post/add.html', response.template_name)
        self.assertIsInstance(response.context_data['view'], CreatePostView)
        self.assertTrue(response.charset == 'utf-8')
        self.assertRaisesMessage(ValidationError,
                                 expected_message="Убедитесь, что это значение содержит не менее 3 символов (сейчас 1)")
        self.assertRaisesMessage(ValidationError,
                                 expected_message="Загрузите правильное изображение. Файл, который вы загрузили, поврежден или не является изображением.")

    def tearDown(self):
        self.user.delete()
        self.profile.delete()
