from django.core.management.base import BaseCommand, CommandError
from django.apps import apps
import pandas as pd


class Command(BaseCommand):
    help = 'Export data from model in Excel'

    def add_arguments(self, parser):
        parser.add_argument('model', type=str, help='Model name')
        parser.add_argument('--fields', type=str, help='Model fields')
        parser.add_argument('--all', action='store_true', help='Export all fields')

    def handle(self, *args, **options):
        model_name = options['model']
        fields_options = options.get('fields')
        export_all = options.get('all')

        try:
            model = apps.get_model('meteo', model_name)
        except LookupError:
            raise CommandError(f'Model "{model_name}" not found')

        if export_all or not fields_options:
            fields = [f.name for f in model._meta.fields]
        else:
            fields = [f.strip() for f in fields_options.split(',')]
            for f in fields:
                if f not in [field.name for field in model._meta.fields]:
                    raise CommandError(f'Field "{f}" not found in model "{model_name}"')

        data = model.objects.all().values(*fields)
        df = pd.DataFrame(list(data))
        file_name = f"{model_name}.xlsx"
        df.to_excel(file_name, index=False)

        self.stdout.write(self.style.SUCCESS(f'File {file_name} success create.'))
