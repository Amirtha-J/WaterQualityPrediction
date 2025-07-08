# import libraries
import pandas as pd
import numpy as np
import joblib
import pickle
import streamlit as st

# Load the model and structure
model = joblib.load("pollution_model.pkl")
model_cols = joblib.load("model_columns.pkl")

# User Interface
st.title("Water Quality Predictor")
st.write("Predict pollutant levels for a given station and year")

# User inputs
year_input = st.number_input("Enter year",min_value = 2000, max_value = 2100, value = 2022)
station_id = st.text_input("Enter Station id",value = '1')

# To encode and predict
if st.button('Predict'):
    if not station_id:
        st.warning("Please enter the Station ID")
    else:
        # Prepare input
        input_df = pd.DataFrame({'year': [year_input], 'id':[station_id]})
        input_encoded = pd.get_dummies(input_df, columns=['id'])

        # Align with model cols
        for col in model_cols:
            if col not in input_encoded.columns:
                input_encoded[col] = 0
        input_encoded = input_encoded[model_cols]

        # Predict
        predicted_pollutants = model.predict(input_encoded)[0]
        pollutants = ['O2', 'NO3', 'NO2', 'SO4', 'PO4','CL']

        safe_limits = {
            'O2': (5.0, 15.0),
            'NO3': (0, 50),
            'NO2': (0,0.1),
            'SO4': (0,250),
            'PO4': (0,0.1),
            'CL': (0,250)
        }

        # Fn to check if water is potable or not
        def is_potable(pollutants_dict):
            for p in pollutants_dict:
                value = pollutants_dict[p]
                safe_min = safe_limits[p][0]
                safe_max = safe_limits[p][1]

                if value < safe_min or value > safe_max:
                    return False
            return True

        # Calculate potability score
        def potable_score(pollutants_dict):
            safe_count = 0
            total = len(pollutants_dict)

            for p in pollutants_dict:
                value = pollutants_dict[p]
                safe_min = safe_limits[p][0]
                safe_max = safe_limits[p][1]

                if safe_min <= value <=safe_max:
                    safe_count +=1
            if total ==0:
                return 0.0
            score = (safe_count / total) * 100
            return score
        
        st.subheader(f"Predicted pollutant levels for the station '{station_id}' in {year_input}:")
        predicted_values = dict(zip(pollutants,predicted_pollutants))

        for p in pollutants:
            st.write(f'{p}: {predicted_values[p]:.2f}')

        # Show potability score
        score = potable_score(predicted_values)
        st.subheader("How safe is the water?")
        st.write("Potability score shows how many pollutants are within safe levels for drinking.")
        st.write(f"\nPotability Score: {score:.2f}%")
        st.progress(int(score))

        # Potability status
        if is_potable(predicted_values):
            st.success("Water is Potable (Safe to drink).")
        elif score >= 60:
            st.info("Water is partially potable. Some pollutants exceed limits.")
        else:
            st.error("Water is Not Potable (Unsafe to drink).")
