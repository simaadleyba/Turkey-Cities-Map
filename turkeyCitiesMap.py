# Import necessary libraries
pip install beautifulsoup4

import requests
import pandas as pd
from bs4 import BeautifulSoup
from unidecode import unidecode
import streamlit as st
from streamlit_folium import folium_static
import folium

# Define the app title
st.title("Turkish Cities Map")

# Load the data
url = 'https://www.atlasbig.com/tr/turkiye-nin-illeri'
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser', from_encoding="utf-8")
table = soup.find('table', {'class': 'table-bordered'})
header = [th.text for th in table.find_all('th')]
rows = []
for tr in table.find_all('tr')[1:]:
    rows.append([td.text for td in tr.find_all('td')])
df = pd.DataFrame(rows, columns=header)
df = df.apply(lambda x: x.str.encode('utf-8').str.decode('utf-8'))

# Convert the "İl" column to ASCII characters using unidecode
df["Il_ascii"] = df["İl"].apply(unidecode)

# Sort the DataFrame by the "Il_ascii" column
df = df.sort_values("Il_ascii").reset_index(drop=True)

# Remove the "Il_ascii" column
df.drop(columns=["Il_ascii"], inplace=True)

# Adding latitude and longitude to df
url = 'http://www.beycan.net/1057/illerin-enlem-ve-boylamlari.html'
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser', from_encoding="utf-8")
table = soup.find('table', {'class': 'stable12'})
latitudes = []
longitudes = []
for row in table.find_all("tr")[1:]:
    cells = row.find_all("td")
    latitudes.append(cells[2].text)
    longitudes.append(cells[3].text)
locations_df = pd.DataFrame({
    "Enlem": latitudes,
    "Boylam": longitudes
})
df = pd.concat([df, locations_df], axis=1)

# Convert the 'Enlem' and 'Boylam' columns to floats
df['Enlem'] = df['Enlem'].str.replace(',', '.').astype(float)
df['Boylam'] = df['Boylam'].str.replace(',', '.').astype(float)

# Create a map object centered on Turkey
m = folium.Map(location=[39.9334, 32.8597], zoom_start=6)

# Add markers to the map for each city
for index, row in df.iterrows():
    # Construct the popup text
    popup_text = f"{row['İl']} ({row['Nüfus']})"

    # Create a marker for this city with a red color
    marker = folium.Marker(location=[row['Enlem'], row['Boylam']], popup=popup_text, icon=folium.Icon(color='red'))

    # Add the marker to the map
    marker.add_to(m)

# Display the map using Streamlit
folium_static(m)
