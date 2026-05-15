import streamlit as st
import sqlite3
import bcrypt
import pandas as pd

# --- إعدادات الصفحة ---
st.set_page_config(page_title="Secure User Management", layout="wide")

# --- CSS التصميم الاحترافي (Glassmorphism) ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0, 0, 0, 0.75), rgba(0, 0, 0, 0.75)), 
                    url('https://images.unsplash.com/photo-1550751827-4bd374c3f58b?q=80&w=2070') !important;
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
    }
    .main-title {
        color: #F5F5DC !important;
        text-align: center !important;
        font-size: 3.5rem !important;
        font-weight: 800 !important;
        margin-top: 20px !important;
    }
    .sub-title {
        color: #E2E8F0 !important;
        text-align: center !important;
        font-size: 1.1rem !important;
        margin-bottom: 30px !important;
    }
    /* تصميم الصندوق الزجاجي والتبويبات */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
        justify-content: center;
    }
    .stTabs [data-baseweb="tab"] {
        color: white !important;
        font-weight: bold !important;
    }
    div[data-testid="stExpander"], div[data-testid="stForm"] {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(15px) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 20px !important;
    }
    label p {
        color: #FFFFFF !important;
        font-weight: bold !important;
    }
    .stButton>button {
        background: linear-gradient(90deg, #3B82F6, #2563EB) !important;
        color: white !important;
        border-radius: 50px !important;
        width: 100% !important;
        font-weight: bold !important;
    }
    .footer {
        text-align: center !important;
        color: #F5F5DC !important;
        margin-top: 40px !important;
        opacity: 0.7;
    }
    </style>
    """, unsafe_allow_html=True)

# --- وظائف قاعدة البيانات ---
def init_db():
    conn = sqlite3.connect('users_secure.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT PRIMARY KEY, password TEXT, role TEXT)''')
    conn.commit()
    conn.close()

def hash_pw(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def check_pw(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

init_db()

# --- إدارة الجلسة ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None

# --- واجهة تسجيل الدخول والاشتراك ---
if not st.session_state.logged_in:
    st.markdown("<h1 class='main-title'>Secure User Management System</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-title'>Advanced Security Framework for Data Protection</p>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        tab1, tab2 = st.tabs(["🔑 Login", "📝 Sign Up"])
        
        with tab1:
            with st.form("login_form"):
                user_in = st.text_input("Username")
                pass_in = st.text_input("Password", type="password")
                if st.form_submit_button("SIGN IN"):
                    conn = sqlite3.connect('users_secure.db')
                    c = conn.cursor()
                    c.execute("SELECT password FROM users WHERE username=?", (user_in,))
                    res = c.fetchone()
                    conn.close()
                    if res and check_pw(pass_in, res[0]):
                        st.session_state.logged_in = True
                        st.session_state.user = user_in
                        st.rerun()
                    else:
                        st.error("Invalid Username or Password")

        with tab2:
            with st.form("signup_form"):
                new_user = st.text_input("Choose Username")
                new_pass = st.text_input("Choose Password", type="password")
                confirm_pass = st.text_input("Confirm Password", type="password")
                if st.form_submit_button("CREATE ACCOUNT"):
                    if new_pass != confirm_pass:
                        st.error("Passwords do not match!")
                    elif len(new_pass) < 6:
                        st.warning("Password should be at least 6 characters.")
                    else:
                        conn = sqlite3.connect('users_secure.db')
                        c = conn.cursor()
                        try:
                            c.execute("INSERT INTO users VALUES (?, ?, ?)", 
                                      (new_user, hash_pw(new_pass), "User"))
                            conn.commit()
                            st.success("Account created! Please login.")
                        except:
                            st.error("Username already taken.")
                        conn.close()

    st.markdown("<p class='footer'>YOUR SECURITY MATTERS</p>", unsafe_allow_html=True)

# --- لوحة التحكم بعد الدخول ---
else:
    st.sidebar.markdown(f"<h2 style='color:#F5F5DC;'>Welcome, {st.session_state.user}</h2>", unsafe_allow_html=True)
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    st.markdown("<h1 class='main-title' style='font-size:2.5rem;'>Dashboard</h1>", unsafe_allow_html=True)
    st.success(f"Secure session active for: {st.session_state.user}")
    
    # عرض البيانات (كمثال)
    with st.expander("View System Users"):
        conn = sqlite3.connect('users_secure.db')
        df = pd.read_sql_query("SELECT username, role FROM users", conn)
        st.table(df)
        conn.close()