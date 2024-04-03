import streamlit as st
from pre import ex,conn,init_schema
ex()

import pyplus.sql as sqlp

ss = sqlp.SchemaStructure('public',conn.engine)

if st.button('init domain'):
    ss.create_domain('url','text')
    ss.create_domain('image_url','text')