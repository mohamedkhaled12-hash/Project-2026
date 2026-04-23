import streamlit as st
import pandas as pd
import joblib
import numpy as np
import plotly.express as px
import warnings
# إضافات المساعد الذكي
import google.generativeai as genai
from PIL import Image
# 📊 إضافات قاعدة البيانات
import json
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

warnings.filterwarnings('ignore')

# 1. Page Config
st.set_page_config(page_title="Vision Analytics AI", page_icon="✨", layout="wide")

# ==========================================
# 📊 إعداد الاتصال بقاعدة بيانات Google Sheets
# ==========================================
@st.cache_resource
def get_gspread_client():
    try:
        # قراءة المفتاح من الـ Secrets
        creds_json = st.secrets["GOOGLE_CREDENTIALS"]
        if isinstance(creds_json, str):
            creds_dict = json.loads(creds_json)
        else:
            creds_dict = creds_json
        
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        return None

db_client = get_gspread_client()

def log_data(sheet_tab, row_data):
    if db_client:
        try:
            # يفتح الشيت الرئيسي ويبحث عن الـ Tab المطلوبة (Students أو Apps)
            sheet = db_client.open("Vision_Analytics_DB").worksheet(sheet_tab)
            # يضيف سطر جديد يحتوي على الوقت والتاريخ + البيانات
            sheet.append_row([datetime.now().strftime("%Y-%m-%d %H:%M:%S")] + row_data)
        except Exception:
            pass  # تجاهل الأخطاء بصمت لعدم إفساد تجربة المستخدم

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
    
    /* إجبار جميع العناصر الداخلية في المربعات على اللون الغامق */
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

    /* 6. استهداف أزرار (Form Submit) بشكل مباشر جداً */
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
            st.session_state['last_analysis_context'] = f"قام المستخدم للتو بتحليل (Student Risk Analysis). النتيجة هي: مستوى خطر {final_label}."
            
            # 📊 تسجيل البيانات في الخلفية
            log_data("Students", [stress, anxiety, depression, support, sleep, exams, final_label])

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
            
        # ==============================================================
        # 📄 دمج تقارير الطالب التفصيلية (Student Risk Scripts) - Styled
        # ==============================================================
        RISK_REPORTS = {
            "Low": """
            <div dir="rtl" style="text-align: right; color: #E2E8F0; font-size: 16px; line-height: 1.8; margin-bottom: 15px;">
                <h4 style="color: #34D399; margin-bottom: 10px;">🌟 الخطر المنخفض</h4>
                يمثل هذا المستوى أكثر الملفات الصحية إيجابية في نموذج الطلاب لديك. النمط المعتاد هنا هو نوم أطول وأكثر انتظامًا، وقلق واكتئاب أقل، ودعم اجتماعي أقوى، واحتراق دراسي منخفض. ولا تكون الدرجات الأكاديمية بالضرورة أعلى بشكل كبير مقارنة بالمجموعات الأخرى، مما يشير إلى أن النموذج يلتقط الرفاه النفسي أكثر من التحصيل وحده. وهذه إشارة جيدة: فهي تعني أن الطالب يتكيف بدلًا من مجرد البقاء تحت الضغط. والهدف الرئيسي هنا هو المحافظة، لأن ملف الخطر المنخفض يمكن أن يتغير سريعًا إذا انهار النوم أو ضعفت شبكة الدعم أو أصبح عبء الدراسة غير منظم.
            </div>
            
            <div dir="ltr" style="text-align: left; color: #94A3B8; font-size: 15px; line-height: 1.6; margin-bottom: 20px; padding: 15px; background: rgba(0,0,0,0.2); border-radius: 10px; border-left: 4px solid #34D399;">
                <b>Low risk:</b> This level represents the healthiest profile in your student model. The typical pattern is longer and more regular sleep, lower anxiety and depression, stronger social support, and low burnout. Academic performance is not necessarily dramatically higher than in other groups, which suggests that the model is mainly capturing well-being rather than grades alone. This is a good sign: it means the student is coping, not simply surviving. The main goal here is maintenance, because a low-risk profile can change quickly if sleep collapses, support weakens, or workload becomes unstructured.
            </div>

            <div style="background: rgba(255,255,255,0.03); padding: 20px; border-radius: 12px; border: 1px solid rgba(52, 211, 153, 0.3);">
                <h4 style="color: #F8FAFC; text-align: center; margin-bottom: 15px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 10px;">💡 التوصيات / Recommendations</h4>
                <div dir="rtl" style="text-align: right; color: #CBD5E1; font-size: 15px; line-height: 1.8; margin-bottom: 15px;">
                    <ul style="list-style-type: '✔️ ';">
                        <li>حافظ على انتظام النوم، لأن ثبات النوم من أقوى عوامل حماية الانتباه والصحة النفسية.</li>
                        <li>حافظ على شبكة الدعم الحالية، لأن الدعم الاجتماعي يرتبط بانخفاض الضغط الأكاديمي والإرهاق العاطفي.</li>
                        <li>استخدم التخطيط الأسبوعي مبكرًا حتى يبقى عبء الدراسة قابلًا للإدارة قبل أن يتحول إلى احتراق.</li>
                    </ul>
                </div>
                <div dir="ltr" style="text-align: left; color: #94A3B8; font-size: 14px; line-height: 1.6;">
                    <ul style="list-style-type: '✔️ ';">
                        <li>Keep sleep consistent, because stable sleep is one of the strongest protectors of focus and mental health.</li>
                        <li>Preserve the support network that is already working, since social support is linked to lower academic stress and emotional exhaustion.</li>
                        <li>Use weekly planning early, so workload stays manageable before pressure turns into burnout.</li>
                    </ul>
                </div>
            </div>
            """,
            "Medium": """
            <div dir="rtl" style="text-align: right; color: #E2E8F0; font-size: 16px; line-height: 1.8; margin-bottom: 15px;">
                <h4 style="color: #FBBF24; margin-bottom: 10px;">⚠️ الخطر المتوسط</h4>
                هذه هي أهم مرحلة “للرصد المبكر”. الطلاب هنا غالبًا يُظهرون إشارات تحذيرية واضحة: نوم أقل، وقلق متزايد، وأعراض اكتئاب أكبر، واحتراق دراسي متوسط، ودعم أقل من فئة الخطر المنخفض. ومع ذلك، يظل الملف قابلًا للإصلاح. تكمن أهمية هذا المستوى في أن الأداء الأكاديمي قد يبدو مقبولًا رغم وجود ضغط نفسي واضح في الخلفية، ولذلك قد لا يلاحظ الطالب المشكلة مبكرًا. وإذا لم يُعالج، يمكن أن يتحول الخطر المتوسط بسرعة إلى خطر مرتفع خلال فترات الامتحانات، أو الضغط العاطفي، أو الضغوط الأسرية.
            </div>

            <div dir="ltr" style="text-align: left; color: #94A3B8; font-size: 15px; line-height: 1.6; margin-bottom: 20px; padding: 15px; background: rgba(0,0,0,0.2); border-radius: 10px; border-left: 4px solid #FBBF24;">
                <b>Medium risk:</b> This is the most important “watch closely” level. Students here usually show clear warning signs: less sleep, rising anxiety, more depression symptoms, moderate burnout, and weaker support than the low-risk group. The profile is still recoverable, but it is less resilient. Academic performance may still look acceptable, which is exactly why this level matters: the strain is visible in the background before it becomes a crisis. If unmanaged, medium risk can move quickly toward high risk during exam periods, emotional stress, or family pressure.
            </div>

            <div style="background: rgba(255,255,255,0.03); padding: 20px; border-radius: 12px; border: 1px solid rgba(251, 191, 36, 0.3);">
                <h4 style="color: #F8FAFC; text-align: center; margin-bottom: 15px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 10px;">💡 التوصيات / Recommendations</h4>
                <div dir="rtl" style="text-align: right; color: #CBD5E1; font-size: 15px; line-height: 1.8; margin-bottom: 15px;">
                    <ul style="list-style-type: '🎯 ';">
                        <li>ثبّت نافذة نوم محددة واحمها باعتبارها جزءًا غير قابل للتفاوض من خطة الدراسة.</li>
                        <li>قسّم المذاكرة إلى فترات قصيرة مع فواصل تعافٍ، لأن الفوضى الدراسية والاحتراق يزدادان عندما يكون العمل غير منظم.</li>
                        <li>تواصل مبكرًا مع صديق أو مرشد أو أخصائي، لأن الدعم الاجتماعي يقلل الضغط والإرهاق العاطفي.</li>
                    </ul>
                </div>
                <div dir="ltr" style="text-align: left; color: #94A3B8; font-size: 14px; line-height: 1.6;">
                    <ul style="list-style-type: '🎯 ';">
                        <li>Fix a sleep window and protect it as a non-negotiable part of the study plan.</li>
                        <li>Break study into short timed blocks with recovery breaks, because overload and academic burnout grow when work is unstructured.</li>
                        <li>Reach out early to a friend, advisor, or counselor, since social support reduces stress and emotional exhaustion.</li>
                    </ul>
                </div>
            </div>
            """,
            "High": """
            <div dir="rtl" style="text-align: right; color: #E2E8F0; font-size: 16px; line-height: 1.8; margin-bottom: 15px;">
                <h4 style="color: #F43F5E; margin-bottom: 10px;">🚨 الخطر المرتفع</h4>
                هذا المستوى يشير إلى أقوى درجات الضغط في نموذج الطلاب لديك. والنمط المعتاد هنا هو نوم قصير، وقلق مرتفع، وأعراض اكتئاب ملحوظة، واحتراق دراسي قوي، ودعم اجتماعي منخفض، وغالبًا مع ضغط أسري كبير وزيادة في خطر الانسحاب الدراسي. وقد لا تبدو النتائج الأكاديمية مختلفة كثيرًا عن المجموعات الأخرى، ما يعني أن الخطر الحقيقي مختبئ في الرفاه النفسي لا في الدرجات فقط. وفي سياق البحث أو الفحص، ينبغي التعامل مع هذه النتيجة بوصفها إشارة دعم قوية لا تشخيصًا. إنها النقطة التي يصبح فيها الدعم، والراحة، وتعديل عبء العمل أمورًا عاجلة.
            </div>

            <div dir="ltr" style="text-align: left; color: #94A3B8; font-size: 15px; line-height: 1.6; margin-bottom: 20px; padding: 15px; background: rgba(0,0,0,0.2); border-radius: 10px; border-left: 4px solid #F43F5E;">
                <b>High risk:</b> This level signals the strongest strain in your student model. The pattern is typically short sleep, high anxiety, noticeable depressive symptoms, strong burnout, and low perceived support, often alongside high family expectation and increased dropout risk. Academic performance may still not look dramatically different from the other groups, which means the risk is hidden in well-being rather than grades. In a research or screening context, this should be treated as a strong alert rather than a diagnosis. It is the point where support, rest, and workload adjustment matter immediately.
            </div>

            <div style="background: rgba(255,255,255,0.03); padding: 20px; border-radius: 12px; border: 1px solid rgba(244, 63, 94, 0.4);">
                <h4 style="color: #F8FAFC; text-align: center; margin-bottom: 15px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 10px;">💡 التوصيات / Recommendations</h4>
                <div dir="rtl" style="text-align: right; color: #CBD5E1; font-size: 15px; line-height: 1.8; margin-bottom: 15px;">
                    <ul style="list-style-type: '🛡️ ';">
                        <li>تعامل مع النتيجة بوصفها إشارة دعم وتواصل مع مرشد نفسي أو أكاديمي أو عضو موثوق من هيئة التدريس مبكرًا.</li>
                        <li>خفف الالتزامات غير الضرورية لفترة قصيرة حتى يتمكن النوم والتعافي من اللحاق بالطالب.</li>
                        <li>أجرِ محادثة صادقة واحدة مع الأسرة أو شخص داعم حول الضغط الحالي وعبء الدراسة.</li>
                    </ul>
                </div>
                <div dir="ltr" style="text-align: left; color: #94A3B8; font-size: 14px; line-height: 1.6;">
                    <ul style="list-style-type: '🛡️ ';">
                        <li>Treat the result as a support signal and contact a counselor, advisor, or trusted faculty member early.</li>
                        <li>Reduce nonessential commitments for a short period so sleep and recovery can catch up.</li>
                        <li>Have one honest conversation with family or a close support person about current pressure and workload.</li>
                    </ul>
                </div>
            </div>
            """
        }

        if 'High' in final_label:
            selected_report = RISK_REPORTS["High"]
        elif 'Medium' in final_label:
            selected_report = RISK_REPORTS["Medium"]
        else:
            selected_report = RISK_REPORTS["Low"]

        st.markdown('<div class="metric-card" style="margin-top:20px;">', unsafe_allow_html=True)
        st.markdown("<h3 style='color:#E9D5FF; text-align:center; margin-bottom:20px;'>📄 Detailed Report / تقرير التحليل التفصيلي</h3>", unsafe_allow_html=True)
        st.markdown(selected_report, unsafe_allow_html=True)
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
                st.session_state['last_analysis_context'] = f"قام المستخدم للتو بتحليل (App Behavior Analysis). النتيجة هي: المستخدم ينتمي للفئة (Class {int(pred)})."
                
                # 📊 تسجيل البيانات في الخلفية
                log_data("Apps", [age, gender, num_apps, screen_time, battery, data_usage, app_usage, int(pred)])

                st.markdown(f"""
                    <div class="metric-card" style="text-align: center; margin-top:25px;">
                        <h3 style='color:#CBD5E1 !important;'>Predicted Class</h3>
                        <h1 style='color:#22D3EE !important; font-size:3.5rem; font-weight:900;'>{int(pred)}</h1>
                    </div>
                """, unsafe_allow_html=True)
                
                # ==============================================================
                # 📄 دمج تقارير السلوك التفصيلية (App Behavior Scripts) - Styled
                # ==============================================================
                APP_REPORTS = {
                    0: """
                    <div dir="rtl" style="text-align: right; color: #E2E8F0; font-size: 15px; line-height: 1.8; margin-bottom: 15px;">
                        <h4 style="color: #34D399; margin-bottom: 5px;">🔹 الجزء المنخفض (حوالي 0–10% شدة)</h4>
                        يمثل هذا الجزء الطرف الأكثر انضباطًا في المقياس. عادةً ما يُظهر المستخدمون هنا زمن استخدام قصيرًا، ووقت شاشة منخفضًا، واستهلاكًا خفيفًا للبطارية، وعددًا قليلًا من التطبيقات المثبتة، واستهلاكًا محدودًا للبيانات. يبدو النمط أقرب إلى “تفقد وظيفي” منه إلى تصفح متواصل. ومن ناحية الانتباه، يوجد تشتت بسيط فقط، وغالبًا يستطيع المستخدم الانفصال عن الهاتف بسهولة. وفي إطار brainrot، ما يزال هذا الجزء “نظيفًا” إلى حد كبير، لكنه يمثل النقطة التي يجب فيها حماية العادات قبل أن تصبح آلية أكثر.
                        
                        <h4 style="color: #34D399; margin-top: 15px; margin-bottom: 5px;">🔸 الجزء المرتفع (حوالي 10–20% شدة)</h4>
                        ما يزال هذا جزءًا منخفض الخطورة، لكنه يشكل الحد الأعلى من Class 0، وغالبًا ما يُظهر تفقدًا أكثر تكرارًا، وجلسات تصفح أطول قليلًا، واعتمادًا أكبر على الهاتف أثناء الملل. المستخدم هنا لم يدخل بعد في حالة الحمل الرقمي الشديد، لكن الجهاز يبدأ في التحول إلى وسيلة افتراضية لملء الفراغ. وهذا مهم لأن التعرض المتكرر لمحفزات وسائل التواصل والاستخدام المتعدد للوسائط قد يضعفان القدرة على التركيز المستمر بمرور الوقت. هذا الجزء يستفيد من الوقاية أكثر من التصحيح: فالتغييرات الصغيرة هنا يمكن أن تمنع الانزلاق إلى الفئات الأعلى.
                    </div>

                    <div dir="ltr" style="text-align: left; color: #94A3B8; font-size: 14px; line-height: 1.6; margin-bottom: 20px; padding: 15px; background: rgba(0,0,0,0.2); border-radius: 10px; border-left: 4px solid #34D399;">
                        <b>Low part (about 0–10% intensity):</b> This is the most controlled end of the scale. Users here usually show very short app use, low screen-on time, light battery drain, few installed apps, and relatively low data consumption. The pattern looks like functional checking rather than continuous scrolling. Attention fragmentation is present only at a mild level, and the user can usually disengage without much effort. In a brainrot framework, this segment is still mostly “clean,” but it is the point where habits should be protected before they become more automatic.<br><br>
                        <b>High part (about 10–20% intensity):</b> This is still a low-risk band, but it is the upper edge of Class 0 and often shows more frequent checking, slightly longer scrolling sessions, and more dependence on the phone during boredom. The user is not yet in heavy overload, but the device is beginning to function as a default filler. That matters because repeated social-media cues and media multitasking can quietly reduce sustained attention over time. This segment benefits from prevention, not correction: small boundary changes here can stop the slide into higher classes.
                    </div>

                    <div style="background: rgba(255,255,255,0.03); padding: 20px; border-radius: 12px; border: 1px solid rgba(52, 211, 153, 0.3);">
                        <h4 style="color: #F8FAFC; text-align: center; margin-bottom: 15px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 10px;">💡 التوصيات / Recommendations</h4>
                        <div dir="rtl" style="text-align: right; color: #CBD5E1; font-size: 15px; line-height: 1.8; margin-bottom: 15px;">
                            <ul style="list-style-type: '✔️ ';">
                                <li>اجعل الإشعارات مقتصرة على التطبيقات الأساسية فقط، حتى لا يصبح الهاتف محفزًا دائمًا للانتباه.</li>
                                <li>استخدم حدًا يوميًا بسيطًا لزمن الشاشة، وتوقف عند الوصول إليه حتى لو كان المحتوى ما يزال سهل المتابعة.</li>
                                <li>استبدل التصفح العشوائي بنشاط غير متصل بالإنترنت مثل المشي أو القراءة أو الاستماع للموسيقى دون صيغة “feed”.</li>
                            </ul>
                        </div>
                        <div dir="ltr" style="text-align: left; color: #94A3B8; font-size: 14px; line-height: 1.6;">
                            <ul style="list-style-type: '✔️ ';">
                                <li>Keep notifications limited to essential apps only, so the phone does not become a constant attention trigger.</li>
                                <li>Use a simple daily screen-time ceiling and stop the session when it is reached, even if the content still feels easy to continue.</li>
                                <li>Replace idle scrolling with a short offline habit such as walking, reading, or music without the feed format.</li>
                            </ul>
                        </div>
                    </div>
                    """,
                    1: """
                    <div dir="rtl" style="text-align: right; color: #E2E8F0; font-size: 15px; line-height: 1.8; margin-bottom: 15px;">
                        <h4 style="color: #60A5FA; margin-bottom: 5px;">🔹 الجزء المنخفض (حوالي 20–30% شدة)</h4>
                        هذا الجزء يمثل خطوة واضحة للأعلى مقارنة بـ Class 0. هنا يقضي المستخدم وقتًا أطول في الأنشطة القائمة على التطبيقات، مع زيادة في وقت الشاشة، وارتفاع في استهلاك البيانات، وعادة أكثر وضوحًا في تفقد الهاتف أثناء الانتقالات وأوقات الفراغ. ما يزال السلوك قابلًا للإدارة، لكن الانتباه لم يعد متأثرًا بشكل خفيف فقط. فالجلسات القصيرة من الفيديوهات القصيرة، والتبديل السريع بين التطبيقات، والدخول المتكرر إلى التطبيقات يمكن أن يجعل التركيز أقل استقرارًا، خصوصًا أثناء الدراسة أو العمل. ويمكن وصف هذا النمط بأنه استخدام متوسط مع بدايات الاعتماد.
                        
                        <h4 style="color: #60A5FA; margin-top: 15px; margin-bottom: 5px;">🔸 الجزء المرتفع (حوالي 30–40% شدة)</h4>
                        في النصف الأعلى من هذه الفئة تصبح العادة أكثر التصاقًا. تطول الجلسات، ويصبح المستخدم أكثر ميلًا للانتقال بين الخلاصات المختلفة، ويبدأ الهاتف في منافسة المهام المقصودة. وتشير البحوث حول تعدد المهام الإعلامي وإلهاء وسائل التواصل الاجتماعي إلى أن هذا النمط قد يضعف التركيز حتى عندما لا يشعر المستخدم بأنه “مدمن”. عمليًا، يعد Class 1 High النقطة التي ينبغي فيها استخدام وسائل مقاومة أقوى: حدود التطبيقات، ووضع grayscale، وفترات واعية خالية من الهاتف.
                    </div>

                    <div dir="ltr" style="text-align: left; color: #94A3B8; font-size: 14px; line-height: 1.6; margin-bottom: 20px; padding: 15px; background: rgba(0,0,0,0.2); border-radius: 10px; border-left: 4px solid #60A5FA;">
                        <b>Low part (about 20–30% intensity):</b> This segment is a clear step up from Class 0. Users are spending longer stretches in app-based activity, with more screen-on time, heavier data use, and a more obvious habit of checking the phone during transitions and downtime. The behavior still looks manageable, but attention is no longer only lightly affected. Short-form content, rapid switching, and repeated re-entry into apps can make focus less stable, especially during study or work blocks. The profile is best described as moderate engagement with early dependency patterns.<br><br>
                        <b>High part (about 30–40% intensity):</b> This upper-half segment is where the habit starts becoming sticky. Session length grows, the user is more likely to drift from one feed to another, and the phone begins to compete with intentional tasks. Research on media multitasking and social-media distraction suggests that this pattern can weaken task focus even when the user does not feel “addicted.” In practice, Class 1 High is the point where the person should start using stronger friction: app limits, grayscale mode, and deliberate no-phone intervals.
                    </div>

                    <div style="background: rgba(255,255,255,0.03); padding: 20px; border-radius: 12px; border: 1px solid rgba(96, 165, 250, 0.3);">
                        <h4 style="color: #F8FAFC; text-align: center; margin-bottom: 15px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 10px;">💡 التوصيات / Recommendations</h4>
                        <div dir="rtl" style="text-align: right; color: #CBD5E1; font-size: 15px; line-height: 1.8; margin-bottom: 15px;">
                            <ul style="list-style-type: '📌 ';">
                                <li>ضع التطبيقات الأكثر إلهاءً داخل مجلد منفصل أو بعيدًا عن الشاشة الرئيسية لإضافة مقاومة قبل فتحها.</li>
                                <li>اعمل في فترات تركيز مدتها 25 إلى 45 دقيقة مع إبعاد الهاتف جسديًا عن المكتب.</li>
                                <li>أوقف التشغيل التلقائي وخصائص التمرير اللانهائي حيثما أمكن، لأنها تزيد الاستهلاك السلبي.</li>
                            </ul>
                        </div>
                        <div dir="ltr" style="text-align: left; color: #94A3B8; font-size: 14px; line-height: 1.6;">
                            <ul style="list-style-type: '📌 ';">
                                <li>Put the most distracting apps in a separate folder or off the home screen to add friction before opening them.</li>
                                <li>Work in 25- to 45-minute focus blocks with the phone physically away from the desk.</li>
                                <li>Turn off autoplay and infinite-scroll features where possible, because those design choices intensify passive consumption.</li>
                            </ul>
                        </div>
                    </div>
                    """,
                    2: """
                    <div dir="rtl" style="text-align: right; color: #E2E8F0; font-size: 15px; line-height: 1.8; margin-bottom: 15px;">
                        <h4 style="color: #FBBF24; margin-bottom: 5px;">🔹 الجزء المنخفض (حوالي 40–50% شدة)</h4>
                        هذه هي منطقة الانتقال من الاستخدام المتوسط إلى الاعتماد الأقوى. المستخدمون هنا يقضون عدة ساعات يوميًا في بيئات التمرير، ولم يعد الهاتف مجرد أداة، بل أصبح بيئة نشطة. النصف الأدنى من Class 2 ما يزال يُظهر بعض السيطرة، لكن المستخدم أصبح الآن معرضًا بما يكفي من التكرار والتجديد والتبديل ليصير الحفاظ على الانتباه المستمر أصعب. وغالبًا ما تكون هذه هي الفئة التي يبدأ فيها الشخص بملاحظة: “أفتح التطبيق دون تفكير”. وهذه إشارة تحذير مهمة في سلوك brainrot.
                        
                        <h4 style="color: #FBBF24; margin-top: 15px; margin-bottom: 5px;">🔸 الجزء المرتفع (حوالي 50–60% شدة)</h4>
                        يمثل هذا الجزء الحد الأعلى من النطاق المتوسط، وغالبًا ما يشير إلى بداية التعود القوي على التمرير. تطول الجلسات، ويرتفع وقت الشاشة بوضوح، ومن المرجح أن يحمل المستخدم عدة عادات تطبيقية في الوقت نفسه. وتُظهر الأبحاث الخاصة بإدمان الفيديو القصير وتعدد المهام الإعلامي أن هذه البيئات تكافئ التجديد السريع وقد تدرب الانتباه على التبديل السريع بدلًا من التركيز المستمر. هذا الجزء لم يصل بعد إلى الحد الأقصى، لكنه بات قريبًا من نقطة يصبح فيها الحمل الرقمي ظاهرًا في الإنتاجية اليومية.
                    </div>

                    <div dir="ltr" style="text-align: left; color: #94A3B8; font-size: 14px; line-height: 1.6; margin-bottom: 20px; padding: 15px; background: rgba(0,0,0,0.2); border-radius: 10px; border-left: 4px solid #FBBF24;">
                        <b>Low part (about 40–50% intensity):</b> This is the transition zone from moderate use to high dependency. Users here spend several hours a day in scrolling environments, and the phone is no longer just a tool; it is an active environment. The lower half of Class 2 still shows some control, but the user is now exposed to enough repetition, novelty, and switching to make sustained attention harder. This is often the band where people begin noticing “I keep opening the app without thinking.” That is an important warning sign in brainrot-style behavior.<br><br>
                        <b>High part (about 50–60% intensity):</b> This is the upper edge of the middle band and often marks the shift into stronger habitual scrolling. Sessions are longer, screen-on time is clearly elevated, and the user is likely carrying multiple app habits at once. Research on short-form video addiction and media multitasking is relevant here: these environments reward rapid novelty and can train attention toward fast switching rather than sustained focus. This segment is not yet extreme, but it is already close to the threshold where digital overload becomes visible in everyday productivity.
                    </div>

                    <div style="background: rgba(255,255,255,0.03); padding: 20px; border-radius: 12px; border: 1px solid rgba(251, 191, 36, 0.3);">
                        <h4 style="color: #F8FAFC; text-align: center; margin-bottom: 15px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 10px;">💡 التوصيات / Recommendations</h4>
                        <div dir="rtl" style="text-align: right; color: #CBD5E1; font-size: 15px; line-height: 1.8; margin-bottom: 15px;">
                            <ul style="list-style-type: '⚡ ';">
                                <li>اجعل هناك فترتين يوميتين ثابتتين لا يُستخدم فيهما الهاتف، خصوصًا قبل الدراسة وقبل النوم.</li>
                                <li>استخدم مراجعة أسبوعية للانتباه لتحديد التطبيقات التي تصنع أطول جلسات غير مفيدة.</li>
                                <li>استبدل التصفح السريع بنشاط واحد مقصود، مثل قراءة مقال واحد أو مشاهدة فيديو واحد مخطط له ثم التوقف.</li>
                            </ul>
                        </div>
                        <div dir="ltr" style="text-align: left; color: #94A3B8; font-size: 14px; line-height: 1.6;">
                            <ul style="list-style-type: '⚡ ';">
                                <li>Set two non-negotiable phone-free periods each day, especially before study and before sleep.</li>
                                <li>Use a weekly “attention audit” to identify which apps create the longest and least useful sessions.</li>
                                <li>Replace quick-feed browsing with a single-purpose activity, such as reading one article or watching one planned video, then stop.</li>
                            </ul>
                        </div>
                    </div>
                    """,
                    3: """
                    <div dir="rtl" style="text-align: right; color: #E2E8F0; font-size: 15px; line-height: 1.8; margin-bottom: 15px;">
                        <h4 style="color: #F97316; margin-bottom: 5px;">🔹 الجزء المنخفض (حوالي 60–70% شدة)</h4>
                        هذا الجزء بالفعل داخل منطقة الاستخدام الكثيف. يقضي المستخدم فترات طويلة على الهاتف، ومن المرجح أن يتضمن النمط تفقدًا متكررًا، وتبديلًا بين التطبيقات، واستهلاكًا كبيرًا للبيانات. وحتى النصف الأدنى من Class 3 يشير إلى عادة تمرير قوية جدًا. ومن منظور الانتباه، فهذا مهم لأن المستخدم لم يعد فقط معرضًا للتشتت، بل أصبح الجهاز نفسه هو المُنظم الافتراضي للملل والوقت الخالي والضغط. وهذه بيئة مهيأة بوضوح للإرهاق الرقمي.
                        
                        <h4 style="color: #F97316; margin-top: 15px; margin-bottom: 5px;">🔸 الجزء المرتفع (حوالي 70–80% شدة)</h4>
                        هذا يمثل ملف brainrot قويًا جدًا. فالمستخدم هنا قريب من أعلى نطاق القياسات، مع وقت شاشة متواصل طويل، واستهلاك كبير للبطارية، ونظام تطبيقات واسع، واستهلاك مرتفع للبيانات. وفي هذه المرحلة لا يكون القلق متعلقًا بالتشتت فقط، بل أيضًا بالحمل المعرفي: فقد يشعر الشخص بأن ذهنه ممتلئ، ومع ذلك يواصل التمرير. وتدعم الأبحاث المتعلقة بالتشبع الرقمي والتشتت الإعلامي فكرة أن هذا النمط قد يُسطّح الانتباه، ويزيد الإرهاق، وقلل جودة التركيز خارج الإنترنت.
                    </div>

                    <div dir="ltr" style="text-align: left; color: #94A3B8; font-size: 14px; line-height: 1.6; margin-bottom: 20px; padding: 15px; background: rgba(0,0,0,0.2); border-radius: 10px; border-left: 4px solid #F97316;">
                        <b>Low part (about 60–70% intensity):</b> This segment is already in the heavy-use zone. The user spends long periods on the phone, and the pattern is likely to include repeated checking, app switching, and significant data use. Even the lower half of Class 3 suggests a highly trained scrolling habit. From an attention perspective, this matters because the user is no longer just exposed to distraction; the device itself is becoming a default regulator of boredom, stress, and idle time. That is a classic setup for digital fatigue.<br><br>
                        <b>High part (about 70–80% intensity):</b> This is a very strong brainrot profile. The user is close to the upper end of the telemetry scale, with long continuous screen time, high battery drain, large app ecosystems, and heavy data use. At this point, the main concern is not just distraction but cognitive overload: the person may feel mentally full yet still keep scrolling. Research on brain rot, digital overload, and media saturation supports the idea that this pattern can flatten attention, increase fatigue, and reduce the quality of offline focus.
                    </div>

                    <div style="background: rgba(255,255,255,0.03); padding: 20px; border-radius: 12px; border: 1px solid rgba(249, 115, 22, 0.3);">
                        <h4 style="color: #F8FAFC; text-align: center; margin-bottom: 15px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 10px;">💡 التوصيات / Recommendations</h4>
                        <div dir="rtl" style="text-align: right; color: #CBD5E1; font-size: 15px; line-height: 1.8; margin-bottom: 15px;">
                            <ul style="list-style-type: '🛑 ';">
                                <li>استخدم حدودًا صارمة للتطبيقات أو قفل وضع التركيز أثناء ساعات الدراسة، وليس مجرد تذكيرات.</li>
                                <li>احذف تطبيقًا عالي التحفيز من الاستخدام اليومي لمدة أسبوع على الأقل لكسر الحلقات الآلية.</li>
                                <li>أنشئ روتينًا ثابتًا لإيقاف الهاتف ليلًا، لأن حماية النوم تصبح أساسية عندما يرتفع وقت الشاشة لهذا الحد.</li>
                            </ul>
                        </div>
                        <div dir="ltr" style="text-align: left; color: #94A3B8; font-size: 14px; line-height: 1.6;">
                            <ul style="list-style-type: '🛑 ';">
                                <li>Use hard app limits or focus-mode locks during study hours, not just reminders.</li>
                                <li>Remove one high-dopamine app from daily use for at least a week to break automatic loops.</li>
                                <li>Create a fixed nighttime shutdown routine, because sleep protection becomes essential when screen time is this high.</li>
                            </ul>
                        </div>
                    </div>
                    """,
                    4: """
                    <div dir="rtl" style="text-align: right; color: #E2E8F0; font-size: 15px; line-height: 1.8; margin-bottom: 15px;">
                        <h4 style="color: #F43F5E; margin-bottom: 5px;">🔹 الجزء المنخفض (حوالي 80–90% شدة)</h4>
                        هذا الجزء قريب جدًا من قمة المقياس، حتى قبل الوصول إلى الحد الأعلى الكامل. المستخدمون هنا يظهرون استخدامًا طويلًا جدًا للتطبيقات، ووقت شاشة كبيرًا جدًا، واستهلاكًا كثيفًا للبطارية والبيانات. وغالبًا ما يعكس النصف الأدنى من Class 4 مشاركة شبه مستمرة في بيئات التمرير، ولكن مع قدر كافٍ من التباين ليبقى دون الذروة المطلقة. عمليًا، يتحول الهاتف هنا من أداة إلى بيئة يومية مهيمنة. وهذه هي النقطة التي يصبح فيها تراجع الانتباه والإرهاق الرقمي صعبَي التجاهل.
                        
                        <h4 style="color: #F43F5E; margin-top: 15px; margin-bottom: 5px;">🔸 الجزء المرتفع (حوالي 90–100% شدة)</h4>
                        هذا هو أقوى ملف brainrot داخل نظامك. المستخدمون في هذه القمة غالبًا يقضون فترات طويلة جدًا على الإنترنت، ويستهلكون كميات ضخمة من المحتوى القصير أو سريع التغير، ويُظهرون أقوى علامات تشتت الانتباه والإرهاق الرقمي. وتشير البحوث حول تشتيت وسائل التواصل، والحمل الإعلامي الزائد، وعادات الفيديو القصير إلى أن هذا النمط يرتبط بانخفاض التركيز المستمر وبازدياد التفقد القهري. وفي العرض التقديمي، يمكن وصف هذه المنطقة بأنها “المنطقة الحمراء” التي تحتاج إلى تعافٍ فعلي، لا إلى نصائح خفيفة فقط.
                    </div>

                    <div dir="ltr" style="text-align: left; color: #94A3B8; font-size: 14px; line-height: 1.6; margin-bottom: 20px; padding: 15px; background: rgba(0,0,0,0.2); border-radius: 10px; border-left: 4px solid #F43F5E;">
                        <b>Low part (about 80–90% intensity):</b> This is already near the top of the model’s scale, even before you reach the very maximum. Users here show very long app usage, heavy screen-on time, large battery drain, and extensive data consumption. The lower half of Class 4 often reflects near-constant engagement with scrolling environments, but with just enough variability to remain below the absolute peak. In practical terms, the phone is operating as a dominant daily environment rather than a tool. That is the point where attention decline and digital burnout risk become difficult to ignore.<br><br>
                        <b>High part (about 90–100% intensity):</b> This is the most intense brainrot profile in your system. Users at the top end are likely spending very long continuous periods online, consuming large volumes of short-form or rapidly changing content, and showing the strongest signs of attention fragmentation and digital fatigue. Research on social-media distraction, media overload, and short-form video habits suggests that this pattern is closely tied to reduced sustained focus and stronger compulsive checking. In a presentation context, this is the “red zone” where the user needs active recovery, not just light advice.
                    </div>

                    <div style="background: rgba(255,255,255,0.03); padding: 20px; border-radius: 12px; border: 1px solid rgba(244, 63, 94, 0.4);">
                        <h4 style="color: #F8FAFC; text-align: center; margin-bottom: 15px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 10px;">💡 التوصيات / Recommendations</h4>
                        <div dir="rtl" style="text-align: right; color: #CBD5E1; font-size: 15px; line-height: 1.8; margin-bottom: 15px;">
                            <ul style="list-style-type: '🚨 ';">
                                <li>ابنِ جدولًا يوميًا صارمًا لاستخدام الجهاز مع فترات دراسة وفترات تعافٍ محددة ومقفلة؛ فالإرادة وحدها غالبًا لا تكفي هنا.</li>
                                <li>أضف محاسبة خارجية، مثل صديق أو فرد من العائلة أو تطبيق حجب يرسل تقارير يومية عن الاستخدام.</li>
                                <li>استبدل التمرير الليلي بروتين يحمي النوم، لأن قلة النوم نفسها تضعف الأداء المعرفي والانتباه.</li>
                            </ul>
                        </div>
                        <div dir="ltr" style="text-align: left; color: #94A3B8; font-size: 14px; line-height: 1.6;">
                            <ul style="list-style-type: '🚨 ';">
                                <li>Build a strict daily device schedule with locked study blocks and locked recovery blocks, because passive self-control is usually not enough here.</li>
                                <li>Add external accountability, such as a friend, family member, or app blocker that reports daily usage.</li>
                                <li>Replace late-night scrolling with sleep-protective routines, since sleep loss itself weakens cognitive functioning and focus.</li>
                            </ul>
                        </div>
                    </div>
                    """
                }

                app_report_text = APP_REPORTS.get(int(pred), "")
                if app_report_text:
                    st.markdown('<div class="metric-card" style="margin-top:20px;">', unsafe_allow_html=True)
                    st.markdown("<h3 style='color:#67E8F9; text-align:center; margin-bottom:20px;'>📄 Behavior Report / تقرير السلوك التفصيلي</h3>", unsafe_allow_html=True)
                    st.markdown(app_report_text, unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)


