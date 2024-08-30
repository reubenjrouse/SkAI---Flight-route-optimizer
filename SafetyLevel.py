import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import StandardScaler
import pickle

weather_data = pd.read_csv('M1_final.csv')


label_mapping = {
    ' Fair / Windy ': 3, ' Fair ': 1, ' Light Rain / Windy ': 7, ' Partly Cloudy ': 2,
    ' Mostly Cloudy ': 2, ' Cloudy ': 5, ' Light Rain ': 6, ' Mostly Cloudy / Windy ': 8,
    ' Partly Cloudy / Windy ': 5, ' Light Snow / Windy ': 4, ' Cloudy / Windy ': 5,
    ' Light Drizzle ': 5, ' Rain ': 6, ' Heavy Rain ': 9, ' Fog ': 8, ' Wintry Mix ': 4,
    ' Light Freezing Rain ': 8, ' Light Snow ': 3, ' Wintry Mix / Windy ': 4,
    ' Fog / Windy ': 8, ' Light Drizzle / Windy ': 6, ' Rain / Windy ': 7,
    ' Drizzle and Fog ': 9, ' Snow ': 3, ' Heavy Rain / Windy ': 10
}

weather_data['SafetyLevel'] = weather_data[' Condition '].map(label_mapping)

print(weather_data[[' Condition ', 'SafetyLevel']].head())

features = ['Temperature', 'Humidity', 'Wind Speed', 'Pressure',]
X = weather_data[features]
y = weather_data['SafetyLevel']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)



model = MLPClassifier(random_state=42)
model.fit(X_train, y_train)
