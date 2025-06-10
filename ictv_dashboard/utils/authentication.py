"""
Simple Authentication for ICTV Dashboard

Provides basic password protection for committee access.
For production, this should be enhanced with proper user management.
"""

import streamlit as st
import hashlib

# In production, these would be stored securely (e.g., environment variables)
# For now, using simple demo credentials
DEMO_PASSWORDS = {
    "committee": "ictv2025",  # General committee access
    "admin": "admin2025",     # Admin access
    "demo": "demo123"         # Demo access for testing
}

def hash_password(password: str) -> str:
    """Hash a password for storing."""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(stored_password_hash: str, provided_password: str) -> bool:
    """Verify a stored password against provided password."""
    return stored_password_hash == hash_password(provided_password)

def check_password() -> bool:
    """Returns True if the user had the correct password."""
    
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        provided_password = st.session_state["password"]
        
        # Check against demo passwords
        for user, password in DEMO_PASSWORDS.items():
            if provided_password == password:
                st.session_state["password_correct"] = True
                st.session_state["user_role"] = "admin" if user == "admin" else "member"
                del st.session_state["password"]  # Don't store password
                return
        
        st.session_state["password_correct"] = False

    # First run or password incorrect
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
        
    if not st.session_state["password_correct"]:
        # Show input for password
        st.markdown("## 🔐 ICTV Dashboard Login")
        st.text_input(
            "Password", 
            type="password", 
            on_change=password_entered, 
            key="password",
            help="Contact ICTV committee for access credentials"
        )
        
        # Show demo hint for testing
        with st.expander("Demo Access"):
            st.info("""
            **For testing purposes:**
            - General access: `demo123`
            - Committee access: `committee` / `ictv2025`
            - Admin access: `admin` / `admin2025`
            """)
        
        if st.session_state.get("password_correct") == False:
            st.error("😕 Password incorrect")
        
        st.stop()
        return False
    
    else:
        # Password correct
        return True

def get_user_role() -> str:
    """Get the current user's role."""
    return st.session_state.get("user_role", "member")

def logout():
    """Log out the current user."""
    for key in ["password_correct", "user_role"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

def show_login_status():
    """Display login status in sidebar."""
    if st.session_state.get("password_correct"):
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"**Logged in as:** {get_user_role()}")
        if st.sidebar.button("Logout"):
            logout()