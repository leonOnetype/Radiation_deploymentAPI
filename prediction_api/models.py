from django.db import models

# Create your models here.

# Le model pour stocké les données necessaires à la prédiction

class Radiation(models.Model):
    
    # Deux champ: l'année et la valeur de la radiation
    year = models.IntegerField()
    month = models.TextField()
    day = models.IntegerField()
    radiation_value = models.FloatField()
    