import streamlit as st
from pre import ex,conn,tag_table
ex()

import pyplus.sql as sqlp

if st.button('init domain'):
    sqlp.create_domain(conn.engine,'url','text')
    sqlp.create_domain(conn.engine,'image_url','text')
    sqlp.create_domain(conn.engine,'text_with_tag','text')

if st.button('init setting'):
    sn_conf = sqlp.create_schema(conn.engine,tag_table['schema'])
    ts = sn_conf.create_table(tag_table['table'],**{'name':'text','val':'text'})
    ts.upload_append(**{'name':'recent_address'})
    ts.upload_append(**{'name':'address_tags'})