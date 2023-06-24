import json
from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Loads data from ingredient.json'

    def handle(self, *args, **options):
        try:
            with open('recipes/data/ingredients.json', 'r') as f:
                data = json.load(f)
                ingredients = ([Ingredient(name=d['name'],
                                measurement_unit=d['measurement_unit'])
                                for d in data])
                Ingredient.objects.bulk_create(ingredients)
                self.stdout.write(self.style.SUCCESS(
                    'Ingredients loaded successfully!')
                )
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR('File not found!'))
        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR('Error decoding JSON file!'))
