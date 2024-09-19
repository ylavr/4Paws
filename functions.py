import json
import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report
import matplotlib.pyplot as  plt
import seaborn as sns



def get_base64_image(image_path):
    import base64
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()
    
def read_pets_file():
    with open('cats_and_dogs.json', 'r') as f:
        data = json.load(f)
    return data

def read_dictionary_file():
    with open('dictionary.json', 'r') as f:
        data = json.load(f)
    return data

def find_pets(pets, **criterias):
    def matches(pet, key, value):
        if value.lower() == 'any':
            return True
        
        if key in pet:
            if isinstance(pet[key], list):
                return value.lower() in (item.lower() for item in pet[key])
            return str(pet[key]).lower() == str(value).lower()
        return False
        
    match_pets = []

    for pet in pets:
        if all(matches(pet, key, value) for key, value in criterias.items()):
            match_pets.append(pet)
    return match_pets

def show_pet(pet):
    pet_name = pet["pet_name"]
    pet_breed = pet["primary_breed"]

    # Safely access dictionary keys using get method
    attributes = [
        ("age", pet.get("age")),
        ("gender", pet.get("gender")),
        ("size", pet.get("size")),
        ("primary_color", pet.get("primary_color"))
    ]

    # Create a list of non-missing attribute values
    descr_parts = [f"{value}" for key, value in attributes if value is not None]

    # Join the parts with a separator
    descr = "  •  ".join(descr_parts)

    st.markdown(
        f"""
        <style>
        .centered-text {{
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100%;
            font-size: 36px; /* Adjust the font size as needed */
            font-weight: bold;
        }}
        .text{{
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100%;
            font-size: 20px; /* Adjust the font size as needed */
        }}
        .text2{{
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100%;
            font-size: 15px; /* Adjust the font size as needed */
        }}        
        </style>
        <div class="centered-text">
            {pet_name}
        </div>    
        <div class="text"> {pet_breed} </div>
        <div class="text2"> {descr} </div>    
        """,
        unsafe_allow_html=True
    )

    # Display the image
    
    if pet["image_url"]:
        image_path = pet['image_url']
    else:
        if pet["pet_type"].lower() == "cat":
            image_path = f"data:image/png;base64,{get_base64_image('resources/cat_856461.png')}"
        else:
            image_path = f"data:image/png;base64,{get_base64_image('resources/dog_4540592.png')}"

    st.markdown(
        f"""
            <style>
                .image-wrapper {{
                    width: 700px;
                    height: 700px;
                    overflow: hidden;
                    position: relative;
                    margin: 50px auto; /* Center horizontally with auto margins */
                    border-radius:100%; /* Make the container a circle */
                }}
                .image-wrapper img {{
                    width: 100%;
                    height: 100%;
                    object-fit: cover;
                    border-radius: 100%; /* Ensure the image itself is clipped to a circle */
                }}
            </style>
            <div class="image-wrapper">
                <img src="{image_path}" alt="{pet['pet_name']}">
            </div>
        """,
        unsafe_allow_html=True
    ) 

    # st.write(pet["characteristics"])
    st.markdown("**Characteristics:**")
    characteristics_line = " • ".join(pet["characteristics"])
    st.markdown(f"{characteristics_line}")

    approval_sign = "✅"
    decline_sign = "❌"

    
    good_with_info = pet.get("good_with", {})
    if good_with_info:
        st.markdown("**Good with:**")
        good_with_line = " | ".join(
            [f"{key.replace('_', ' ').capitalize()}: {approval_sign if value else decline_sign}" for key, value in good_with_info.items()]
        )
        st.markdown(good_with_line)


    st.markdown("**Description:**")
    st.write(pet["description"])  

    st.write("")

    show_model_buttons(pet)


