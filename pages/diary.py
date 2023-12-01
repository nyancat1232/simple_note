from pyplus.streamlit.external import check_password
import streamlit as st

if not check_password():
    st.stop()  # Do not continue if check_password is not True.

