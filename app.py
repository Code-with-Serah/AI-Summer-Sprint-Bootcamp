import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from collections import Counter
from datetime import datetime
import re
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pycountry

# Page configuration
st.set_page_config(
    page_title="AI Job Market Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        margin: 2rem 0 1rem 0;
        color: #333;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<h1 class="main-header">🤖 AI Job Market Analysis Dashboard</h1>', unsafe_allow_html=True)

# Sidebar for file upload and filters
st.sidebar.header("📁 Data Upload & Filters")

# File upload
uploaded_file = st.sidebar.file_uploader("Upload your CSV file", type=['csv'])

if uploaded_file is not None:
    # Load the dataset
    df = pd.read_csv(uploaded_file)
    
    # Dataset overview
    st.sidebar.success(f"Dataset loaded successfully!")
    st.sidebar.metric("Total Records", df.shape[0])
    st.sidebar.metric("Total Columns", df.shape[1])
    
    # Optional filters
    st.sidebar.header("🔍 Apply Filters")
    
    # Experience level filter
    if 'experience_level' in df.columns:
        exp_levels = df['experience_level'].dropna().unique()
        selected_exp = st.sidebar.multiselect("Experience Level", exp_levels, default=exp_levels)
        df = df[df['experience_level'].isin(selected_exp)]
    
    # Salary filter
    if 'salary_usd' in df.columns:
        min_salary = st.sidebar.number_input("Minimum Salary (USD)", 0, int(df['salary_usd'].max()), 0)
        df = df[df['salary_usd'] >= min_salary]
    
    # Data preprocessing
    @st.cache_data
    def preprocess_data(data):
        # Clean & Tokenize required_skills
        data['required_skills'] = data['required_skills'].fillna('')
        
        def extract_skills(skill_str):
            cleaned = re.sub(r'[^\w,\s]', '', skill_str)
            return [skill.strip().lower() for skill in cleaned.split(',') if skill.strip()]
        
        data['skill_list'] = data['required_skills'].apply(extract_skills)
        
        # Convert dates
        if 'posting_date' in data.columns:
            data['posting_date'] = pd.to_datetime(data['posting_date'])
            data['month'] = data['posting_date'].dt.to_period('M').astype(str)
        
        # Experience level ordering
        experience_order = ['EN', 'MI', 'SE', 'EX']
        experience_labels = ['Entry', 'Mid', 'Senior', 'Executive']
        
        if 'experience_level' in data.columns:
            data['experience_label'] = pd.Categorical(
                data['experience_level'],
                categories=experience_order,
                ordered=True
            ).rename_categories(experience_labels)
        
        # Education level ordering
        education_order = ['None', 'Associate', 'Bachelor', 'Master', 'PhD']
        if 'education_required' in data.columns:
            data['education_required'] = pd.Categorical(
                data['education_required'],
                categories=education_order,
                ordered=True
            )
        
        # Remote work categorization
        if 'remote_ratio' in data.columns:
            def categorize_remote(ratio):
                if ratio == 0:
                    return 'On-site'
                elif ratio == 50:
                    return 'Hybrid'
                elif ratio == 100:
                    return 'Remote'
                else:
                    return 'Other'
            data['remote_type'] = data['remote_ratio'].apply(categorize_remote)
        
        return data
    
    df = preprocess_data(df)
    
    # Create tabs for different analyses
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Skills Analysis", 
        "📈 Trends Over Time", 
        "💼 Job Market Insights",
        "💰 Salary Analysis",
        "🌍 Geographic Analysis",
        "📋 Dataset Overview"
    ])
    
    with tab1:
        st.markdown('<div class="section-header">Skills Analysis</div>', unsafe_allow_html=True)
        
        # Skills frequency analysis
        all_skills = [skill for skills in df['skill_list'] for skill in skills]
        skill_freq = Counter(all_skills)
        top_skills = skill_freq.most_common(20)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🔝 Top 20 Most Common Skills")
            if top_skills:
                skills, counts = zip(*top_skills)
                fig, ax = plt.subplots(figsize=(10, 8))
                sns.barplot(x=list(counts), y=list(skills), palette='plasma', ax=ax)
                ax.set_title("Top 20 Most Common Skills in Job Postings")
                ax.set_xlabel("Frequency")
                ax.set_ylabel("Skill")
                plt.tight_layout()
                st.pyplot(fig)
        
        with col2:
            st.subheader("☁️ Skills Word Cloud")
            if skill_freq:
                wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(skill_freq)
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.axis('off')
                ax.set_title("Word Cloud of Required Skills")
                st.pyplot(fig)
        
        # Skills by experience level
        if 'experience_level' in df.columns:
            st.subheader("🎯 Skills by Experience Level")
            df_exploded = df.explode('skill_list')
            
            exp_levels = df_exploded['experience_level'].dropna().unique()
            top_5_skills = df_exploded['skill_list'].value_counts().head(5).index.tolist()
            
            comparison_data = []
            for level in exp_levels:
                level_df = df_exploded[df_exploded['experience_level'] == level]
                skill_counts = level_df['skill_list'].value_counts()
                total = skill_counts.sum()
                
                for skill in top_5_skills:
                    freq = skill_counts.get(skill, 0)
                    percent = (freq / total * 100) if total else 0
                    comparison_data.append({
                        'Experience Level': level,
                        'Skill': skill,
                        'Frequency (%)': round(percent, 2),
                        'Count': freq
                    })
            
            comparison_df = pd.DataFrame(comparison_data)
            
            if not comparison_df.empty:
                fig = px.bar(
                    comparison_df,
                    x='Skill',
                    y='Frequency (%)',
                    color='Experience Level',
                    barmode='group',
                    title="📊 Top Skills by Experience Level"
                )
                fig.update_layout(template="plotly_white")
                st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.markdown('<div class="section-header">Trends Over Time</div>', unsafe_allow_html=True)
        
        if 'month' in df.columns:
            # Monthly job posting trend
            monthly_postings = df.groupby('month').size().reset_index(name='job_count')
            
            fig1 = px.line(
                monthly_postings,
                x='month',
                y='job_count',
                markers=True,
                title='📅 Monthly Job Posting Trend'
            )
            fig1.update_layout(template="plotly_white")
            st.plotly_chart(fig1, use_container_width=True)
            
            # Skill trends over time
            tracked_skills = ['python', 'sql', 'docker', 'aws', 'mlops', 'nlp', 'azure', 'tableau', 'linux', 'kubernetes']
            df_exploded = df.explode('skill_list')
            filtered_df = df_exploded[df_exploded['skill_list'].isin(tracked_skills)]
            
            if not filtered_df.empty:
                monthly_skill_counts = filtered_df.groupby(['month', 'skill_list']).size().reset_index(name='count')
                
                fig2 = px.line(
                    monthly_skill_counts,
                    x='month',
                    y='count',
                    color='skill_list',
                    markers=True,
                    title='📈 Skill Demand Trends Over Time'
                )
                fig2.update_layout(template="plotly_white")
                st.plotly_chart(fig2, use_container_width=True)
                
                # Heatmap
                heatmap_data = monthly_skill_counts.pivot(index='skill_list', columns='month', values='count').fillna(0)
                heatmap_data = heatmap_data.loc[heatmap_data.sum(axis=1).sort_values(ascending=False).index]
                
                fig3 = go.Figure(data=go.Heatmap(
                    z=heatmap_data.values,
                    x=heatmap_data.columns,
                    y=heatmap_data.index,
                    colorscale='YlGnBu'
                ))
                fig3.update_layout(
                    title='🔥 Skill Frequency Heatmap by Month',
                    template='plotly_white'
                )
                st.plotly_chart(fig3, use_container_width=True)
    
    with tab3:
        st.markdown('<div class="section-header">Job Market Insights</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Top job titles
            st.subheader("🏆 Top Job Titles")
            top_jobs = df['job_title'].value_counts().head(10).reset_index()
            top_jobs.columns = ['job_title', 'count']
            
            fig = px.bar(
                top_jobs,
                x='count',
                y='job_title',
                orientation='h',
                title='Top 10 Job Titles'
            )
            fig.update_layout(template="plotly_white", yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Company size distribution
            if 'company_size' in df.columns:
                st.subheader("🏢 Company Size Distribution")
                company_size_counts = df['company_size'].value_counts().reset_index()
                company_size_counts.columns = ['company_size', 'count']
                
                fig = px.pie(
                    company_size_counts,
                    names='company_size',
                    values='count',
                    title='Company Size Distribution'
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Remote work distribution
        if 'remote_type' in df.columns:
            st.subheader("🌍 Remote Work Distribution")
            remote_counts = df['remote_type'].value_counts().reset_index()
            remote_counts.columns = ['remote_type', 'count']
            
            fig = px.pie(
                remote_counts,
                names='remote_type',
                values='count',
                title='Remote vs Hybrid vs On-site Jobs'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.markdown('<div class="section-header">Salary Analysis</div>', unsafe_allow_html=True)
        
        if 'salary_usd' in df.columns:
            col1, col2 = st.columns(2)
            
            with col1:
                # Salary by experience level
                if 'experience_label' in df.columns:
                    st.subheader("📈 Salary by Experience Level")
                    avg_salary = df.groupby('experience_label')['salary_usd'].mean().reset_index()
                    avg_salary['salary_usd'] = avg_salary['salary_usd'].round(0)
                    
                    fig, ax = plt.subplots(figsize=(8, 5))
                    sns.barplot(data=avg_salary, x='experience_label', y='salary_usd', palette='viridis', ax=ax)
                    
                    for index, row in avg_salary.iterrows():
                        ax.text(index, row.salary_usd + 2000, f"${int(row.salary_usd):,}", ha='center', fontsize=11)
                    
                    ax.set_title('Average Salary by Experience Level')
                    ax.set_xlabel('Experience Level')
                    ax.set_ylabel('Average Salary (USD)')
                    ax.grid(axis='y', linestyle='--', alpha=0.4)
                    plt.tight_layout()
                    st.pyplot(fig)
            
            with col2:
                # Salary by education level
                if 'education_required' in df.columns:
                    st.subheader("🎓 Salary by Education Level")
                    edu_salary = df.groupby('education_required')['salary_usd'].mean().reset_index()
                    edu_salary = edu_salary.dropna(subset=['salary_usd'])
                    edu_salary['salary_usd'] = edu_salary['salary_usd'].round(0)
                    
                    fig, ax = plt.subplots(figsize=(8, 5))
                    sns.barplot(data=edu_salary, x='education_required', y='salary_usd', palette='mako', ax=ax)
                    
                    for index, row in edu_salary.iterrows():
                        ax.text(index, row.salary_usd + 2000, f"${int(row.salary_usd):,}", ha='center', fontsize=11)
                    
                    ax.set_title('Average Salary by Education Level')
                    ax.set_xlabel('Education Level')
                    ax.set_ylabel('Average Salary (USD)')
                    ax.grid(axis='y', linestyle='--', alpha=0.4)
                    plt.tight_layout()
                    st.pyplot(fig)
            
            # Salary by remote work type
            if 'remote_type' in df.columns:
                st.subheader("💻 Salary by Work Type")
                remote_salary = df.groupby('remote_type')['salary_usd'].mean().reset_index()
                remote_salary['salary_usd'] = remote_salary['salary_usd'].round(0)
                
                fig, ax = plt.subplots(figsize=(8, 5))
                sns.barplot(data=remote_salary, x='remote_type', y='salary_usd', palette='crest', ax=ax)
                
                for index, row in remote_salary.iterrows():
                    ax.text(index, row.salary_usd + 2000, f"${int(row.salary_usd):,}", ha='center', fontsize=11)
                
                ax.set_title('Average Salary by Work Type')
                ax.set_xlabel('Work Type')
                ax.set_ylabel('Average Salary (USD)')
                ax.grid(axis='y', linestyle='--', alpha=0.4)
                plt.tight_layout()
                st.pyplot(fig)
            
            # Salary distribution by top skills
            df_exploded = df.explode('skill_list')
            top_skills = df_exploded['skill_list'].value_counts().head(5).index.tolist()
            df_salary = df_exploded[df_exploded['skill_list'].isin(top_skills)]
            
            if not df_salary.empty:
                st.subheader("💰 Salary Distribution by Top Skills")
                fig = px.box(
                    df_salary,
                    x='skill_list',
                    y='salary_usd',
                    title='Salary Distribution by Top Skills'
                )
                fig.update_layout(template="plotly_white")
                st.plotly_chart(fig, use_container_width=True)
    
    with tab5:
        st.markdown('<div class="section-header">Geographic Analysis</div>', unsafe_allow_html=True)
        
        if 'employee_residence' in df.columns:
            # Geographic distribution
            df_exploded = df.explode('skill_list')
            top_skills = df_exploded['skill_list'].value_counts().head(3).index.tolist()
            df_top_skills = df_exploded[df_exploded['skill_list'].isin(top_skills)]
            
            country_skill_counts = df_top_skills.groupby(['employee_residence', 'skill_list']).size().reset_index(name='count')
            
            def get_alpha3(country_name):
                try:
                    return pycountry.countries.search_fuzzy(country_name)[0].alpha_3
                except:
                    return None
            
            country_skill_counts['iso_alpha'] = country_skill_counts['employee_residence'].apply(get_alpha3)
            country_skill_counts = country_skill_counts.dropna(subset=['iso_alpha'])
            
            for skill in top_skills:
                skill_df = country_skill_counts[country_skill_counts['skill_list'] == skill]
                
                if not skill_df.empty:
                    st.subheader(f"🌍 Global Demand for '{skill.title()}' Skill")
                    fig = px.choropleth(
                        skill_df,
                        locations="iso_alpha",
                        color="count",
                        hover_name="employee_residence",
                        color_continuous_scale="YlOrRd",
                        title=f"Global Demand for '{skill.title()}' Skill"
                    )
                    fig.update_layout(template="plotly_white")
                    st.plotly_chart(fig, use_container_width=True)
    
    with tab6:
        st.markdown('<div class="section-header">Dataset Overview</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Records", df.shape[0])
        with col2:
            st.metric("Total Columns", df.shape[1])
        with col3:
            st.metric("Missing Values", df.isnull().sum().sum())
        
        st.subheader("📊 Dataset Info")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Column Types:**")
            st.dataframe(df.dtypes.to_frame('Data Type'))
        
        with col2:
            st.write("**Missing Values:**")
            missing_df = df.isnull().sum().to_frame('Missing Count')
            missing_df['Percentage'] = (missing_df['Missing Count'] / len(df) * 100).round(2)
            st.dataframe(missing_df[missing_df['Missing Count'] > 0])
        
        st.subheader("🔍 Sample Data")
        st.dataframe(df.head(10))
        
        st.subheader("📈 Basic Statistics")
        st.dataframe(df.describe())

else:
    st.info("👆 Please upload a CSV file to begin the analysis")
    st.markdown("""
    ### Expected CSV Structure:
    Your CSV file should contain columns such as:
    - `job_title`: Job position titles
    - `required_skills`: Comma-separated list of skills
    - `salary_usd`: Salary in USD
    - `experience_level`: Experience level (EN, MI, SE, EX)
    - `education_required`: Required education level
    - `remote_ratio`: Remote work percentage (0, 50, 100)
    - `company_size`: Company size (S, M, L)
    - `employee_residence`: Employee country
    - `posting_date`: Job posting date
    - `industry`: Industry sector
    """)