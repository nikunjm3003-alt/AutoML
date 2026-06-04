import streamlit as st
import pandas as pd
from sqlalchemy import text
import uuid
import bcrypt
import secrets
from utils.mailer import send_verification_email, is_valid_email,is_real_email

from utils.style import set_login_background, set_app_background
from utils.preprocessor import load_and_preprocess
from utils.trainer import train_model
from utils.detector import detect

# Page configuration
st.set_page_config(page_title="AUTOML STUDIO", layout='centered')

# Establishing a connection
conn = st.connection('postgresql', type='sql')

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.username = None

params = st.query_params
token = params.get("token", "").strip()

if token:
    with conn.session as s:
        matched = s.execute(
            text("SELECT user_id FROM users_automl WHERE verify_token = :token"),
            {"token": token}
        ).fetchone()

        if matched:
            s.execute(
                text("UPDATE users_automl SET verified = TRUE, verify_token = NULL WHERE verify_token = :token"),
                {"token": token}
            )
            s.commit()
            st.success("Email verified! You can now log in.")
        else:
            st.warning("Invalid or already used verification link. If you already verified, just log in.")
    st.query_params.clear()
    st.stop()

# Registration and login page
def auth_page():
    
    set_login_background("assets/Backg.jpg")

    st.title("AutoML Studio")
    tab1, tab2 = st.tabs(["Register", "Login"])

    with tab1:
        new_un = st.text_input("Username", key='reg_un', placeholder="criticoflife54")
        new_email = st.text_input("Email", key='reg_mail', placeholder='criticoflife54@gmail.com')
        new_pw = st.text_input("Password", key='reg_pw', type='password', placeholder="********")

        if st.button("Register", use_container_width=True):
            with st.spinner("Just a sec...."):
                if not new_un or not new_email or not new_pw:
                    st.warning("Please fill in all the details")
                elif not is_valid_email(new_email):
                    st.warning("Please enter a valid email")
                elif not is_real_email(new_email):
                    st.warning("Please Enter a real email!!!")
                else:
                    try:
                        existing = conn.query(
                            "SELECT user_id FROM users_automl WHERE username = :un OR email = :mail",
                            params={"un": new_un, "mail": new_email},
                            ttl=0
                        )
                        if not existing.empty:
                            st.error("Username or email already registered")
                        else:
                            user_id = str(uuid.uuid4())
                            hashed_pw = bcrypt.hashpw(new_pw.encode(), bcrypt.gensalt()).decode()
                            verify_token = secrets.token_urlsafe(32)

                            try:
                                send_verification_email(new_email, new_un, verify_token)
                            except Exception:
                                st.error("Could not send verification email. Please check your email address and try again.")
                                st.stop()

                            with conn.session as s:
                                s.execute(
                                    text("""
                                        INSERT INTO users_automl(user_id, username, email, password, verified, verify_token)
                                        VALUES(:uid, :un, :mail, :pw, FALSE, :token)
                                    """),
                                    {"uid": user_id, "un": new_un, "mail": new_email, "pw": hashed_pw, "token": verify_token}
                                )
                                s.commit()
                            st.success("Registered! Check your email to verify your account.")
                    except Exception as e:
                        st.error(f"Database error: {e}")

    with tab2:
        login_un = st.text_input("Username", placeholder="levi", key='log_un')
        login_pass = st.text_input("Password", placeholder="your password", type='password', key='log_pass')

        if st.button("Login", use_container_width=True):
            with st.spinner("Just a sec...."):
                if not login_un or not login_pass:
                    st.warning("Please enter your details")
                else:
                    try:
                        result = conn.query(
                            "SELECT user_id, username, email, password, verified FROM users_automl WHERE LOWER(username) = LOWER(:un)",
                            params={"un": login_un},
                            ttl=0
                        )

                        if result.empty:
                            st.error("Invalid username or password")
                        else:
                            # DEBUG - remove after fixing
                            st.write("✅ User found:", result.iloc[0]['username'])
                            st.write("✅ Verified:", result.iloc[0]['verified'])
                            st.write("✅ Hash preview:", repr(result.iloc[0]['password'][:20]))
                            st.write("✅ BCrypt result:", bcrypt.checkpw(login_pass.encode(), result.iloc[0]['password'].strip().encode()))

                            stored_hash = result.iloc[0]['password']
                            if isinstance(stored_hash, str):
                                stored_hash = stored_hash.strip().encode()

                            if bcrypt.checkpw(login_pass.encode(), stored_hash):
                                if not result.iloc[0]['verified']:
                                    st.warning("⚠️ Please verify your email before logging in.")
                                    if st.button("Resend Verification Email", key="resend"):
                                        new_token = secrets.token_urlsafe(32)
                                        with conn.session as s:
                                            s.execute(
                                                text("UPDATE users_automl SET verify_token = :token WHERE username = :un"),
                                                {"token": new_token, "un": result.iloc[0]["username"]}
                                            )
                                            s.commit()
                                        try:
                                            send_verification_email(result.iloc[0]["email"], result.iloc[0]["username"], new_token)
                                            st.success("Verification email resent! Check your inbox.")
                                        except Exception:
                                            st.error("Could not resend verification email.")
                                else:
                                    st.session_state.logged_in = True
                                    st.session_state.user_id = result.iloc[0]["user_id"]
                                    st.session_state.username = result.iloc[0]["username"]
                                    st.success("Login Successful!")
                                    st.rerun()
                            else:
                                st.error("Invalid username or password!")
                    except Exception as e:
                        st.error(f"Database Connection Error: {e}")


