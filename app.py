
import streamlit as st
from PIL import Image
from functions import *

st.set_page_config(layout="wide")

apply_custom_cursor("cursor.cur")

#Show Header Bar
show_toolbar()

#Get the page query parameter
page = st.query_params.get("page", "home")

# Display the appropriate page based on the query parameter
display_selected_page(page)