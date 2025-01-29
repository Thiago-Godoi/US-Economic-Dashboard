import streamlit as st
from utils import fetch_data, nav_page, frequency_map, get_latest_date
import pandas as pd
from io import BytesIO

# Hide the sidebar completely
st.set_page_config(page_title="Capacity Utilization", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS styling for both buttons (Home and Download)
st.markdown(
    """
    <style>
    body {
        background-color: #1f1f1f;  /* Softer dark background */
        color: #e0e0e0;  /* Light text for contrast */
    }

    h1 {
        color: #e0e0e0;  /* Light text for title */
        text-align: center;
        font-size: 3em;
        text-shadow: 0 0 15px rgba(255, 255, 255, 0.7), 0 0 30px rgba(255, 255, 255, 0.1);  /* Glow effect on title */
    }

    h2 {
        color: #e0e0e0;  /* Light text for title */
        font-size: 3em;
        text-shadow: 0 0 15px rgba(255, 255, 255, 0.5), 0 0 30px rgba(255, 255, 255, 0.1);  /* Glow effect on title */
    }

    /* Custom button styles */
    .stButton>button, .stDownloadButton>button {
        background-color: #333333;  /* Dark gray background */
        color: white;
        border-radius: 12px;
        padding: 10px 20px;
        font-size: 1.1em;
        border: none;
        cursor: pointer;
        transition: background-color 0.3s, box-shadow 0.3s;
    }

    .stButton>button:hover, .stDownloadButton>button:hover {
        background-color: #444444;  /* Slightly lighter gray on hover */
        color: white;
        box-shadow: 0 0 10px 2px rgba(255, 255, 255, 0.1);  /* Glow effect */
    }

    .stTextInput>div>div>input {
        background-color: #333333;  /* Soft dark gray input background */
        color: #e0e0e0;
        border-radius: 8px;
        padding: 10px;
        transition: box-shadow 0.3s;
    }

    .stTextInput>div>div>input:focus {
        box-shadow: 0 0 10px 2px rgba(255, 255, 255, 0.6);  /* Blue glow on focus */
    }

    .stSidebar {
        background-color: #333333;  /* Lighter sidebar gray */
        color: #e0e0e0;
    }

    .stMarkdown {
        font-family: 'Arial', sans-serif;
    }
    </style>
    """,
    unsafe_allow_html=True
)

if "frequency" not in st.session_state:
    st.session_state.frequency = "Monthly"

freq_code = frequency_map.get(st.session_state.frequency, "m")

st.title("Capacity Utilization: Total Index")

units_options = {
    "Absolute value": "lin",
    "Percent change one year ago": "pc1",
    "Percent change": "pch"
    }
selected_units = st.selectbox(
    "Select data type: ",
    options=list(units_options.keys()),
    index=1,
    help="Choose how you want the data to be displayed on this page"
)

units_code = units_options[selected_units]

st.subheader(f"Data: {selected_units}")

try:
    latest_date = get_latest_date("TCU")
    data = fetch_data("TCU", start_date=st.session_state.start_date, frequency=freq_code, units=units_code)

    if not data.empty:
        first_data_date = data.index.min().strftime("%Y-%m-%d")
    else:
        first_data_date = "No data available"

    st.line_chart(data["value"])

    excel_file = BytesIO()
    data.to_excel(excel_file, index=True, sheet_name="Capacity Utilization Data")
    excel_file.seek(0)

    csv_file = data.to_csv(index=True).encode("utf-8")

    st.markdown(f"First data from: {first_data_date}")
    st.markdown(f"Last data from: {latest_date}")
    st.markdown('<div class="stDownloadButton">', unsafe_allow_html=True)
    st.download_button(
        label="💾 Download Capacity Utilization Data as Excel",
        data=excel_file,
        file_name="Capacity_Utilization_Data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    st.download_button(
        label="📄 Download Capacity Utilizatiom Data as CSV",
        data=csv_file,
        file_name="Capacity_Utilization_Data.csv",
        mime="text/csv"
    )
    st.markdown('</div>', unsafe_allow_html=True)
except Exception as e:
    st.error(f"Error fetching Capacity Utilization data: {e}")

# Step 1: Add a "Go to Home" button
if st.button("🏠︎"):
    # This will redirect to the Home.py page
    nav_page("Home")
