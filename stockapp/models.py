from django.db import models

# Create your models here.
class KospiData(models.Model):
    date = models.DateField(unique=True)
    open_price = models.FloatField()
    high_price = models.FloatField()
    low_price = models.FloatField()
    close_price = models.FloatField()
    volume = models.FloatField()

    def __str__(self):
        return f"{self.date}"

