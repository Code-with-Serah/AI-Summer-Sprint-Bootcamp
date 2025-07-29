import streamlit as st
import pandas as pd
import numpy as np
import pickle
from lightfm import LightFM
from scipy.sparse import coo_matrix

# Page config
st.set_page_config(page_title="🧠 Product Recommender", layout="wide")
st.title("🛒 Product Recommendation System (LightFM Model)")

# Upload files
uploaded_purchase = st.file_uploader("📂 Upload Purchase History CSV", type=["csv"])
uploaded_model = st.file_uploader("🤖 Upload Trained LightFM Model (.pkl)", type=["pkl"])

# Check both files are uploaded
if uploaded_purchase and uploaded_model:

    # Load purchase history
    df = pd.read_csv(uploaded_purchase)

    st.subheader("📋 Data Preview")
    st.write("**Purchase History**")
    st.dataframe(df.head())

    # Validate required columns
    required_cols = {"user_id", "product_id", "product_name", "purchase_date"}
    if not required_cols.issubset(df.columns):
        st.error(f"❌ Missing columns in data: {required_cols - set(df.columns)}")
        st.stop()

    # Clean & process data
    df["user_id"] = df["user_id"].astype(str)
    df["product_id"] = df["product_id"].astype(str)
    df.dropna(subset=["user_id", "product_id", "product_name"], inplace=True)
    df["purchase_date"] = pd.to_datetime(df["purchase_date"])
    product_names = df[["product_id", "product_name"]].drop_duplicates().set_index("product_id").to_dict()["product_name"]

    # Map users and products to indices
    user_mapping = {uid: idx for idx, uid in enumerate(df["user_id"].unique())}
    item_mapping = {pid: idx for idx, pid in enumerate(df["product_id"].unique())}
    reverse_item_mapping = {idx: pid for pid, idx in item_mapping.items()}

    # Build sparse interaction matrix
    rows = df["user_id"].map(user_mapping)
    cols = df["product_id"].map(item_mapping)
    data = np.ones(len(df))
    interactions = coo_matrix((data, (rows, cols)), shape=(len(user_mapping), len(item_mapping)))

    # Load LightFM model
    try:
        model = pickle.load(uploaded_model)
    except Exception as e:
        st.error(f"Failed to load LightFM model: {e}")
        st.stop()

    # Select user
    selected_user = st.selectbox("🎯 Select a User ID", sorted(user_mapping.keys()))
    user_idx = user_mapping[selected_user]

    # Predict scores for all items for this user
    all_item_indices = np.arange(len(item_mapping))
    scores = model.predict(user_ids=user_idx, item_ids=all_item_indices)

    # Remove already purchased items
    purchased_pids = df[df["user_id"] == selected_user]["product_id"].unique()
    purchased_indices = [item_mapping[pid] for pid in purchased_pids if pid in item_mapping]
    mask = np.ones(len(scores), dtype=bool)
    mask[purchased_indices] = False

    scores = scores[mask]
    candidate_indices = all_item_indices[mask]

    # Get top N
    top_n = st.slider("Top N Recommendations", min_value=1, max_value=10, value=5)
    top_indices = np.argsort(-scores)[:top_n]
    top_item_ids = [reverse_item_mapping[i] for i in candidate_indices[top_indices]]

    # Show recommendations
    st.subheader("💡 Top Product Recommendations")
    if not top_item_ids:
        st.info("No recommendations found for this user.")
    else:
        for pid in top_item_ids:
            pname = product_names.get(pid, "Unknown Product")
            st.markdown(f"- **{pname}**")

    # Popular products
    st.subheader("📊 Most Purchased Products")
    popular = df["product_name"].value_counts().head(10)
    st.bar_chart(popular)

    # Purchase trends
    st.subheader("🗓️ Purchases Over Time")
    trend = df.groupby(df["purchase_date"].dt.to_period("M")).size()
    trend.index = trend.index.astype(str)
    st.line_chart(trend)

else:
    st.info("⬆️ Please upload both the purchase history CSV and the LightFM model.")
