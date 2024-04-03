import streamlit as st
from pre import ex,conn,init_schema
ex()

import pyplus.sql as sqlp

schema_list = init_schema()

ss = sqlp.SchemaStructure(schema_list,conn.engine)

if st.button('init domain'):
    ss.create_domain('url','text')
    ss.create_domain('image_url','text')