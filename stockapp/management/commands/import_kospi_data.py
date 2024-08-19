import yfinance as yf
from django.core.management.base import BaseCommand
from stockapp.models import KospiData

class Command(BaseCommand):
    help = "Imports historical KOSPI data from 1996-12-11 ~ today"

    def handle(self, *args, **kwargs):
        kospi = yf.Ticker("^KS11")
        data = kospi.history(start="1996-12-11", end="2024-08-12")

        for index, row in data.iterrows():
            KospiData.objects.update_or_create(
                date=index.date(),
                defaults={
                    'open_price': row['Open'],
                    'high_price': row['Close'],
                    'low_price': row['High'],
                    'close_price': row['Low'],
                    'volume': row['Volume'],
                }
            )
        self.stdout.write(self.style.SUCCESS("Success"))
