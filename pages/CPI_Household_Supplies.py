import streamlit as st
from utils import fetch_data, nav_page, frequency_map, get_latest_date, fetch_latest_value
import pandas as pd
from io import BytesIO

# Page configuration
st.set_page_config(page_title="CPI - Household Supplies", layout="wide", initial_sidebar_state="collapsed")

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

# Title and Header
st.title("Consumer Price Index (CPI) - Household Supplies")

if "frequency" not in st.session_state:
    st.session_state.frequency = "Monthly"

freq_code = frequency_map.get(st.session_state.frequency, "m")

# Units options for display
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

# Fetch and display data for the Food CPI subcategory

try:
    latest_date = get_latest_date("CUUS0000SAH31")
    data = fetch_data("CUUS0000SAH31", start_date=st.session_state.start_date, frequency=freq_code, units=units_code)

    if not data.empty:
        first_data_date = data.index.min().strftime("%Y-%m-%d")
    else:
        first_data_date = "No data available"

    st.line_chart(data["value"])

    excel_file = BytesIO()
    data.to_excel(excel_file, index=True, sheet_name="Household Supplies CPI Data")
    excel_file.seek(0)

    csv_file = data.to_csv(index=True).encode("utf-8")

    st.markdown(f"First data from: {first_data_date}")
    st.markdown(f"Last data from: {latest_date}")
    st.markdown('<div class="stDownloadButton">', unsafe_allow_html=True)
    st.download_button(
        label="💾 Download Household Supplies CPI Data as Excel",
        data=excel_file,
        file_name="Household_Supplies_CPI_Data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    st.download_button(
        label="📄 Download Household Supplies CPI Data as CSV",
        data=csv_file,
        file_name="CPI_Data.csv",
        mime="text/csv"
    )
    st.markdown('</div>', unsafe_allow_html=True)
except Exception as e:
    st.markdown("Household Supplies CPI data is only available on a semiannual or annual basis. Please adjust the frequency to view this window properly")
    print(f"Error fetching Household Supplies CPI data: {e}")

# Add a navigation button to return to the main CPI page
if st.button("Back to CPI"):
    nav_page("CPI")
