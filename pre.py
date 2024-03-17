import streamlit as st
import pyplus.streamlit as stp

def ex():
    if not stp.check_password():
        st.stop()
conn = st.connection('myaddress',type='sql')