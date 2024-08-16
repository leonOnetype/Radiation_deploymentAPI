from rest_framework.views import APIView
from django.shortcuts import render
from rest_framework.response import Response

from .models import Radiation

from .serializers import RadiationSerializer

#from tensorflow.keras.models import load_model
import numpy as np
import json
from pathlib import Path
import tensorflow as tf
#import pickle


# chargement du model et définition de quelques variable
BASE_DIR = Path(__file__).resolve().parent

# les variables utilent à la prédiction
with open(BASE_DIR /'extras/variables.txt', 'r') as file:
    json_data = file.read()
data = json.loads(json_data) # data est un dict
sequence_len, end_train_year, end_train_month, end_train_day = data.values()

last_sequence = np.load(BASE_DIR /'extras/last_sequence_test.npy')

with open(BASE_DIR /'extras/variables.txt', 'r') as file:
    json_data = file.read()
data = json.loads(json_data) # data est un dict

#with open(BASE_DIR /'extras/scaler.pkl', 'rb') as file:
#    scaler = pickle.load(file)


model = tf.keras.models.load_model(BASE_DIR/'extras/best_model.keras')


days_per_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
month_labels = ["janvier", "fevrier", "mars", "avril", "mai", "juin", "juillet", "aout", "septembre", "novembre", "decembre"]


def predict_radiation(year, month, day):
    year, month, day = int(year), int(month), int(day)
    # Preparation des données pour la prédiction
    # Idée: Aller dans le fichier csv old_observations prendre 
    # sequence_len anciènnes observations (la model à été 
    # entrainé pour prédire la sequence_len+1 observation
    # connaissant les sequence_len observations) puis itéré

    # Détermination du nombre d'itérations
    nbr_iter = (year - end_train_year-1)*12*30
    
    # Ajout du nombre d'itérations pour ateindre le mois entré
    for i in range(month):
        nbr_iter += days_per_month[i]
    
    # Ajout du nombre d'itérations pour ateindre le jour entré
    nbr_iter += day
    
    # inférence
    pred_sequence = list(last_sequence) # on le converti en liste pour pouvoir ajouter successivement les futurs prédictions
    
    for i in range(nbr_iter):
        sequence = pred_sequence[-sequence_len:] # on prend les sequence_len dernières vecteurs de pred_sequence
        predictions = model.predict(np.expand_dims(np.array(sequence), axis=0), verbose=0)
        pred_sequence.append(predictions[0])
    
    # On recupère la dernière prediction
    radiation_value = np.array(pred_sequence[-1])[0]
    print("Nombre d'itérations= ", radiation_value)
    
    
    # recupération du nombres d'anciènnes observation necessaire
    return radiation_value


class RadiationView(APIView):
    
    def post(self, request):
        year = int(request.data.get('year'))
        month = int(request.data.get('month'))
        day = int(request.data.get('day'))
        
        # Prédiction de la radiation
        radiation_value = predict_radiation(year, month, day)
        
        # Enregistrement de la prédiction dans la base de données
        prediction = Radiation.objects.create(year=year, month=month_labels[month-1], day=day, radiation_value=radiation_value) 
        
        data = {'year':year, 'month':month_labels[month], 'day':day, 'radiation_value':radiation_value}
        
        # Les données à renvoyer au client
        serializer = RadiationSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            data = serializer.data 
         
        return render(request, 'prediction_api/result.html', context={'prediction':prediction})
        # return data
    
    def get(self, request):
        return render(request, 'prediction_api/index.html')