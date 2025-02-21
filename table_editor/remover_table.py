import streamlit as st
import pandas as pd
import pyplus.sql as sqlp
import pyplus.streamlit as stp

"load"
ts:sqlp.TableStructure = st.session_state['global_selected_table']
df= st.session_state['global_selected_table_dataframe']
df

"select"
@st.fragment
def select_deletion(df:pd.DataFrame,ts:sqlp.TableStructure):
    event = st.dataframe(df,on_select='rerun',selection_mode=['multi-column','multi-row'])
    event

    "remove col"
    df[event['selection']['columns']]
    event['selection']['columns']
    if st.button('delete columns'):
        for col in event['selection']['columns']:
            st.toast(col)
            ts.delete_column(col)
        st.rerun()

    "remove row"
    df_filtered_row=df.iloc[event['selection']['rows']]
    rows=df_filtered_row.index.to_list()
    rows
    if st.button('delete rows'):
        for row in rows:
            st.toast(row)
            ts.delete_row(row)
        st.rerun()

tp = stp.TabsPlus(titles=['row_col'])
with tp.row_col:
    select_deletion(df,ts)