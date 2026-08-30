import io
import json
import re
import textwrap
import time
from typing import Any, Dict, List, Optional
import google.generativeai as genai
import pandas as pd
import streamlit as st

# ==========================================
# ۱. مدیریت و ترکیب کلید API جهت تست و MVP
# ==========================================
KEY_PART_1 = "AQ.Ab8RN6L5dkjpT7BQnsaAfJnZwhfoGL"
KEY_PART_2 = "_74t6wmSMHoItCLCWKiQ"


def get_combined_api_key(user_key: str = "") -> str:
    """در صورت عدم ورود کلید توسط کاربر، دو بخش کلید تست ترکیب می‌شوند."""
    if user_key and user_key.strip():
        return user_key.strip()
    return KEY_PART_1 + KEY_PART_2


# ==========================================
# ۲. تنظیمات اولیه صفحه Streamlit
# ==========================================
st.set_page_config(
    page_title="سامانه هوشمند ارزیابی ریسک و نظارت مالی ",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================
# ۳. استایل‌دهی جامع RTL، اصلاح تب‌ها، چت‌بات و UX
# ==========================================
CUSTOM_CSS = """
<style>
    @import url('https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css');
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');

    * {
        font-family: 'Vazirmatn', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    html, body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"] {
        direction: rtl !important;
        text-align: right !important;
        background-color: #f8fafc;
    }
    
    /* 2. حذف فاصله از بالای کانتینر اصلی */
    [data-testid="stMainBlockContainer"], .block-container {
        padding-top: 2rem !important;
    }

    /* 3. شفاف‌سازی و کاهش ارتفاع هدر پیش‌فرض استریم‌لیت */
    [data-testid="stHeader"] {
        background-color: transparent !important;
        height: 2rem !important;
    }

    /* آیکون‌های متریال استریم‌لیت */
    [class*="material-symbols"],
    [class*="MaterialSymbols"],
    [data-testid="stIcon"] {
        font-family: 'Material Symbols Outlined' !important;
        font-weight: normal !important;
        font-style: normal !important;
        direction: rtl !important;
        display: inline-block !important;
        white-space: nowrap !important;
        word-wrap: normal !important;
    }

    /* اصلاح راست‌چین و Justify متن درون Expander ها */
    [data-testid="stExpander"] {
        direction: rtl !important;
        text-align: right !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 12px !important;
        background-color: #ffffff !important;
        margin-bottom: 1rem !important;
    }
    
    [data-testid="stExpander"] summary {
        direction: rtl !important;
        text-align: right !important;
        display: flex !important;
        flex-direction: row-reverse !important;
        align-items: center !important;
        justify-content: space-between !important;
        gap: 12px !important;
        background-color: #f1f5f9 !important;
        border-radius: 10px !important;
        padding: 0.75rem 1rem !important;
    }

    [data-testid="stExpander"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stExpander"] div {
        direction: rtl !important;
        text-align: justify !important;
        line-height: 1.8 !important;
    }

    [data-testid="stSidebarCollapseButton"] {
        direction: ltr !important;
    }

    svg, svg * {
        font-family: unset !important;
    }

    h1, h2, h3, h4, h5, h6, 
    [data-testid="stHeading"] *, 
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5 {
        font-family: 'Vazirmatn', sans-serif !important;
        direction: rtl !important;
        text-align: right !important;
        font-weight: 700 !important;
        letter-spacing: normal !important;
    }

    .app-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #ffffff;
        padding: 2rem 2.5rem;
        border-radius: 16px;
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.25);
        margin-bottom: 2rem;
        border: 1px solid #334155;
    }
    
    .app-header h1 {
        color: #4ed793 !important;
        font-size: 2.1rem !important;
        font-weight: 800 !important;
        margin-bottom: 0.6rem !important;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .app-header p {
        color: #cbd5e1 !important;
        font-size: 1.05rem !important;
        line-height: 1.7 !important;
        margin: 0 !important;
        direction: rtl !important;
        text-align: right !important;
    }

    .metric-card {
        background: #454a53;
        padding: 1.25rem 1.4rem;
        border-radius: 14px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
        transition: all 0.25s ease;
        height: 100%;
    }
    
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 20px -5px rgba(0, 0, 0, 0.08);
        border-color: #cbd5e1;
    }
    
    .metric-title {
        color: #ffffff;
        font-size: 0.88rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .metric-value {
        color: #ffffff;
        font-size: 1.45rem;
        font-weight: 700;
        line-height: 1.4;
    }

    .risk-card-alert {
        background: linear-gradient(135deg, #fff1f2 0%, #ffe4e6 100%);
        border: 2px solid #f43f5e;
        border-radius: 14px;
        padding: 1.5rem;
        color: #881337;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 15px rgba(244, 63, 94, 0.1);
        direction: rtl !important;
        text-align: justify !important;
    }

    .risk-card-recovery {
        background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
        border: 2px solid #f59e0b;
        border-radius: 14px;
        padding: 1.5rem;
        color: #78350f;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 15px rgba(245, 158, 11, 0.1);
        direction: rtl !important;
        text-align: justify !important;
    }

    .risk-card-resolution {
        background: linear-gradient(135deg, #faf5ff 0%, #f3e8ff 100%);
        border: 2px solid #a855f7;
        border-radius: 14px;
        padding: 1.5rem;
        color: #581c87;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 15px rgba(168, 85, 247, 0.1);
        direction: rtl !important;
        text-align: justify !important;
    }

    [data-testid="stSidebar"] {
        background-color: #0f172a;
        border-left: 1px solid #1e293b;
    }
    
    [data-testid="stSidebar"] * {
        color: #f1f5f9 !important;
    }
    
    [data-testid="stSidebar"] .stSelectbox label, 
    [data-testid="stSidebar"] .stTextInput label,
    [data-testid="stSidebar"] .stSlider label {
        color: #8e97ad !important;
        font-weight: 600;
    }

    /* ==========================================
       اصلاح کامل و جامع Tab ها و فواصل آن‌ها
       ========================================== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 4px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 48px;
        background-color: #ffffff;
        border-radius: 10px 10px 0 0;
        padding: 10px 24px;
        font-weight: 700 !important;
        color: #475569 !important;
        border: 1px solid #e2e8f0;
        border-bottom: none;
        transition: all 0.2s ease;
    }

    .stTabs [aria-selected="true"] {
        background-color: #2d4b81  !important;
        color: #ffffff !important;
        border-color: #535fa1 !important;
        box-shadow: 0 4px 10px rgba(2, 132, 199, 0.2);
    }

    

    .stButton button {
        border-radius: 10px !important;
        font-weight: 800 !important;
        padding: 0.55rem 1.2rem !important;
        transition: all 0.2s ease !important;
        background-color: #a43232 !important;
        border: 4px solid #f65858 !important;
        color: #ffffff !important;
    }

    /* ==========================================
       اصلاح کامل چت‌بات، جدول‌ها، بولت‌ها و شماره‌گذاری‌ها (RTL & Right-Align)
       ========================================== */
    [data-testid="stChatMessage"] {
        border-radius: 14px !important;
        padding: 1.25rem !important;
        margin-bottom: 1rem !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
        direction: rtl !important;
        text-align: right !important;
    }
    
    [data-testid="stChatMessageContent"],
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"],
    [data-testid="stChatMessage"] .stMarkdown {
        direction: rtl !important;
        text-align: right !important;
    }

    [data-testid="stChatMessage"] p,
    [data-testid="stChatMessageContent"] p {
        direction: rtl !important;
        text-align: justify !important;
        line-height: 1.8 !important;
    }

    [data-testid="stChatMessageAvatar"] {
        margin-left: 10px !important;
        margin-right: 0px !important;
    }

    /* راست‌چین کردن کامل لیست‌های بولت‌دار و شماره‌دار در چت‌بات و مارک‌داون */
    [data-testid="stChatMessage"] ul,
    [data-testid="stChatMessage"] ol,
    [data-testid="stChatMessageContent"] ul,
    [data-testid="stChatMessageContent"] ol,
    .stMarkdown ul,
    .stMarkdown ol {
        direction: rtl !important;
        text-align: right !important;
        padding-right: 1.8rem !important;
        padding-left: 0 !important;
        margin-right: 0 !important;
        margin-left: 0 !important;
    }

    [data-testid="stChatMessage"] li,
    [data-testid="stChatMessageContent"] li,
    .stMarkdown li {
        direction: rtl !important;
        text-align: right !important;
        margin-bottom: 0.4rem !important;
        line-height: 1.8 !important;
    }

    /* راست‌چین کردن کامل جداول رندر شده در چت‌بات و پاسخ‌های هوش مصنوعی */
    [data-testid="stChatMessage"] table,
    [data-testid="stChatMessageContent"] table,
    .stMarkdown table {
        direction: rtl !important;
        text-align: right !important;
        width: 100% !important;
        margin: 1rem 0 !important;
        border-collapse: collapse !important;
        border-radius: 8px !important;
        overflow: hidden !important;
    }

    [data-testid="stChatMessage"] th,
    [data-testid="stChatMessage"] td,
    [data-testid="stChatMessageContent"] th,
    [data-testid="stChatMessageContent"] td,
    .stMarkdown th,
    .stMarkdown td {
        direction: rtl !important;
        text-align: right !important;
        padding: 10px 14px !important;
        border: 1px solid #cbd5e1 !important;
    }

    [data-testid="stChatMessage"] th,
    [data-testid="stChatMessageContent"] th,
    .stMarkdown th {
        background-color: #f1f5f9 !important;
        font-weight: 700 !important;
        color: #1e293b !important;
    }

    [data-testid="stChatMessage"]:nth-child(even) {
        background-color: #f0f9ff !important;
        border-right: 5px solid #5390a1 !important;
        border-left: none !important;
    }

    [data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #ffffff !important;
        border-right: 5px solid #10b981 !important;
        border-left: none !important;
    }

    .stTable table, [data-testid="stTable"] table {
        direction: rtl !important;
        text-align: right !important;
        border-radius: 10px;
        overflow: hidden;
    }
    
    .stTable th, [data-testid="stTable"] th {
        text-align: right !important;
        background-color: #f1f5f9 !important;
        color: #1e293b !important;
        font-weight: 700 !important;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ==========================================
# ۴. مدیریت حافظه نشست (Session State)
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "cache_metadata" not in st.session_state:
    st.session_state.cache_metadata = {}

if "excel_data_json" not in st.session_state:
    st.session_state.excel_data_json = None

if "cache_object" not in st.session_state:
    st.session_state.cache_object = None

if "risk_prediction_result" not in st.session_state:
    st.session_state.risk_prediction_result = None

# ==========================================
# ۵. منوی کناری (Sidebar Menu)
# ==========================================
with st.sidebar:
    st.markdown("### 🧠 سامانه تحلیل هوشمند")

    st.markdown("---")
    st.markdown("### ⚙ تنظیمات ")

    ttl_minutes = st.slider(
        "⏱️ مدت زمان اعتبار کش (TTL به دقیقه):",
        min_value=5,
        max_value=60,
        value=30,
        step=5,
        help="زمان ماندگاری داده‌های کش‌شده در سرورهای هوش مصنوعی",
    )

    temperature = st.slider(
        "🎯 درجه خلاقیت (Temperature):",
        min_value=0.0,
        max_value=1.0,
        value=0.1,
        step=0.1,
        help=(
            "مقادیر پایین‌تر پاسخ‌های دقیق‌تر، رسمی‌تر و پایبندتر به متون ارائه"
            " می‌دهند."
        ),
    )

    st.markdown("---")

    if st.button("🗑️ بازنشانی حافظه و پاک‌سازی کش", use_container_width=True):
        st.session_state.messages = []
        st.session_state.excel_data_json = None
        st.session_state.cache_metadata = {}
        st.session_state.cache_object = None
        st.session_state.risk_prediction_result = None
        st.success("حافظه برنامه و کش داده‌ها با موفقیت پاک‌سازی شد.")
        st.rerun()

    st.markdown("---")

    custom_api_key = st.text_input(
        "🔑 کلید اختصاصی API (اختیاری):",
        type="password",
        placeholder="در صورت داشتن کلید اختصاصی وارد کنید...",
        help=(
            "در صورت خالی بودن، کلید پیش‌فرض ترکیب‌شده پیش‌فرض برنامه استفاده"
            " می‌شود."
        ),
    )

    final_api_key = get_combined_api_key(custom_api_key)

    AVAILABLE_MODELS = ["gemma-4-31b-it"]

    model_name = st.selectbox(
        "🤖 انتخاب مدل هوش مصنوعی اصلی:",
        AVAILABLE_MODELS,
        index=0,
        help=(
            "در صورت عدم دسترسی یا اتمام سهمیه مدل انتخابی، سیستم به‌صورت"
            " خودکار مدل‌های دیگر را جایگزین خواهد کرد."
        ),
    )

    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; color: #94a3b8; font-size: 0.8rem; line-height: 1.7;">
            🛡️ <b>سامانه ارزیابی ریسک تخلفات و تحلیل گزارشات نظارتی حوزه بانکی مبتنی بر هوش مصنوعی </b><br>
            
        </div>
    """,
        unsafe_allow_html=True,
    )

