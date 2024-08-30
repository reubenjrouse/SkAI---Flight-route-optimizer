import tkinter as tk
from tkinter import ttk
# from PIL import Image, ImageTk
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from RouteOptimization import load_data, create_graph, find_optimized_path, plot
import ast
import warnings
import ServiceStatus
from customtkinter import *
from PIL import Image, ImageTk


warnings.filterwarnings("ignore")
fl_df = pd.read_csv('csv\Flight_Database.csv') 
weather_data = pd.read_csv('csv\M1_final.csv')
cities_weather = pd.read_csv('csv\weather_data_cities.csv')
cities_time = pd.read_csv('csv\Cities_FlightDuration_Mins.csv')
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



filename = 'csv\Cities_FlightDuration_Mins.csv'
nodes, graph_data = load_data(filename)
G = create_graph(nodes, graph_data)

def safetyCalculator(city, time):
    time_obj = datetime.strptime(time, "%H:%M") 
    minute = time_obj.minute
    if minute >= 30:
        time_obj += timedelta(hours=1)
    time_obj = time_obj.replace(minute=0, second=0)
    time = time_obj.strftime("%H:%M")

    string_stats = cities_weather[cities_weather['City'] == city][time].values[0]  
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

def displaySafetyLevels(dep_city, dep_time, arr_city, RouteFrame):
    table_frame = CTkScrollableFrame(master=RouteFrame, width = 200, height = 250, orientation='vertical', border_color='white', border_width=2, fg_color='black')

    # Create labels for headers
    header_city = CTkLabel(master=table_frame, text="City", font=("Arial", 14), text_color='white')
    header_city.grid(row=0, column=0, padx=10)

    header_safety = CTkLabel(master=table_frame, text="Safety", font=("Arial", 14), text_color='white')
    header_safety.grid(row=0, column=1, padx=10)  

   
    row_index = 1 
    for city in G.nodes():
        time_of_day = (datetime.strptime(dep_time, "%H:%M") + timedelta(minutes=int(cities_time[cities_time['City'] == dep_city][city].values[0]))).strftime("%H:%M")
        safety_level = safetyCalculator(city, time_of_day)
        if city==dep_city:
            if safety_level>=5:
                color = '#ff8099'
            else:
                color = '#80ff88'
        else:
            if safety_level>=6:
                color = '#ff8099'
            else:
                color = '#80ff88'

        
        city_label = CTkLabel(master=table_frame, text=f'{city} at {time_of_day}', font=("Arial", 12), text_color=color)
        city_label.grid(row=row_index, column=0, padx=10)  

        
        safety_label = CTkLabel(
            master=table_frame, text=safety_level, font=("Arial", 12), text_color=color
        )
        safety_label.grid(row=row_index, column=1, padx=10)  

        row_index += 1  
    table_frame.pack(fill="both", expand=True)
    table_frame.place(relx=0.5, rely=0.45, anchor="center")


    unsafe_nodes, safe_nodes = unsafeCities(dep_city, arr_city, dep_time, G)
    primary_path, primary_time, alternate_path, alternate_time = find_optimized_path(G, dep_city, arr_city, unsafe_nodes)
    primary_path_str = f"Primary path: {primary_path} (Total Time: {primary_time} minutes)"
    if alternate_path and len(primary_path) > 2:
        reroute_city = primary_path[1]  
        primary_path_str += f"\nRerouted due to bad weather at {reroute_city} "

    label_primary_path= CTkLabel(master=RouteFrame, text=primary_path_str, font=("Arial", 13, "bold"), text_color='black')
    label_primary_path.place(relx=0.02, rely=0.85, anchor="w")

    if alternate_path:
        alternate_path_str=f"Rerouted path: {alternate_path} (Total Time: {alternate_time} minutes)"
    else:
        alternate_path_str ="No Reroute needed"

    label_alternate_path= CTkLabel(master=RouteFrame, text=alternate_path_str, font=("Arial", 13, "bold"), text_color='black')
    label_alternate_path.place(relx=0.02, rely=0.95, anchor="w")
    generate_map = CTkButton(
        master=RouteFrame,
        text="Map",
        text_color="white",
        fg_color="red",
        corner_radius=8,
        hover=True,
        hover_color="gray",
        command=lambda: plot(G, primary_path, alternate_path, dep_city, arr_city) ,
        width=5
    )

    
    generate_map.place(relx=0.9, rely=0.9, anchor="center")

