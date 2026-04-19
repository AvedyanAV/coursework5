from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory, APIClient
from rest_framework import status
from habits.models import Habit
from habits.serializers import HabitSerializer

User = get_user_model()


class HabitValidatorTestCase(TestCase):
    """Тестирование валидаторов привычек"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

        # Создаем приятную привычку для тестов
        self.pleasant_habit = Habit.objects.create(
            user=self.user,
            action='Приятная привычка',
            place='Дома',
            time='20:00:00',
            is_pleasant=True,
            duration_seconds=60
        )

        # Создаем фабрику запросов для контекста
        self.factory = APIRequestFactory()
        self.request = self.factory.get('/')
        self.request.user = self.user

    def test_duration_validation(self):
        """Тест: время выполнения не более 120 секунд"""
        data = {
            'action': 'Тестовая привычка',
            'place': 'Дом',
            'time': '10:00:00',
            'duration_seconds': 300,
            'periodicity': 1
        }
        serializer = HabitSerializer(data=data, context={'request': self.request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('duration_seconds', serializer.errors)

    def test_periodicity_validation(self):
        """Тест: периодичность от 1 до 7 дней"""
        data = {
            'action': 'Тестовая привычка',
            'place': 'Дом',
            'time': '10:00:00',
            'duration_seconds': 60,
            'periodicity': 8
        }
        serializer = HabitSerializer(data=data, context={'request': self.request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('periodicity', serializer.errors)

    def test_reward_and_related_habit_together(self):
        """Тест: нельзя одновременно reward и related_habit"""
        data = {
            'action': 'Тестовая привычка',
            'place': 'Дом',
            'time': '10:00:00',
            'duration_seconds': 60,
            'reward': 'Шоколадка',
            'related_habit': self.pleasant_habit.id
        }
        serializer = HabitSerializer(data=data, context={'request': self.request})
        self.assertFalse(serializer.is_valid())
        # Проверяем наличие ошибки non_field_errors
        self.assertIn('non_field_errors', serializer.errors)
        # Проверяем текст ошибки (без конкретной фразы)
        error_text = str(serializer.errors['non_field_errors'])
        self.assertTrue('нельзя' in error_text.lower() or 'cannot' in error_text.lower())

    def test_related_habit_must_be_pleasant(self):
        """Тест: связанная привычка должна быть приятной"""
        # Создаем полезную привычку (не приятную)
        useful_habit = Habit.objects.create(
            user=self.user,
            action='Полезная привычка',
            place='Офис',
            time='15:00:00',
            is_pleasant=False,
            duration_seconds=60
        )

        data = {
            'action': 'Тестовая привычка',
            'place': 'Дом',
            'time': '10:00:00',
            'duration_seconds': 60,
            'related_habit': useful_habit.id
        }
        serializer = HabitSerializer(data=data, context={'request': self.request})
        self.assertFalse(serializer.is_valid())
        # Проверяем, что есть ошибка
        self.assertTrue(serializer.errors)

    def test_pleasant_habit_no_reward(self):
        """Тест: у приятной привычки не может быть вознаграждения"""
        data = {
            'action': 'Приятная привычка',
            'place': 'Дома',
            'time': '21:00:00',
            'is_pleasant': True,
            'reward': 'Вознаграждение',
            'duration_seconds': 60
        }
        serializer = HabitSerializer(data=data, context={'request': self.request})
        self.assertFalse(serializer.is_valid())
        # Проверяем, что есть ошибка в reward или non_field_errors
        has_error = 'reward' in serializer.errors or 'non_field_errors' in serializer.errors
        self.assertTrue(has_error, f"Ожидалась ошибка, но получили: {serializer.errors}")

    def test_successful_habit_creation(self):
        """Тест: успешное создание привычки"""
        data = {
            'action': 'Успешная привычка',
            'place': 'Работа',
            'time': '14:00:00',
            'duration_seconds': 90,
            'periodicity': 2,
            'reward': 'Кофе'
        }
        # Передаем user напрямую в контекст
        serializer = HabitSerializer(data=data, context={'user': self.user})
        self.assertTrue(serializer.is_valid(), f"Ошибки: {serializer.errors}")
        habit = serializer.save()
        self.assertEqual(habit.user, self.user)
        self.assertEqual(habit.action, 'Успешная привычка')


class HabitModelTest(TestCase):
    """Тестирование модели Habit"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_create_habit(self):
        """Тест создания привычки"""
        habit = Habit.objects.create(
            user=self.user,
            action='Тестовая привычка',
            place='Дом',
            time='10:00:00',
            duration_seconds=60
        )
        self.assertEqual(habit.action, 'Тестовая привычка')
        self.assertEqual(habit.user.username, 'testuser')
        self.assertEqual(habit.execution_count, 0)

    def test_mark_as_executed(self):
        """Тест отметки выполнения"""
        habit = Habit.objects.create(
            user=self.user,
            action='Выполняемая привычка',
            place='Офис',
            time='14:00:00',
            duration_seconds=90
        )

        habit.mark_as_executed()

        self.assertEqual(habit.execution_count, 1)
        self.assertEqual(habit.streak_days, 1)
        self.assertIsNotNone(habit.last_executed)

    def test_is_due(self):
        """Тест проверки, пора ли выполнять"""
        habit = Habit.objects.create(
            user=self.user,
            action='Ежедневная привычка',
            place='Спортзал',
            time='08:00:00',
            duration_seconds=60,
            periodicity=1
        )

        # Новая привычка - должна быть просрочена
        self.assertTrue(habit.is_due())

        # Выполняем привычку
        habit.mark_as_executed()

        # Сразу после выполнения - не просрочена
        self.assertFalse(habit.is_due())


