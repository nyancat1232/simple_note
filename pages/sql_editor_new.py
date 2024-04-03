from pre import conn,ex,table_selector
ex()
import streamlit as st
import pyplus.sql as sqlp
import pyplus.streamlit as stp
import pandas as pd
from typing import Literal

with st.sidebar:
    schema,table=table_selector('select table')

first_ts = sqlp.TableStructure(schema,table,conn.engine)

def filter_new(df:pd.DataFrame,col='new')->pd.DataFrame:
    d={upper_col[0]:df[upper_col[0],col] for upper_col in df.columns}
    return pd.DataFrame(d)

def get_custom_column_configs(ts:sqlp.TableStructure):
    types = ts.get_types().to_dict(orient='index')
    types_link = {col for col in types if types[col]['domain_name'] == 'url'}
    types_img = {col for col in types if types[col]['domain_name'] == 'image_url'}

    column_configs = dict()
    for col in types_link:
        column_configs[col] = st.column_config.LinkColumn(f'{col}')
    for col in types_img:
        column_configs[col] = st.column_config.ImageColumn(f'{col}',)
    return column_configs

custom_configs = get_custom_column_configs(first_ts)

df_read = first_ts.read()
df_expanded = first_ts.read_expand()
if st.checkbox('readonly'):
    st.dataframe(df_expanded,column_config=custom_configs)
    st.stop()

df_edited = st.data_editor(df_expanded,disabled=first_ts.refresh_identity())

st.subheader('edit mode')

df_compare2=df_edited.compare(df_expanded,keep_equal=False,result_names=('new','old'))

df_new=filter_new(df_compare2)
recs = df_new.to_dict(orient='index')

for row in recs:
    row
    recs[row]

if st.button('upload'):
    for row in recs:
        row
        recs[row]
        first_ts.upload(row,**recs[row])


st.subheader('append mode')

df_append = df_expanded.copy()
df_append = df_append.loc[0:0]
df_append = df_append.reset_index(drop=True)

cols_append = df_append.columns.to_list()
cols_has_default_val = first_ts.get_default_value().index.to_list()
cols_default = [col for col in cols_append if col not in cols_has_default_val]
cols_append = st.multiselect(label=f'select {first_ts.schema_name}.{first_ts.table_name}',options=cols_append,default=cols_default)
df_append = df_append[cols_append]

df_append = st.data_editor(df_append,num_rows='dynamic')

appends = df_append.to_dict(orient='records')
if st.button('append'):
    for append in appends:
        first_ts.upload_append(**append)