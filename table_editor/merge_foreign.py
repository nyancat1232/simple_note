import streamlit as st
import pyplus.sql as sqlp


with st.sidebar:
    all_records_list= sqlp.get_table_list(st.session_state['conn'].engine).to_dict('records')
    all_table_list = [".".join([row['table_schema'],row['table_name']]) for row in all_records_list]
    current_address = st.selectbox('select address',all_table_list).split('.')
    ts = sqlp.TableStructure(schema_name=current_address[0],table_name=current_address[1],engine=st.session_state['conn'].engine)


"load"
df_expand = ts.read_expand()
df_expand

"select"
foreigns = ts.get_foreign_tables()
merge = st.selectbox('merge this local foreign id',foreigns)

"rename"
def apply_check(col):
    new_col=col[col.find('.')+1:] 
    if new_col in df_expand.columns:
        return new_col+'__'+col[:col.find('.')]
    else:
        return new_col
replacer = {col:apply_check(col) for col in df_expand.columns if col.startswith(merge+'.')}
df_expand = df_expand.rename(columns= replacer)
df_expand

"filter uploader"
df_expand = df_expand[[replacer[key] for key in replacer]]
df_expand