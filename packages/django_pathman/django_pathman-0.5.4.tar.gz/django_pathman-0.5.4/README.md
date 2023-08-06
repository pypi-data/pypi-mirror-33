# Django-Pathman

Django-pathman - это расширения для django, позволяющее внедрить партиционирование таблицы через [pg_pathman](https://postgrespro.ru/docs/postgrespro/9.6/pg-pathman)

Его особенности:

- Все работает в рамках стандартного механизма миграций
- Не нужно актуализировать состояние дочерних таблицы (колонки, индексы, ограничения изменяются автоматически)
- Теперь планировщик более избирательно работает с множеством партиций
- Не обязательно использовать триггер на insert в родительской таблице
- Перенос данных в партиции происходит автоматически
- При откате миграции создания партиций данные возвращаются в родительскую таблицу

Недостатки:

- Отсутствие глобальных индексов (уникальность значения в поле или в комбинации полей во всем партициях из коробки не реализуется, нужен триггер)
- Невозможно создать ограничение ForeignKey на родительскую таблицу
- Пока невозможно менять правила партиционирования (во избежание потери данных)
- Встраивание в джангу грязными хаками
- Пока поддерживается только разбиение по интервалу

# Требования

- Django >= 1.9.5
- PostgreSQL >= 9.5
- pg_pathman >= 1.3

# Установка

Сначала необходимо установить само расширение pg_pathman. Как это сделать описание в его [документации] (https://github.com/postgrespro/pg_pathman). Затем устанавливаем через pip этот пакет.
```bash
pip install git+ssh://git@gitlab.fix.ru/vendors/django_pathman.git
```
Убедитесь, что у пользователя, запускающего pip прописан .ssh/id_rsa вашего пользователя из гитлаба
<br/>Затем выполняем:
```bash
python manage.py migrate
```

# Использование

Для того, чтобы включить партиционирование нужно:

- Прописать django_pathman в **INSTALLED_APPS** (settings.py) после служебных приложений django:
- В модели в **Meta** прописываем атрибут **partition**:
  ```python
  class RequestLog(Model):
      created = models.DateTimeField(verbose_name=u'Время')
      text = models.TextField(verbose_name=u'Текст')
      msisdn = models.CharField(max_length=30, verbose_name=u'MSISDN', db_index=True)
      subscription = models.ForeignKey(Subscription, verbose_name=u'Подписка', null=True)
      msg_uid = models.CharField(max_length=72, null=True, db_index=True, unique=True)

      Meta:
          partition = ('created', '\'2017-05-01 00:00:00+03\'::TIMESTAMP WITH TIME ZONE', 'INTERVAL \'1 month\'')
  ```
  Нулевой элемент кортежа - поле, по которому производится партиционирование <br/>
  Первый элемент кортежа - начальное значение разбиения в нотации PostgreSQL <br/>
  Второй элемент кортежа - интервал разбиения в нотации PostgreSQL

- Создаем файл миграции:

  ```sh
  python manage.py makemigrations
  ```

- Выполняем миграцию:

  ```sh
  python manage.py migrate
  ```