# ==========================================
# ۶. هدر اصلی برنامه
# ==========================================
st.markdown(
    """
    <div class="app-header">
        <h1>🛡️ سامانه ارزیابی ریسک تخلفات و گزارشات نظارت بانکی </h1>
        <p>تحلیل جامع گزارشات نظارتی و بازرسی دستگاه های ناظر و بانک های عامل بصورت هوشمند</p>
    </div>
""",
    unsafe_allow_html=True,
)


# ==========================================
# ۷. تابع پردازش و تبدیل اکسل به JSON برای CAG
# ==========================================
def process_excel_to_cag_structure(uploaded_file):
    excel_file = pd.ExcelFile(uploaded_file)
    sheet_names = excel_file.sheet_names

    sheets_metadata = []
    full_dataset = []
    total_records = 0

    for sheet in sheet_names:
        try:
            df = pd.read_excel(uploaded_file, sheet_name=sheet)
            df = df.fillna("نامشخص/ثبت نشده")

            row_count = len(df)
            col_count = len(df.columns)
            total_records += row_count

            records = df.to_dict(orient="records")
            formatted_sheet_data = []
            for idx, record in enumerate(records, start=1):
                formatted_sheet_data.append(
                    {"sheet_name": sheet, "row_id": idx, "content": record}
                )

            full_dataset.append({
                "sheet_title": sheet,
                "total_rows": row_count,
                "columns": list(df.columns),
                "rows": formatted_sheet_data,
            })

            sheets_metadata.append({
                "sheet_name": sheet,
                "rows": row_count,
                "cols": col_count,
                "columns_list": list(df.columns),
                "status": "موفق",
                "error": None,
            })
        except Exception as e:
            sheets_metadata.append({
                "sheet_name": sheet,
                "rows": 0,
                "cols": 0,
                "columns_list": [],
                "status": "خطا",
                "error": str(e),
            })

    cag_json_string = json.dumps(full_dataset, ensure_ascii=False, indent=2)
    file_size_kb = len(uploaded_file.getvalue()) / 1024

    summary_metadata = {
        "file_name": uploaded_file.name,
        "file_size_kb": f"{file_size_kb:.2f} KB",
        "sheet_count": len(sheet_names),
        "total_records": total_records,
        "sheets_details": sheets_metadata,
    }

    return summary_metadata, cag_json_string, sheets_metadata