def predictService(flightID, ServiceFrame):
    modelMapping = {'Airbus A319': 1, 'Airbus A320': 2, 'Boeing 777': 3, 'Boeing 787': 4}
    servicingData = pd.DataFrame({
        "Days Since Servicing": [fl_df[fl_df['FlightID'] == flightID]['Days_Since_Serving'].values[0]],
        "Warranty Status": [fl_df[fl_df['FlightID'] == flightID]['Warranty_Status'].values[0]],
        "Days Since Purchase": [fl_df[fl_df['FlightID'] == flightID]['Days_Since_Purchase'].values[0]],
        "Company": [modelMapping[fl_df[fl_df['FlightID'] == flightID]['Model'].values[0]]]
    })

    predictions = ServiceStatus.serviceModel.predict(servicingData)
    serviceStatus = predictions[0]
    service_status_label = CTkLabel(
        master=ServiceFrame,
        text=serviceStatus,
        font=("Arial", 14, "bold"),
        text_color="black",
        padx=20,
        pady=10,
    )
    service_status_label.place(relx=0.5, rely=0.90, anchor="center")
    return serviceStatus

def timeString(days):
    years = days // 365
    days %= 365
    months = days // 30
    days = days % 30

    
    years_text = f"{years:02} YEARS"
    months_text = f"{months:02} MONTHS"
    days_text = f"{days:02} DAYS"
    

    return years_text, months_text, days_text


def displayServiceFrame(flight_id, ServiceFrame):
    days_servicing = fl_df[fl_df['FlightID'] == flight_id]['Days_Since_Serving'].values[0]
    days_servicing_label = CTkLabel(
        master=ServiceFrame,
        text='Time since servicing',
        font=("Arial", 14, "bold"),
        text_color="black",
        padx=20,
        pady=10,
    )
    days_servicing_label.place(relx=0.5, rely=0.2, anchor="center")
    years_service, months_service, days_service = timeString(days_servicing)

    service_years_label = CTkLabel(
        master=ServiceFrame,
        text=years_service,
        font=("Arial", 10, "bold"),
        fg_color="black",
        text_color="#80ff88",
        padx=20,
        pady=10,
    )
    service_months_label = CTkLabel(
        master=ServiceFrame,
        text=months_service,
        font=("Arial", 10, "bold"),
        fg_color="black",
        text_color="#80ff88",
        padx=20,
        pady=10,
    )
    service_days_label = CTkLabel(
        master=ServiceFrame,
        text=days_service,
        font=("Arial", 10, "bold"),
        fg_color="black",
        text_color="#80ff88",
        padx=20,
        pady=10,
    )
    service_years_label.place(relx=0.32,rely=0.275,anchor="center")
    service_months_label.place(relx=0.5,rely=0.275,anchor="center")
    service_days_label.place(relx=0.68,rely=0.275,anchor="center")

    last_purchase = fl_df[fl_df['FlightID'] == flight_id]['Days_Since_Purchase'].values[0]

    years_purchase, months_purchase, days_purchase = timeString(last_purchase)
    days_purchasing_label = CTkLabel(
        master=ServiceFrame,
        text='Time since purchase',
        font=("Arial", 14, "bold"),
        text_color="black",
        padx=20,
        pady=10,
    )
    days_purchasing_label.place(relx=0.5, rely=0.375, anchor="center")
    service_years_label = CTkLabel(
        master=ServiceFrame,
        text=years_purchase,
        font=("Arial", 10, "bold"),
        fg_color="black",
        text_color="#80ff88",
        padx=20,
        pady=10,
    )
    service_months_label = CTkLabel(
        master=ServiceFrame,
        text=months_purchase,
        font=("Arial", 10, "bold"),
        fg_color="black",
        text_color="#80ff88",
        padx=20,
        pady=10,
    )
    service_days_label = CTkLabel(
        master=ServiceFrame,
        text=days_purchase,
        font=("Arial", 10, "bold"),
        fg_color="black",
        text_color="#80ff88",
        padx=20,
        pady=10,
    )
    service_years_label.place(relx=0.32,rely=0.45,anchor="center")
    service_months_label.place(relx=0.5,rely=0.45,anchor="center")
    service_days_label.place(relx=0.68,rely=0.45,anchor="center")


    model = fl_df[fl_df['FlightID'] == flight_id]['Model'].values[0]
    model_label = CTkLabel(
        master=ServiceFrame,
        text=f'Model: {model}',
        font=("Arial", 14, "bold"),
        text_color="black",
        padx=20,
        pady=10,
    )
    model_label.place(relx=0.5, rely=0.55, anchor="center")

    warranty_status = fl_df[fl_df['FlightID'] == flight_id]['Warranty_Status'].values[0]
    if (warranty_status == True):
        warranty_status = "Active"
    else:
        warranty_status = "Expired"
    warranty_status_label = CTkLabel(
        master=ServiceFrame,
        text=f'Warranty status: {warranty_status}',
        font=("Arial", 14, "bold"),
        text_color="black",
        padx=20,
        pady=10,
    )
    warranty_status_label.place(relx=0.5, rely=0.65, anchor="center")

    
    check_service_status = CTkButton(
        master=ServiceFrame,
        text="Check service status",
        text_color="white",
        fg_color="red",
        corner_radius=8,
        hover=True,
        hover_color="gray",
        command=lambda: predictService(flight_id,ServiceFrame)    
    )
    check_service_status.place(relx=0.5, rely=0.80, anchor="center")





   