if not st.session_state.logged_in:
    auth_page()
else:
    set_app_background("assets/Back2.jpg")

    # Hero title
    st.markdown("""
        <h1 style="font-family:'Orbitron',monospace; font-size:2.4rem; font-weight:700;
                   background: linear-gradient(90deg,#a78bfa,#60a5fa);
                   -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                   margin-bottom:0;"> AutoML Studio</h1>
        <p style="font-family:'Exo 2',sans-serif; color:rgba(200,200,255,0.7);
                  font-size:0.95rem; margin-top:4px; letter-spacing:0.04em;">
            Automated machine learning — upload, train, predict.
        </p>
    """, unsafe_allow_html=True)

    col_title, col_logout = st.columns([5, 1])
    with col_title:
        st.markdown(f"<p style='color:rgba(180,180,255,0.85); font-size:0.9rem;'>Logged in as <b>{st.session_state.username}</b></p>", unsafe_allow_html=True)
    with col_logout:
        if st.button("Logout", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    upload_file = st.file_uploader("Upload CSV", type=['csv'])

    if upload_file is not None:
        df = pd.read_csv(upload_file)
        st.dataframe(df.head())

        target_col = st.selectbox("Select Target Column", df.columns.tolist())

        if st.button("Train Model", use_container_width=True):
            with st.spinner("Training models...this may take a minute"):
                X, y, encoder, target_encoder, dropped_cols = load_and_preprocess(df.copy(), target_col)
                problem_type = detect(y)
                model, best_model_name, results_df = train_model(X, y, problem_type)

                st.session_state.model = model
                st.session_state.encoder = encoder
                st.session_state.target_encoder = target_encoder
                st.session_state.results_df = results_df
                st.session_state.best_model_name = best_model_name
                st.session_state.problem_type = problem_type
                st.session_state.feature_names = X.columns.tolist()
                st.session_state.df = df
                st.session_state.target_col = target_col
                st.session_state.dropped_cols = dropped_cols

            st.success(f"Training Complete! Best Model : **{best_model_name}** ({problem_type})")

    if st.session_state.get('model') is not None:
        st.divider()
        st.subheader("Navigate to")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Dashboard", use_container_width=True):
                st.switch_page("pages/1_dashboard.py")
        with col2:
            if st.button("Predictions", use_container_width=True):
                st.switch_page("pages/2_predictions.py")