# ==========================================
# ۸. تابع مدیریت هوشمند خطا (Retry + Fallback برای 429 و 404)
# ==========================================
def generate_content_with_retry_and_fallback(
    prompt: str,
    primary_model: str,
    available_models: List[str],
    system_prompt: Optional[str] = None,
    cached_object: Any = None,
    temp: float = 0.1,
    stream: bool = False,
):
    candidate_models = [primary_model] + [
        m for m in available_models if m != primary_model
    ]

    last_error = None

    for m_name in candidate_models:
        for attempt in range(2):
            try:
                if cached_object and cached_object != "IN_MEMORY":
                    model = genai.GenerativeModel.from_cached_content(
                        cached_content=cached_object,
                        generation_config={"temperature": temp},
                    )
                else:
                    model = genai.GenerativeModel(
                        model_name=m_name,
                        system_instruction=(
                            system_prompt if system_prompt else None
                        ),
                    )

                response = model.generate_content(
                    prompt,
                    generation_config={"temperature": temp},
                    stream=stream,
                )
                return response, m_name
            except Exception as e:
                err_msg = str(e)
                last_error = e

                if (
                    "404" in err_msg
                    or "not available" in err_msg
                    or "429" in err_msg
                    or "Quota exceeded" in err_msg
                    or "ResourceExhausted" in err_msg
                ):
                    if "404" in err_msg or "not available" in err_msg:
                        break
                    if attempt == 0:
                        time.sleep(2)
                        continue
                    break
                else:
                    raise e

    raise last_error


st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# ۹. تفکیک برنامه به ۳ زبانه (Tabs)
# ==========================================
tab1, tab2, tab3 = st.tabs([
    "📥 ۱. بارگذاری داده‌ها و گزارش‌های فایل",
    "🛡️ ۲. گزارش‌های ارزیابی ریسک، نظارت و دستیار تخصصی",
    "⚖️ ۳. دستیار تحلیلی حوزه مالی و نظارت بانکی",
])

# ------------------------------------------
# 📌 زبانـه اول: بارگذاری داده‌ها و گزارش‌ها
# ------------------------------------------
with tab1:
    st.markdown("### 📂 بارگذاری اسناد و فایل‌های مالی/اعتباری اکسل")

    with st.expander(
        "📖 **راهنمای جامع استانداردسازی و بارگذاری اسناد**", expanded=False
    ):
        st.markdown("""
        **جهت حصول بهترین نتیجه در تحلیل‌های هوش مصنوعی و کشف دقیق انحرافات، به نکات زیر توجه فرمایید:**
        1. **فرمت فایل:** فایل شما باید با پسوند `.xlsx` یا `.xls` باشد.
        2. **ساختار اسناد:** هر Sheet می‌تواند نماینده یک بخش (مانند *تسهیلات اعتباری، وثایق، صورت‌های مالی، پرونده‌های مشکوک*) باشد.
        3. ** عناوین ستون‌ها:** حتماً در سطر اول هر Sheet عناوین واضح مانند `نام مشتری`، `مبلغ تسهیلات`، `سررسید`، `نوع وثیقه`، `درجه ریسک` و ... درج شده باشد.
        4. **پوشش داده‌ها:** هوش مصنوعی به‌صورت سطر به سطر تمامی رکوردهای بارگذاری‌شده را نمایه (Index) کرده و در پاسخ‌ها دقیقاً شماره سطر و نام شیت را ارجاع خواهد داد.
        """)

    st.markdown("<br>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "لطفاً فایل اکسل نتایج حاصل از گزارشهای نظارتی یا اسناد مورد بررسی را"
        " انتخاب کنید:",
        type=["xlsx", "xls"],
    )

    if uploaded_file is not None:
        if st.session_state.cache_metadata.get("file_name") != uploaded_file.name:
            with st.spinner(
                "⏳ در حال استخراج، تحلیل ساختار و بسته‌بندی داده‌ها برای"
                " کانتکست CAG..."
            ):
                metadata, json_str, sheets_info = (
                    process_excel_to_cag_structure(uploaded_file)
                )
                st.session_state.cache_metadata = metadata
                st.session_state.excel_data_json = json_str
                st.session_state.cache_object = None
                st.session_state.messages = []
                st.session_state.risk_prediction_result = None

        metadata = st.session_state.cache_metadata

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 📊 خلاصه وضعیت و مشخصات فنی فایل بارگذاری‌شده")

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-title"><i class="fa-solid fa-file-excel"></i> نام فایل</div>
                    <div class="metric-value" style="font-size: 1rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{metadata['file_name']}</div>
                </div>
            """,
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-title"><i class="fa-solid fa-weight-hanging"></i> حجم فایل</div>
                    <div class="metric-value">{metadata['file_size_kb']}</div>
                </div>
            """,
                unsafe_allow_html=True,
            )
        with c3:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-title"><i class="fa-solid fa-layer-group"></i> تعداد شیت‌ها</div>
                    <div class="metric-value">{metadata['sheet_count']}</div>
                </div>
            """,
                unsafe_allow_html=True,
            )
        with c4:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-title"><i class="fa-solid fa-list-check"></i> کل رکوردهای پردازش‌شده</div>
                    <div class="metric-value">{metadata['total_records']:,}</div>
                </div>
            """,
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 📋 جزئیات تفکیکی شیت‌ها و ستون‌های شناساگر")

        sheet_display = []
        for s in metadata["sheets_details"]:
            sheet_display.append({
                "نام Sheet": s["sheet_name"],
                "تعداد سطر (رکورد)": s["rows"],
                "تعداد ستون": s["cols"],
                "نمونه ستون‌ها": (
                    ", ".join(s["columns_list"][:6])
                    + ("..." if len(s["columns_list"]) > 6 else "")
                ),
                "وضعیت تحلیل": (
                    "✅ موفق"
                    if s["status"] == "موفق"
                    else f"❌ خطا: {s['error']}"
                ),
            })
        st.table(pd.DataFrame(sheet_display))

        st.markdown("### 🔍 پیش‌نمایش محتوای شیت‌ها")
        selected_sheet = st.selectbox(
            "انتخاب شیت جهت پیش‌نمایش داده‌ها:",
            [s["sheet_name"] for s in metadata["sheets_details"]],
        )

        if selected_sheet:
            df_preview = pd.read_excel(uploaded_file, sheet_name=selected_sheet)
            df_sub = df_preview.head(10).fillna("نامشخص/ثبت نشده")

            st.dataframe(
                df_sub,
                use_container_width=True,
                hide_index=True
            )

    else:
        st.info(
            "👈 جهت شروع تحلیل، لطفاً فایل اکسل خود را از کادر فوق بارگذاری"
            " نمایید."
        )

