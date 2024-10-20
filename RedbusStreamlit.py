# importing libraries
import pandas as pd
import mysql.connector
import streamlit as slt
from streamlit_option_menu import option_menu
import plotly.express as px
import time

# Function to fetch CSV data for buses
def load_data(file_path):
    df = pd.read_csv(file_path)
    return df["Route_name"].tolist()

# Loading routes for different states
df_k = load_data(r'C:\Users\kirub\OneDrive\Desktop\Redbus\df_k.csv')
df_A = load_data(r'C:\Users\kirub\OneDrive\Desktop\Redbus\df_A.csv')
df_T = load_data(r'C:\Users\kirub\OneDrive\Desktop\Redbus\df_T.csv')
df_G = load_data(r'C:\Users\kirub\OneDrive\Desktop\Redbus\df_G.csv')
df_R = load_data(r'C:\Users\kirub\OneDrive\Desktop\Redbus\df_R.csv')
df_SB = load_data(r'C:\Users\kirub\OneDrive\Desktop\Redbus\df_SB.csv')
df_H = load_data(r'C:\Users\kirub\OneDrive\Desktop\Redbus\df_H.csv')
df_AS = load_data(r'C:\Users\kirub\OneDrive\Desktop\Redbus\df_AS.csv')
df_UP = load_data(r'C:\Users\kirub\OneDrive\Desktop\Redbus\df_UP.csv')
df_WB = load_data(r'C:\Users\kirub\OneDrive\Desktop\Redbus\df_WB.csv')

# Dictionary to map state to route lists
state_routes = {
    "Kerala": df_k, "Adhra Pradesh": df_A, "Telugana": df_T, "Goa": df_G,
    "Rajastan": df_R, "South Bengal": df_SB, "Haryana": df_H, 
    "Assam": df_AS, "Uttar Pradesh": df_UP, "West Bengal": df_WB
}

# Streamlit page configuration
slt.set_page_config(layout="wide")

# Streamlit option menu for navigation
web = option_menu(
    menu_title="🚌Quickride",
    options=["Home", "📍States and Routes"],
    icons=["house", "info-circle"],
    orientation="horizontal"
)

# Home page setting
if web == "Home":
    slt.markdown("<h1 style='text-align: center;'>Welcome to Redbus</h1>", unsafe_allow_html=True)
    slt.image("C:/Users/kirub/OneDrive/Desktop/redbuslogo.png", width=400)

    slt.markdown("""
        <h2>Redbus Data Scraping with Selenium & Dynamic Filtering using Streamlit</h2>
        <p>This project automates data extraction from Redbus and visualizes bus travel details like routes, schedules, fares, and more.</p>
        """, unsafe_allow_html=True)

    slt.subheader(":blue[Skills:] Selenium, Python, Pandas, MySQL, Streamlit.")

# States and Routes page setting
if web == "📍States and Routes":
    S = slt.selectbox("Select a State", list(state_routes.keys()))

    col1, col2 = slt.columns(2)
    with col1:
        select_type = slt.radio("Bus Type", ("Sleeper", "Semi-sleeper", "Others"))
    with col2:
        select_fare = slt.radio("Fare Range", ("50-1000", "1000-2000", "2000 and above"))

    TIME = slt.time_input("Start Time")

    # Select route based on the state
    selected_route = slt.selectbox("Select Route", state_routes[S])

    def fetch_bus_data(route_name, bus_type, fare_range):
        conn = mysql.connector.connect(
            host="localhost", user="root", password="Kiru@2000", database="RED_BUS_DETAILS"
        )
        cursor = conn.cursor()

        # Define fare range
        fare_min, fare_max = (50, 1000) if fare_range == "50-1000" else (1000, 2000) if fare_range == "1000-2000" else (2000, 100000)

        # Bus type condition
        bus_type_condition = {
            "Sleeper": "Bus_type LIKE '%Sleeper%'",
            "Semi-sleeper": "Bus_type LIKE '%Semi Sleeper%'",
            "Others": "Bus_type NOT LIKE '%Sleeper%' AND Bus_type NOT LIKE '%Semi Sleeper%'"
        }[bus_type]

        # SQL query
        query = f'''
            SELECT * FROM bus_details
            WHERE Price BETWEEN {fare_min} AND {fare_max}
            AND Route_name = "{route_name}"
            AND {bus_type_condition} 
            AND Start_time >= '{TIME}'
            ORDER BY Price DESC, Start_time ASC
        '''
        cursor.execute(query)
        data = cursor.fetchall()
        conn.close()

        # Convert to dataframe
        df = pd.DataFrame(data, columns=[
            "ID", "Bus_name", "Bus_type", "Start_time", "End_time", 
            "Total_duration", "Price", "Seats_Available", "Ratings", "Route_link", "Route_name"
        ])
        return df

    # Fetch and display filtered bus data
    bus_data = fetch_bus_data(selected_route, select_type, select_fare)
    slt.dataframe(bus_data)

    
    # Pie chart for seat availability
    slt.subheader("Seat Availability")
    fig_pie = px.pie(bus_data, names="Seats_Available", title="Seats Available")
    slt.plotly_chart(fig_pie, use_container_width=True)
