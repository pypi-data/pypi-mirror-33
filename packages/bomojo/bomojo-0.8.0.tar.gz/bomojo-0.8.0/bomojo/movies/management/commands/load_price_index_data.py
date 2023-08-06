from django.core.management.base import BaseCommand
from bomojo.movies.models import PriceIndex

import pycpi

class Command(BaseCommand):
    help = 'Loads CPI data from the BLS API'

    def handle(self, *args, **options):
        months_by_name = {
            'January': 1,
            'February': 2,
            'March': 3,
            'April': 4,
            'May': 5,
            'June': 6,
            'July': 7,
            'August': 8,
            'September': 9,
            'October': 10,
            'November': 11,
            'December': 12
        }

        latest_data = PriceIndex.objects.order_by('year', 'month').last()
        start_year = latest_data.year if latest_data is not None else 1920

        print('Loading CPI data from %d' % start_year)
        for year, month, value in pycpi.get_data(start_year):
            price_index, created = PriceIndex.objects.get_or_create(
                year=year, month=months_by_name[month], value=value)
            if created:
                print(price_index)
