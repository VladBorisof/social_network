from http import HTTPStatus

from .set_up_date import SetUpDate


class PostsURLTests(SetUpDate):
    def test_urls_exists_for_guest_client(self) -> None:
        for guest in self.user_group.guest:
            with self.subTest(url=guest.url):
                response = self.guest_client.get(guest.url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_posts_id_edit_url_exists_only_author(self) -> None:
        response = self.authorized_non_author.get(self.user_group.author.url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_create_posts_url_exists_authorized(self) -> None:
        response = self.authorized_non_author.get(
            self.user_group.authorized.url
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_posts_url_redirect_anonymous_on_admin_login(self) -> None:
        response = self.guest_client.get('/create/')
        self.assertRedirects(
            response,
            '/auth/login/?next=/create/'
        )

    def test_urls_uses_correct_template_guest(self) -> None:
        for url, _, _, template in self.user_group.guest:
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertTemplateUsed(
                    response,
                    template,
                    'Url не соответствует templates'
                )

    def test_urls_uses_correct_template_authorized(self) -> None:
        url, _, _, template = self.user_group.authorized
        response = self.authorized_non_author.get(url, follow=True)
        self.assertTemplateUsed(
            response,
            template,
            'Url не соответствует templates'
        )

    def test_urls_uses_correct_template_author(self) -> None:
        url, _, _, template = self.user_group.author
        response = self.authorized_author.get(url, follow=True)
        self.assertTemplateUsed(
            response,
            template,
            'Url не соответствует templates'
        )

    def test_wrong_url_returns_404(self):
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(
            response.status_code,
            HTTPStatus.NOT_FOUND,
            'Показывает несуществующую страницу'
        )
        self.assertTemplateUsed(
            response,
            'core/404.html',
            'Url не соответствует templates'
        )
