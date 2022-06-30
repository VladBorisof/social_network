from django import forms
from django.conf import settings
from django.urls import reverse

from ..forms import PostForm
from ..models import Follow, Post
from .set_up_date import SetUpDate

TOTAL_NUMBER_OF_POSTS_IN_PAGINATOR_TEST = 13
NUMBER_OF_POSTS_ON_LAST_PAGE = (
    TOTAL_NUMBER_OF_POSTS_IN_PAGINATOR_TEST - settings.POSTS_PER_PAGE
)


class PostsPagesTests(SetUpDate):
    def check_post_exist_and_context(self, response, is_post_detail=False):
        if is_post_detail:
            post = response.context.get('post')
        else:
            post = response.context.get('page_obj')[0]
        self.assertIsInstance(post, Post)
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.author.username, self.post.author.username)
        self.assertEqual(post.group.slug, self.post.group.slug)
        self.assertEqual(post.pub_date, self.post.pub_date)
        self.assertEqual(post.image, self.post.image)

    def test_pages_uses_correct_template(self):
        tuple_with_non_author = (*self.user_group.guest,
                                 self.user_group.authorized)
        for _, page, args, template in tuple_with_non_author:
            reverse_name = reverse(page, args=args)
            with self.subTest(page=page):
                response = self.authorized_non_author.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_pages_uses_correct_template_author(self):
        _, page, args, template = self.user_group.author
        reverse_name = reverse(page, args=args)
        response = self.authorized_author.get(reverse_name)
        self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        _, page, _, _ = self.tuple_with_url_page_args_template.index
        response = self.guest_client.get(reverse(page))
        self.check_post_exist_and_context(response)

    def test_group_list_page_show_correct_context(self):
        _, page, args, _ = self.tuple_with_url_page_args_template.group_list
        response = self.guest_client.get(
            reverse(page, args=args)
        )
        self.check_post_exist_and_context(response)
        first_object = response.context.get('group')
        self.assertEqual(first_object.title, self.group.title)
        self.assertEqual(first_object.slug, self.group.slug)
        self.assertEqual(first_object.description, self.group.description)

    def test_profile_page_show_correct_context(self):
        _, page, args, _ = self.tuple_with_url_page_args_template.profile
        response = self.guest_client.get(
            reverse(page, args=args)
        )
        self.check_post_exist_and_context(response)
        second_object = response.context.get('author')
        self.assertEqual(second_object.username, self.author.username)

    def test_post_detail_page_show_correct_context(self):
        _, page, args, _ = self.tuple_with_url_page_args_template.post_detail
        response = self.guest_client.get(
            reverse(page, args=args)
        )
        self.check_post_exist_and_context(response, True)

    def test_create_or_edit_post_page_show_correct_context(self):
        _, page, args, _ = self.tuple_with_url_page_args_template.post_edit
        response = self.authorized_author.get(
            reverse(page, args=args)
        )
        first_object = response.context.get('is_edit')
        self.assertTrue(first_object)

        pages = (self.user_group.authorized, self.user_group.author)
        for _, page, args, _ in pages:
            reverse_name = reverse(page, args=args)
            response = self.authorized_author.get(reverse_name)
            form_fields = {
                'text': forms.fields.CharField,
                'group': forms.fields.ChoiceField
            }
            self.assertIsInstance(response.context.get('form'), PostForm)
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    form_field = response.context.get('form').fields[value]
                    self.assertIsInstance(form_field, expected)

    def test_post_another_group(self):
        """Пост не попал в другую группу"""
        _, page, args, _ = self.tuple_with_url_page_args_template.group_list
        response = self.authorized_non_author.get(
            reverse(page, args=args)
        )
        first_object = response.context.get('page_obj')[0]
        self.assertTrue(first_object.text, 'Тестовая пост 2')


class PaginatorViewsTest(SetUpDate):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.posts = [
            Post(
                author=cls.author,
                text=f'Тестовая пост {i}',
                group=cls.group
            ) for i in range(
                1, TOTAL_NUMBER_OF_POSTS_IN_PAGINATOR_TEST
            )
        ]
        Post.objects.bulk_create(cls.posts)
        Follow.objects.create(user=cls.user, author=cls.author)

        cls.tuple_for_testing_paginator = (
            cls.tuple_with_url_page_args_template.index,
            cls.tuple_with_url_page_args_template.group_list,
            cls.tuple_with_url_page_args_template.profile,
            cls.tuple_with_url_page_args_template.follow_index
        )

    def test_first_page_contains_ten_records(self):
        for _, page, args, _ in self.tuple_for_testing_paginator:
            response = self.authorized_user.get(reverse(page, args=args))
            self.assertEqual(
                len(response.context.get('page_obj')), settings.POSTS_PER_PAGE
            )

    def test_second_page_contains_three_records(self):
        for _, page, args, _ in self.tuple_for_testing_paginator:
            response = self.authorized_user.get(
                reverse(page, args=args) + '?page=2'
            )
            self.assertEqual(
                len(response.context.get('page_obj')),
                NUMBER_OF_POSTS_ON_LAST_PAGE
            )


class PostCacheTest(SetUpDate):
    def test_index_cache(self):
        _, page, _, _ = self.tuple_with_url_page_args_template.index
        response = self.guest_client.get(reverse(page))
        Post.objects.filter(pk=self.post.pk).delete()
        response_1 = self.guest_client.get(reverse(page))
        self.assertEqual(response.content, response_1.content)


class FollowingTest(PaginatorViewsTest):
    def test_follow_and_unfollow(self):
        (_, page,
         args, _) = self.tuple_with_url_page_args_template.profile_follow
        self.authorized_user.get(reverse(page, args=args))
        self.assertEqual(
            Post.objects.filter(
                author__following__user=self.user
            ).count(),
            TOTAL_NUMBER_OF_POSTS_IN_PAGINATOR_TEST
        )

    def test_delete_one_post_from_follow(self):
        (_, page,
         args, _) = self.tuple_with_url_page_args_template.profile_follow
        self.authorized_user.get(reverse(page, args=args))
        Post.objects.get(pk=1).delete()
        self.assertEqual(
            Post.objects.filter(
                author__following__user=self.user
            ).count(),
            TOTAL_NUMBER_OF_POSTS_IN_PAGINATOR_TEST - 1
        )

    def test_unfollow(self):
        (_, page,
         args, _) = self.tuple_with_url_page_args_template.profile_unfollow
        self.authorized_user.get(reverse(page, args=args))
        self.assertEqual(
            Post.objects.filter(
                author__following__user=self.user
            ).count(),
            0
        )

    def test_new_post_in_following(self):
        Post.objects.create(
            author=self.author,
            text='Новый Тестовая пост',
            group=self.group
        )
        (_, page,
         _, _) = self.tuple_with_url_page_args_template.follow_index
        response = self.authorized_user.get(reverse(page))
        first_object = response.context.get('page_obj')[0]
        self.assertEqual(first_object.text, 'Новый Тестовая пост')
        self.assertEqual(first_object.author, self.author)

    def test_no_new_post_for_unfollower(self):
        Post.objects.create(
            author=self.author,
            text='Новый Тестовая пост',
            group=self.group
        )
        (_, page,
         _, _) = self.tuple_with_url_page_args_template.follow_index
        response = self.authorized_non_author.get(reverse(page))
        first_object = response.context.get('page_obj')
        self.assertEqual(len(first_object), 0)
