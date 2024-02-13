import streamlit as st
import pyplus.streamlit as stp
from sqlutil.sql_util_new import table_selector
from pyplus.sql import TableStructure 

if not stp.check_password():
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

            tabs = stp.TabsPlus('append','edit')
            with tabs['append']:
                                        
                tsr = res_df.copy()

                tt = current_ts.get_types()
                tt
                tf = current_ts.get_foreign_table()
                td = current_ts.get_default_value()
                cur_cols = tsr.columns.copy()
                exclude_defaults = st.multiselect(label=f'exclude {current_ts.schema_name}.{current_ts.table_name}',options=td.index)
                exclude_foreigns = st.multiselect(label=f'exclude foreign {current_ts.schema_name}.{current_ts.table_name}',options=tf.index)
                cur_cols = cur_cols.drop(exclude_defaults)
                cur_cols = cur_cols.drop(exclude_foreigns)
                cur_cols

                cur_cols_dtype = {col:tsr.dtypes[col] for col in cur_cols}
                cur_cols_dtype

                up_value = {col:[None] for col in cur_cols}
                def define_streamlit_column(pd_type:str):
                    match pd_type:
                        case "datetime64[ns]":
                            return st.column_config.DatetimeColumn()
                        case "datetime64[ns, UTC]":
                            return st.column_config.DatetimeColumn(timezone="UTC")
                        case "Int64":
                            return st.column_config.NumberColumn(step=1)
                        case "Float64":
                            return st.column_config.NumberColumn()
                        case "string":
                            return st.column_config.TextColumn()
                        case "boolean":
                            return st.column_config.CheckboxColumn()
                        case _:
                            raise NotImplementedError(f"{pd_type} Not implemented. Report this error.")

                up_col_config = {col:define_streamlit_column(cur_cols_dtype[col]) for col in cur_cols}
                up_value = st.data_editor(up_value,num_rows='dynamic',column_config=up_col_config)


                



                if st.button(f'upload {current_ts.schema_name}.{current_ts.table_name}'):
                    def ite_row():
                        def get_row_count():
                            for col in up_value:
                                return len(up_value[col])
                        for row in range(get_row_count()):
                            yield {col:up_value[col][row] for col in up_value}
                    for cur_row in ite_row():
                        rr=current_ts.upload_append(**cur_row)
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