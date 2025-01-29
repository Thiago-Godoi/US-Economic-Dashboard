import streamlit as st
from utils import fetch_data, fetch_latest_value, nav_page, frequency_map
from datetime import datetime
from pathlib import Path

# Step 1: Hide the default sidebar and set up the page config
st.set_page_config(page_title="Dashboard - Home", layout="wide", initial_sidebar_state="collapsed")

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
        text-shadow: 0 0 15px rgba(255, 255, 255, 0.2), 0 0 30px rgba(255, 255, 255, 0.1);  /* Glow effect on title */
    }

    .stButton > button {
        width: 317px !important;  /* Increase width slightly */
        padding: 8px 16px;  /* Adjust the padding to keep the height the same */
        font-size: 14px;  /* Maintain smaller font size */
        margin: 5px 0;  /* Add some spacing between buttons */
    }

    .stButton>button:hover {
        background-color: #444444;
        color: white;  /* Keep text white on hover */
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

st.session_state.page = "Home"  # Default to Home if no page is set

# Step 3: Create your custom sidebar using columns (replace the default sidebar)
sidebar, content = st.columns([1, 3])

# Custom sidebar content
with sidebar:
    st.markdown("## 📁 Navigation")
    st.markdown("### 💸 Inflation Data")
    if st.button("CPI (Consumer Price Index)"):
        nav_page("CPI")
    if st.button("PPI - Commodities"):
        nav_page("PPI_Commodities")
    if st.button("PPI - Industry"):
        nav_page("PPI_Industry")
    if st.button("PCE (Personal Consumption Expenditures)"):
        nav_page("PCE")

    st.markdown("### 🏛️ Government Data")
    if st.button("GDP (Gross Domestic Product)"):
        nav_page("GDP")
    if st.button("GNP (Gross National Product)"):
        nav_page("GNP")
    if st.button("Government Spending"):
        nav_page("Government_Spending")
    if st.button("Net Exports"):
        nav_page("Net_Exports")

    st.markdown("### 👷 Employment Data")
    if st.button("Employment"): 
        nav_page("Employment")
    if st.button("Layoffs"):
        nav_page("Layoffs")
    if st.button("Unemployment Rate"):
        nav_page("Unemployment_Rate")

    st.markdown("### 🛍️ Sales Data")
    if st.button("Retail Sales"):
        nav_page("Retail_Sales")
    if st.button("Retail Inventories"):
        nav_page("Retail_Inventories")

    st.markdown("### 🏗️ Construction Data")
    if st.button("Construction"):
        nav_page("Construction")

    st.markdown("### 🏭 Capacity Data")
    if st.button("Capacity Utilization"):
        nav_page("Capacity_Utilization")

    st.markdown("### 📋 Survey Data")
    if st.button("Consumer Sentiment"):
        nav_page("Consumer_Sentiment")

# Main content: Your main page content goes here (in the `content` column)
with content:
    st.title("📈 US Economic Dashboard")
    st.subheader(f"YoY%", help="Based on the latest released number for each data")

    if "frequency" not in st.session_state:
        st.session_state.frequency = "Monthly"

    # Frequency map to translate human-readable to FRED API short codes
    frequency = st.selectbox(
        "Data frequency: ",
        ["Monthly", "Quarterly", "Semiannual", "Annual"],
        index=["Monthly", "Quarterly", "Semiannual", "Annual"].index(st.session_state.frequency),
        help="Frequency will apply to all data."
    )

    st.session_state.frequency = frequency
    
    if "start_date" not in st.session_state:
        st.session_state.start_date = "2000-01-01"

    year_input = st.text_input("Enter a year (YYYY) for the start date: ", value=st.session_state.start_date.split("-")[0], help="The start date will apply to all data. Date will automatically adjust to the first available one if entered year is not available. The start date is set to be YYYY-01-01.")
    try:
        start_year = int(year_input)
        if start_year > int(datetime.now().year):
            st.error("Year can't be later than current year")
        elif start_year < 1600:
            st.error("Minimum value is 1600")
        else:
            st.session_state.start_date = f"{start_year}-01-01"
    except ValueError:
        st.error("Please enter a valid year (e.g., 2021).")
        st.session_state.start_date = "2000-01-01"
    
    # Dataset list for the homepage
    datasets_list = [
        ("Inflation Data", {"CPI (Consumer Price Index)": "CPIAUCSL", "PPI - Industry (Producer Price Index by Industry)": "PCUOMFGOMFG", "PPI - Commodities (Producer Price Index by Industry)": "PPIACO", "PCE (Personal Consumption Expenditures)": "PCEPI"}),
        ("Government Data", {"GDP (Gross Domestic Product)": "GDP", "GNP (Gross National Product)": "GNP", "Government Spending (Government Total Expenditures)": "W068RCQ027SBEA", "Net Exports of Goods and Services": "NETEXP"}),
        ("Sales Data", {"Advance Retail Sales: Retail Trade and Food Services": "RSAFS", "Retailers: Inventories to Sales Ratio": "RETAILIRSA"}),
        ("Construction Data", {"Construction (New Privately-Owned Housing Units Under Construction)": "UNDCONTSA"}),
        ("Capacity Data", {"Capacity Utilization (Capacity Utilization: Total Index)": "TCU"}),
        ("Employment Data", {"Employment (All Employees: Total Nonfarm)": "PAYEMS", "Layoffs (Layoffs and Discharges: Total Nonfarm)": "JTSLDL", "Unemployment Rate": "UNRATE"}),
        ("Survey Data", {"Consumer Sentiment (University of Michigan: Consumer Sentiment)": "UMCSENT"})
    ]

    # Code to display the datasets
    cols = st.columns(3)
    col_idx = 0

    for data_name, dataset in datasets_list:
        with cols[col_idx]:

            st.subheader(f"{data_name}")
            st.markdown("<br>", unsafe_allow_html=True)

            for name, series_id in dataset.items():
                value, date = fetch_latest_value(series_id, frequency=st.session_state.frequency)

                if value == "---":

                    st.metric(
                    label=name, 
                    value="---", 
                    delta="",
                    delta_color="off"
                    )

                else:

                    st.metric(
                    label=name, 
                    value=f"{value:.2f}%", 
                    delta=value,
                    delta_color="normal"
                    )

        col_idx += 1
        if col_idx > 2:
            col_idx = 0

    st.markdown("---")
    st.markdown("Developed by Thiago Godoi (https://github.com/Thiago-Godoi) | Data from FRED API")


#Open the dashboard on your browser with: streamlit run "c:/Users/thiag/OneDrive/Documentos/Summer Parcitas/dashboard/Home.py"
#Add this to the top of each page to change page name: " st.set_page_config(page_title="CPI Analysis") "