import shutil
import tempfile
from typing import NamedTuple, Optional, Tuple

from django.conf import settings
from django.test import Client, TestCase, override_settings

from ..models import Group, Post, User


class ContainerInner(NamedTuple):
    url: Optional['str']
    page: Optional['str']
    args: Optional[Tuple]
    template: Optional['str']


class Container(NamedTuple):
    index: ContainerInner
    profile: tuple
    create: tuple
    post_detail: tuple
    post_edit: tuple
    group_list: tuple
    follow_index: tuple
    profile_follow: tuple
    profile_unfollow: tuple
    add_comment: tuple


class AccessRights(NamedTuple):
    guest: tuple
    authorized: tuple
    author: tuple


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class SetUpDate(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.user = User.objects.create_user(username='user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовая пост',
            group=cls.group
        )

        cls.tuple_with_url_page_args_template = Container(
            index=ContainerInner(
                '/', 'posts:index',
                None, 'posts/index.html'
            ),
            profile=ContainerInner(
                f'/profile/{cls.author}/', 'posts:profile',
                (cls.author,), 'posts/profile.html'
            ),
            create=ContainerInner(
                '/create/', 'posts:post_create',
                None, 'posts/create_post.html'
            ),
            post_detail=ContainerInner(
                f'/posts/{cls.post.id}/', 'posts:post_detail',
                (cls.post.id,), 'posts/post_detail.html',
            ),
            post_edit=ContainerInner(
                f'/posts/{cls.post.id}/edit/', 'posts:post_edit',
                (cls.post.id,), 'posts/create_post.html'
            ),
            group_list=ContainerInner(
                f'/group/{cls.group.slug}/', 'posts:group_list',
                (cls.group.slug,), 'posts/group_list.html'
            ),
            follow_index=ContainerInner(
                '/follow/', 'posts:follow_index',
                None, 'posts/follow.html'
            ),
            profile_follow=ContainerInner(
                f'profile/{cls.author}/follow/', 'posts:profile_follow',
                (cls.author,), None
            ),
            profile_unfollow=ContainerInner(
                f'profile/{cls.author}/unfollow/', 'posts:profile_unfollow',
                (cls.author,), None
            ),
            add_comment=ContainerInner(
                f'posts/{cls.post.id}/comment/', 'posts:add_comment',
                (cls.post.id,), None
            )
        )

        cls.user_group = AccessRights(
            guest=(
                cls.tuple_with_url_page_args_template.index,
                cls.tuple_with_url_page_args_template.profile,
                cls.tuple_with_url_page_args_template.group_list,
                cls.tuple_with_url_page_args_template.post_detail
            ),
            authorized=(
                cls.tuple_with_url_page_args_template.create
            ),
            author=(
                cls.tuple_with_url_page_args_template.post_edit
            )
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self) -> None:
        self.guest_client = Client()
        self.authorized_author = Client()
        self.authorized_author.force_login(self.author)
        self.non_author = User.objects.create_user(username='non_author')
        self.authorized_non_author = Client()
        self.authorized_non_author.force_login(self.non_author)
        self.authorized_user = Client()
        self.authorized_user.force_login(self.user)
