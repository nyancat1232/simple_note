import streamlit as st
import pyplus.streamlit as stp

def ex():
    if not stp.check_password():
        st.stop()
if 'conn' not in st.session_state:
    st.session_state['conn'] = st.connection('myaddress',type='sql')

conn = st.session_state['conn']