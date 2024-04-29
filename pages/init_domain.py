import streamlit as st
from pre import ex,conn,sn_config_table
ex()

import pyplus.sql as sqlp

if st.button('init domain'):
    sqlp.create_domain(conn.engine,'url','text')
    sqlp.create_domain(conn.engine,'image_url','text')
    sqlp.create_domain(conn.engine,'text_with_tag','text')

if st.button('init setting'):
    sn_conf = sqlp.create_schema(conn.engine,sn_config_table['schema'])
    ts = sn_conf.create_table(sn_config_table['table'],**{'name':'text','value':'text'})
    ts.upload_append(**{'name':'recent_address'})

    def upload_table_content(table_name,**types):
        sn_conf.create_table(table_name,**types)
        ts.upload_append(**{'name':f'address_{table_name}','value':f'{sn_config_table['schema']}.{table_name}'})
    upload_table_content('tag_content',**{'content':'text','tags':'text[]','date':'timestamp with time zone'})
    upload_table_content('timer_content',**{'content':'text','type':'text','start_time':'timestamp with time zone'})