# ------------------------------------------------------------------
# Page 3: AI Assistant 🤖 (نظام الهجين الذكي - Smart Hybrid)
# ------------------------------------------------------------------
elif page == "AI Assistant 🤖":
    st.markdown("<h3 style='color: #A855F7 !important; font-weight: 700; animation: fadeInUp 0.6s ease-out forwards;'>🤖 Smart AI Assistant</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94A3B8 !important;'>اسألني عن النتائج، أو ارفع صورة للمخطط البياني وسأقوم بتحليله لك استناداً إلى أحدث تقنيات Gemini.</p>", unsafe_allow_html=True)

    # 1. محاولة جلب مفتاحك السري المخفي ليعمل الأبلكيشن تلقائياً
    try:
        dev_api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        dev_api_key = ""

    # 2. تهيئة مساحة لحفظ مفتاح المستخدم في حالة الطوارئ
    if "user_api_key" not in st.session_state:
        st.session_state.user_api_key = ""

    # 3. واجهة الطوارئ (تكون مغلقة بشكل افتراضي لعدم إزعاج المستخدمين)
    with st.expander("⚙️ الخادم مشغول؟ (أدخل مفتاحك الخاص لتجاوز الزحام)", expanded=False):
        st.markdown("""
        <p style='color:#CBD5E1; font-size:14px; line-height: 1.6;'>
        هذا التطبيق يوفر شات مجاني تماماً. ولكن في حال ظهور رسالة خطأ تخبرك بأن <b>الحد اليومي المسموح به قد انتهى</b> بسبب الضغط العالي، يمكنك وضع مفتاح Gemini API الخاص بك هنا لاستكمال محادثتك فوراً من خلال حسابك الخاص. <br>
        <a href='https://aistudio.google.com/app/apikey' target='_blank' style='color:#38BDF8;'>اضغط هنا للحصول على مفتاح مجاني في ثوانٍ.</a>
        </p>
        """, unsafe_allow_html=True)
        
        user_input_key = st.text_input("مفتاح API الاحتياطي (اختياري):", value=st.session_state.user_api_key, type="password")
        if user_input_key:
            st.session_state.user_api_key = user_input_key
            st.success("✅ تم تفعيل مفتاحك الخاص بنجاح! يمكنك الآن استخدام الشات.")

    # 4. اختيار المفتاح المستخدم: (لو المستخدم حط مفتاحه الخاص، هنستخدمه، لو لأ، هنستخدم مفتاحك السري)
    active_api_key = st.session_state.user_api_key if st.session_state.user_api_key else dev_api_key

    # التأكد من وجود مفتاح للعمل
    if not active_api_key:
        st.error("⚠️ لم يتم العثور على أي مفتاح API صالح. يرجى إعداد الـ Secrets أو إدخال مفتاحك الخاص ليعمل الشات.")
        st.stop()
    else:
        # إعداد الاتصال بالموديل
        genai.configure(api_key=active_api_key)

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

            # ==========================================
            # 🚀 تعليمات الموديل (System Prompt) المحدثة
            # ==========================================
            sys_instruct = """أنت مهندس بيانات ومساعد ذكي مدمج في منصة 'Vision Analytics'. وظيفتك تحليل البيانات والرد على استفسارات المستخدمين باحترافية وتقديم رؤى واضحة.
            يجب أن تفهم جيداً أن هذه المنصة تحتوي على نظامين منفصلين للذكاء الاصطناعي:
            1. نظام (Student Risk Analysis): مخصص للطلاب فقط. يتوقع احتمالية تعرض الطالب للخطر (مثل التسرب الدراسي أو الانهيار النفسي) بناءً على عوامل نفسية وبيئية. عندما يسألك طالب عن نتيجته، قدم له توصيات دراسية وأكاديمية ونفسية وروتين يساعده على تخطي الضغوط والنجاح.
            2. نظام (App Behavior Analysis): مخصص لأي مستخدم (ليس بالضرورة طالب). يحلل السلوك التقني لمستخدمي الهواتف الذكية. عندما يسألك المستخدم عن نتيجته، لا تكتفِ مطلقاً بنصائح تقنية جافة مثل "قلل استهلاك البطارية"، بل ركز بشدة على "صحة المستخدم"، وقدم له روتيناً يومياً أو نصائح لـ "الديتوكس الرقمي" (Digital Detox) لحمايته من أضرار الإفراط في استخدام الموبايل (مثل إجهاد العين، مشاكل النوم، أو الإدمان الرقمي).
            
            بناءً على هذا الفهم، قم بالإجابة على أسئلة المستخدم أو تحليل الصور التي يرفعها بدقة عالية، وقدم نصائح صحية وعملية ومباشرة لحل المشاكل التي تظهر في البيانات."""
            
            if 'last_analysis_context' in st.session_state:
                sys_instruct += f"\n\n[سياق مخفي هام جداً للإجابة]: أحدث نتيجة تحليل قام بها المستخدم للتو على المنصة هي: {st.session_state['last_analysis_context']}"

            # استخدام الموديل المستقر
            model = genai.GenerativeModel(
                model_name='gemini-flash-latest',
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
                        if "429" in str(e) or "Quota" in str(e):
                            st.error("⚠️ يبدو أن الضغط عالٍ جداً على خوادمنا المجانية في الوقت الحالي! لضمان استمرار خدمتك، يرجى فتح القائمة العلوية ⚙️ وإدخال مفتاح API الخاص بك لتتجاوز الزحام.")
                        else:
                            st.error(f"حدث خطأ أثناء معالجة الطلب. (الخطأ: {e})")
