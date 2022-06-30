from django.conf import settings

from ..models import Post
from .set_up_date import SetUpDate


class PostsModelTest(SetUpDate):
    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = Post.objects.create(
            author=self.author,
            text=3 * 'Тестовая пост',
            group=self.group
        )
        group = self.group
        text = 3 * 'Тестовая пост'
        self.assertEqual(str(post), text[:settings.FIRST_15_SYMBOLS])
        self.assertEqual(str(group), 'Тестовая группа')
