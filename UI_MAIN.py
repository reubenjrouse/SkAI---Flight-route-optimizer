import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from RouteOptimization import load_data, create_graph, find_optimized_path, plot
import ast
import warnings
import ServiceStatus

warnings.filterwarnings("ignore")


filename = 'Cities_FlightDuration_Mins.csv'
nodes, graph_data = load_data(filename)
G = create_graph(nodes, graph_data)

fl_df = pd.read_csv('Flight_Database.csv') 
weather_data = pd.read_csv('M1_final.csv')
cities_weather = pd.read_csv('weather_data_cities.csv')
cities_time = pd.read_csv('Cities_FlightDuration_Mins.csv')

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

features = ['Temperature', 'Humidity', 'Wind Speed', 'Pressure',]
X = weather_data[features]
y = weather_data['SafetyLevel']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = MLPClassifier(random_state=42)
model.fit(X_train, y_train)

def safetyCalculator(city, time):
    time_obj = datetime.strptime(time, "%H:%M")  # rounds off to the nearest hour
    minute = time_obj.minute
    if minute >= 30:
        time_obj += timedelta(hours=1)
    time_obj = time_obj.replace(minute=0, second=0)
    time = time_obj.strftime("%H:%M")

    string_stats = cities_weather[cities_weather['City'] == city][time].values[0]  # converts string dict to dictionary
    string_stats = string_stats.replace("'", "").replace("{", "").replace("}", "")
    key_value_pairs = string_stats.split(", ")
    input_stats = {}
    for pair in key_value_pairs:
        key, value = pair.split(": ")
        input_stats[key] = float(value)

    input_array = np.array([input_stats[feature] for feature in features]).reshape(1, -1)
    prediction = model.predict(input_array)

    return prediction[0]

def unsafeCities(DEP_City, ARR_City, DEP_Time, G):
    unsafe_nodes = []
    safe_nodes = []
    for node in G.nodes():
        if node == DEP_City:
            if safetyCalculator(DEP_City, DEP_Time) >= 5:
                print('Delay takeoff')
        elif node == ARR_City:
            continue
        else:
            time_from_dep_2_node = cities_time[cities_time['City'] == DEP_City][node].values[0]
            time_of_day = (datetime.strptime(DEP_Time, "%H:%M") + timedelta(minutes=int(time_from_dep_2_node))).strftime("%H:%M")
            if safetyCalculator(node, time_of_day) >= 6:
                print(node, "at", time_of_day, ":", safetyCalculator(node, time_of_day))
                unsafe_nodes.append(node)
            else:
                print(node, "at", time_of_day, ":", safetyCalculator(node, time_of_day))
                safe_nodes.append(node)

    print("Unsafe cities from", DEP_City, "to", ARR_City, ":", unsafe_nodes)
    return unsafe_nodes, safe_nodes

def get_safety_info(dep_city, dep_time):
    safety_info = ""
    for city in G.nodes():
        time_of_day = (datetime.strptime(dep_time, "%H:%M") + timedelta(minutes=int(cities_time[cities_time['City'] == dep_city][city].values[0]))).strftime("%H:%M")
        safety_level = safetyCalculator(city, time_of_day)
        safety_info += f"{city} at {time_of_day}: {safety_level}\n"
    return safety_info

def update_info():
    flight_id = entry_flight_id.get()

    if not fl_df[fl_df['FlightID'] == flight_id].empty:
        dep_city = fl_df[fl_df['FlightID'] == flight_id]['DEP_City'].values[0]
        dep_time = fl_df[fl_df['FlightID'] == flight_id]['Dep_Time'].values[0]
        arr_city = fl_df[fl_df['FlightID'] == flight_id]['ARR_City'].values[0]

        serviceStatus = predictService(flight_id)
        label_servicing.config(text=f"Service status: {serviceStatus}")

        unsafe_nodes, safe_nodes = unsafeCities(dep_city, arr_city, dep_time, G)
        primary_path, primary_time, alternate_path, alternate_time = find_optimized_path(G, dep_city, arr_city, unsafe_nodes)

        label_safety.config(text=f"Safety levels at a particular time:\n{get_safety_info(dep_city, dep_time)}")

        primary_path_str = f"Primary path: {primary_path} (Total Time: {primary_time} minutes)"
        if primary_path and len(primary_path) > 2:
            reroute_city = primary_path[1]  # Get the second city in the primary path
            primary_path_str += f"\n Rerouted due to bad weather at {reroute_city} "

        label_primary_path.config(text=primary_path_str)

        if alternate_path:
            label_alternate_path.config(text=f"Rerouted path: {alternate_path} (Total Time: {alternate_time} minutes)")
            label_unsafe_cities.config(text=f"Unsafe cities: {', '.join(unsafe_nodes)}", foreground='red')
            plot_alternate_path(alternate_path)
        else:
            label_alternate_path.config(text="No Reroute needed")
            label_unsafe_cities.config(text="")
            plot_alternate_path(primary_path)

        
    else:
        label_safety.config(text="Invalid Flight ID. Please enter a valid Flight ID.")
        label_primary_path.config(text="")
        label_alternate_path.config(text="")
        label_unsafe_cities.config(text="")

def plot_alternate_path(path):
    plot(G, path)

def predictService(flightID):
    modelMapping = {'Airbus A319': 1, 'Airbus A320': 2, 'Boeing 777': 3, 'Boeing 787': 4}
    servicingData = pd.DataFrame({
        "Days Since Servicing": [fl_df[fl_df['FlightID'] == flightID]['Days_Since_Serving'].values[0]],
        "Warranty Status": [fl_df[fl_df['FlightID'] == flightID]['Warranty_Status'].values[0]],
        "Days Since Purchase": [fl_df[fl_df['FlightID'] == flightID]['Days_Since_Purchase'].values[0]],
        "Company": [modelMapping[fl_df[fl_df['FlightID'] == flightID]['Model'].values[0]]]
    })

    predictions = ServiceStatus.serviceModel.predict(servicingData)
    serviceStatus = predictions[0]
    return serviceStatus

root = tk.Tk()
root.title("Flight Route Information")

label_flight_id = ttk.Label(root, text="Enter flight:")
label_flight_id.grid(row=0, column=0, padx=10, pady=10)

entry_flight_id = ttk.Entry(root)
entry_flight_id.grid(row=0, column=1, padx=10, pady=10)

button_get_info = ttk.Button(root, text="Get Information", command=update_info)
button_get_info.grid(row=0, column=2, padx=10, pady=10)

label_safety = ttk.Label(root, text="Safety levels at a particular time:\n")
label_safety.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

label_primary_path = ttk.Label(root, text="Primary path: ")
label_primary_path.grid(row=2, column=0, columnspan=3, padx=10, pady=10)

label_alternate_path = ttk.Label(root, text="Alternate path: ")
label_alternate_path.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

label_image = ttk.Label(root, text="Rerouted Path Visualization:")
label_image.grid(row=4, column=0, columnspan=3, padx=10, pady=10)

label_servicing = ttk.Label(root, text="Servicing status:")
label_servicing.grid(row=5, column=0, columnspan=3, padx=10, pady=10)

label_unsafe_cities = ttk.Label(root, text="")
label_unsafe_cities.grid(row=6, column=0, columnspan=3, padx=10, pady=10)

root.mainloop()
