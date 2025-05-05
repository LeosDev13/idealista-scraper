import os
import sys

import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.Database import Database
from core.Logger import Logger

st.set_page_config(page_title="Idealista Scraper", page_icon="🏠", layout="wide")

st.title("🏠 Idealista Scraper")

logger = Logger("streamlit_app")
db = Database(logger)


@st.cache_data(ttl=600)
def load_locations():
    locations = db.get_locations()
    return locations


locations = load_locations()

if not locations:
    st.error("❌ No se encontraron ubicaciones en la base de datos.")
else:
    location_options = {
        f"{loc['title']} ({loc['number_of_properties']} propiedades)": loc["path"]
        for loc in locations
    }

    st.subheader("Selecciona una ubicación:")
    selected_location = st.selectbox(
        "Ubicación",
        options=list(location_options.keys()),
        index=0,
        help="Selecciona la ubicación para ver sus propiedades",
    )

    location_id = location_options[selected_location]

    selected_loc = next((loc for loc in locations if loc["path"] == location_id), None)

    if selected_loc:
        st.write(f"**Ubicación seleccionada:** {selected_loc['title']}")
        st.write(f"**Número de propiedades:** {selected_loc['number_of_properties']}")
        st.write(f"**URL:** {selected_loc['path'].replace('mapa', '')}")

        if st.button("Ver propiedades"):
            st.info("Funcionalidad para mostrar propiedades en desarrollo...")
