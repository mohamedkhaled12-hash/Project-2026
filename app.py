import streamlit as st
import pandas as pd
import joblib
import numpy as np
import plotly.express as px

# 1. Page Config
st.set_page_config(page_title="Vision Analytics AI", page_icon="✨", layout="wide")

# ==========================================
# 🎨 Premium UI/UX: Animations & Refined Glassmorphism
# ==========================================
st.markdown("""
<style>
    /* 1. الخلفية الأساسية (Deep Space) - بدون تغيير الألوان */
    .stApp {
        background: radial-gradient(circle at 50% 0%, #1e1b4b 0%, #020617 100%) !important;
        background-attachment: fixed;
    }

    /* إخفاء الشريط العلوي */
    [data-testid="stHeader"] { background-color: transparent !important; }
    [data-testid="stHeader"] * { color: #F8FAFC !important; }

    /* 2. الخطوط والعناوين العامة */
    h1, h2, h3, label, p, li {
        color: #F8FAFC !important;
        font-family: 'Inter', 'Segoe UI', -apple-system, sans-serif;
        font-weight: 600 !important;
        letter-spacing: 0.2px;
    }

    /* تأثير العنوان الرئيسي (Glow & Gradient) */
    .gradient-text {
        background: linear-gradient(135deg, #A855F7 0%, #38BDF8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900;
        font-size: 3.2rem;
        text-align: center;
        margin-top: -20px;
        letter-spacing: -1px;
        text-shadow: 0px 4px 20px rgba(168, 85, 247, 0.3); /* توهج خلف العنوان */
    }

    /* ==========================================
       🚀 الانبهار الحركي (Animations)
       ========================================== */
    @keyframes fadeInUp {
        0% { opacity: 0; transform: translateY(30px); }
        100% { opacity: 1; transform: translateY(0); }
    }

    @keyframes pulseGlow {
        0% { box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.5); }
        70% { box-shadow: 0 0 0 12px rgba(59, 130, 246, 0); }
        100% { box-shadow: 0 0 0 0 rgba(59, 130, 246, 0); }
    }

    /* 3. الكروت الزجاجية (مع حركة الدخول وتأثير الطفو) */
    [data-testid="stForm"], .metric-card {
        background: rgba(15, 23, 42, 0.45) !important;
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 30px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.08);
        transition: transform 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275), box-shadow 0.4s ease;
        animation: fadeInUp 0.8s ease-out forwards; /* الدخول السينمائي */
    }
    
    /* الكارت يترفع لفوق لما تقف عليه بالماوس */
    [data-testid="stForm"]:hover, .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.15);
    }

    /* 4. مربعات الإدخال (نفس الألوان مع تفاعل أنعم) */
    div[data-baseweb="select"] > div,
    div[data-baseweb="base-input"] > input {
        background-color: #F8FAFC !important;
        color: #0F172A !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        border-radius: 10px !important;
        border: 2px solid transparent !important;
        -webkit-text-fill-color: #0F172A !important;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }
    div[data-baseweb="select"] > div:hover,
    div[data-baseweb="base-input"] > input:hover {
        border: 2px solid rgba(56, 189, 248, 0.5) !important;
        transform: scale(1.01); /* تكبير خفيف جداً للمربع */
    }

    /* القائمة المنسدلة */
    ul[data-baseweb="menu"] {
        background-color: #F8FAFC !important;
        border-radius: 10px !important;
        box-shadow: 0 15px 35px rgba(0,0,0,0.3) !important;
    }
    ul[data-baseweb="menu"] li {
        color: #0F172A !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        padding: 10px 15px !important;
    }

    /* 5. أزرار التنقل (Top Tabs) */
    div[role="radiogroup"] {
        display: flex;
        flex-direction: row;
        justify-content: center !important;
        gap: 8px;
        background: rgba(15, 23, 42, 0.6);
        padding: 6px;
        border-radius: 100px;
        width: fit-content;
        margin: 0 auto 35px auto;
        border: 1px solid rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        animation: fadeInUp 0.5s ease-out forwards;
    }
    .stRadio [role="radio"] { display: none !important; }
    .stRadio label {
        background: transparent !important;
        padding: 10px 30px !important;
        border-radius: 100px !important;
        cursor: pointer;
        transition: all 0.3s ease;
        margin: 0 !important;
        border: none !important;
    }
    .stRadio label:hover { background: rgba(255, 255, 255, 0.05) !important; }
    .stRadio label:has(input:checked) {
        background: linear-gradient(135deg, #6366F1 0%, #A855F7 100%) !important;
        box-shadow: 0 4px 15px rgba(168, 85, 247, 0.5);
    }
    .stRadio label:has(input:checked) div {
        color: #FFFFFF !important;
        font-weight: 800 !important;
        letter-spacing: 0.3px;
    }

    /* 6. تصميم زر التحليل (زر بينبض لفت الانتباه) */
    [data-testid="baseButton-secondary"] {
        background: linear-gradient(135deg, #06B6D4 0%, #3B82F6 100%) !important;
        border: none !important;
        padding: 16px 24px !important;
        border-radius: 12px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        animation: pulseGlow 2.5s infinite; /* تأثير النبض */
    }
    [data-testid="baseButton-secondary"] * {
        color: #FFFFFF !important;
        font-weight: 800 !important;
        font-size: 16px !important;
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    [data-testid="baseButton-secondary"]:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 15px 30px -5px rgba(59, 130, 246, 0.6) !important;
        animation: none; /* إيقاف النبض عند وقوف الماوس */
    }

    /* تنسيق القائمة القابلة للطي (Expander) للإرشادات */
    [data-testid="stExpander"] {
        background: rgba(15, 23, 42, 0.45) !important;
        backdrop-filter: blur(20px);
        border-radius: 15px !important;
        border: 1px solid rgba(56, 189, 248, 0.3) !important;
        margin-bottom: 20px;
        animation: fadeInUp 0.7s ease-out forwards;
    }
    [data-testid="stExpander"] summary p {
        color: #38BDF8 !important;
        font-weight: 800 !important;
        font-size: 16px;
    }
    [data-testid="stExpanderDetails"] { background: transparent !important; }

</style>
""", unsafe_allow_html=True)

