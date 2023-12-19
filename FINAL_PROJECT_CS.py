"""
Name:       Joshua Emmanuel
CS230:      Section 5
Data:       Boston Building Violations
URL:        Link to your web application on Streamlit Cloud (if posted)

Description:
The program is intended for people who are already familiar in the Building business.
They are assumed to already know the building violation codes.
Users are able to pinpoint buildings with specific violation codes and types of violations.
The website has a feature that allows the user to create a radius around the point of interest, allowing the user to see
their closest building that are not up to code.

"""

import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px
from PIL import Image


# Add your image paths
image_paths = ['houseviolation1.jpg', 'houseviolation2.jpg', 'houseviolation3.jpg']

# Set a common width for all images
common_width = 300

# Display resized images horizontally



df = pd.read_csv('BViolation.csv')

st.title('Boston Building Violations')
for image_path in image_paths:
    st.image(Image.open(image_path), width=common_width, caption=f'{image_path[:-4]}')
st.sidebar.header('Search Parameters')
selected_city = st.sidebar.selectbox('Select City:', df['violation_city'].unique())
zip_codes = sorted(df['violation_zip'].unique().astype(int))
selected_zip = st.sidebar.selectbox('Select Zip Code:', zip_codes)
radius = st.sidebar.slider('Select Radius (miles):', min_value=0.1, max_value=10.0, step=0.1)
selected_violation_type = st.sidebar.selectbox('Select Violation Type:', ['All'] + list(df['description'].unique()))

if selected_zip:
    try:
        selected_zip = int(selected_zip)
        filtered_df = df[(df['violation_city'] == selected_city) & (df['violation_zip'] == selected_zip)]
        filtered_df = filtered_df[filtered_df['latitude'].notnull() & filtered_df['longitude'].notnull()]

        if selected_violation_type != 'All':
            filtered_df = filtered_df[filtered_df['description'] == selected_violation_type]

        if not filtered_df.empty:
            map_center = [filtered_df['latitude'].mean(), filtered_df['longitude'].mean()]

            layer = pdk.Layer(
                "ScatterplotLayer",
                data=filtered_df,
                get_position=['longitude', 'latitude'],
                get_radius=50,
                get_color=[255, 0, 0],
                pickable=True,
            )

            view_state = pdk.ViewState(
                latitude=map_center[0],
                longitude=map_center[1],
                zoom=12,
                pitch=0,
            )

            my_map = pdk.Deck(
                layers=[layer],
                initial_view_state=view_state,
            )

            st.pydeck_chart(my_map)

        else:
            st.warning('No violations found for the specified city, zip code, and violation type.')

        st.header('Building Violations Details')
        st.write(filtered_df[['code', 'description', 'violation_zip']])

    except ValueError:
        st.warning('Invalid Zip Code. Please enter a valid numerical Zip Code.')
else:
    st.warning('Please enter a Zip Code.')

violations_per_city = df.groupby('violation_city').size().reset_index(name='Number of Violations')
fig_pie = px.pie(violations_per_city, names='violation_city', values='Number of Violations', title='Violations per City')
st.plotly_chart(fig_pie)

st.sidebar.header('Search by Violation Code')
searched_violation_code = st.sidebar.text_input('Enter Violation Code:')
if searched_violation_code:
    filtered_by_code_df = df[df['code'] == searched_violation_code]

    if not filtered_by_code_df.empty:
        map_center = [filtered_by_code_df['latitude'].mean(), filtered_by_code_df['longitude'].mean()]

        layer_code = pdk.Layer(
            "ScatterplotLayer",
            data=filtered_by_code_df,
            get_position=['longitude', 'latitude'],
            get_radius=50,
            get_color=[0, 0, 255],
            pickable=True,
        )

        view_state_code = pdk.ViewState(
            latitude=map_center[0],
            longitude=map_center[1],
            zoom=12,
            pitch=0,
        )

        my_map_code = pdk.Deck(
            layers=[layer_code],
            initial_view_state=view_state_code,
        )

        st.header(f'Building Violations for Code {searched_violation_code}')
        st.pydeck_chart(my_map_code)

    else:
        st.warning(f'No violations found for the specified violation code {searched_violation_code}.')
