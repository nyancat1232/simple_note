import streamlit as st

import pyplus.sql as sqlp

if st.button('init domain'):
    sqlp.create_domain(st.session_state['conn'].engine,'url','text')
    sqlp.create_domain(st.session_state['conn'].engine,'image_url','text')
    sqlp.create_domain(st.session_state['conn'].engine,'video_url','text')
    sqlp.create_domain(st.session_state['conn'].engine,'text_with_tag','text')
    st.toast('Initialization succeed domain')