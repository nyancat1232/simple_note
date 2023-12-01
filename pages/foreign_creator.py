import streamlit as st
import pandas as pd
from pyplus.streamlit.external import check_password
from pyplus.sql.pgplus import read_from_server,get_columns,write_to_server,create_empty_with_id_with_column
from sqlutil.sql_util import table_selection

if not check_password():
    st.stop()  # Do not continue if check_password is not True.


    
st_connff = st.connection(name='postgresql',type='sql')


with st.sidebar:
    input = table_selection(st_connff,'input')

st.subheader('total')
df_data = read_from_server(schema_name=input.schema,table_name=input.table,st_conn=st_connff)
df_data_colums = get_columns(schema_name=input.schema,table_name=input.table,st_conn=st_connff)
st.dataframe(df_data)

foreign_column = st.multiselect(label='create as foreign key of',options=df_data.columns)

st.write('rr')

df_create_foreign = df_data[foreign_column].drop_duplicates()
df_create_foreign
_dict_col=df_data_colums.loc[foreign_column].to_dict()['data_type']
_dict_col

#df_create_foreign.insert(0,'_id',0)
#for one,two in enumerate(df_create_foreign.iterrows()):
#    df_create_foreign.at[two[0],'_id']=one
#
#df_create_foreign
#_merge_for_left={
#    'left':df_data,
#    'left_on':foreign_column
#}
#_merge_for_right={
#    'right':df_create_foreign,
#    'right_on':foreign_column
#}
#first_place=df_data.columns.to_list().index(foreign_column[0])
#first_place
#df_original = pd.merge(**_merge_for_left,**_merge_for_right,how='inner')
#df_original = df_original.drop(columns=foreign_column)
#
#col_order = df_original.columns
#col_order = col_order.drop('_id')
#col_order = col_order.insert(first_place,'_id')
#
#df_original[col_order]

def create_as_foreign_key(df_input_create_foreign):
    write_to_server(df_data,input.schema,input.table+'_backup',st_connff)
    create_empty_with_id_with_column(_dict_col,input.schema,input.table+'_foreign',st_connff)
    write_to_server(df_create_foreign,input.schema,input.table+'_foreign',st_connff)

st.button('write',on_click=create_as_foreign_key,args=[df_create_foreign])