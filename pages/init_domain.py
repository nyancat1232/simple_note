import streamlit as st
from pre import ex,conn
ex()

import pyplus.sql as sqlp

if st.button('init domain'):
    sqlp.create_domain(conn.engine,'url','text')
    sqlp.create_domain(conn.engine,'image_url','text')
    sqlp.create_domain(conn.engine,'text_with_tag','text')
    st.toast('Initialization succeed domain')