class HabitAPITest(TestCase):
    """Тестирование API эндпоинтов"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

        self.habit = Habit.objects.create(
            user=self.user,
            action='Тестовая привычка',
            place='Дом',
            time='10:00:00',
            duration_seconds=60
        )

    def test_get_habits_list(self):
        """Тест получения списка привычек"""
        url = '/api/habits/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_habit(self):
        """Тест создания привычки через API"""
        url = '/api/habits/'
        data = {
            'action': 'Новая привычка',
            'place': 'Офис',
            'time': '15:00:00',
            'duration_seconds': 90,
            'periodicity': 2,
            'reward': 'Кофе'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habit.objects.count(), 2)

    def test_execute_habit(self):
        """Тест выполнения привычки через API"""
        url = f'/api/habits/{self.habit.id}/execute/'
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.habit.refresh_from_db()
        self.assertEqual(self.habit.execution_count, 1)

    def test_unauthorized_access(self):
        """Тест доступа без авторизации"""
        self.client.force_authenticate(user=None)
        url = '/api/habits/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_public_habits_list(self):
        """Тест списка публичных привычек"""
        # Создаем публичную привычку
        Habit.objects.create(
            user=self.user,
            action='Публичная привычка',
            place='Парк',
            time='12:00:00',
            duration_seconds=60,
            is_public=True
        )

        # Исправленный URL (без /habits/ в середине)
        url = '/api/public-habits/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_habit_statistics(self):
        """Тест статистики привычек"""
        # Исправленный URL
        url = '/api/statistics/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_habits', response.data)


class PaginationTestCase(TestCase):
    """Тестирование пагинации"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

        # Создаем 12 привычек (больше одной страницы)
        for i in range(1, 13):
            Habit.objects.create(
                user=self.user,
                action=f'Привычка {i}',
                place='Дом',
                time=f'{i % 24:02d}:00:00',
                duration_seconds=60
            )

    def test_first_page_has_5_items(self):
        """Тест: первая страница должна содержать 5 элементов"""
        response = self.client.get('/api/habits/?page=1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 5)

    def test_second_page_has_5_items(self):
        """Тест: вторая страница содержит 5 элементов"""
        response = self.client.get('/api/habits/?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 5)

    def test_third_page_has_2_items(self):
        """Тест: третья страница содержит 2 элемента (остаток)"""
        response = self.client.get('/api/habits/?page=3')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 2)

    def test_total_count(self):
        """Тест: общее количество привычек = 12"""
        response = self.client.get('/api/habits/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 12)

    def test_total_pages(self):
        """Тест: количество страниц = 3 (12 / 5 = 3)"""
        response = self.client.get('/api/habits/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total_pages'], 3)

    def test_page_out_of_range(self):
        """Тест: запрос несуществующей страницы"""
        response = self.client.get('/api/habits/?page=99')
        self.assertEqual(response.status_code, 404)

    def test_custom_page_size(self):
        """Тест: кастомный размер страницы"""
        response = self.client.get('/api/habits/?page=1&page_size=10')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 10)

    def test_links_are_correct(self):
        """Тест: ссылки на下一页 и предыдущую страницу корректны"""
        response = self.client.get('/api/habits/?page=2')
        self.assertIsNotNone(response.data['next'])
        self.assertIsNotNone(response.data['previous'])

    def test_first_page_no_previous(self):
        """Тест: у первой страницы нет ссылки 'previous'"""
        response = self.client.get('/api/habits/?page=1')
        self.assertIsNone(response.data['previous'])

    def test_last_page_no_next(self):
        """Тест: у последней страницы нет ссылки 'next'"""
        response = self.client.get('/api/habits/?page=3')
        self.assertIsNone(response.data['next'])
