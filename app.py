import streamlit as st
import pandas as pd
import joblib
import numpy as np
import plotly.express as px
import warnings
# إضافات المساعد الذكي
import google.generativeai as genai
from PIL import Image

warnings.filterwarnings('ignore')

# 1. Page Config
st.set_page_config(page_title="Vision Analytics AI", page_icon="✨", layout="wide")

# تهيئة المفتاح في الـ Session State عشان مايتمسحش لما اليوزر يغير الصفحة
if "gemini_api_key" not in st.session_state:
    st.session_state.gemini_api_key = ""

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
    
    /* التعديل هنا: إجبار جميع العناصر الداخلية في المربعات على اللون الغامق */
    div[data-baseweb="select"] *, div[data-baseweb="base-input"] * {
        color: #0F172A !important;
    }

    div[data-baseweb="select"] > div:hover,
    div[data-baseweb="base-input"] > input:hover {
        border: 2px solid rgba(56, 189, 248, 0.5) !important;
        transform: scale(1.01); /* تكبير خفيف جداً للمربع */
    }

    /* إصلاح القائمة المنسدلة بالكامل لتظهر الحروف الغامقة */
    ul[data-baseweb="menu"], div[data-baseweb="popover"] {
        background-color: #F8FAFC !important;
        border-radius: 10px !important;
        box-shadow: 0 15px 35px rgba(0,0,0,0.3) !important;
    }
    ul[data-baseweb="menu"] li, ul[data-baseweb="menu"] li *, div[data-baseweb="popover"] * {
        color: #0F172A !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        -webkit-text-fill-color: #0F172A !important;
    }
    ul[data-baseweb="menu"] li {
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

    /* 6. التعديل الجذري هنا: استهداف أزرار (Form Submit) بشكل مباشر جداً */
    div[data-testid="stFormSubmitButton"] > button,
    [data-testid="baseButton-secondary"] {
        background: linear-gradient(135deg, #06B6D4 0%, #3B82F6 100%) !important;
        border: none !important;
        padding: 16px 24px !important;
        border-radius: 12px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        animation: pulseGlow 2.5s infinite; /* تأثير النبض */
    }
    div[data-testid="stFormSubmitButton"] > button *,
    [data-testid="baseButton-secondary"] * {
        color: #0F172A !important; 
        -webkit-text-fill-color: #0F172A !important; /* إجبار المتصفح على اللون الغامق */
        font-weight: 900 !important; 
        font-size: 16px !important;
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    div[data-testid="stFormSubmitButton"] > button:hover,
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

# ✨ إضافة الصفحة الثالثة للـ Navigation
page = st.radio("", ["Student Risk Analysis", "App Behavior Analysis", "AI Assistant 🤖"], horizontal=True, label_visibility="collapsed")

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
            stress = st.selectbox("Stress Level:", list(stress_map.keys()))
            anxiety = st.selectbox("Anxiety Level:", list(anxiety_map.keys()))
            depression = st.selectbox("Mood & Energy:", list(dep_map.keys()))
        with col2:
            st.markdown("<b style='color:#38BDF8 !important; font-size: 18px;'>🌍 Environmental Factors</b>", unsafe_allow_html=True)
            support = st.selectbox("Social Support:", list(support_map.keys()))
            sleep = st.selectbox("Daily Sleep:", list(sleep_map.keys()))
            exams = st.selectbox("Academic Workload:", list(exam_map.keys()))
        submit_risk = st.form_submit_button("Initiate AI Analysis", use_container_width=True)

    if submit_risk:
        features = pd.DataFrame([{
            'stress_level': float(stress_map[stress]), 'anxiety_score': float(anxiety_map[anxiety]),
            'depression_score': float(dep_map[depression]), 'social_support': float(support_map[support]),
            'sleep_hours': float(sleep_map[sleep]), 'exam_pressure': float(exam_map[exams])
        }])

        with st.spinner("Processing..."):
            probs = risk_model.predict_proba(features)[0]
            clean_classes = [str(c).strip().title() for c in encoder.classes_]
            prob_dict = {c: p for c, p in zip(clean_classes, probs)}
            
            if prob_dict.get('High', 0.0) >= 0.25: final_label = 'High'
            elif prob_dict.get('Medium', 0.0) >= 0.35: final_label = 'Medium'
            else: final_label = clean_classes[np.argmax(probs)]

            # 💡 حفظ النتيجة في السياق ليستخدمها المساعد الذكي لاحقاً
            st.session_state['last_analysis_context'] = f"The user analyzed Student Risk. Result: {final_label} Risk."

        res_col1, res_col2 = st.columns([1, 1.5])
        with res_col1:
            st.markdown('<div class="metric-card" style="text-align: center;">', unsafe_allow_html=True)
            if 'High' in final_label: st.markdown("<h2 style='color:#F43F5E;'>🚨 HIGH RISK</h2>", unsafe_allow_html=True)
            elif 'Medium' in final_label: st.markdown("<h2 style='color:#FBBF24;'>🟡 MEDIUM RISK</h2>", unsafe_allow_html=True)
            else: st.markdown("<h2 style='color:#34D399;'>✅ LOW RISK</h2>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with res_col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            fig = px.bar(x=probs*100, y=clean_classes, orientation='h', color=clean_classes, color_discrete_map={'High':'#F43F5E', 'Medium':'#FBBF24', 'Low':'#34D399'})
            fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#F8FAFC'), height=200, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------------------------------------------
# Page 2: App Behavior Analysis
# ------------------------------------------------------------------
elif page == "App Behavior Analysis":
    st.markdown("<h3 style='color: #67E8F9 !important;'>📱 App Behavior Tech-Metrics</h3>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    with st.expander("💡 Guide: How to find these metrics on your phone?"):
        col_android, col_ios = st.columns(2)
        
        with col_android:
            st.markdown("<h4 style='color:#34D399; margin-bottom:5px;'>🤖 Android Devices</h4>", unsafe_allow_html=True)
            st.markdown("""
            * **Screen On Time & Usage Time:** Go to **Settings > Digital Wellbeing & parental controls**.
            * **Battery Drain:** Go to **Settings > Battery > Battery usage**.
            * **Data Usage:** Go to **Settings > Network & internet > Internet > App data usage**.
            """)
            
        with col_ios:
            st.markdown("<h4 style='color:#F87171; margin-bottom:5px;'>🍏 iOS (iPhone)</h4>", unsafe_allow_html=True)
            st.markdown("""
            * **Screen On Time & Usage Time:** Go to **Settings > Screen Time > See All Activity**.
            * **Battery Drain:** Go to **Settings > Battery**.
            * **Data Usage:** Go to **Settings > Cellular** (scroll down to Cellular Data).
            """)
            
        st.markdown("<hr style='border-color: rgba(255,255,255,0.1); margin: 15px 0;'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color:#A855F7; margin-bottom:5px;'>🔋 How to calculate Battery Drain (mAh)?</h4>", unsafe_allow_html=True)
        st.markdown("""
        Most phones display battery usage as a percentage (e.g., 50%). To convert this into **mAh** for the model, use this simple formula:
        > **` (Percentage Used ÷ 100) × Total Battery Capacity (mAh) `**
        
        *Example:* If you used 40% of a 5000 mAh battery: `(40 ÷ 100) × 5000 = 2000 mAh`.
        """, unsafe_allow_html=True)

    with st.form("app_behavior_form"):
        st.subheader("⚙️ Technical Telemetry")
        st.markdown("<hr style='border-color: rgba(255,255,255,0.1); margin: 10px 0 25px 0;'>", unsafe_allow_html=True)
        col1, col2 = st.columns(2, gap="large")
        with col1:
            age = st.number_input("Age:", 10, 100, 20)
            gender = st.selectbox("Gender:", ["Male", "Female"])
            num_apps = st.number_input("Apps Installed:", 0, 500, 50)
        with col2:
            screen_time = st.number_input("Screen Time (hours):", 0.0, 24.0, 5.0)
            battery = st.number_input("Battery Drain (mAh):", 0, 10000, 2000)
            data_usage = st.number_input("Data (MB):", 0, 50000, 1000)
            app_usage = st.number_input("Usage Time (min):", 0, 1440, 300)
        submit_app = st.form_submit_button("ANALYZE USER BEHAVIOR", use_container_width=True)

    if submit_app:
        with st.spinner("Analyzing..."):
            raw_data = {
                'App Usage Time (min/day)': [float(app_usage)],
                'Screen On Time (hours/day)': [float(screen_time)],
                'Battery Drain (mAh/day)': [float(battery)],
                'Number of Apps Installed': [float(num_apps)],
                'Data Usage (MB/day)': [float(data_usage)],
                'Age': [float(age)],
                'Gender': [gender]
            }
            
            df_app = pd.DataFrame(raw_data)
            
            if hasattr(app_model, 'feature_names_in_'):
                expected_cols = list(app_model.feature_names_in_)
                
                if 'Gender_Male' in expected_cols:
                    df_app['Gender_Male'] = 1.0 if gender == "Male" else 0.0
                    df_app['Gender_Female'] = 1.0 if gender == "Female" else 0.0
                    if 'Gender' in df_app.columns:
                        df_app = df_app.drop(columns=['Gender'])
                
                df_app = df_app.reindex(columns=expected_cols, fill_value=0.0)

            try:
                pred = app_model.predict(df_app)[0]
                success = True
            except Exception as e1:
                try:
                    df_app['Gender'] = 1.0 if gender == "Male" else 0.0
                    df_app = df_app.astype(float)
                    pred = app_model.predict(df_app)[0]
                    success = True
                except Exception as e2:
                    success = False
                    st.error("⚠️ الموديل رافض شكل البيانات! دي رسالة الخطأ:")
                    st.code(str(e2))
                    
                    if hasattr(app_model, 'feature_names_in_'):
                        st.warning("🔍 الموديل متدرب ومستني الأعمدة دي بالظبط (انسخها عشان نعرف المشكلة):")
                        st.write(list(app_model.feature_names_in_))
            
            if success:
                # 💡 حفظ النتيجة في السياق ليستخدمها المساعد الذكي لاحقاً
                st.session_state['last_analysis_context'] = f"The user analyzed App Behavior. Predicted Class: {int(pred)}."

                st.markdown(f"""
                    <div class="metric-card" style="text-align: center; margin-top:25px;">
                        <h3 style='color:#CBD5E1 !important;'>Predicted Class</h3>
                        <h1 style='color:#22D3EE !important; font-size:3.5rem; font-weight:900;'>{int(pred)}</h1>
                    </div>
                """, unsafe_allow_html=True)

# ------------------------------------------------------------------
# Page 3: AI Assistant 🤖 (الجديدة)
# ------------------------------------------------------------------
elif page == "AI Assistant 🤖":
    st.markdown("<h3 style='color: #A855F7 !important; font-weight: 700; animation: fadeInUp 0.6s ease-out forwards;'>🤖 Smart AI Assistant</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94A3B8 !important;'>اسألني عن النتائج، أو ارفع صورة للمخطط البياني وسأقوم بتحليله لك استناداً إلى أحدث تقنيات Gemini.</p>", unsafe_allow_html=True)

    # ==========================================
    # 🔑 قسم إعداد الـ API Key وإرشادات المستخدم
    # ==========================================
    with st.expander("🔑 إعداد مفتاح الذكاء الاصطناعي (API Key) - اضغط هنا للبدء", expanded=not st.session_state.gemini_api_key):
        st.markdown("""
        <h4 style='color:#38BDF8; margin-top:0;'>خطوات الحصول على مفتاح مجاني:</h4>
        <ol style='color:#CBD5E1; line-height: 1.8; font-size: 15px;'>
            <li>ادخل على منصة المطورين: <a href='https://aistudio.google.com/app/apikey' target='_blank' style='color:#A855F7; font-weight:bold;'>Google AI Studio</a> وسجل دخول بحساب جوجل الخاص بك.</li>
            <li>اضغط على الزر الأزرق <b>Create API key</b> الموجود في الصفحة.</li>
            <li>انسخ المفتاح الذي سيظهر لك (يبدأ بحروف <code>AIza...</code>) والصقه في المربع بالأسفل.</li>
        </ol>
        """, unsafe_allow_html=True)
        
        # حقل إدخال المفتاح
        user_api_key = st.text_input("أدخل مفتاح Gemini API الخاص بك:", value=st.session_state.gemini_api_key, type="password")
        
        if user_api_key:
            st.session_state.gemini_api_key = user_api_key
            st.success("✅ تم حفظ المفتاح بنجاح! يمكنك الآن بدء المحادثة في الأسفل.")

    # التأكد من وجود المفتاح قبل تشغيل الشات
    if not st.session_state.gemini_api_key:
        st.warning("👆 يرجى إدخال مفتاح Gemini API في المربع بالأعلى لتفعيل الشات بوت.")
    else:
        # إعداد الاتصال بالموديل
        genai.configure(api_key=st.session_state.gemini_api_key)

        # تهيئة تاريخ المحادثة
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # عرض المحادثات السابقة
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # واجهة رفع الصورة (اختياري)
        with st.expander("📷 إرفاق صورة للتحليل (اختياري)"):
            uploaded_file = st.file_uploader("اختر صورة (PNG, JPG, JPEG)", type=["png", "jpg", "jpeg"])
            if uploaded_file is not None:
                st.image(uploaded_file, caption="الصورة المرفوعة", width=250)

        # مربع المحادثة
        if prompt := st.chat_input("اكتب سؤالك هنا... (مثال: اشرح لي نتيجتي الأخيرة)"):
            
            # عرض رسالة المستخدم
            with st.chat_message("user"):
                st.markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})

            # تجهيز السياق للموديل
            sys_instruct = "أنت مساعد ذكي مدمج في تطبيق (Vision Analytics) لتحليل بيانات الطلاب وسلوك التطبيقات. أجب باحترافية وبطريقة تساعد المستخدم على فهم البيانات."
            if 'last_analysis_context' in st.session_state:
                sys_instruct += f"\n[سياق مخفي]: أحدث نتيجة تحليل قام بها المستخدم هي: {st.session_state['last_analysis_context']}"

            # إعداد الموديل الصحيح بناءً على ما اكتشفناه
            model = genai.GenerativeModel(
                model_name='gemini-2.5-flash',
                system_instruction=sys_instruct
            )

            # طلب الرد
            with st.chat_message("assistant"):
                with st.spinner("جاري التحليل... 🧠"):
                    try:
                        if uploaded_file is not None:
                            img = Image.open(uploaded_file)
                            response = model.generate_content([prompt, img])
                        else:
                            response = model.generate_content(prompt)
                        
                        st.markdown(response.text)
                        st.session_state.messages.append({"role": "assistant", "content": response.text})
                    
                    except Exception as e:
                        st.error(f"حدث خطأ أثناء معالجة الطلب. تأكد من صلاحية الـ API Key الخاص بك. (الخطأ: {e})")
