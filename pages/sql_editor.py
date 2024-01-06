import streamlit as st
from pyplus.streamlit.external import check_password
from sqlutil.sql_util_new import table_selector
from pyplus.sql import TableStructure 
import pyplus.streamlit as pps

if not check_password():
    st.stop()  # Do not continue if check_password is not True.



st_connff = st.connection(name='simple_note',type='sql')


with st.sidebar:
    schema,table = table_selector(st_connff,'input')
    st.button('refresh',on_click=st.rerun)


st.subheader('total')
first_ts = TableStructure(schema_name=schema,table_name=table,
                    engine=st_connff.engine)
st.dataframe(first_ts.expand_read())

children = first_ts.get_all_children()

from typing import Dict,List
gen:Dict[int,List[TableStructure]] = {}
for child in children:
    try:
        gen[child.generation].append(child)
    except:
        gen[child.generation] = []
        gen[child.generation].append(child)

for g in gen:
    length = len(gen[g])
    cols = st.columns(length)
    for col in range(length):
        with cols[col]:
            current_ts = gen[g][col]
            with st.expander(f'expand {current_ts.schema_name}.{current_ts.table_name}'):
                try:
                    res_df = current_ts.read()
                    res_df

                    tabs = pps.TabsPlus('append','edit')

                    with tabs['edit']:
                        edit_df = st.data_editor(res_df) 
                        new_df = edit_df.compare(res_df)
                        new_df
                        if st.button(f'{current_ts.schema_name}.{current_ts.table_name}'):
                            for i in new_df.index:
                                current_row=edit_df.loc[i].to_dict()
                                current_row
                                current_ts.upload(i,**current_row)
                except:
                    st.write('duplicated')