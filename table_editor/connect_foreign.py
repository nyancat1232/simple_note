import streamlit as st
import pyplus.streamlit as stp
import pandas as pd
import pyplus.sql as sqlp

"Need to implement second table selection"
conn = st.session_state['conn']
ts:sqlp.TableStructure = st.session_state['selected_table']
df:pd.DataFrame = st.session_state['selected_table_dataframe']

selected_column_left = st.dataframe(df,on_select='rerun',selection_mode='single-column')['selection']['columns']
if not selected_column_left:
    selected_column_left = st.text_input('New column name')
    override = False
else:
    selected_column_left = selected_column_left[0]
    override = True

all_tables= sqlp.get_table_list(st.session_state['conn'].engine).to_dict('records')
address_right=st.selectbox('select a second table',all_tables,format_func=lambda x:f"{x['table_schema']}/{x['table_name']}")

ts_right = sqlp.TableStructure(schema_name=address_right['table_schema'],table_name=address_right['table_name'],engine=st.session_state['conn'].engine)
df_right = ts_right.read()
if override:
    selected_column_right = st.dataframe(df_right,on_select='rerun',selection_mode='single-column')['selection']['columns']

    if not selected_column_right:
        selected_column_right = ts_right.get_identity()[0]
    df_merged = df.merge(df_right.reset_index(),left_on=selected_column_left,right_on=selected_column_right,how='left')
    df_merged
else:
    df_right
    if st.button('upload'):
        st.toast('uploading')
        ts.append_column(**{selected_column_left:'bigint'})
        ts.connect_foreign_column(ts_right,selected_column_left)
        st.rerun()

st.stop()

tp=stp.TabsPlus(layout='column',titles=['original','foreign'])
with tp['original']:
    ts_left=table_selector()
with tp['foreign']:
    ts_right=table_selector('select a foreign table')
with tp['original']:
    df_left=ts_left.read()
    event_left = st.dataframe(df_left,on_select='rerun',selection_mode='single-column')
with tp['foreign']:
    df_right=ts_right.read()
    event_right = st.dataframe(df_right,on_select='rerun',selection_mode='single-column')

left_column = event_left['selection']['columns'][0]
try:
    right_column = event_right['selection']['columns'][0]
    df_right_to_id = ts_right.get_local_val_to_id(right_column)
except:
    df_right_to_id = {val:val for val in df_right.index.to_list()}

def apply_foreign(val):
    if val in df_right_to_id:
        return df_right_to_id[val]
    else:
        return None

override = st.checkbox('override a column')
if override:
    #Overriding a column

    ser_override_column=df_left[left_column].apply(lambda val:apply_foreign(val))
    df_left[left_column]=ser_override_column
    df_left
    "changing column to"
    ser_override_column
    "connect"
    f"{left_column} and {ts_right.column_identity[0]}"
    if st.button('upload'):
        upload_val = ser_override_column.to_dict()
        st.toast('override existing column')
        for id in upload_val:
            ts_left.upload(id,**{ser_override_column.name:upload_val[id]})
            st.toast([id,{ser_override_column.name:upload_val[id]}])
        st.toast('connect foreign column')
        ts_left.connect_foreign_column(ts_right,left_column)
        st.rerun()

else:
    local_column = st.text_input('new id column name')

    ser_new_col=df_left[left_column].apply(lambda val:apply_foreign(val))
    ser_new_col=ser_new_col.astype("Int64")
    ser_new_col.name = local_column
    df_disp_res=pd.concat([df_left,ser_new_col],axis=1)
    df_disp_res
    "append column"
    ser_new_col
    "connect"
    f"{ser_new_col.name} and {ts_right.column_identity[0]}"
    if st.button('upload'):
        st.toast(f'create a column {ser_new_col.name}')
        ts_left.append_column(**{ser_new_col.name:"bigint"})
        upload_val = ser_new_col.to_dict()
        st.toast('upload a column')
        for id in upload_val:
            ts_left.upload(id,**{ser_new_col.name:upload_val[id]})
            st.toast([id,{ser_new_col.name:upload_val[id]}])
        st.toast('connect foreign column')
        ts_left.connect_foreign_column(ts_right,ser_new_col.name)
        st.rerun()