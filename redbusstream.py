import streamlit as st
import mysql.connector
import pandas as pd
from streamlit_option_menu import option_menu

st.set_page_config(layout="wide")
web = option_menu(menu_title="Quickride",
                  options=["Home", "📍Find Your Way"],
                  icons=["house", "info-circle"],
                  orientation="horizontal"
                  )


# Custom styles for the Streamlit app
# Custom styles for the Streamlit app
st.markdown(
    """
    <style>
        body {
            background-color: #F0F4F8;  /* Soft light blue */
            font-family: 'Arial', sans-serif; /* Changed font to Arial */
        }
        h1 {
            text-align: center;
            color: #E92421; /* Red color */
            font-size: 48px; /* Adjusted font size */
            margin: 20px 0;
            font-weight: bold;
        }
        .header-home {
            font-size: 42px;
            color: #E92421;
            font-weight: bold;
        }
        .header-filter {
            font-size: 36px;
            color: #E92421;
            font-weight: bold;
        }
        .header-help {
            font-size: 36px;
            color: #E92421;
            font-weight: bold;
        }
        .welcome {
            text-align: center;
            font-size: 36px;
            color: #E92421;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .image-center {
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .image-center img {
            max-width: 80%;  /* Set max width for responsive scaling */
            height: auto;     /* Keep original aspect ratio */
            border: none;     /* Remove border styling */
        }
        .image-caption {
            text-align: center;
            font-size: 20px;
            color: #4a4a4a;
            margin-top: 10px;
            font-weight: normal;
        }
        .filter-header, .filter-label {
            color: #E92421;
            font-weight: bold;
        }
        .input-text, .select-box, .slider {
            border: 1px solid #E92421;
            border-radius: 5px;
            padding: 8px;
            font-size: 16px;
            width: 100%;
        }
    </style>
    """, unsafe_allow_html=True
)

# Home Tab
if web == "Home":
    

    # Set the title of the app
    st.title("🚍 Welcome to RedBus!")

    

    # Description
    st.write("""
    RedBus is your go-to platform for booking bus tickets online. Whether you're planning a trip with friends or heading home for the holidays, we have the best options for you. 
    Explore our user-friendly interface to find, compare, and book buses from various operators.
    """)

    # Features Section
    st.header("Key Features")
    st.write("- **Wide Range of Options:** Choose from numerous bus operators and routes.")
    st.write("- **Easy Booking:** Simple and quick booking process.")
    st.write("- **Secure Payments:** Multiple secure payment options for your convenience.")
    st.write("- **Customer Support:** 24/7 support for any queries or issues.")

    # Call to Action
    st.header("Start Your Journey")
    st.write("Ready to book your bus tickets? Click the button below to explore available routes!")

    if st.button("Book Now"):
        st.write("Redirecting to booking page...")
        # Here you can add functionality to redirect to the booking page or show available options

    # Footer
    st.markdown("---")
    st.write("© 2024 RedBus. All rights reserved.")


# Filtered Data Tab
if web == "📍Find Your Way":
    # Title of the app
    st.markdown("<h1 style='color: green; font-weight: bold;'>Bus Data</h1>", unsafe_allow_html=True)

    # MySQL connection setup
    def get_connection():
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="Kiru@2000",  # Replace with your MySQL root password
            database="RED_BUS_DETAILS"
        )

    # Function to filter data based on user input
    def filter_data(state, route, bus_type, price_range, star_rating_range, seat_availability, Start_time=None, End_time=None):
        query = "SELECT * FROM bus_details WHERE 1=1"
        params = []

        # State filter
        if state:
            query += " AND state = %s"
            params.append(state)

        # Route filter
        if route:
            query += " AND route_name IN (%s)" % ','.join(['%s'] * len(route))
            params.extend(route)

        # Bus type filter (A/C or Non-A/C based on radio button)
        if bus_type == 'A/C':
            query += " AND bus_type = %s"
            params.append('A/C')
        elif bus_type == 'NON A/C':
            query += " AND bus_type = %s"
            params.append('NON A/C')
        else:
            # Exclude "Sleeper" and "Semi-Sleeper" types using parameterized queries
            query += " AND bus_type NOT LIKE %s AND bus_type NOT LIKE %s"
            params.extend(['%Sleeper%', '%Semi-Sleeper%'])

        # Price range filter
        query += " AND price BETWEEN %s AND %s"
        params.extend(price_range)

        # Star rating filter
        if star_rating_range[0] > 0.0 or star_rating_range[1] < 5.0:
            query += " AND star_rating BETWEEN %s AND %s"
            params.extend(star_rating_range)

        # Seat availability filter
        if seat_availability > 0:
            query += " AND seats_available >= %s"
            params.append(seat_availability)

        # Departing time filter
        if Start_time is not None:
            query += " AND Start_time >= %s"
            params.append(Start_time)

        # Reaching time filter
        if End_time is not None:
            query += " AND End_time <= %s"
            params.append(End_time)

        return query, params

    # Fetch data from MySQL database based on query
    def load_data(query, params=None):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(rows, columns=columns)
        conn.close()
        return df

    # Sidebar filters
    st.sidebar.header("Find Your Ideal Bus Route!")

    # State Filter
    states = load_data("SELECT DISTINCT state FROM bus_details")
    state_filter = st.sidebar.selectbox("State", states['state'])

    # Route Name Filter (filtered based on the selected state)
    if state_filter:
        routes = load_data("SELECT DISTINCT route_name FROM bus_details WHERE state = %s", [state_filter])
        route_filter = st.sidebar.multiselect("Route Name", routes['route_name'])
    else:
        route_filter = []

    # Bus Type Filter (using radio buttons)
    bus_type_filter = st.sidebar.radio("Bus Type", ['A/C', 'NON A/C', 'others'])  # A/C or Non A/C

    # Price Range Filter
    price_min, price_max = load_data("SELECT MIN(price), MAX(price) FROM bus_details WHERE state = %s", [state_filter]).iloc[0]
    price_range_filter = st.sidebar.slider("Price Range", float(price_min), float(price_max), (float(price_min), float(price_max)))

    # Star Rating Filter (double-sided slider for a range)
    star_rating_range_filter = st.sidebar.slider("Star Rating Range", 0.0, 5.0, (0.0, 5.0))

    # Seat Availability Filter
    seat_availability_filter = st.sidebar.slider("Minimum Seats Available", 0, 50, 0)

    # Time Selection Filters for Departing and Reaching
    Start_time_filter = st.sidebar.time_input("Start Time", None)
    End_time_filter = st.sidebar.time_input("End Time", None)

    # Convert times to 24-hour format (if None, pass None to avoid filtering by time)
    def time_to_24hr(time_input):
        return time_input.strftime('%H:%M') if time_input is not None else None

    # Filter data based on user input
    query, params = filter_data(state_filter, route_filter, bus_type_filter, price_range_filter, star_rating_range_filter, seat_availability_filter, time_to_24hr(Start_time_filter), time_to_24hr(End_time_filter))
    filtered_data = load_data(query, params)

    # Display filtered data
    st.write("### Filtered Bus Data")
    st.dataframe(filtered_data)
