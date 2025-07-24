import streamlit as st
import pandas as pd
st.title("📊 Job Market Dashboard")
@st.cache_data
def load_data():
    try:
        return pd.read_csv("./DataSets/ai_job_dataset.csv")
    except:
        st.write("error loading file")
        return None
df = load_data()
if df is not None:
    st.subheader("Raw Data")
    st.dataframe(df.head(10))
    if st.checkbox("Show column names"):
        st.write(df.columns)
    if "job_title" in df.columns:
        st.subheader("Top 10 Jobs")
        st.bar_chart(df["job_title"].value_counts().head(10))
    if "company_name" in df.columns:
        st.subheader("Top Companies")
        st.bar_chart(df["company_name"].value_counts().head(10))
    if "company_location" in df.columns:
        st.subheader("Top Locations")
        st.bar_chart(df["company_location"].value_counts().head(10))