import streamlit as st
import joblib 
import numpy as np

st.title("Calories burnt prediction")

st.divider()

st.write("with this app you can get the calories burnt during exercise")

gender=st.selectbox("enter your gender",{"Male","Female"})
age=st.number_input(value=None,step=0.1,label="enter your age")
height=st.number_input(value=None,step=0.1,label="enter your height")
weight=st.number_input(value=None,step=0.1,label="enter your weight")
duration=st.number_input(value=None,step=0.1,label="enter the duration")
heart_rate=st.number_input(value=None,step=0.1,label="enter heart rate")
body_temp=st.number_input(value=None,step=0.1,label="enter body temperature")



model=joblib.load("linearmodel.pkl")

st.divider()

predict=st.button("generate")




if predict:
    st.balloons()
    gender_selected=1 if gender=="Female" else 0
    # i normalize the inputs because the model trained on normalized data

    age_normalized=age/79
    height_normalized=height/222
    weight_normalized=weight/132
    duration_normalized=duration/30
    heart_rate_normalized=heart_rate/128
    body_temp_normalized=body_temp/41.5
    x=[gender_selected,age_normalized,height_normalized,weight_normalized,duration_normalized,heart_rate_normalized,body_temp_normalized]

    x1=np.array([x])
    prediction=model.predict(x1)
    st.write(f'predicted calories are: {prediction*314}')

else:
   "please press the button for app to make calories prediction"