def get_flight_info():
    
    flight_id = combobox.get()
    if not fl_df[fl_df['FlightID'] == flight_id].empty:
        dep_city = fl_df[fl_df['FlightID'] == flight_id]['DEP_City'].values[0]
        dep_time = fl_df[fl_df['FlightID'] == flight_id]['Dep_Time'].values[0]
        arr_city = fl_df[fl_df['FlightID'] == flight_id]['ARR_City'].values[0]
        fuel_cap = fl_df[fl_df['FlightID'] == flight_id]['Fuel_Cap'].values[0]
        pass_cap = fl_df[fl_df['FlightID'] == flight_id]['Pass_Load'].values[0]

        info_window = CTk()
        info_window.geometry("1200x700")
        set_appearance_mode("light")

        # Create 3 frames for different information sections
        flightInfoFrame = CTkFrame(master=info_window, corner_radius=10, fg_color="#cfcfcf", width=1106)
        flightInfoFrame.pack(expand=True)
        flightInfoFrame.place(relx=0.5, rely=0.15, anchor="center")

        label_flght_id = CTkLabel(
        master=flightInfoFrame,
        text=f'Flight ID: {flight_id}',
        font=("Arial", 20, "bold"),
        text_color="black"
        )
        label_flght_id.place(relx=0.5, rely=0.15, anchor="center") 

        label_dep_time = CTkLabel(
            master=flightInfoFrame,
            text=f'Departure time: {dep_time}',
            font=("Arial", 15),
            text_color="black"
        )
        label_dep_time.place(relx=0.5, rely=0.30, anchor="center")  

        label_origin_2_destination = CTkLabel(
            master=flightInfoFrame,
            text=f'From: {dep_city} to {arr_city}',
            font=("Arial", 15),
            text_color="black"
        )
        label_origin_2_destination.place(relx=0.5, rely=0.45, anchor="center")

        label_fuel_capacity = CTkLabel(
            master=flightInfoFrame,
            text=f'Total fuel capacity: {fuel_cap}',
            font=("Arial", 15),
            text_color="black"
        )
        label_fuel_capacity.place(relx=0.5, rely=0.60, anchor="center")

        label_pass_load = CTkLabel(
            master=flightInfoFrame,
            text=f'Total passenger load: {pass_cap}',
            font=("Arial", 15),
            text_color="black"
        )
        label_pass_load.place(relx=0.5, rely=0.75, anchor="center")
        




        RouteFrame = CTkFrame(master=info_window, corner_radius=10, fg_color="#cfcfcf", width=550, height=400)
        RouteFrame.pack(expand=True)
        RouteFrame.place(relx=0.27, rely=0.6, anchor="center")
        displaySafetyLevels(dep_city, dep_time, arr_city, RouteFrame)

        


        ServiceFrame = CTkFrame(master=info_window, corner_radius=10, fg_color="#cfcfcf", width=550, height=400)
        ServiceFrame.pack(expand=True)
        ServiceFrame.place(relx=0.74, rely=0.6, anchor="center")
        displayServiceFrame(flight_id, ServiceFrame)


        
        info_window.mainloop()
        

        
    else:
        label_error = CTkLabel(
            master=app,
            text=f'',
            font=("Arial", 15),
            text_color="black"
        )
        label_error.place(relx=0.5, rely=0.85, anchor="center")
        label_error.configure(text="Invalid Flight ID. Please enter a valid Flight ID.")
 
app = CTk()
app.geometry("1200x700")
set_appearance_mode("light")
label_select_flight = CTkLabel(master=app, text="SELECT A FLIGHT", font = ("Arial", 25), text_color="black")
label_select_flight.place(relx=0.5, rely=0.4, anchor="center")
flight_ids = fl_df["FlightID"].tolist()
combobox = CTkComboBox(
    master=app,
    values=flight_ids,
    fg_color="white",
    border_color="black",
    corner_radius=5,
    dropdown_text_color="black",
    dropdown_font=CTkFont(size=14),
    hover=True,
    button_hover_color="lightgray",
    dropdown_hover_color="red",
)
get_info_button = CTkButton(
    master=app,
    text="Get Information",
    text_color="white",
    fg_color="red",
    corner_radius=8,
    hover=True,
    hover_color="gray",
    command=get_flight_info,  
)

get_info_button.place(relx=0.5, rely=0.6, anchor="center")
logo_path = "assets\Group 1finalLogo.png" 
logo = Image.open(logo_path)


resized_image = logo

photo_image = ImageTk.PhotoImage(resized_image)

image_label = CTkLabel(master=app, image=photo_image,text="")
image_label.place(relx=0.5,rely=0.5, anchor="center")
image_label.pack() 



combobox.place(relx=0.5, rely=0.5, anchor="center")
app.mainloop()