def show_main_page():
    # #Header and Title
    # st.title("FourPaws - Each life matter!")
    # st.subheader("One step can save lifes")

    # Initialize session state variables if they don't exist
    if 'index' not in st.session_state:
        st.session_state.index = 0

    #Read Dictionary with different categories
    dictionary = read_dictionary_file()
    st.session_state.dictionary = dictionary

    #Filters
    st.sidebar.header("Filters")
    pet_type = st.sidebar.selectbox("Pet", dictionary["pet_type"])

    if pet_type == 'Cat':
        breedType = 'catBreeds'
    else:
        breedType = 'dogBreeds'
    
    st.markdown(
        """
        <style>
            [data-testid="stSidebar"]{
                min-width: 250px;
                max-width: 250px;
            }
        </style>
        """,
        unsafe_allow_html=True
    )
    breed = st.sidebar.selectbox("Breed", dictionary[breedType])
    age = st.sidebar.selectbox("Age", dictionary["age"])
    gender = st.sidebar.selectbox("Gender", dictionary["gender"])
    size = st.sidebar.selectbox("Size", dictionary["size"])
    coat_length = st.sidebar.selectbox("Coat length", dictionary["coat_length"])
    special_needs = st.sidebar.selectbox("Special needs", dictionary["special_needs"])
   
    # pets = read_pets_file()

    # total_amount_of_pets = len(pets)
    # total_amount_of_cats = total_amount_of_dogs = 0
    # for pet in pets:
    #     if pet["pet_type"].lower() == "cat":
    #         total_amount_of_cats += 1
    #     else:
    #         total_amount_of_dogs += 1

    # st.sidebar.markdown(f"**Total amount of pets:** {total_amount_of_pets}")
    # st.sidebar.markdown(f"**Total amount of cats:** {total_amount_of_cats}")
    # st.sidebar.markdown(f"**Total amount of dogs:** {total_amount_of_dogs}")

    #Search button in the sidebar
    if st.sidebar.button("Search"):
        match_pets = []
        pets = read_pets_file()
        match_pets = find_pets(pets, pet_type=pet_type, primary_breed=breed, age=age, gender=gender, size=size, coat_length=coat_length,medical_care =special_needs )
        st.sidebar.markdown(f"**Pets found by your request:** {len(match_pets)}")
        st.session_state.match_pets = match_pets
        st.session_state.index = 0  # Reset index when a new search is performed

    if 'match_pets' in st.session_state and st.session_state.match_pets:
        # Display Animal Profiles
        # st.write("### Found Pets")
        #Show animal from search results
        show_navigation_buttons( )
        if 0 <= st.session_state.index < len(st.session_state.match_pets):
            show_pet(st.session_state.match_pets[st.session_state.index])
            show_social_media( st.session_state.match_pets[st.session_state.index] )
        else:
            st.write("No pets found")
         
        
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        

def show_about_page():
    # st.title("4 Paws")
    st.write("""
    ###         
    ### About This Project
    Welcome to the Pet Shelter Adoption Prediction and Recommendation Tool! This project aims to assist pet shelters in predicting the probability of pet adoption and providing recommendations.
    Our tool utilizes machine learning algorithms to analyze various factors influencing adoption rates and suggests potential matches between pets and adopters.

    ### Key Features
    - **Adoption Prediction**: Predict the percentage likelihood of a pet being adopted based on historical data and various attributes such as age, breed, health status, and more.
    - **Recommendation Engine**: Provide personalized pet recommendations to potential adopters based on their preferences and lifestyle, enhancing the chances of a successful match.
    - **Data Visualization**: Visualize adoption trends, success rates, and other insightful metrics to help shelters make informed decisions.

    ### Project Goals
    The main goals of this project are:
    1. Increase the adoption rates of pets in shelters by identifying key factors that influence adoption.
    2. Assist potential shelter workers in finding the right pet and adopter that match their preferences and lifestyle.
    3. Provide shelters with actionable insights through data analysis and visualization.
             

    """)
    return


def show_dashboard_page():
    st.title("Analytics and reporting page")
    st.write("This page is in progress and will be deployed very soon...")
    
    # Centering the image
    st.markdown(
         f"""
        <style>
        .center {{
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100%;
        }}
        .center img {{
            max-width: 100%;
            height: auto;
            width: 100%; /* Adjust this percentage to control image size */
        }}
        figcaption {{
           text-align: center;
        }}
        </style>
        <div class="center">
        <figure>
        <img src="data:image/png;base64,{get_base64_image('Screenshot 2024-07-26 174039.png')}" alt="Future Dashboard Placeholder">
        <figcaption>Future Dashboard Placeholder</figcaption>
        </figure>
        </div>
        """,
        unsafe_allow_html=True
    )

    
    st.markdown("</div>", unsafe_allow_html=True)
    return

