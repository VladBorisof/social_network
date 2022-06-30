import tempfile
from http import HTTPStatus

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from ..models import Comment, Group, Post
from .set_up_date import SetUpDate

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class PostCreateFormTests(SetUpDate):
    def form_date_count_post(self):
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый заголовок 1',
            'group': self.group.id,
            'image': uploaded,
        }
        return posts_count, form_data

    def test_create_post(self):
        posts_count, form_data = self.form_date_count_post()
        response = self.authorized_non_author.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        _, page, _, _ = self.tuple_with_url_page_args_template.profile
        self.assertRedirects(
            response, reverse(page, args=(self.non_author,))
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        post = Post.objects.first()
        self.assertEqual(post.text, form_data.get('text'))
        self.assertEqual(post.group.title, self.group.title)
        self.assertEqual(
            post.image.name,
            'posts/' + form_data.get('image').name
        )

    def test_guest_submit_form(self):
        posts_count, form_data = self.form_date_count_post()
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, '/auth/login/?next=/create/')
        self.assertEqual(Post.objects.count(), posts_count)

    def test_author_edit_post(self):
        posts_count = Post.objects.count()
        new_group = Group.objects.create(
            title='Тестовая группа 2',
            slug='test-slug-2',
            description='Тестовое описание 2',
        )
        form_data = {
            'text': 'Тестовый заголовок 2',
            'group': new_group.id
        }
        _, page, args, _ = self.user_group.author
        response_edit = self.authorized_author.post(
            reverse(page, args=args),
            data=form_data,
            follow=True,
        )
        post_2 = Post.objects.get(pk=self.post.id)
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(response_edit.status_code, HTTPStatus.OK)
        self.assertEqual(post_2.text, form_data.get('text'))
        self.assertEqual(post_2.group.title, new_group.title)

    def test_add_comment(self):
        comment_count = Comment.objects.count()
        form_data = {'text': 'Новый комментарий'}
        _, page, args, _ = self.tuple_with_url_page_args_template.add_comment
        response = self.authorized_author.post(
            reverse(page, args=args),
            data=form_data,
            follow=True,
        )
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertRedirects(
            response,
            self.tuple_with_url_page_args_template.post_detail.url
        )
        self.assertEqual(Comment.objects.first().text, form_data.get('text'))
