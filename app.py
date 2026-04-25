import streamlit as st
import pandas as pd
import joblib
import numpy as np
import plotly.express as px
import warnings
import google.generativeai as genai
from PIL import Image
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
            sheet = db_client.open("Vision_Analytics_DB").worksheet(sheet_tab)
            sheet.append_row([datetime.now().strftime("%Y-%m-%d %H:%M:%S")] + row_data)
        except Exception:
            pass  

if "gemini_api_key" not in st.session_state:
    st.session_state.gemini_api_key = ""

# ==========================================
# 🎨 Premium UI/UX: Animations & Refined Glassmorphism
# ==========================================
st.markdown("""
<style>
    .stApp {
        background: radial-gradient(circle at 50% 0%, #1e1b4b 0%, #020617 100%) !important;
        background-attachment: fixed;
    }
    [data-testid="stHeader"] { background-color: transparent !important; }
    [data-testid="stHeader"] * { color: #F8FAFC !important; }

    h1, h2, h3, h4, label, p, li {
        color: #F8FAFC !important;
        font-family: 'Inter', 'Segoe UI', -apple-system, sans-serif;
        font-weight: 600 !important;
        letter-spacing: 0.2px;
    }

    .gradient-text {
        background: linear-gradient(135deg, #A855F7 0%, #38BDF8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900;
        font-size: 3.2rem;
        text-align: center;
        margin-top: -20px;
        letter-spacing: -1px;
        text-shadow: 0px 4px 20px rgba(168, 85, 247, 0.3); 
    }

    @keyframes fadeInUp {
        0% { opacity: 0; transform: translateY(30px); }
        100% { opacity: 1; transform: translateY(0); }
    }

    @keyframes pulseGlow {
        0% { box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.5); }
        70% { box-shadow: 0 0 0 12px rgba(59, 130, 246, 0); }
        100% { box-shadow: 0 0 0 0 rgba(59, 130, 246, 0); }
    }

    [data-testid="stForm"], .metric-card {
        background: rgba(15, 23, 42, 0.45) !important;
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 30px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.08);
        transition: transform 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275), box-shadow 0.4s ease;
        animation: fadeInUp 0.8s ease-out forwards;
    }
    
    [data-testid="stForm"]:hover, .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.15);
    }

    div[data-baseweb="select"] > div, div[data-baseweb="base-input"] > input {
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
    
    div[data-baseweb="select"] *, div[data-baseweb="base-input"] * {
        color: #0F172A !important;
    }

    div[data-baseweb="select"] > div:hover, div[data-baseweb="base-input"] > input:hover {
        border: 2px solid rgba(56, 189, 248, 0.5) !important;
        transform: scale(1.01);
    }

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
    ul[data-baseweb="menu"] li { padding: 10px 15px !important; }

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

    div[data-testid="stFormSubmitButton"] > button, [data-testid="baseButton-secondary"] {
        background: linear-gradient(135deg, #06B6D4 0%, #3B82F6 100%) !important;
        border: none !important;
        padding: 16px 24px !important;
        border-radius: 12px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        animation: pulseGlow 2.5s infinite;
    }
    div[data-testid="stFormSubmitButton"] > button *, [data-testid="baseButton-secondary"] * {
        color: #0F172A !important; 
        -webkit-text-fill-color: #0F172A !important;
        font-weight: 900 !important; 
        font-size: 16px !important;
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    div[data-testid="stFormSubmitButton"] > button:hover, [data-testid="baseButton-secondary"]:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 15px 30px -5px rgba(59, 130, 246, 0.6) !important;
        animation: none;
    }

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
    
    .script-text { line-height: 1.8; font-size: 15px; margin-bottom: 15px; }
    .script-title { font-size: 20px; font-weight: 800; margin-bottom: 15px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 10px;}
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

            st.session_state['last_analysis_context'] = f"قام المستخدم للتو بتحليل (Student Risk Analysis). النتيجة هي: مستوى خطر {final_label}."
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

        # ==========================================
        # 📝 إسكريبت تقييم الطلاب كاملاً من الورد
        # ==========================================
        student_scripts = {
            'Low': """
            <div dir="rtl" style="text-align: right;" class="script-text">
                <div class="script-title" style="color:#34D399;">مستوى الخطر المنخفض | Low Risk Level</div>
                <p><b>التحليل:</b><br>
                يشير مستوى الخطر المنخفض إلى أنك تتنقل في بيئتك الأكاديمية بنجاح مع توازن عقلي وعاطفي ممتاز. من المحتمل أنك تبلغ عن أنماط نوم صحية، وعبء عمل أكاديمي يمكن إدارته، ومزاج متفائل بشكل عام. نظراً لأن مستويات التوتر والقلق لديك مستقرة، تظل وظائفك المعرفية حادة، مما يسمح بأداء أكاديمي عالٍ. أنت تستفيد بشكل كبير من أنظمة الدعم الاجتماعي القوية وآليات التكيف الصحية، مما يضمن عدم تحول الضغوط العرضية إلى احتراق. أنت تنظر إلى دراستك كتمثيل لتحدٍ إيجابي وليس كعبء ساحق. تحميك هذه الحالة المرنة بقوة ضد الاحتراق الرقمي، مما يعني أنه يمكنك استخدام التكنولوجيا للتعلم دون الوقوع في فخ التمرير اللانهائي أو استخدام وسائل التواصل الاجتماعي للهروب من الواقع الأكاديمي.</p>
                
                <p><b>التوصيات:</b></p>
                <ul>
                    <li><b>الحفاظ على عادات نوم صحية ومتسقة:</b> استمر في إعطاء الأولوية للنوم من 7 إلى 9 ساعات. الراحة عالية الجودة هي الركيزة الأساسية لنجاحك الأكاديمي الحالي وتنظيمك العاطفي الممتاز.</li>
                    <li><b>التوجيه ودعم الأقران:</b> نظراً لأن لديك دعماً اجتماعياً قوياً، فكر في توجيه الآخرين. إن تعليم الأقران لا يعزز معرفتك فحسب، بل يعمق أيضاً روابطك الاجتماعية القيمة.</li>
                    <li><b>إدارة الوقت الاستباقية:</b> استمر في استخدام المخططات أو التقويمات الرقمية لجدولة مهامك مسبقاً. البقاء متقدماً على المواعيد النهائية يضمن بقاء عبء العمل قابلاً للإدارة وبقاء التوتر منخفضاً بشكل ملحوظ.</li>
                </ul>
            </div>
            <div dir="ltr" style="text-align: left; margin-top:20px; border-top: 1px dashed rgba(255,255,255,0.2); padding-top:15px;" class="script-text">
                <p>A Low Risk Level indicates that you are successfully navigating your academic environment with excellent mental and emotional balance. You likely report healthy sleep patterns, a manageable academic workload, and a generally optimistic mood. Because your stress and anxiety levels are stable, your cognitive functions remain sharp, allowing for high academic performance. You benefit greatly from strong social support systems and healthy coping mechanisms, ensuring that occasional pressures do not escalate into burnout. You view your studies as a positive challenge rather than an overwhelming burden. This resilient state strongly protects you against digital burnout, meaning you can utilize technology for learning without falling into the trap of endless scrolling or using social media to escape academic reality.</p>
                <b>Recommendations:</b>
                <ul>
                    <li><b>Maintain Consistent Sleep Hygiene:</b> Continue prioritizing your 7 to 9 hours of sleep. High-quality rest is the foundational pillar of your current academic success and excellent emotional regulation.</li>
                    <li><b>Mentorship and Peer Support:</b> Since you have strong social support, consider mentoring others. Teaching peers not only reinforces your own knowledge but also deepens your valuable social connections.</li>
                    <li><b>Proactive Time Management:</b> Keep using planners or digital calendars to schedule your tasks in advance. Staying ahead of deadlines ensures your workload remains manageable and your stress stays remarkably low.</li>
                </ul>
            </div>
            """,
            'Medium': """
            <div dir="rtl" style="text-align: right;" class="script-text">
                <div class="script-title" style="color:#FBBF24;">مستوى الخطر المتوسط | Medium Risk Level</div>
                <p><b>التحليل:</b><br>
                يشير مستوى الخطر المتوسط إلى أنك تتأرجح على حافة الإرهاق الأكاديمي. أنت تعاني من ارتفاع التوتر، والحزن العرضي، والقلق الخفيف. قد يكون نومك غير كافٍ، حيث يتقلب بين 4 إلى 6 ساعات، مما يعيق بشكل مباشر قدرة دماغك على التعافي. يتزايد الضغط الأكاديمي، مما يجعل الشعور بعبء العمل أكثر صعوبة في الإدارة. في هذه المرحلة، أنت معرض بشدة لاستخدام الوسائط الرقمية كآلية للتكيف. قد تجد نفسك تقوم بالتمرير بشكل سلبي لتجنب التفكير في الاختبارات القادمة، مبدلاً دون قصد الراحة المجددة للنشاط بالتشتت الرقمي. يخلق هذا حلقة مفرغة خطيرة حيث يؤدي ضعف النوم والاحتراق الخفيف إلى مزيد من وقت الشاشة، والذي بدوره يقلل من دافعك العام وتركيزك اليومي.</p>

                <p><b>التوصيات:</b></p>
                <ul>
                    <li><b>إنشاء روتين للاسترخاء:</b> استبدل الدراسة أو التمرير في وقت متأخر من الليل بروتين مهدئ قبل النوم. قراءة كتاب أو ممارسة التنفس العميق يساعد على نقل دماغك من الضغط الأكاديمي العالي إلى النوم المجدد للنشاط.</li>
                    <li><b>تقسيم المهام إلى خطوات صغيرة:</b> تؤدي أعباء العمل المرهقة إلى سلوكيات التجنب مثل التمرير الكارثي. قم بتقسيم مهامك إلى مهام صغيرة مدتها 15 دقيقة لبناء الزخم وتقليل القلق المرتبط بالمشاريع الكبيرة.</li>
                    <li><b>جدولة "وقت للقلق":</b> خصص 20 دقيقة يومياً تحديداً لتدوين مخاوفك الأكاديمية. احتواء توترك في نافذة زمنية محددة يمنعه من التسرب إلى وقت استرخائك ونومك.</li>
                    <li><b>الاستفادة من موارد الحرم الجامعي:</b> لا تنتظر حتى يتم إرهاقك تماماً. شكل مجموعة دراسية أو قم بزيارة مركز الدعم الأكاديمي بجامعتك لتوزيع الضغط بشكل خفيف وتحسين شبكة الدعم الاجتماعي الخاصة بك.</li>
                </ul>
            </div>
            <div dir="ltr" style="text-align: left; margin-top:20px; border-top: 1px dashed rgba(255,255,255,0.2); padding-top:15px;" class="script-text">
                <p>A Medium Risk Level suggests you are balancing on the edge of academic fatigue. You are experiencing elevated stress, occasional sadness, and mild anxiety. Your sleep might be insufficient, fluctuating between 4 to 6 hours, which directly hampers your brain's ability to recover. The academic pressure is building, making your workload feel increasingly difficult to manage. At this stage, you are highly vulnerable to using digital media as a coping mechanism. You might find yourself passively scrolling to avoid thinking about upcoming exams, unintentionally trading restorative rest for digital distraction. This creates a dangerous feedback loop where poor sleep and mild burnout lead to more screen time, which in turn further decreases your overall motivation and daily focus.</p>
                <b>Recommendations:</b>
                <ul>
                    <li><b>Establish a Wind-Down Routine:</b> Swap late-night studying or scrolling for a calming pre-sleep routine. Reading a book or practicing deep breathing helps transition your brain from high academic stress to restorative sleep.</li>
                    <li><b>Break Tasks into Micro-Steps:</b> Overwhelming workloads trigger avoidance behaviors like doomscrolling. Break your assignments into tiny, 15-minute tasks to build momentum and reduce the anxiety associated with large projects.</li>
                    <li><b>Schedule "Worry Time":</b> Allocate 20 minutes a day specifically to write down your academic anxieties. Containing your stress to a specific window prevents it from bleeding into your relaxation and sleep time.</li>
                    <li><b>Leverage Campus Resources:</b> Don't wait until you are fully overwhelmed. Form a study group or visit your university's academic support center to lightly distribute the pressure and improve your social support network.</li>
                </ul>
            </div>
            """,
            'High': """
            <div dir="rtl" style="text-align: right;" class="script-text">
                <div class="script-title" style="color:#F43F5E;">مستوى الخطر المرتفع | High Risk Level</div>
                <p><b>التحليل:</b><br>
                مستوى الخطر المرتفع هو علامة تحذير حاسمة من الاحتراق الأكاديمي والرقمي الشديد. من المحتمل أنك تعاني من ضغط شديد، وحالات مزاجية منخفضة متكررة، وقلق حاد. نومك إما محروم بشدة أو مفرط كاستجابة للإرهاق. مع الضغط الأكاديمي الساحق والدعم الاجتماعي المحدود، أنت تعمل بالكامل في وضع "البقاء على قيد الحياة". في هذا المستوى، يكون احتمال الاستخدام الإشكالي لوسائل التواصل الاجتماعي مرتفعاً بشكل لا يصدق. قد تستخدم المحتوى اللانهائي للانفصال تماماً عن الضغط الشديد لحياتك اليومية. يضعف هذا الإرهاق الشديد ذاكرتك، ويسحق وظائفك التنفيذية، ويدمر أداءك الأكاديمي. دماغك مثقل بشكل كبير، ويتطلب تدخلاً فورياً ورحيماً لاستعادة رفاهيتك الجسدية والعقلية.</p>

                <p><b>التوصيات:</b></p>
                <ul>
                    <li><b>إعطاء الأولوية للراحة فوق كل شيء:</b> النجاح الأكاديمي مستحيل دون الأداء المعرفي. يجب عليك على الفور إعطاء الأولوية للحصول على ما لا يقل عن 7 ساعات من النوم، حتى لو كان ذلك يعني طلب تمديد لمهامك الحالية.</li>
                    <li><b>طلب الاستشارة المهنية:</b> يتطلب الاحتراق عالي المستوى تدخلاً مهنياً. تواصل مع خدمات الصحة النفسية في جامعتك على الفور لوضع خطة منظمة وواقعية لإدارة قلقك الشديد.</li>
                    <li><b>التواصل مع الأساتذة:</b> لا تخفِ معاناتك. تواصل بصراحة حول إرهاقك مع أساتذتك أو مرشديك الأكاديميين. يميل معظم أعضاء هيئة التدريس إلى تقديم تسهيلات عندما يدركون أنك في أزمة.</li>
                    <li><b>الانفصال الرقمي الجذري:</b> نظراً لأن الشاشات من المحتمل أن تغذي انفصالك عن الواقع، قم بتنفيذ التخلص من السموم الرقمية بصرامة. استخدم أدوات حظر مواقع الويب على الكمبيوتر المحمول الخاص بك لتقييد وصولك إلى الإنترنت بشكل صارم على البوابات الأكاديمية الأساسية فقط.</li>
                </ul>
            </div>
            <div dir="ltr" style="text-align: left; margin-top:20px; border-top: 1px dashed rgba(255,255,255,0.2); padding-top:15px;" class="script-text">
                <p>A High Risk Level is a critical warning sign of severe academic and digital burnout. You are likely enduring extreme stress, frequent low moods, and severe anxiety. Your sleep is either severely deprived or excessive as an exhaustion response. With overwhelming academic pressure and limited social support, you are functioning entirely in survival mode. In this tier, the likelihood of problematic social media use is incredibly high. You may be using endless content to completely dissociate from the intense pressure of your daily life. This severe exhaustion impairs your memory, crushes your executive functioning, and ruins your academic performance. Your brain is drastically overloaded, requiring an immediate and compassionate intervention to restore your physical and mental well-being.</p>
                <b>Recommendations:</b>
                <ul>
                    <li><b>Prioritize Rest Above All:</b> Academic success is impossible without cognitive functioning. You must immediately prioritize getting at least 7 hours of sleep, even if it means requesting extensions on your current assignments.</li>
                    <li><b>Seek Professional Counseling:</b> High-level burnout requires professional intervention. Reach out to your university's mental health services immediately to develop a structured, realistic plan for managing your severe anxiety.</li>
                    <li><b>Communicate with Professors:</b> Do not hide your struggle. Openly communicate your burnout to your professors or academic advisors. Most faculty members are willing to offer accommodations when they understand you are in crisis.</li>
                    <li><b>Radical Digital Disconnect:</b> Since screens are likely fueling your dissociation, implement a strict digital detox. Use website blockers on your laptop to strictly limit your internet access to only essential academic portals.</li>
                </ul>
            </div>
            """
        }

        risk_key = 'High' if 'High' in final_label else 'Medium' if 'Medium' in final_label else 'Low'
        st.markdown(f'''<div class="metric-card" style="margin-top: 25px;">{student_scripts.get(risk_key, "")}</div>''', unsafe_allow_html=True)

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
            * **Data Usage:** Go to **Settings > Cellular**.
            """)
        st.markdown("<hr style='border-color: rgba(255,255,255,0.1); margin: 15px 0;'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color:#A855F7; margin-bottom:5px;'>🔋 How to calculate Battery Drain (mAh)?</h4>", unsafe_allow_html=True)
        st.markdown("""
        > **` (Percentage Used ÷ 100) × Total Battery Capacity (mAh) `**<br>
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
                    st.error(f"⚠️ خطأ في توافق البيانات: {e2}")
            
            if success:
                st.session_state['last_analysis_context'] = f"قام المستخدم للتو بتحليل (App Behavior Analysis). النتيجة هي: المستخدم ينتمي للفئة (Class {int(pred)})."
                log_data("Apps", [age, gender, num_apps, screen_time, battery, data_usage, app_usage, int(pred)])

                st.markdown(f"""
                    <div class="metric-card" style="text-align: center; margin-top:25px;">
                        <h3 style='color:#CBD5E1 !important;'>Predicted Class</h3>
                        <h1 style='color:#22D3EE !important; font-size:3.5rem; font-weight:900;'>{int(pred)}</h1>
                    </div>
                """, unsafe_allow_html=True)

                # ==========================================
                # 📝 إسكريبت تقييم التطبيقات كاملاً (مُصنف لـ 0,1,2,3,4)
                # ==========================================
                app_scripts = {
                    0: """
                    <div dir="rtl" style="text-align: right;" class="script-text">
                        <div class="script-title" style="color:#34D399;">الفئة (النتيجة 0): توافق Class 1 (الخطر الأدنى - Minimal Risk)</div>
                        <p><b>الجزء المنخفض (المنفعة الوظيفية):</b><br>
                        في هذا الجزء، تُظهر علاقة واعية ومقصودة جداً مع جهازك، حيث تستخدمه بشكل أساسي للتواصل الضروري، والتعلم، والأدوات المهمة. تكاد تكون "نسبة تعفن الدماغ" (Brainrot Percentage) معدومة (0% - 5%). وقت استخدامك للتطبيقات منخفض، واستهلاك البطارية يعكس تفاعلاً ضئيلاً. أنت تنظر إلى التكنولوجيا كمساعد مفيد وليس كفخ. ولأن مسارات الدوبامين لديك لا يتم التلاعب بها، فإن مدى انتباهك يظل حاداً، ولا يوجد إرهاق رقمي. يمثل هذا المعيار الذهبي للرفاهية الرقمية.</p>

                        <p><b>الجزء المرتفع (الترفيه العرضي):</b><br>
                        لا تزال تحتفظ بسيطرة ممتازة، لكنك تنغمس أحياناً في فترات قصيرة من الترفيه الرقمي (نسبة تعفن الدماغ 6% - 15%). نادراً ما تفقد الإحساس بالوقت، مما يوضح أنه يمكنك الاستمتاع بأمان بالعالم الرقمي دون التدخل في مسؤولياتك. وظائفك الإدراكية والتنظيم العاطفي تظل سليمة تماماً.</p>

                        <p><b>التوصيات:</b></p>
                        <ul>
                            <li><b>الحفاظ على مناطق خالية من التكنولوجيا:</b> اجعل غرفة نومك خالية تماماً من الشاشات لحماية جودة نومك العالية وتجنب التمرير الليلي.</li>
                            <li><b>فحص الجهاز المجدول:</b> استمر في التحقق من تطبيقاتك في أوقات محددة بدلاً من الاستجابة لكل إشعار للحفاظ على تركيزك الممتاز.</li>
                            <li><b>تبني الهوايات التناظرية:</b> خصص وقتاً لقراءة الكتب الورقية أو ممارسة الرياضات الخارجية لتعزيز مدى انتباهك القوي.</li>
                        </ul>
                    </div>
                    <div dir="ltr" style="text-align: left; margin-top:20px; border-top: 1px dashed rgba(255,255,255,0.2); padding-top:15px;" class="script-text">
                        <p><b>Low Part (Functional Utility):</b><br>
                        You exhibit a highly intentional relationship with your device, utilizing it for essential communication, learning, and necessary tools. Brainrot Percentage is non-existent (0%-5%). Your app usage and battery drain reflect minimal engagement with algorithms. You view technology as a helpful assistant. Dopamine pathways aren't hijacked, attention remains sharp, and digital fatigue is absent. This is the gold standard of digital well-being.</p>
                        
                        <p><b>High Part (Casual Entertainment):</b><br>
                        You maintain excellent control, indulging occasionally in short bursts of digital entertainment (6%-15%). You rarely lose track of time, safely enjoying the digital world without interfering with responsibilities. Cognitive functions and emotional regulation remain completely intact.</p>

                        <p><b>Recommendations:</b></p>
                        <ul>
                            <li><b>Maintain Tech-Free Zones:</b> Keep your bedroom screen-free to protect sleep.</li>
                            <li><b>Scheduled Device Checks:</b> Check apps at designated times rather than responding to every notification.</li>
                            <li><b>Embrace Analog Hobbies:</b> Dedicate time to reading physical books or outdoor sports.</li>
                        </ul>
                    </div>
                    """,
                    1: """
                    <div dir="rtl" style="text-align: right;" class="script-text">
                        <div class="script-title" style="color:#6EE7B7;">الفئة (النتيجة 1): توافق Class 2 (عادة ناشئة - Emerging Habit)</div>
                        <p><b>الجزء المنخفض (وقت الفراغ السلبي):</b><br>
                        تعكس عاداتك الرقمية وقت فراغ سلبي وعرضي (نسبة تعفن الدماغ 16% - 25%). تستخدم التطبيقات بشكل متكرر للاسترخاء بعد يوم طويل، وتسمح للخوارزميات بتوجيهك لفترات قصيرة. وقت الشاشة واستخدام البيانات مرتفعان بشكل معتدل. قد تلاحظ أحياناً ممانعة طفيفة لترك الهاتف. إنها مرحلة انتقالية تتشكل فيها العادات الرقمية، لكنها لم تتسبب بعد في تشتت ملحوظ.</p>

                        <p><b>الجزء المرتفع (التمرير المشتت):</b><br>
                        تظهر العلامات الحقيقية الأولى للتشتت الرقمي (26% - 35%). تظهر زيادة في استهلاك البطارية والتبديل المتكرر بين التطبيقات. غالباً ما تلتقط هاتفك لسبب معين، لتجد نفسك تقوم بالتمرير بلا هدف. بدأت الخوارزميات في التقاط انتباهك. قد تعاني من إرهاق عقلي خفيف، والدماغ يكيف نفسه ببطء لاشتهاء جرعات متكررة من الدوبامين.</p>

                        <p><b>التوصيات:</b></p>
                        <ul>
                            <li><b>قاعدة الـ 30 دقيقة:</b> قصر جلسات التمرير على 30 دقيقة يومياً. تظهر الدراسات أن تقييد وسائل التواصل يحسن الحالة المزاجية بشكل كبير ويقلل من القلق.</li>
                            <li><b>إيقاف الإشعارات غير الضرورية:</b> قم بتعطيل التنبيهات لتطبيقات التواصل الاجتماعي لاستعادة السيطرة على انتباهك.</li>
                            <li><b>الاستخدام المقصود للتطبيقات:</b> قبل فتح أي تطبيق، اذكر بصوت عالٍ الغرض من ذلك. إذا لم تتمكن من التحديد، فضع الهاتف جانباً لكسر التحقق الطائش.</li>
                        </ul>
                    </div>
                    <div dir="ltr" style="text-align: left; margin-top:20px; border-top: 1px dashed rgba(255,255,255,0.2); padding-top:15px;" class="script-text">
                        <p><b>Low Part (Passive Leisure):</b><br>
                        Digital habits reflect casual, passive leisure (Brainrot 16%-25%). You frequently use apps for relaxation, letting algorithms guide you. Screen time is moderately elevated. Your brain receives constant low-level stimulation. It's a transitional phase forming digital habits without severe disruption yet.</p>
                        
                        <p><b>High Part (Distracted Scrolling):</b><br>
                        First real signs of digital distraction (26%-35%). Increased battery drain and frequent app switching. You often scroll aimlessly. Social media algorithms are successfully holding your attention. Mild mental fatigue occurs as constant novelty conditions your brain for dopamine hits.</p>

                        <p><b>Recommendations:</b></p>
                        <ul>
                            <li><b>The 30-Minute Rule:</b> Limit scrolling sessions to 30 minutes daily to improve mood.</li>
                            <li><b>Turn Off Non-Essential Notifications:</b> Disable push alerts for social apps to regain attention control.</li>
                            <li><b>Intentional App Usage:</b> Before opening an app, verbally state your purpose. If you cannot, put the phone down.</li>
                        </ul>
                    </div>
                    """,
                    2: """
                    <div dir="rtl" style="text-align: right;" class="script-text">
                        <div class="script-title" style="color:#FBBF24;">الفئة (النتيجة 2): توافق Class 3 (خطر متوسط - Moderate Risk)</div>
                        <p><b>الجزء المنخفض (الاستهلاك الروتيني):</b><br>
                        يتحول تفاعلك الرقمي إلى استهلاك روتيني (36% - 45%). وقت الشاشة مرتفع، وأصبح التمرير اللانهائي عادة يومية. تعتمد على المحتوى السريع لتهدئة نفسك. دماغك في حالة تأهب دائم مما يمنع التعافي. المهام الأطول (كالدراسة أو القراءة) تبدو محبطة ومملة بشكل غير عادي. بداية مرحلة "تشتت الانتباه".</p>

                        <p><b>الجزء المرتفع (تشتت الانتباه):</b><br>
                        العبء الرقمي الزائد يصبح واضحاً (46% - 60%). انجذاب قوي نحو "التمرير الكارثي" (Doomscrolling). مهام متعددة وانتقال سريع بين المنصات. أنت تعاني من "الضباب العقلي" (Brainrot). المعلومات المجزأة تثقل الذاكرة العاملة وتقلل التفكير النقدي. انخفض مدى الانتباه بشكل واضح، مما يجعل العمل المركز صراعاً.</p>

                        <p><b>التوصيات:</b></p>
                        <ul>
                            <li><b>تنفيذ 'فترات راحة للتمرير':</b> قم بجدولة فترات راحة 10 دقائق أثناء الدراسة ثم العودة فوراً للعمل.</li>
                            <li><b>تنظيم المحتوى الخاص بك:</b> إلغاء متابعة الحسابات الطائشة واستبدالها بصناع محتوى تعليميين ومفيدين.</li>
                            <li><b>ممارسة تقنية بومودورو:</b> 25 دقيقة تركيز تليها 5 دقائق استراحة بدون تكنولوجيا.</li>
                            <li><b>التخلص من السموم الرقمية الصباحية:</b> تجنب الهاتف في الساعة الأولى بعد الاستيقاظ لمنع ارتفاع الدوبامين الفوري.</li>
                        </ul>
                    </div>
                    <div dir="ltr" style="text-align: left; margin-top:20px; border-top: 1px dashed rgba(255,255,255,0.2); padding-top:15px;" class="script-text">
                        <p><b>Low Part (Routine Consumption):</b><br>
                        Engagement shifts to routine consumption (Brainrot 36%-45%). Endless scrolling is a daily habit. You rely on fast-paced content to self-soothe. Your brain is kept alert, preventing mental recovery. Longer tasks feel unusually frustrating or boring. This marks the beginning of "attention fragmentation."</p>

                        <p><b>High Part (Attention Fragmentation):</b><br>
                        Digital overload becomes apparent (46%-60%). Strong pull toward doomscrolling. Frequent multitasking across platforms causes "mental fog" (brain rot). Bite-sized information overloads working memory, decreasing critical thinking. Sustained attention has visibly declined.</p>

                        <p><b>Recommendations:</b></p>
                        <ul>
                            <li><b>Implement 'Scroll Breaks':</b> Schedule 10-minute scroll breaks, then return to task immediately.</li>
                            <li><b>Curate Your Feeds:</b> Unfollow mindless entertainment and replace with educational creators.</li>
                            <li><b>Practice the Pomodoro Technique:</b> 25-minute work intervals followed by a 5-minute tech-free break.</li>
                            <li><b>Morning Digital Detox:</b> Avoid your phone for the first hour after waking up.</li>
                        </ul>
                    </div>
                    """,
                    3: """
                    <div dir="rtl" style="text-align: right;" class="script-text">
                        <div class="script-title" style="color:#F87171;">الفئة (النتيجة 3): توافق Class 4 (خطر مرتفع - High Risk)</div>
                        <p><b>الجزء المنخفض (التمرير الكارثي القهري):</b><br>
                        تحول من العادة إلى السلوك القهري (61% - 75%). وقت شاشة طويل جداً واستنزاف كبير للبطارية ليلاً. أنت تقوم بالتمرير لأنك مضطر لذلك. يؤثر هذا بشدة على جودة نومك (تأخير الميلاتونين وتشتت النوم العميق). الضجيج الرقمي يؤدي إلى تآكل التنظيم العاطفي وزيادة التوتر.</p>

                        <p><b>الجزء المرتفع (الإرهاق المعرفي):</b><br>
                        إرهاق معرفي شديد (76% - 85%). استهلاك هائل للبيانات واعتماد شبه كلي على التحفيز. المحتوى القصير أعاد برمجة مسارات المكافأة (انخفاض كبير في مدى الانتباه). التعلم التقليدي شبه مستحيل. حالة مزمنة من التشتت والقلق وانسحاب من الهوايات الواقعية. أنت على حافة الاحتراق الرقمي الكامل.</p>

                        <p><b>التوصيات:</b></p>
                        <ul>
                            <li><b>وضع حدود صارمة للتطبيقات:</b> استخدم أدوات الرفاهية الرقمية لقفل التطبيقات بعد وقت محدد (حاجز مادي).</li>
                            <li><b>صيام الدوبامين:</b> خصص يوماً كاملاً في الأسبوع لتكون خاليًا تماماً من الشاشات لإعادة ضبط الدماغ.</li>
                            <li><b>الوضع الرمادي (Grayscale Mode):</b> تغيير إعدادات العرض للأبيض والأسود لجعل الشاشة أقل جاذبية للمخ.</li>
                            <li><b>إعادة تقديم الوسائط الطويلة:</b> أجبر نفسك على مشاهدة فيديوهات طويلة أو قراءة مقالات دون القيام بمهام متعددة.</li>
                        </ul>
                    </div>
                    <div dir="ltr" style="text-align: left; margin-top:20px; border-top: 1px dashed rgba(255,255,255,0.2); padding-top:15px;" class="script-text">
                        <p><b>Low Part (Compulsive Doomscrolling):</b><br>
                        A shift from habit to compulsion (Brainrot 61%-75%). Extensive screen-on time late into the night. You scroll because you feel you have to. Severely impacts sleep quality, delaying melatonin and fragmenting deep sleep. Constant digital noise aggressively erodes emotional regulation.</p>
                        
                        <p><b>High Part (Cognitive Fatigue):</b><br>
                        Intense cognitive fatigue (76%-85%). Massive daily data consumption. Short-form content has severely rewired reward pathways, causing significant attention span decline. Long-form reading feels impossible. Persistent overstimulation leads to a chronic state of distraction, draining mental energy.</p>

                        <p><b>Recommendations:</b></p>
                        <ul>
                            <li><b>Set Hard App Limits:</b> Use digital wellbeing tools to lock apps after a time limit.</li>
                            <li><b>Dopamine Fasting:</b> Dedicate one day a week to be completely screen-free.</li>
                            <li><b>Grayscale Mode:</b> Change display to black and white to naturally reduce compulsive doomscrolling urges.</li>
                            <li><b>Reintroduce Long-Form Media:</b> Force yourself to watch longer videos or read articles without multitasking.</li>
                        </ul>
                    </div>
                    """,
                    4: """
                    <div dir="rtl" style="text-align: right;" class="script-text">
                        <div class="script-title" style="color:#EF4444;">الفئة (النتيجة 4): توافق Class 5 (خطر شديد جداً - Severe Risk)</div>
                        <p><b>الجزء المنخفض (الاحتراق الرقمي):</b><br>
                        لقد وصلت إلى الاحتراق الرقمي الفعلي (86% - 95%). إفراط شديد في جميع المجالات وآلية تكيف لا هوادة فيها. التبديل المستمر أضعف الوظائف التنفيذية. ضباب عقلي مزمن، خمول شديد، وشعور بالخدر العاطفي. تفاعلات الحياة الواقعية تبدو مملة للغاية، مما يؤدي لعزلة اجتماعية عميقة.</p>

                        <p><b>الجزء المرتفع (التبلد الحسي الكامل):</b><br>
                        أشد مستويات العبء الرقمي الزائد (96% - 100%). إدمان يستهلك كل شيء. تقضي جميع ساعات استيقاظك متصلاً، مما يؤدي لحمل إدراكي زائد كامل وتبلد حسي للحياة. تغييرات هيكلية في معالجة المعلومات والمتعة. انتباه محطم، إجهاد عين، أرق حاد. يتطلب تغييرات جذرية وفورية.</p>

                        <p><b>التوصيات:</b></p>
                        <ul>
                            <li><b>طلب الدعم المهني:</b> استشارة مستشار أو معالج متخصص في الإدمان الرقمي لعلاج الأسباب الكامنة.</li>
                            <li><b>حذف التطبيقات عالية الخطورة:</b> إزالة تطبيقات التمرير اللانهائي تماماً وإجبار النفس على المتصفح للضرورة.</li>
                            <li><b>أمسيات إلزامية خالية من الشاشات:</b> منع الشاشات قبل ساعتين من النوم واستبدالها بالتمدد وتدوين اليوميات.</li>
                            <li><b>إعادة بناء روابط العالم الحقيقي:</b> جدولة لقاءات جسدية مع الأصدقاء لعكس العزلة العميقة.</li>
                            <li><b>التدخل بالنشاط البدني:</b> 30 دقيقة تمارين يومياً لزيادة تدفق الدم وإصلاح الوظائف الإدراكية.</li>
                        </ul>
                    </div>
                    <div dir="ltr" style="text-align: left; margin-top:20px; border-top: 1px dashed rgba(255,255,255,0.2); padding-top:15px;" class="script-text">
                        <p><b>Low Part (Digital Burnout):</b><br>
                        You have hit actual digital burnout (Brainrot 86%-95%). Chronically online, using digital media as a relentless coping mechanism. Constant task switching has severely impaired executive functioning. Chronic brain fog, extreme lethargy, emotional numbness. Real-life interactions feel incredibly dull, leading to deep social isolation.</p>
                        
                        <p><b>High Part (Complete Desensitization):</b><br>
                        Most severe level of digital overload (96%-100%). All-consuming digital addiction causing complete cognitive overload and profound desensitization. Extreme structural changes to brain processing. Sustained attention is entirely shattered. Physical symptoms include severe eye strain and insomnia. Immediate drastic lifestyle changes required.</p>

                        <p><b>Recommendations:</b></p>
                        <ul>
                            <li><b>Seek Professional Support:</b> Consult a therapist specializing in digital addiction.</li>
                            <li><b>Delete High-Risk Apps:</b> Completely remove apps causing endless scrolling loops.</li>
                            <li><b>Mandatory Screen-Free Evenings:</b> Enforce a strict no-screens rule two hours before bedtime.</li>
                            <li><b>Rebuild Real-World Connections:</b> Actively schedule face-to-face meetups to reverse deep isolation.</li>
                            <li><b>Physical Activity Intervention:</b> Commit to 30 minutes of moderate exercise daily to repair cognitive functioning.</li>
                        </ul>
                    </div>
                    """
                }

                st.markdown(f'''<div class="metric-card" style="margin-top: 15px;">{app_scripts.get(int(pred), "تعذر جلب التحليل الخاص بهذه الفئة.")}</div>''', unsafe_allow_html=True)

# ------------------------------------------------------------------
# Page 3: AI Assistant 🤖
# ------------------------------------------------------------------
elif page == "AI Assistant 🤖":
    st.markdown("<h3 style='color: #A855F7 !important; font-weight: 700; animation: fadeInUp 0.6s ease-out forwards;'>🤖 Smart AI Assistant</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94A3B8 !important;'>اسألني عن النتائج، أو ارفع صورة للمخطط البياني وسأقوم بتحليله لك استناداً إلى أحدث تقنيات Gemini.</p>", unsafe_allow_html=True)

    try:
        dev_api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        dev_api_key = ""

    if "user_api_key" not in st.session_state:
        st.session_state.user_api_key = ""

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

    active_api_key = st.session_state.user_api_key if st.session_state.user_api_key else dev_api_key

    if not active_api_key:
        st.error("⚠️ لم يتم العثور على أي مفتاح API صالح. يرجى إعداد الـ Secrets أو إدخال مفتاحك الخاص ليعمل الشات.")
        st.stop()
    else:
        genai.configure(api_key=active_api_key)

        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        with st.expander("📷 إرفاق صورة للتحليل (اختياري)"):
            uploaded_file = st.file_uploader("اختر صورة (PNG, JPG, JPEG)", type=["png", "jpg", "jpeg"])
            if uploaded_file is not None:
                st.image(uploaded_file, caption="الصورة المرفوعة", width=250)

        if prompt := st.chat_input("اكتب سؤالك هنا... (مثال: اشرح لي نتيجتي الأخيرة)"):
            
            with st.chat_message("user"):
                st.markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})

            sys_instruct = """أنت مهندس بيانات ومساعد ذكي مدمج في منصة 'Vision Analytics'. وظيفتك تحليل البيانات والرد على استفسارات المستخدمين باحترافية وتقديم رؤى واضحة.
            يجب أن تفهم جيداً أن هذه المنصة تحتوي على نظامين منفصلين للذكاء الاصطناعي:
            1. نظام (Student Risk Analysis): مخصص للطلاب فقط. يتوقع احتمالية تعرض الطالب للخطر بناءً على عوامل نفسية وبيئية.
            2. نظام (App Behavior Analysis): يحلل السلوك التقني لمستخدمي الهواتف الذكية. ركز على نصائح "الديتوكس الرقمي" والصحة.
            بناءً على هذا الفهم، قم بالإجابة بدقة عالية وقدم نصائح عملية ومباشرة."""
            
            if 'last_analysis_context' in st.session_state:
                sys_instruct += f"\n\n[سياق مخفي هام جداً للإجابة]: أحدث نتيجة تحليل قام بها المستخدم للتو هي: {st.session_state['last_analysis_context']}"

            model = genai.GenerativeModel(
                model_name='gemini-flash-latest',
                system_instruction=sys_instruct
            )

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