# 2. Load Models
@st.cache_resource
def load_assets():
    risk_model = joblib.load('risk_model_pipeline.pkl')
    app_model = joblib.load('app_behavior_model_xgb.pkl')
    encoder = joblib.load('label_encoder.pkl')
    return risk_model, app_model, encoder

try:
    risk_model, app_model, encoder = load_assets()
except Exception as e:
    st.error(f"⚠️ Failed to load models. Error: {e}")
    st.stop()

# ==========================================
# 🚀 Navigation Header
# ==========================================
st.markdown("<div class='gradient-text'>Vision Analytics</div>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94A3B8 !important; margin-bottom: 25px; font-size: 1.1rem; animation: fadeInUp 0.4s ease-out forwards;'>Empowered by Advanced Machine Learning</p>", unsafe_allow_html=True)

page = st.radio("", ["Student Risk Analysis", "App Behavior Analysis"], horizontal=True, label_visibility="collapsed")

# ------------------------------------------------------------------
# Page 1: Student Risk Analysis
# ------------------------------------------------------------------
if page == "Student Risk Analysis":
    st.markdown("<h3 style='color: #E9D5FF !important; font-weight: 700; display:flex; align-items:center; gap:10px; animation: fadeInUp 0.6s ease-out forwards;'>🧠 Student Risk Intelligence</h3>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    stress_map = {"Very Calm": 1.0, "Normal Stress": 4.0, "Highly Stressed": 7.0, "Extremely Stressed": 10.0}
    anxiety_map = {"Stable": 1.0, "Mild Anxiety": 3.5, "Constant Tension": 7.0, "Severe Panic": 10.0}
    support_map = {"Completely Isolated": 1.0, "Limited Support": 4.0, "Good Support": 7.5, "Strong Support": 10.0}
    dep_map = {"Optimistic & Energetic": 1.0, "Occasional Sadness": 4.5, "Frequent Low Mood": 7.5, "Severe Despair": 10.0}
    sleep_map = {"< 4 hours (Severely Deprived)": 3.0, "4-6 hours (Insufficient)": 5.0, "7-9 hours (Healthy)": 8.0, "> 9 hours (Oversleeping)": 10.0}
    exam_map = {"No Immediate Exams": 1.0, "Manageable Workload": 4.0, "High Academic Stress": 7.5, "Overwhelming Pressure": 10.0}

    with st.form("risk_form"):
        st.subheader("📋 Behavioral Assessment")
        st.markdown("<hr style='border-color: rgba(255,255,255,0.1); margin: 10px 0 25px 0;'>", unsafe_allow_html=True)
        col1, col2 = st.columns(2, gap="large")

        with col1:
            st.markdown("<b style='color:#38BDF8 !important; font-size: 18px;'>🧬 Psychological Factors</b>", unsafe_allow_html=True)
            stress = st.selectbox("Stress Level:", options=list(stress_map.keys()))
            anxiety = st.selectbox("Anxiety Level:", options=list(anxiety_map.keys()))
            depression = st.selectbox("Mood & Energy Levels:", options=list(dep_map.keys()))

        with col2:
            st.markdown("<b style='color:#38BDF8 !important; font-size: 18px;'>🌍 Environmental Factors</b>", unsafe_allow_html=True)
            support = st.selectbox("Social Support Network:", list(support_map.keys()))
            sleep = st.selectbox("Average Daily Sleep:", list(sleep_map.keys()))
            exams = st.selectbox("Academic Workload:", options=list(exam_map.keys()))

        st.markdown("<br>", unsafe_allow_html=True)
        submit_risk = st.form_submit_button("Initiate AI Analysis", use_container_width=True)

    if submit_risk:
        features = pd.DataFrame([[
            stress_map[stress], anxiety_map[anxiety], dep_map[depression],
            support_map[support], sleep_map[sleep], exam_map[exams]
        ]], columns=['stress_level', 'anxiety_score', 'depression_score', 'social_support', 'sleep_hours', 'exam_pressure'])

        with st.spinner("Processing neural pathways..."):
            probs = risk_model.predict_proba(features)[0]
            clean_classes = [str(c).strip().title() for c in encoder.classes_]
            max_idx = np.argmax(probs)
            base_label = clean_classes[max_idx]
            
            prob_dict = {c: p for c, p in zip(clean_classes, probs)}
            high_prob = prob_dict.get('High', 0.0)
            medium_prob = prob_dict.get('Medium', 0.0)
            
            if high_prob >= 0.25:
                final_label = 'High'
            elif medium_prob >= 0.35:
                final_label = 'Medium'
            else:
                final_label = base_label

        st.markdown("<h3 style='margin-top: 35px; color:#F8FAFC; animation: fadeInUp 0.4s ease-out forwards;'>🎯 Predictive Intelligence Result</h3>", unsafe_allow_html=True)
        res_col1, res_col2 = st.columns([1, 1.5], gap="large")

        with res_col1:
            st.markdown('<div class="metric-card" style="text-align: center; display: flex; flex-direction: column; justify-content: center; height: 100%;">', unsafe_allow_html=True)
            if 'High' in final_label:
                st.markdown("<h2 style='color:#F43F5E !important; font-weight: 900; font-size: 2.5rem; margin-bottom:5px;'>🚨 HIGH RISK</h2>", unsafe_allow_html=True)
                st.markdown("<p style='color:#CBD5E1 !important; font-size: 16px; font-weight: 500 !important;'>Immediate clinical intervention recommended.</p>", unsafe_allow_html=True)
            elif 'Medium' in final_label:
                st.markdown("<h2 style='color:#FBBF24 !important; font-weight: 900; font-size: 2.5rem; margin-bottom:5px;'>🟡 MEDIUM RISK</h2>", unsafe_allow_html=True)
                st.markdown("<p style='color:#CBD5E1 !important; font-size: 16px; font-weight: 500 !important;'>Proactive monitoring and counseling advised.</p>", unsafe_allow_html=True)
            else:
                st.markdown("<h2 style='color:#34D399 !important; font-weight: 900; font-size: 2.5rem; margin-bottom:5px;'>✅ LOW RISK</h2>", unsafe_allow_html=True)
                st.markdown("<p style='color:#CBD5E1 !important; font-size: 16px; font-weight: 500 !important;'>Profile indicates high emotional resilience.</p>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with res_col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            neon_colors = {'High':'#F43F5E', 'Medium':'#FBBF24', 'Low':'#34D399'}

            fig = px.bar(
                x=probs*100, y=clean_classes, orientation='h',
                labels={'x':'Confidence Probability (%)', 'y':''},
                color=clean_classes,
                color_discrete_map=neon_colors,
                text=np.round(probs*100, 1),
                title="AI Confidence Distribution"
            )
            fig.update_traces(textposition='inside', textfont=dict(color='white', size=14, family='Inter, sans-serif'), marker_line_color='rgba(255,255,255,0.2)', marker_line_width=1)
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=0, r=0, t=40, b=0), height=220, showlegend=False,
                font=dict(color='#F8FAFC', size=13, family='Inter, sans-serif'),
                xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', title_font=dict(color='#94A3B8')),
                title_font=dict(size=16, color='#94A3B8')
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------------------------------------------
# Page 2: App Behavior Analysis
# ------------------------------------------------------------------
else:
    st.markdown("<h3 style='color: #67E8F9 !important; font-weight: 700; display:flex; align-items:center; gap:10px; animation: fadeInUp 0.6s ease-out forwards;'>📱 App Behavior Tech-Metrics</h3>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    with st.expander("💡 How to find these metrics on your phone? (Quick Guide)"):
        col_android, col_ios = st.columns(2)
        with col_android:
            st.markdown("<h4 style='color:#34D399; margin-bottom:5px;'>🤖 Android Devices</h4>", unsafe_allow_html=True)
            st.markdown("""
            * **Screen On Time & App Usage:** Go to **Settings** > **Digital Wellbeing & parental controls** > Dashboard.
            * **Battery Drain:** Go to **Settings** > **Battery** > **Battery usage**.
            * **Data Usage:** Go to **Settings** > **Network & internet** > **Internet** > App data usage.
            """)
        with col_ios:
            st.markdown("<h4 style='color:#F87171; margin-bottom:5px;'>🍏 iOS (iPhone)</h4>", unsafe_allow_html=True)
            st.markdown("""
            * **Screen On Time & App Usage:** Go to **Settings** > **Screen Time** > See All Activity.
            * **Battery Drain:** Go to **Settings** > **Battery** (Check the 'Last 24 Hours' usage).
            * **Data Usage:** Go to **Settings** > **Cellular** > Scroll down to 'Cellular Data'.
            """)
            
        st.markdown("<hr style='border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color:#A855F7; margin-bottom:5px;'>🔋 How to calculate Battery Drain (mAh) from Percentage (%)?</h4>", unsafe_allow_html=True)
        st.markdown("""
        Phones usually show battery drain as a percentage (e.g., "Used 40% today"). To input **mAh** into the model, use this simple formula:
        > **Formula:** `(Percentage Used ÷ 100) × Total Battery Capacity (mAh)`
        
        **Example:** If you used **50%** of your battery today, and your phone has a **4000 mAh** battery capacity:
        * `(50 ÷ 100) × 4000 = ` **`2000 mAh`**
        """, unsafe_allow_html=True)

    with st.form("app_behavior_form"):
        st.subheader("⚙️ Technical Telemetry")
        st.markdown("<hr style='border-color: rgba(255,255,255,0.1); margin: 10px 0 25px 0;'>", unsafe_allow_html=True)
        col1, col2 = st.columns(2, gap="large")

        with col1:
            st.markdown("<b style='color:#D8B4FE !important; font-size: 18px;'>👤 User Demographics</b>", unsafe_allow_html=True)
            age = st.number_input("Age:", 10, 100, 20)
            gender = st.selectbox("Gender:", ["Male", "Female"])
            num_apps = st.number_input("Number of Apps Installed:", 0, 500, 50)

        with col2:
            st.markdown("<b style='color:#D8B4FE !important; font-size: 18px;'>🔋 Device Usage Metrics</b>", unsafe_allow_html=True)
            screen_time = st.number_input("Screen On Time (hours/day):", 0.0, 24.0, 5.0)
            battery = st.number_input("Battery Drain (mAh/day):", 0, 10000, 2000)
            data_usage = st.number_input("Data Usage (MB/day):", 0, 50000, 1000)
            app_usage = st.number_input("App Usage Time (min/day):", 0, 1440, 300)

        st.markdown("<br>", unsafe_allow_html=True)
        submit_app = st.form_submit_button("ANALYZE USER BEHAVIOR", use_container_width=True)

    if submit_app:
        try:
            if hasattr(app_model, 'feature_names_in_'): expected_cols = list(app_model.feature_names_in_)
            elif hasattr(app_model, 'steps') and hasattr(app_model.steps[0][1], 'feature_names_in_'): expected_cols = list(app_model.steps[0][1].feature_names_in_)
            else: expected_cols = ['App Usage Time (min/day)', 'Screen On Time (hours/day)', 'Battery Drain (mAh/day)', 'Number of Apps Installed', 'Data Usage (MB/day)', 'Age', 'Gender']

            raw_data = {
                'App Usage Time (min/day)': float(app_usage), 'Screen On Time (hours/day)': float(screen_time),
                'Battery Drain (mAh/day)': float(battery), 'Number of Apps Installed': float(num_apps),
                'Data Usage (MB/day)': float(data_usage), 'Age': float(age), 'Gender': gender
            }

            df_app = pd.DataFrame(columns=expected_cols)
            df_app.loc[0] = 0.0

            for col in expected_cols:
                clean_col = col.strip()
                if clean_col in raw_data: df_app.at[0, col] = raw_data[clean_col]
                elif 'gender' in clean_col.lower(): df_app.at[0, col] = raw_data['Gender']

            with st.spinner("Processing technical metrics..."):
                try:
                    pred = app_model.predict(df_app)[0]
                    st.markdown('<div class="metric-card" style="text-align: center; margin-top:25px; animation: fadeInUp 0.5s ease-out forwards;">', unsafe_allow_html=True)
                    st.markdown(f"<h3 style='color:#CBD5E1 !important; font-size:1.5rem; font-weight:600; margin-bottom:10px;'>Predicted Class</h3><h1 style='color:#22D3EE !important; font-size:3.5rem; font-weight:900; margin:0;'>{pred}</h1>", unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                except Exception as e_inner:
                    if 'isnan' in str(e_inner).lower() or 'convert' in str(e_inner).lower():
                        for col in expected_cols:
                            if 'gender' in col.lower(): df_app.at[0, col] = 1.0 if gender == "Male" else 0.0
                        df_app = df_app.astype(float)
                        pred = app_model.predict(df_app)[0]
                        st.markdown('<div class="metric-card" style="text-align: center; margin-top:25px; animation: fadeInUp 0.5s ease-out forwards;">', unsafe_allow_html=True)
                        st.markdown(f"<h3 style='color:#CBD5E1 !important; font-size:1.5rem; font-weight:600; margin-bottom:10px;'>Predicted Class</h3><h1 style='color:#22D3EE !important; font-size:3.5rem; font-weight:900; margin:0;'>{pred}</h1>", unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.error(f"Prediction Error: {e_inner}")

        except Exception as e_outer:
            st.error(f"Unexpected Error: {e_outer}")