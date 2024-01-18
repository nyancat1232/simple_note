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
gen

def in_a_table(current_ts:TableStructure):
    with st.expander(f'expand {current_ts.schema_name}.{current_ts.table_name}'):
        try:
            res_df = current_ts.read()
            res_df
            st.write(res_df.dtypes)

            tabs = pps.TabsPlus('append','edit')
            with tabs['append']:
                                        
                tsr = current_ts.read()
                st.write(current_ts.expand_read())

                tt = current_ts.get_types()
                tt
                tf = current_ts.get_foreign_table()
                td = current_ts.get_default_value()
                cur_cols = tsr.columns.copy()
                exclude_defaults = st.multiselect(label=f'exclude {current_ts.schema_name}.{current_ts.table_name}',options=td.index)
                exclude_foreigns = st.multiselect(label=f'exclude foreign {current_ts.schema_name}.{current_ts.table_name}',options=tf.index)
                cur_cols = cur_cols.drop(exclude_defaults)
                cur_cols = cur_cols.drop(exclude_foreigns)
                up_value = {}

                stcols = st.columns(len(cur_cols))
                for ind,cur_col in enumerate(cur_cols):
                    with stcols[ind]:
                        ckey = f'{current_ts.schema_name}.{current_ts.table_name} {cur_col}'
                        match tt.loc[cur_col]['data_type']:
                            case 'text':
                                up_value[cur_col] = st.text_area(cur_col,key=ckey)
                            case 'bigint':
                                up_value[cur_col] = int(st.number_input(cur_col,step=1,key=ckey))
                            case 'integer':
                                up_value[cur_col] = int(st.number_input(cur_col,step=1,key=ckey))
                            case 'double precision':
                                up_value[cur_col] = st.number_input(cur_col,key=ckey)
                            case 'boolean':
                                up_value[cur_col] = st.checkbox(cur_col,key=ckey)
                            case 'date':
                                up_value[cur_col] = st.date_input(cur_col,key=ckey)
                            case 'ARRAY':
                                up_value[cur_col] = st.data_editor([''],num_rows='dynamic')
                            case _:
                                raise NotImplementedError(tt.loc[cur_col]['data_type'] )
                if st.button(f'upload {current_ts.schema_name}.{current_ts.table_name}'):

                    rr=current_ts.upload_append(**up_value)
                    rr

                                        
            with tabs['edit']:
                edit_df = st.data_editor(res_df) 
                new_df = edit_df.compare(res_df)
                new_df
                def iter_row(upload:bool=False):
                    for i in new_df.index:
                        current_row=edit_df.loc[i].dropna().to_dict()
                        current_row
                        if upload:
                            current_ts.upload(i,**current_row)
                iter_row()

                if st.button(f'{current_ts.schema_name}.{current_ts.table_name}'):
                    iter_row(upload=True)
        except Exception as e:
            st.write(e)

for g in gen:
    length = len(gen[g])
    cols = st.columns(length)
    for ind,col in enumerate(cols):

        with col:
            current_ts = gen[g][ind]
            in_a_table(current_ts)