def show_contacts_page():
    return

    
def show_toolbar():
    # Header bar with HTML and CSS
    # st.subheader("One step can save lifes")        
    
    st.markdown(
        f"""
        <style>
        .header {{
            display: flex;
            align-items: center;
            padding: 10px;
            background-color: #f0f2f6;
            color: #333;
            border-bottom: 1px solid #e6e9ef;
            width: 100%;
            box-sizing: border-box;
        }}
        .header .title {{
            display: flex;
            align-items: center;
            flex: 1;
            font-size: 24px;
            font-weight: bold;
            margin-right: auto; /* Pushes the title and icons to the left */
        }}
        .header .title img {{
            width: 24px; /* Adjust the size of the icons */
            height: 24px;
            margin-left: 10px; /* Space between icons and text */
        }}
        .header .nav-links {{
            display: flex;
            align-items: center;
        }}
        .header .nav-links a {{
            margin: 0 15px;
            color: #333;
            text-decoration: none;
            font-weight: normal;
        }}
        .header .nav-links a:hover {{
            color: #007bff;
        }}
        </style>
        <div class="header">
            <div class="title">
                <!-- Title Text -->
                FourPaws - Where Every Paw Finds a Home
                <!-- Icons -->
                <img src="data:image/png;base64,{get_base64_image('resources/icons/footprints.png')}" alt="Paw Icon">
                <img src="data:image/png;base64,{get_base64_image('resources/icons/footprints.png')}" alt="Paw Icon">                
            </div>
            <div class="nav-links">
                <a href="/?page=about">About</a>
                <a href="/?page=home">Home</a>
                <a href="/?page=analytics and reporting">Analytics and reporting</a>
                 <!-- <a href="/?page=contact">Contact</a> -->
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def display_selected_page(page):
    if page == "home":
        show_main_page()
    elif page == "about":
        show_about_page()
    elif page == "analytics and reporting":
        show_dashboard_page()
    # elif page == "contact":
    #     show_contacts_page()
    else:
        st.title("Page not found")
        st.write("The page you're looking for does not exist.")


def show_social_media(pet):
    # New buttons for external links
    twitter_link = pet['twitter_url']
    pinterest_link = pet['pinterest_url']
    facebook_link = pet['facebook_url']
    

    # Read the SVG content
    def load_svg(file_path):
        with open(file_path, "r") as file:
            return file.read()
        
    st.write("")
    st.write("Share this profile at social media:")   

    st.markdown(
        f"""
        <style>
        .icon-button-container {{
            display: flex;
            justify-content: flex-start; /* Align items to the left */
            gap: 20px; /* Adjust the gap between icons */
            margin-top: 1px;
        }}
        .icon-button-container a {{
            text-decoration: none;
            display: inline-block;
            padding: 0;
            margin-left: 20px
            cursor: pointer;
        }}        
        .icon-button-container a svg {{
            width: 40px; /* Adjust the size of the icons */
            height: 40px;
            vertical-align: middle;
        }}
        .icon-button-container a:hover svg {{
            fill: #45a049; /* Change color on hover */
        }}
        </style>
        <div class="icon-button-container">
            <a href="{twitter_link}" target="_blank">{load_svg("resources/icons/twitter.svg")}</a>
            <a href="{pinterest_link}" target="_blank">{load_svg("resources/icons/pinterest.svg")}</a>
            <a href="{facebook_link}" target="_blank">{load_svg("resources/icons/facebook.svg")}</a>
        </div>
        """,
        unsafe_allow_html=True
    )       

def show_navigation_buttons( ):
    col1, col2, col3, col4, col5, col6 = st.columns([4, 1, 1, 1, 1, 1])

    # with col1:
       
    with col5:
         #"Previous" button functionality
        if st.button("Previous Pet", key="left"):
            if st.session_state.index - 1 >= 0:
                st.session_state.index -= 1
        
    with col6: 
        #"Next" button functionality
        if st.button('Next Pet', key="right"):
            if st.session_state.index + 1 < len(st.session_state.match_pets):
                st.session_state.index += 1
            else:
                st.write("No more pets.")        

def show_model_buttons(pet):
    col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1, 2, 1, 1])

    # with col1:
    recomendations = {}

    with col3:
         #Adoption model
        if st.button("Predict addoption"):
            probability_of_adoption = prediction_model_result(pet)
            st.write(f"Probability of adoption: {probability_of_adoption:.1%}")
    
        
    with col4: 
        #"Owner prediction model
        if st.button("Recommended owners"):
            recomendations = recommendation_engine(pet)

            if recomendations:
                for key, value in recomendations.items():
                    st.write(f"**{key.replace('_', ' ').capitalize()}**: {value}")


def apply_custom_cursor(cursor_path):
    # import base64
    # with open(cursor_path, "rb") as image_file:
    #     cursor_base64 = base64.b64encode(image_file.read()).decode("utf-8")
    
    custom_css = """
    <style type="text/css">body { cursor: url('data:image/x-icon;base64,AAACAAEAICAAAAAAAACoEAAAFgAAACgAAAAgAAAAQAAAAAEAIAAAAAAAABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABkZGQEAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/LCwsDQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAcHBwIAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABwcHAgAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8LCwsNAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHBwcCAAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/xwcHAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wUFBQMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP8AAAD/AAAA/wAAAP8AAAD/oo/9/6KP/f+ij/3/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD/AAAA/wAAAP8AAAD/AAAA/6KP/f+ij/3/oo/9/6KP/f+ij/3/opD9/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA/wAAAP8AAAD/o5H9/6OR/f8AAAD/oo/9/6KP/f+ij/3/oo/9/6KP/f+ikP3/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD/AAAA/6KP/f+ij/3/oo/9/wAAAP+ij/3/oo/9/6KP/f+ij/3/oo/9/6KQ/f8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP8AAAD/AAAA/6KP/f8AAAD/AAAA/6KP/f+ij/3/oo/9/6KP/f+ij/3/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/6KP/f+ij/3/oo/9/wAAAP+ij/3/o5H9/wAAAP8AAAD/AAAA/wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA/wAAAP8AAAD/oo/9/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/6KP/f+ij/3/oo/9/wAAAP8AAAD/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD/AAAA/6KP/f+ij/3/oo/9/wAAAP8AAAD/oo/9/wAAAP8AAAD/oo/9/6OR/f8AAAD/AAAA/wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP8AAAD/AAAA/6KP/f+ij/3/AAAA/6KP/f+ij/3/oo/9/wAAAP8AAAD/o5H9/wAAAP8AAAD/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP8AAAD/oo/9/wAAAP8AAAD/oo/9/6KP/f+ij/3/AAAA/wAAAP8AAAD/AAAA/wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/oo/9/wAAAP8AAAD/AAAA/wAAAP8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA/////////////4B///4AH//8AB///AAf//gAH//4AD//+AA///AAP//wAH//8AB//+AAf//gAP//wAD//4AB//8AAf/+AAH//AAD//gAA//4AAP/+AAH//gAB//8AAf//AAP//wAD//+AB///gA///8Af///gf////////////8='), auto; }</style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

##Recomendation engine:

def load_data():
    data = pd.read_excel('survey_results_modified.xlsx')
    # Making all data between 0-1
    data['age'] = (data['age'] - 19) / (52 - 19)
    data['gender'] = data['gender'].replace({'Male': 0, 'Female': 1})
    data['living'] = data['living'].replace({'Apartment': 0, 'Other:Flat': 0, 'House': 1, 'Other:Apartment with garden ': 1})
    data['activity'] = (data['activity'].fillna(1) - 1) / 8
    data['experience'] = data['experience'].replace({'Experienced': 0, 'First-time owner': 1})
    data['dog'] = data['type'].replace({'Dog': 1, 'Cat': 0, 'Other:Keine': 1, 'Other': 0, 'Other:crocodile': 0})
    data['cat'] = data['type'].replace({'Dog': 0, 'Cat': 1, 'Other:Keine': 0, 'Other': 0, 'Other:crocodile': 0})
    data['pet_male'] = data['gender_pet'].fillna('Any').replace({'Male': 1, 'Female': 0, 'Any': 0})
    data['pet_female'] = data['gender_pet'].fillna('Any').replace({'Male': 0, 'Female': 1, 'Any': 0})
    data['age_pet'] = data['age_pet'].replace({'Young': 0, 'Adult': 1})
    data['vaccine_pet'] = data['vaccine_pet'].replace({'No, vaccination is not so important for me': 0, "Yes, i'm ready to take only vaccinated pet": 1})
    data['allergies_pet'] = data['allergies_pet'].replace({'No': 0, 'Yes': 1})
    data['shelter_time'] = data['shelter_time'].replace({1: 0, 2: 0.5, 3: 1})
    data['special_needs?'] = data['special_needs?'].replace({'No': 0, 'Yes': 1})
    data = data.drop(columns=['type', 'gender_pet', 'size_pet'])
    return data

def transform_data_pets(row):
    # json_file_path = 'D:\IronHack\Study\Bootcamp\Project6_Pet_tinder\PETS/cats_and_dogs.json'
    # with open(json_file_path, 'r') as file:
    #     data = json.load(file)
    # row = data[600]
    age_group = 0.33 if row['age'] == 'Baby' else 0 if row['age'] == 'Young' else 1 if row['age'] == 'Adult' else 0.66 if row['age'] == 'Senior' else -1
    cat_type = 1 if row['pet_type'] == 'Cat' else 0
    dog_type = 1 if row['pet_type'] == 'Dog' else 0
    allergies = 0
    size = 0 if row['size'] == 'Small' else 1 if row['size'] == 'Medium' else 2
    shelter_period_category = 0 if '>30' in row['days_on_petfinder'] else 0.5
    health_condition = 0 if row['medical_care'] == 'no special needs' else 1
    vaccination = 1 if 'Shots Current' in row.get('characteristics', []) else 0
    pet_gender_male = 1 if row['gender'] == 'Male' else 0
    pet_gender_female = 1 if row['gender'] == 'Female' else 0

    new_pet = {
        'age_pet': age_group,
        'vaccine_pet': vaccination,
        'allergies_pet': allergies,
        'cat': cat_type,
        'dog': dog_type,
        'Size': size,
        'shelter_time': shelter_period_category,
        'special_needs?': health_condition,
        'pet_male': pet_gender_male,
        'pet_female': pet_gender_female
    }
    return new_pet

def compare_new_pet_with_pet_in_database(row, new_pet):
    distance = np.sqrt(
        (new_pet['age_pet'] - row['age_pet'])**2 +
        (new_pet['vaccine_pet'] - row['vaccine_pet'])**2 +
        (new_pet['allergies_pet'] - row['allergies_pet'])**2 +
        (new_pet['shelter_time'] - row['shelter_time'])**2 +
        (new_pet['special_needs?'] - row['special_needs?'])**2 +
        (new_pet['dog'] - row['dog'])**2 +
        (new_pet['cat'] - row['cat'])**2 +
        (new_pet['pet_male'] - row['pet_male'])**2 +
        (new_pet['pet_female'] - row['pet_female'])**2
    )
    similarity = 1 / (distance + 1)
    return similarity**2

def compare_new_pet_with_all_database(pet_properties_database, new_pet):
    return pet_properties_database.apply(lambda x: compare_new_pet_with_pet_in_database(x, new_pet), axis=1)

def recommendation_engine(pet):
    data = load_data()
    pet_properties_database = data[['age_pet', 'vaccine_pet', 'allergies_pet', 'shelter_time', 'special_needs?', 'dog', 'cat', 'pet_male', 'pet_female']]
    
    new_pet = transform_data_pets(pet)
    similarities = compare_new_pet_with_all_database(pet_properties_database, new_pet)
    
    def predict_feature_weighted_average(feature):
        weighted_sum = (data[feature] * similarities).sum()
        average_weighted = weighted_sum / similarities.sum()
        return average_weighted

    # Predicting age
    average_weighted_age = predict_feature_weighted_average('age')
    recommended_owner_age = (average_weighted_age * (52 - 19)) + 19

    # Predicting gender
    average_weighted_gender = predict_feature_weighted_average('gender')
    recommended_gender = 'Female' if average_weighted_gender >= 0.5 else 'Male'

    # Predicting living situation
    average_weighted_living = predict_feature_weighted_average('living')
    recommended_living = 'House or Apartment with garden' if average_weighted_living >= 0.5 else 'Apartment'

    # Predicting activity level
    average_weighted_activity = predict_feature_weighted_average('activity')
    recommended_activity = (average_weighted_activity * 8) + 1

    # Predicting experience
    average_weighted_experience = predict_feature_weighted_average('experience')
    recommended_experience = 'First-time owner' if average_weighted_experience >= 0.5 else 'Experienced'

    # Predicting concerns about time in shelter
    average_weighted_concern = predict_feature_weighted_average('shelter_time')
    if average_weighted_concern < 0.5:
        recommended_concerns = 'Not concerned'
    elif 0.5 <= average_weighted_concern < 0.75:
        recommended_concerns = 'Slightly concerned'
    else:
        recommended_concerns = 'Extremely concerned'

    # Predicting readiness to take a pet with special needs
    average_weighted_readiness = predict_feature_weighted_average('special_needs?')
    recommended_readiness = 'Yes' if average_weighted_readiness >= 0.5 else 'No'
    return { "recommended_owner_age": recommended_owner_age,
            "recommended_gender": recommended_gender,
            "recommended_activity": recommended_activity,
            "recommended_living conditions": recommended_living,
            "recommended_experience with pets": recommended_experience,
            "recommended_concerns about time in shelter": recommended_concerns
            # "recommended_readiness": recommended_readiness
    }
 


## Predict adoption:

def transform_data(row):
         # Predict probabilities for new data
    # json_file_path = r'D:\IronHack\Study\Bootcamp\Project6_Pet_tinder\PETS/cats_and_dogs.json'

    # with open(json_file_path, 'r') as file:
    #     data = json.load(file)

    # row = data[2]

        # Function to transform the JSON data into the required format
    age_group = 0 if row['age'] == 'Baby' else 1 if row['age'] == 'Young' else 2 if row['age'] == 'Adult' else 3 if row['age'] == 'Senior' else -1
    pet_type = 3 if row['pet_type'] == 'Cat' else 2
    size = 0 if row['size'] == 'Small' else 1 if row['size'] == 'Medium' else 2
    shelter_period_category = 0 if '>30' in row['days_on_petfinder'] else 1
    health_condition = 0 if row['medical_care'] == 'no special needs' else 1
    adoption_fee = row['adoption_fee'] if row['adoption_fee'] is not None else 0
    previous_owner = 1 if 'House trained' in row.get('characteristics', []) else 0  

    a =  pd.DataFrame({
            'age_group': [age_group],
            'PetType': [pet_type],
            'Size': [size],
            'shelter_period_category': [shelter_period_category],
            'HealthCondition': [health_condition],
            'AdoptionFee': [adoption_fee],
            'PreviousOwner': [previous_owner]
                    })
    return a


def prediction_model_result(pet_row):
    train_csv = pd.read_csv("pet_adoption_data.csv")
    train_csv.drop("PetID",axis=1, inplace = True)
    train_csv["PetType"]=train_csv["PetType"].map({"Bird":0,"Rabbit":1,"Dog":2,"Cat":3})
    train_csv["Size"]=train_csv["Size"].map({"Small":0,"Large":2,"Medium":1})
    train_csv['shelter_period_category'] = train_csv['TimeInShelterDays'].apply(lambda x: 0 if x > 30 else 1)
    bins = [0, 6, 18, 60, float('inf')]
    labels = [0, 1, 2, 3]  
    train_csv['age_group'] = pd.cut(train_csv['AgeMonths'], bins=bins, labels=labels, right=True)
    train_csv.drop(["Breed","Color","AgeMonths","WeightKg","TimeInShelterDays"],axis=1, inplace = True)
    target = train_csv['AdoptionLikelihood']
    train_csv=train_csv.drop('AdoptionLikelihood', axis=1)
 
    features = train_csv[['age_group', 'PetType', 'Size', 'shelter_period_category', 'HealthCondition', 'AdoptionFee', 'PreviousOwner' ]]

    scaler = StandardScaler()

    # X = scaler.fit_transform(features)
    X  = features
    y = target



    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestClassifier()
    model.fit(X_train, y_train)

    probabilities = model.predict_proba(transform_data(pet_row))

    return probabilities[0][1]





