from django.db import models

class Settings(models.Model):
    key = models.CharField(max_length=100)
    value = models.CharField(max_length=100)

    def __str__(self):
        return self.key

class TempHistory(models.Model):
    current_temp = models.FloatField()
    heater_on = models.BooleanField()
    time_created = models.IntegerField()

    def __str__(self):
        return str(self.current_temp) + " " + str(self.heater_on) + " " + str(self.time_created)
        # return 'test'