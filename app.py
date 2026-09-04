import streamlit as st
import pandas as pd
import sqlite3
import pydeck as pdk

st.set_page_config(page_title="Soviet Enterprises Registry", layout="wide")

# Підключення до бази даних
conn = sqlite3.connect("enterprises.db")
df = pd.read_sql_query("SELECT * FROM enterprises", conn)
conn.close()

# Бокове меню навігації
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select View:", ["📋 Data Table", "🗺️ Enterprise Map"])

# ----------------- СТОРІНКА 1: ТАБЛИЦЯ -----------------
if page == "📋 Data Table":
    st.title("🏛️ Soviet Industrial Enterprises (1920–1991)")
    
    search = st.text_input("🔍 Search by name, city, or region:")
    
    filtered_df = df.copy()
    if search:
        filtered_df = filtered_df[
            filtered_df['firm_name'].astype(str).str.contains(search, case=False, na=False) |
            filtered_df['firm_city'].astype(str).str.contains(search, case=False, na=False) |
            filtered_df['firm_region'].astype(str).str.contains(search, case=False, na=False)
        ]
    
    st.dataframe(filtered_df, use_container_width=True)

# ----------------- СТОРІНКА 2: МАПА -----------------
elif page == "🗺️ Enterprise Map":
    st.title("🗺️ Industrial Map of Ukraine")
    
    # Розбиваємо 'firm_coordinates' ("lat, lon") на два числові стовпчики
    if not df.empty and 'firm_coordinates' in df.columns:
        coords = df['firm_coordinates'].astype(str).str.split(',', expand=True)
        if coords.shape[1] == 2:
            df['lat'] = pd.to_numeric(coords[0], errors='coerce')
            df['lon'] = pd.to_numeric(coords[1], errors='coerce')
            map_df = df.dropna(subset=['lat', 'lon'])
        else:
            map_df = pd.DataFrame()
    else:
        map_df = pd.DataFrame()

    if map_df.empty:
        st.warning("No valid coordinates found in database. Ensure 'firm_coordinates' are formatted as 'lat, lon'.")
    else:
        # Налаштування шару точок
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=map_df,
            get_position=["lon", "lat"],
            get_color="[220, 53, 69, 180]",  # Червоний колір точок
            get_radius=12000,                # Розмір точки в метрах
            pickable=True,
        )

        # Центрування мапи на Україні
        view_state = pdk.ViewState(
            latitude=48.3794,
            longitude=31.1656,
            zoom=5.5,
            pitch=0,
        )

        # Кастомний тултіп при наведенні курсора
        tooltip = {
            "html": """
            <div style="font-family: sans-serif; padding: 5px;">
                <b style="font-size: 14px; color: #ffeb3b;">{firm_name}</b><br/>
                <b>Location:</b> {firm_city}, {firm_region}<br/>
                <b>Employees:</b> {employees_amount}<br/>
                <b>Revenue:</b> {yearly_revenue}<br/>
                <b>Data Year:</b> {data_collected_year}
            </div>
            """,
            "style": {"backgroundColor": "#1e1e1e", "color": "white", "borderRadius": "5px"}
        }

        # Відображення мапи
        st.pydeck_chart(pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip=tooltip
        ))