# ------------------------------------------
# 📌 زبانـه دوم: گزارش‌های ارزیابی ریسک
# ------------------------------------------
with tab2:
    if st.session_state.excel_data_json is None:
        st.warning(
            "⚠️ لطفاً ابتدا در زبانه اول (📥 بارگذاری داده‌ها)، فایل اکسل اسناد"
            " را بارگذاری نمایید."
        )
    else:
        st.markdown("### ⚖️ گزارش ارزیابی، مدیریت ریسک و وضعیت نظارتی بانک")

        with st.expander("📌 **راهنمای تحلیلگر**", expanded=False):
            st.markdown("""
            **این بخش بر اساس استانداردهای نظارتی و مالی از جمله شاخص های CAMELS طراحی شده است:**
            - **وضعیت اخطار (Alert):** شناسایی انحرافات اعتباری، نقض آیین‌نامه‌ها، مطالبات غیرجاری یا کسر وثایق که نیازمند اخطار فوری به هیئت‌مدیره است.
            - **وضعیت ریکاوری (Recovery):** پیشنهاد برنامه‌های وصول مطالبات، ترمیم وثایق، امهال ضابطه‌مند و تجدید ارزیابی دارایی‌ها.
            - **وضعیت گزیر (Resolution):** پیش‌بینی اقدامات ساختاری، نقل و انتقال یا مداخلات قهری در صورت احراز ناترازی عمیق و تخلفات کلان.
            """)

        genai.configure(api_key=final_api_key, transport="rest")

        SYSTEM_PROMPT = """
تو به مانند یک تحلیلگر و متخصص نظارت بانکی، حسابرس و بازرس ویژه یا حسابرس ارشد و مستشار ارشد مدیریت ریسک و نظارت بر بانک‌ها و موسسات اعتباری هستید. به سوالات پاسخ صریح و روشن براساس متن ورودی بده و در ارائه توصیه و پیشنهاد راهکار اعلام کن که این صرفا تحلیل تو بر اساس داده های ورودی است و قبل از هر گونه اقدام با کارشناس متخصص این حوزه بررسی و تصمیم گیری لازم با سنجیدن همه ابعاد صورت پذیرد تا کمترین آسیب به شبکه بانکی و اعتماد مردم وارد شود. در پاسخ به سوالات گزارشات کلی و جامع و ارائه راهکار کلی و گزارشات تحلیل برای ناظر و بازرس و گزارش کلی ریسک حتما از بخش بندی مرتبط و جداول با آکون مناسب استفاده کن.
 وظایف اصلی شما در صورت مرتبط بودن سوال و نیاز:
۱. تحلیل دقیق داده‌ها با رویکرد بازرسی ویژه، کشف تخلفات آیین‌نامه‌ای، معوقات اعتباری و سوءجریانات احتمالی.
۲. تحلیل و تعیین پیش‌بینی کلان وضعیت پرونده/بانک بین فازهای چهارگانه استاندارد در مواجهه با بانک‌های ناتراز صرفا در صورت مرتبط بودن سوال:
- ⚠️"فاز پیشگیری و آمادگی (Prevention & Readiness)": حتی پیش از بروز بحران، همه بانک‌ها موظفند سناریوهای بحران (Stress Testing) را تمرین کرده و طرح‌های ریکاوری خود را از قبل بنویسند.
-⚠️ ". فاز مداخله زودهنگام "(Early Intervention)" ورود رسمی ناظر به محض دیدن اولین نشانه‌های ناترازی (اینجا محل صدور اخطار و هشدار و ابلاغ Action Plan است).
- 🔄 ". فاز بازسازی و ریکاوری (Recovery)": اجرای عملیات نجات دارایی‌ها توسط خودِ بانک تحت نظارت مقیم بانک مرکزی.
-. 🚨 "فاز گزیر یا حل و فصل(Resolution) ": سلب اختیار از مالکان و مدیریت دولتی/حاکمیتی بانک برای جلوگیری از سرایت بحران به کل بازار و ورود به فاز تسویه و خروج از بازار.

۳. ارائه KPIهای دقیق ریسک مالی (شامل تخلفات عمده، ریسک اعتباری و عملیاتی، کیفیت وثایق، کفایت سرمایه و غیره) صرفا در صورت مزتبط بودن سوال.

- پاسخ دقیق و بدون تصرف به سوالات کاربر و خواسته های آن در موضوع گزارشات مالی و نظارت بانکی براساس صرفا فایل ورودی است و نه چارچوب خارج از فایل ورودی. 
- همچنین فقط در صورت نیاز برای پاسخ به سایر استانداردها، شیوه نامه اقدام بانک های ناتراز و چارچوب های مالی مانند CAMELS توجه کن در غیر این صورت نیاز نیست. 

۴. الزامی: در تمامی پاسخ‌ها، هرجا به هر رکورد یا داده‌ای اشاره می‌کنید حتماً مرجع آن را با فرمت دقیق [مرجع: شیت X - ردیف Y] قید نمایید.
        """

        if st.session_state.cache_object is None:
            with st.spinner(
                "⏳ در حال تحلیل اسناد و آماده‌سازی مدل نظارتی ..."
            ):
                try:
                    cache_content = (
                        "اطلاعات اسناد جهت ارزیابی نظارتی و"
                        f" حسابرسی:\n\n{st.session_state.excel_data_json}"
                    )
                    try:
                        from google.generativeai import caching

                        cache = caching.CachedContent.create(
                            model=model_name,
                            display_name=(
                                "cag_audit_"
                                f"{st.session_state.cache_metadata.get('file_name', 'file')}"
                            ),
                            contents=[cache_content],
                            ttl=pd.Timedelta(minutes=ttl_minutes),
                        )
                        st.session_state.cache_object = cache
                    except Exception as e_cache:
                        st.session_state.cache_object = "IN_MEMORY"
                except Exception as e:
                    st.error(f"خطا در ارتباط با API گوگل: {str(e)}")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 📊 ارزیابی تخصصی بر اساس شاخص‌های شش‌گانه CAMELS")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.session_state.get("camels_analysis_result") is None:
            if st.button(
                "🚀 اجرای تحلیل و ارزیابی ریسک بر اساس شاخص‌های CAMELS",
                type="primary",
                use_container_width=True,
            ):
                with st.spinner(
                    "🧠 در حال تحلیل داده‌ها، استخراج انحرافات و ارزیابی شاخص‌های"
                    " CAMELS..."
                ):
                    try:
                        camels_prompt = """
        تو به عنوان مستشار و ارشد نظارت مالی و حسابرسی بانکی، داده‌های زیر را بر اساس استانداردهای نظارتی و شاخص‌های شش‌گانه CAMELS تحلیل کن.

        برای هر یک از 6 شاخص زیر، دقیقاً یکی از ۵ حالت وضعیت ریسک را انتخاب کن:
        - "بحرانی"
        - "ریسک بالا"
        - "ریسک متوسط"
        - "پایین"
        - "نامشخص/اظهار نظر نشده"

        شاخص‌های شش‌گانه:
        1. C - کفایت سرمایه (Capital Adequacy)
        2. A - کیفیت دارایی‌ها (Asset Quality)
        3. M - کیفیت مدیریت (Management)
        4. E - سودآوری (Earnings)
        5. L - نقدینگی (Liquidity)
        6. S - حساسیت به ریسک بازار (Sensitivity to Market Risk)

        پاسخ را دقیقاً در قالب فرمت ساختاریافته JSON زیر برگردان و هیچ متن اضافی، توضیح یا خروجی دیگری قبل یا بعد از آن نیاور:
        {
          "camels": {
            "capital": {
              "title": "C - کفایت سرمایه",
              "status": "یکی از 5 حالت فوق",
              "violations": "مصادیق تخلفات و انحرافات (در صورت عدم وجود: موردی ثبت نشده)",
              "reasons": "تحلیل و دلایل فنی وضعیت تعیین شده با ذکر دقیق مرجع [شیت X - ردیف Y]"
            },
            "assets": {
              "title": "A - کیفیت دارایی‌ها",
              "status": "یکی از 5 حالت فوق",
              "violations": "مصادیق تخلفات و انحرافات",
              "reasons": "تحلیل و دلایل فنی با ذکر مرجع"
            },
            "management": {
              "title": "M - کیفیت مدیریت",
              "status": "یکی از 5 حالت فوق",
              "violations": "مصادیق تخلفات و انحرافات",
              "reasons": "تحلیل و دلایل فنی با ذکر مرجع"
            },
            "earnings": {
              "title": "E - سودآوری",
              "status": "یکی از 5 حالت فوق",
              "violations": "مصادیق تخلفات و انحرافات",
              "reasons": "تحلیل و دلایل فنی با ذکر مرجع"
            },
            "liquidity": {
              "title": "L - نقدینگی",
              "status": "یکی از 5 حالت فوق",
              "violations": "مصادیق تخلفات و انحرافات",
              "reasons": "تحلیل و دلایل فنی با ذکر مرجع"
            },
            "sensitivity": {
              "title": "S - حساسیت به ریسک بازار",
              "status": "یکی از 5 حالت فوق",
              "violations": "مصادیق تخلفات و انحرافات",
              "reasons": "تحلیل و دلایل فنی با ذکر مرجع"
            }
          },
          "high_risk_warning": "تحلیل مشروح پرخطرترین موارد و ریسک‌های بحرانی شناسایی‌شده",
          "contagion_risk_warning": "تذکر و تحلیل دقیق ریسک‌های با امکان سرایت به سایر بانک‌ها و شبکه بانکی به منظور پیشگیری",
          "systemic_risk_warning": "ارزیابی و تذکر ریسک‌های سیستماتیک و ساختاری کلان",
          "final_expert_opinion": "جمع‌بندی و اظهار نظر نهایی تخصصی کارشناس ارشد مالی و نظارت بانکی"
        }
        """
                        prompt_full = (
                            "داده‌های سند جهت"
                            f" بررسی:\n{st.session_state.excel_data_json}\n\n{camels_prompt}"
                        )

                        res, used_m = generate_content_with_retry_and_fallback(
                            prompt=prompt_full,
                            primary_model=model_name,
                            available_models=AVAILABLE_MODELS,
                            system_prompt=SYSTEM_PROMPT,
                            temp=0.1,
                            stream=False,
                        )

                        raw_response = res.text.strip()
                        json_match = re.search(
                            r"\{.*\}", raw_response, re.DOTALL
                        )

                        if json_match:
                            json_clean = json_match.group(0)
                            st.session_state.camels_analysis_result = (
                                json.loads(json_clean)
                            )
                            st.rerun()
                        else:
                            st.error(
                                "⚠️ پاسخ دریافتی از هوش مصنوعی ساختار JSON"
                                " معتبر ندارد. لطفاً مجدداً دکمه ارزیابی را"
                                " فشار دهید."
                            )

                    except json.JSONDecodeError as e:
                        st.error(
                            "❌ خطا در قالب‌بندی خروجی JSON. لطفاً مجدداً دکمه"
                            " پردازش را بزنید."
                        )
                    except Exception as ex:
                        st.error(f"خطا در دریافت ارزیابی CAMELS: {str(ex)}")

        if st.session_state.get("camels_analysis_result"):
            camels_data = st.session_state.camels_analysis_result.get(
                "camels", {}
            )

            STATUS_CONFIG = {
                "بحرانی": {
                    "bg": "#fef2f2",
                    "border": "#ef4444",
                    "text": "#991b1b",
                    "badge_bg": "#dc2626",
                    "badge_color": "#ffffff",
                    "icon": "fa-skull-crossbones",
                },
                "ریسک بالا": {
                    "bg": "#fff7ed",
                    "border": "#f97316",
                    "text": "#9a3412",
                    "badge_bg": "#ea580c",
                    "badge_color": "#ffffff",
                    "icon": "fa-triangle-exclamation",
                },
                "ریسک متوسط": {
                    "bg": "#fefce8",
                    "border": "#eab308",
                    "text": "#854d0e",
                    "badge_bg": "#ca8a04",
                    "badge_color": "#ffffff",
                    "icon": "fa-circle-exclamation",
                },
                "پایین": {
                    "bg": "#f0fdf4",
                    "border": "#22c55e",
                    "text": "#166534",
                    "badge_bg": "#16a34a",
                    "badge_color": "#ffffff",
                    "icon": "fa-circle-check",
                },
                "نامشخص/اظهار نظر نشده": {
                    "bg": "#f8fafc",
                    "border": "#94a3b8",
                    "text": "#475569",
                    "badge_bg": "#64748b",
                    "badge_color": "#ffffff",
                    "icon": "fa-circle-question",
                },
            }

            CAMELS_METADATA = [
                ("capital", "C - کفایت سرمایه", "fa-building-columns"),
                ("assets", "A - کیفیت دارایی‌ها", "fa-vault"),
                ("management", "M - کیفیت مدیریت", "fa-user-tie"),
                ("earnings", "E - سودآوری", "fa-chart-line-up"),
                ("liquidity", "L - نقدینگی", "fa-faucet-drip"),
                ("sensitivity", "S - حساسیت به ریسک بازار", "fa-chart-area"),
            ]

            st.markdown("#### 📌 خلاصه وضعیت شاخص‌های شش‌گانه")

            col_rows = [st.columns(3), st.columns(3)]
            for idx, (key, label, default_icon) in enumerate(CAMELS_METADATA):
                col = col_rows[idx // 3][idx % 3]
                item = camels_data.get(key, {})
                status = item.get("status", "نامشخص/اظهار نظر نشده")
                cfg = STATUS_CONFIG.get(
                    status, STATUS_CONFIG["نامشخص/اظهار نظر نشده"]
                )

                with col:
                    st.markdown(
                        f"""
                        <div style="
                            background: {cfg['bg']};
                            border: 2px solid {cfg['border']};
                            border-radius: 14px;
                            padding: 1.1rem;
                            margin-bottom: 1rem;
                            box-shadow: 0 4px 12px rgba(0,0,0,0.04);
                            transition: all 0.25s ease;
                        ">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.6rem;">
                                <span style="font-size: 1.05rem; font-weight: 800; color: #1e293b; display: flex; align-items: center; gap: 8px;">
                                    <i class="fa-solid {default_icon}" style="color: {cfg['border']}; font-size: 1.2rem;"></i>
                                    {label}
                                </span>
                            </div>
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.5rem;">
                                <span style="font-size: 0.85rem; color: #64748b; font-weight: 600;">وضعیت ریسک:</span>
                                <span style="
                                    background-color: {cfg['badge_bg']};
                                    color: {cfg['badge_color']};
                                    padding: 4px 12px;
                                    border-radius: 20px;
                                    font-size: 0.85rem;
                                    font-weight: 700;
                                    display: inline-flex;
                                    align-items: center;
                                    gap: 5px;
                                ">
                                    <i class="fa-solid {cfg['icon']}"></i> {status}
                                </span>
                            </div>
                        </div>
                    """,
                        unsafe_allow_html=True,
                    )

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("#### 📋 جدول تفکیکی شاخص‌های CAMELS و ارزیابی ریسک")

            table_rows_html = ""
            for key, label, icon in CAMELS_METADATA:
                item = camels_data.get(key, {})
                status = item.get("status", "نامشخص/اظهار نظر نشده")
                violations = item.get("violations", "موردی ثبت نشده")
                reasons = item.get("reasons", "-")
                cfg = STATUS_CONFIG.get(
                    status, STATUS_CONFIG["نامشخص/اظهار نظر نشده"]
                )

                row = (
                    '<tr style="border-bottom: 1px solid #e2e8f0; font-size:'
                    ' 0.95rem;"><td style="padding: 12px 16px; font-weight:'
                    ' 700; color: #0f172a; text-align: right; white-space:'
                    f' nowrap;"><i class="fa-solid {icon}" style="color:'
                    f' #475569; margin-left: 6px;"></i> {label}</td><td'
                    ' style="padding: 12px 16px; text-align: center;'
                    ' white-space: nowrap;"><span'
                    f' style="background-color: {cfg["bg"]}; color:'
                    f' {cfg["text"]}; border: 1px solid {cfg["border"]};'
                    " padding: 6px 14px; border-radius: 8px; font-weight: 700;"
                    ' font-size: 0.88rem; display: inline-block;"><i'
                    f' class="fa-solid {cfg["icon"]}"></i> {status}</span></td><td'
                    ' style="padding: 12px 16px; color: #334155; text-align:'
                    ' justify; line-height:'
                    f' 1.6;">{violations}</td><td style="padding: 12px 16px;'
                    ' color: #334155; text-align: justify; line-height:'
                    f' 1.6;">{reasons}</td></tr>'
                )
                table_rows_html += row

            camels_table_html = (
                '<div style="overflow-x: auto; border-radius: 12px; border: 1px'
                " solid #cbd5e1; box-shadow: 0 4px 15px rgba(0,0,0,0.03);"
                ' margin-bottom: 2rem;"><table style="width: 100%;'
                " border-collapse: collapse; direction: rtl; text-align: right;"
                " background-color: #ffffff; font-family: 'Vazirmatn',"
                ' sans-serif;"><thead><tr style="background-color: #1e293b;'
                ' color: #ffffff; font-size: 0.95rem; font-weight: 700;"><th'
                ' style="padding: 14px 16px; width: 20%; text-align: right;">شاخص'
                ' CAMELS</th><th style="padding: 14px 16px; width: 15%;'
                ' text-align: center;">وضعیت ریسک</th><th style="padding: 14px'
                ' 16px; width: 30%; text-align: right;">مصادیق تخلفات و'
                ' انحرافات</th><th style="padding: 14px 16px; width: 35%;'
                ' text-align: right;">دلایل وضعیت ریسک و ارجاعات</th></tr></thead><tbody>'
                f"{table_rows_html}"
                "</tbody></table></div>"
            )

            st.markdown(camels_table_html, unsafe_allow_html=True)

            st.markdown(
                "### 🏛️ جمع‌بندی مدیریتی و اظهار نظر کارشناس ارشد نظارت بانکی"
            )

            res_data = st.session_state.camels_analysis_result

            st.markdown(
                f"""
                <div style="
                    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
                    border-right: 6px solid #10b981;
                    border-radius: 14px;
                    padding: 1.5rem;
                    color: #ffffff;
                    margin-bottom: 1.5rem;
                    box-shadow: 0 8px 20px rgba(15, 23, 42, 0.15);
                    direction: rtl;
                    text-align: justify;
                ">
                    <h4 style="color: #34d399 !important; margin-top: 0; font-size: 1.2rem; display: flex; align-items: center; gap: 10px; text-align: right;">
                        <i class="fa-solid fa-user-shield"></i> اظهار نظر تخصصی مستشار ارشد مالی و نظارتی
                    </h4>
                    <p style="color: #f1f5f9; line-height: 1.8; font-size: 1rem; margin-bottom: 0; text-align: justify; direction: rtl;">
                        {res_data.get('final_expert_opinion', 'اظهار نظر تخصصی ثبت نشده است.')}
                    </p>
                </div>
            """,
                unsafe_allow_html=True,
            )

            warn_col1, warn_col2, warn_col3 = st.columns(3)

            with warn_col1:
                st.markdown(
                    f"""
                    <div style="
                        background-color: #fff1f2;
                        border: 2px solid #f43f5e;
                        border-radius: 12px;
                        padding: 1.2rem;
                        height: 100%;
                        direction: rtl;
                        text-align: justify;
                    ">
                        <h5 style="color: #9f1239 !important; margin-top: 0; font-size: 1.05rem; display: flex; align-items: center; gap: 8px; text-align: right;">
                            <i class="fa-solid fa-fire" style="color: #e11d48;"></i> پرخطرترین موارد
                        </h5>
                        <p style="color: #881337; font-size: 0.92rem; line-height: 1.8; margin-bottom: 0; text-align: justify; direction: rtl;">
                            {res_data.get('high_risk_warning', '-')}
                        </p>
                    </div>
                """,
                    unsafe_allow_html=True,
                )

            with warn_col2:
                st.markdown(
                    f"""
                    <div style="
                        background-color: #fffbeb;
                        border: 2px solid #f59e0b;
                        border-radius: 12px;
                        padding: 1.2rem;
                        height: 100%;
                        direction: rtl;
                        text-align: justify;
                    ">
                        <h5 style="color: #92400e !important; margin-top: 0; font-size: 1.05rem; display: flex; align-items: center; gap: 8px; text-align: right;">
                            <i class="fa-solid fa-network-wired" style="color: #d97706;"></i> ریسک‌های سرایت به شبکه بانکی
                        </h5>
                        <p style="color: #78350f; font-size: 0.92rem; line-height: 1.8; margin-bottom: 0; text-align: justify; direction: rtl;">
                            {res_data.get('contagion_risk_warning', '-')}
                        </p>
                    </div>
                """,
                    unsafe_allow_html=True,
                )

            with warn_col3:
                st.markdown(
                    f"""
                    <div style="
                        background-color: #f0f9ff;
                        border: 2px solid #0284c7;
                        border-radius: 12px;
                        padding: 1.2rem;
                        height: 100%;
                        direction: rtl;
                        text-align: justify;
                    ">
                        <h5 style="color: #075985 !important; margin-top: 0; font-size: 1.05rem; display: flex; align-items: center; gap: 8px; text-align: right;">
                            <i class="fa-solid fa-globe" style="color: #0284c7;"></i> ریسک‌های سیستماتیک
                        </h5>
                        <p style="color: #0c4a6e; font-size: 0.92rem; line-height: 1.8; margin-bottom: 0; text-align: justify; direction: rtl;">
                            {res_data.get('systemic_risk_warning', '-')}
                        </p>
                    </div>
                """,
                    unsafe_allow_html=True,
                )

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔄 به‌روزرسانی و ارزیابی مجدد شاخص‌های CAMELS"):
                st.session_state.camels_analysis_result = None
                st.rerun()

        st.markdown("<hr>", unsafe_allow_html=True)

# ------------------------------------------
# 📌 زبانه سوم: ⚖️ ۳. دستیار تحلیلی حوزه مالی و نظارت بانکی
# ------------------------------------------
with tab3:
    if st.session_state.excel_data_json is None:
        st.warning(
            "⚠️ لطفاً ابتدا در زبانه اول (📥 بارگذاری داده‌ها)، فایل اکسل اسناد"
            " را بارگذاری نمایید."
        )
    else:
        st.markdown("### ⚖️ ۳. دستیار تحلیلی حوزه مالی و نظارت بانکی")

        with st.expander("📌 **راهنمای تحلیلگر**", expanded=False):
            st.markdown("""
            **این بخش بر اساس استانداردهای نظارتی و مالی از جمله شاخص های CAMELS طراحی شده است:**
            - **وضعیت اخطار (Alert):** شناسایی انحرافات اعتباری، نقض آیین‌نامه‌ها، مطالبات غیرجاری یا کسر وثایق که نیازمند اخطار فوری به هیئت‌مدیره است.
            - **وضعیت ریکاوری (Recovery):** پیشنهاد برنامه‌های وصول مطالبات، ترمیم وثایق، امهال ضابطه‌مند و تجدید ارزیابی دارایی‌ها.
            - **وضعیت گزیر (Resolution):** پیش‌بینی اقدامات ساختاری، نقل و انتقال یا مداخلات قهری در صورت احراز ناترازی عمیق و تخلفات کلان.
            """)

        genai.configure(api_key=final_api_key, transport="rest")

        SYSTEM_PROMPT = """
تو به مانند یک تحلیلگر و متخصص نظارت بانکی، حسابرس و بازرس ویژه یا حسابرس ارشد و مستشار ارشد مدیریت ریسک و نظارت بر بانک‌ها و موسسات اعتباری هستید. به سوالات پاسخ صریح و روشن براساس متن ورودی بده و در ارائه توصیه و پیشنهاد راهکار اعلام کن که این صرفا تحلیل تو بر اساس داده های ورودی است و قبل از هر گونه اقدام با کارشناس متخصص این حوزه بررسی و تصمیم گیری لازم با سنجیدن همه ابعاد صورت پذیرد تا کمترین آسیب به شبکه بانکی و اعتماد مردم وارد شود. در پاسخ به سوالات گزارشات کلی و جامع و ارائه راهکار کلی و گزارشات تحلیل برای ناظر و بازرس و گزارش کلی ریسک حتما از بخش بندی مرتبط و جداول با آکون مناسب استفاده کن.
 وظایف اصلی شما در صورت مرتبط بودن سوال و نیاز:
۱. تحلیل دقیق داده‌ها با رویکرد بازرسی ویژه، کشف تخلفات آیین‌نامه‌ای، معوقات اعتباری و سوءجریانات احتمالی.
۲. تحلیل و تعیین پیش‌بینی کلان وضعیت پرونده/بانک بین فازهای چهارگانه استاندارد در مواجهه با بانک‌های ناتراز صرفا در صورت مرتبط بودن سوال:
- ⚠️"فاز پیشگیری و آمادگی (Prevention & Readiness)": حتی پیش از بروز بحران، همه بانک‌ها موظفند سناریوهای بحران (Stress Testing) را تمرین کرده و طرح‌های ریکاوری خود را از قبل بنویسند.
-⚠️ ". فاز مداخله زودهنگام "(Early Intervention)" ورود رسمی ناظر به محض دیدن اولین نشانه‌های ناترازی (اینجا محل صدور اخطار و هشدار و ابلاغ Action Plan است).
- 🔄 ". فاز بازسازی و ریکاوری (Recovery)": اجرای عملیات نجات دارایی‌ها توسط خودِ بانک تحت نظارت مقیم بانک مرکزی.
-. 🚨 "فاز گزیر یا حل و فصل(Resolution) ": سلب اختیار از مالکان و مدیریت دولتی/حاکمیتی بانک برای جلوگیری از سرایت بحران به کل بازار و ورود به فاز تسویه و خروج از بازار.

۳. ارائه KPIهای دقیق ریسک مالی (شامل تخلفات عمده، ریسک اعتباری و عملیاتی، کیفیت وثایق، کفایت سرمایه و غیره) صرفا در صورت مزتبط بودن سوال.

- پاسخ دقیق و بدون تصرف به سوالات کاربر و خواسته های آن در موضوع گزارشات مالی و نظارت بانکی براساس صرفا فایل ورودی است و نه چارچوب خارج از فایل ورودی. 
- همچنین فقط در صورت نیاز برای پاسخ به سایر استانداردها، شیوه نامه اقدام بانک های ناتراز و چارچوب های مالی مانند CAMELS توجه کن در غیر این صورت نیاز نیست. 

۴. الزامی: در تمامی پاسخ‌ها، هرجا به هر رکورد یا داده‌ای اشاره می‌کنید حتماً مرجع آن را با فرمت دقیق [مرجع: شیت X - ردیف Y] قید نمایید.
        """

        if st.session_state.cache_object is None:
            with st.spinner(
                "⏳ در حال تحلیل اسناد و آماده‌سازی مدل نظارتی ..."
            ):
                try:
                    cache_content = (
                        "اطلاعات اسناد جهت ارزیابی نظارتی و"
                        f" حسابرسی:\n\n{st.session_state.excel_data_json}"
                    )
                    try:
                        from google.generativeai import caching

                        cache = caching.CachedContent.create(
                            model=model_name,
                            display_name=(
                                "cag_audit_"
                                f"{st.session_state.cache_metadata.get('file_name', 'file')}"
                            ),
                            contents=[cache_content],
                            ttl=pd.Timedelta(minutes=ttl_minutes),
                        )
                        st.session_state.cache_object = cache
                    except Exception as e_cache:
                        st.session_state.cache_object = "IN_MEMORY"
                except Exception as e:
                    st.error(f"خطا در ارتباط با API گوگل: {str(e)}")

        st.markdown(
            "### 💬 دستیار تخصصی پرس‌وجو حوزه پایش سلامت و نظارت بانکی"
        )
        st.markdown(
            "می‌توانید سوالات تحلیلی، استعلام ردیف‌های دارای تخلف یا"
            " گزارش‌های تفکیکی را مطرح نمایید:"
        )

        cq1, cq2, cq3 = st.columns(3)
        preset_prompt = None
        if cq1.button(
            "📋 گزارش جامع تخلفات اعتباری", use_container_width=True
        ):
            preset_prompt = (
                "لطفاً گزارش جامعی از تمامی ردیف‌ها و مواردی که دارای تخلف از"
                " آیین‌نامه، معوقات اعتباری یا عدم اخذ وثایق کافی هستند با"
                " ارجاع دقیق به شیت و سطر ارائه دهید. سعی کن این گزارش تا حد"
                " امکان مبتنی بر دسته بندی شاخص های کملز CAMELS و سایر تخلفات"
                " مهم و موثر در شبکه بانکی با رویکرد سرایت به سایر سیستم بانکی"
                " باشد"
            )
        if cq2.button(
            "🔍 ارائه گزارش چند تخلف و ریسک عمده", use_container_width=True
        ):
            preset_prompt = (
                "کدام تخلفات و تخطی ها و گزارشات و ردیف‌ها دارای بالاترین سطح"
                " ریسک اعتباری/عملیاتی هستند؟ لیست ۵ مورد اول را با شماره شیت و"
                " سطر مشخص کن."
            )

        if cq3.button(
            "⚖️ گزارش تحلیلی برای ناظر و واحد بازرسی",
            use_container_width=True,
        ):
            preset_prompt = (
                "یک گزارش مدیریتی ساختاریافته در قالب جدول برای ارائه به"
                " هیئت‌مدیره، دستگاه ناظر و اداره ثبات و سلامت بانکی و بازرسی"
                " ویژه آماده کن که شامل خلاصه انحرافات و ارزیابی نهایی باشد."
            )

        for msg in st.session_state.messages:
            avatar_icon = "👤" if msg["role"] == "user" else "🤖"
            with st.chat_message(msg["role"], avatar=avatar_icon):
                st.markdown(msg["content"], unsafe_allow_html=True)

        user_input = st.chat_input(
            "سوال یا درخواست تحلیلی خود را در رابطه با پرونده‌ها و ریسک‌ها"
            " بنویسید..."
        )

        if preset_prompt:
            user_input = preset_prompt

        if user_input:
            st.session_state.messages.append(
                {"role": "user", "content": user_input}
            )
            with st.chat_message("user", avatar="👤"):
                st.markdown(user_input)

            with st.chat_message("assistant", avatar="🤖"):
                try:
                    if (
                        st.session_state.cache_object
                        and st.session_state.cache_object != "IN_MEMORY"
                    ):
                        prompt_to_send = user_input
                        cache_to_pass = st.session_state.cache_object
                    else:
                        prompt_to_send = (
                            "محتوای"
                            f" اسناد:\n{st.session_state.excel_data_json}\n\nسوال"
                            f" کاربر:\n{user_input}"
                        )
                        cache_to_pass = None

                    try:
                        response_stream, used_model = (
                            generate_content_with_retry_and_fallback(
                                prompt=prompt_to_send,
                                primary_model=model_name,
                                available_models=AVAILABLE_MODELS,
                                system_prompt=SYSTEM_PROMPT,
                                cached_object=cache_to_pass,
                                temp=temperature,
                                stream=True,
                            )
                        )

                        def get_stream_chunks():
                            for chunk in response_stream:
                                if chunk.text:
                                    yield chunk.text

                        ans_text = st.write_stream(get_stream_chunks())
                    except Exception as stream_err:
                        res_single, used_model = (
                            generate_content_with_retry_and_fallback(
                                prompt=prompt_to_send,
                                primary_model=model_name,
                                available_models=AVAILABLE_MODELS,
                                system_prompt=SYSTEM_PROMPT,
                                cached_object=cache_to_pass,
                                temp=temperature,
                                stream=False,
                            )
                        )
                        ans_text = res_single.text
                        st.markdown(ans_text)

                    st.session_state.messages.append(
                        {"role": "assistant", "content": ans_text}
                    )
                except Exception as err:
                    err_str = str(err)
                    if "429" in err_str or "Quota exceeded" in err_str:
                        st.error(
                            "⚠️ سهمیه روزانه یا لحظه‌ای مدل‌ها محدود شده است."
                            " چند ثانیه دیگر مجدداً تلاش نمایید."
                        )
                    else:
                        st.error(
                            f"❌ خطا در دریافت پاسخ از هوش مصنوعی: {err_str}"
                        )
