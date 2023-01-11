import json

from django.core.management.base import BaseCommand

from recipes.models import Ingredient

ALREADY_LOADED_ERROR_MESSAGE = (
    'Кажется, в базе уже есть ингредиенты...'
)
SUCCESS_MESSAGE = 'Ингредиенты загружены в базу данных!'

json_path = '../data/ingredients.json'


class Command(BaseCommand):
    help = 'Load data in database (SQLite3) from CSV-file.'

    def handle(self, *args, **kwargs):
        if Ingredient.objects.exists():
            print(ALREADY_LOADED_ERROR_MESSAGE)
            return

        with open(json_path, encoding='utf-8') as json_file:
            json_list = json.load(json_file)
            ingredients_instances = [
                Ingredient(i + 1, item['name'], item['measurement_unit'])
                for i, item in enumerate(json_list)
            ]
            Ingredient.objects.bulk_create(ingredients_instances,
                                           batch_size=10000)

        print(SUCCESS_MESSAGE)
