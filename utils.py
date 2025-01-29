import requests
import pandas as pd
from datetime import datetime
import json
import streamlit as st
import plotly.express as px
import statsmodels.api as sm
from pmdarima import auto_arima

API_KEY = '05f031602f9e164084ccd6f8d44894eb'
BASE_URL = 'https://api.stlouisfed.org/fred/'

# Frequency map to translate human-readable to FRED API short codes
frequency_map = {
    "Monthly": "m",
    "Quarterly": "q",
    "Semiannual": "sa",
    "Annual": "a"
}

def load_frequency_from_file():
    try:
        with open("frequency.json", "r") as f:
            return json.load(f).get("frequency", "Monthly")
    except FileNotFoundError:
        return "Monthly"

def get_latest_date(series_id):
    """
    Fetch the latest available date for a given FRED series.
    Returns the latest date in YYYY-MM-DD format.
    """
    endpoint = 'series/observations'
    params = {
        "series_id": series_id,
        "api_key": API_KEY,
        "file_type": "json",
        "sort_order": "desc",  # Get the latest data first
        "limit": 1  # Only fetch the latest observation
    }
    response = requests.get(BASE_URL + endpoint, params=params)
    
    if response.status_code == 200:
        data = response.json()
        if "observations" in data and data["observations"]:
            latest_date = data["observations"][0]["date"]
            try:
                # Ensure the date is valid and in YYYY-MM-DD format
                return datetime.strptime(latest_date, "%Y-%m-%d").strftime("%Y-%m-%d")
            except ValueError:
                raise ValueError(f"Invalid date format returned by FRED: {latest_date}")
        else:
            # No data observations available
            print(f"No data available for series_id = {series_id}.")
            return None
    else:
        raise ValueError(f"Failed to fetch latest date for series_id = {series_id}: {response.text}")

@st.cache_data
def fetch_data(series_id, start_date="2000-01-01", end_date=None, frequency='m', units='pc1'):
    """
    Fetch data from the FRED API with dynamic end_date.
    """

    valid_frequencies = {
        "CUUS0000SAH31": ["sa", "a"]
    }
    # Check if the series has restrictions
    if series_id in valid_frequencies and frequency not in valid_frequencies[series_id]:
        print(f"Frequency '{frequency}' is not supported for series '{series_id}'. Returning empty data.")
        return pd.DataFrame()  # Return an empty DataFrame

    # Fetch the latest available end_date if not provided
    if end_date is None:
        end_date = get_latest_date(series_id)
        if not end_date:
            raise ValueError(f"No valid end_date available for series_id = {series_id}.")
    
    print(f"Fetching data for series_id = {series_id}, frequency = {frequency}, end_date = {end_date}")
    
    endpoint = 'series/observations'
    params = {
        "series_id": series_id,
        "api_key": API_KEY,
        "file_type": "json",
        "observation_start": start_date,
        "observation_end": end_date,  # Use the dynamically fetched end_date
        "frequency": frequency.lower(),
        "units": units
    }
    response = requests.get(BASE_URL + endpoint, params=params)
    if response.status_code == 200:
        data = response.json()
        if "observations" in data and data["observations"]:
            df = pd.DataFrame(data["observations"])
            df["date"] = pd.to_datetime(df["date"])
            df.set_index("date", inplace=True)
            df["value"] = pd.to_numeric(df["value"].replace('.', None), errors="coerce")
            return df
        else:
            raise ValueError(f"No observations found for series_id = {series_id}.")
    else:
        raise ValueError(f"Failed to fetch data: {response.text}")

@st.cache_data
def fetch_latest_value(series_id, frequency="Monthly"):
    """
    Fetch the most recent value of a series, handling edge cases.
    """
    try:
        freq_code = frequency_map.get(frequency, "m")
        df = fetch_data(series_id, frequency=freq_code)
        
        if df.empty:
            # No data available for this frequency
            return "---", "---"
        
        # Ensure 'value' column is numeric
        df["value"] = pd.to_numeric(df["value"], errors="coerce")

        # Drop rows with NaN values in 'value' column
        df = df.dropna(subset=["value"])

        if df.empty:
            # Data exists but all values are NaN
            return "---", "---"

        # Return the most recent non-NaN value
        return df.iloc[-1]["value"], df.index[-1]
    except Exception as e:
        # Log the error for debugging
        print(f"Error in fetch_latest_value: {e}")
        return "---", "---"


from streamlit.components.v1 import html

def nav_page(page_name, timeout_secs=3):
    nav_script = """
        <script type="text/javascript">
            function attempt_nav_page(page_name, start_time, timeout_secs) {
                var links = window.parent.document.getElementsByTagName("a");
                for (var i = 0; i < links.length; i++) {
                    if (links[i].href.toLowerCase().endsWith("/" + page_name.toLowerCase())) {
                        links[i].click();
                        return;
                    }
                }
                var elasped = new Date() - start_time;
                if (elasped < timeout_secs * 1000) {
                    setTimeout(attempt_nav_page, 100, page_name, start_time, timeout_secs);
                } else {
                    alert("Unable to navigate to page '" + page_name + "' after " + timeout_secs + " second(s).");
                }
            }
            window.addEventListener("load", function() {
                attempt_nav_page("%s", new Date(), %d);
            });
        </script>
    """ % (page_name, timeout_secs)
    html(nav_script)