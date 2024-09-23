import yfinance as yf
from django.core.management.base import BaseCommand
from stockapp.models import KospiData
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = "Imports historical KOSPI data from 1996-12-11 ~ today"

    def handle(self, *args, **kwargs):
        # Get the most recent date in the database
        latest_entry = KospiData.objects.order_by("-date").first()

        # If there is no data, start from 1996-12-11; otherwise, start from the day after the last entry
        if latest_entry:
            start_date = latest_entry.date + timedelta(days=1)
        else:
            start_date = datetime(1996, 12, 11).date()

        # Set the end date to today
        end_date = datetime.now().date()

        # Fetch KOSPI data from start_date to end_date
        kospi = yf.Ticker("^KS11")
        data = kospi.history(start=start_date, end=end_date)

        for index, row in data.iterrows():
            KospiData.objects.update_or_create(
                date=index.date(),
                defaults={
                    "open_price": row["Open"],
                    "high_price": row["High"],
                    "low_price": row["Low"],
                    "close_price": row["Close"],
                    "volume": row["Volume"],
                },
            )
        self.stdout.write(self.style.SUCCESS("Success"))
