import streamlit as st
from pyplus.sql.pgplus import read_from_server,get_default_value,get_foreign_keys,get_identity,get_table_list
from dataclasses import dataclass

def r_d_sql(schema_name,table_name,st_conn,expand_column=True):
    result = read_from_server(schema_name=schema_name,table_name=table_name,st_conn=st_conn)
    st.subheader(f'result of {schema_name}.{table_name}')
    #result = result.sort_index()
    #result = result.drop(columns=identity)
    st.dataframe(result)
    
    df_foreign_keys = get_foreign_keys(schema_name,table_name,st_conn)
    list_foreign_keys = df_foreign_keys.index.to_list()
    st.write('v')
    try:
        
        if expand_column:
            columns = st.columns(len(list_foreign_keys))
            for index,row in enumerate(list_foreign_keys):
                with columns[index]:
                    r_d_sql(schema_name=df_foreign_keys.loc[row,'upper_schema'],table_name=df_foreign_keys.loc[row,'upper_table'],st_conn=st_conn,expand_column=False)
        else:
            for index,row in enumerate(list_foreign_keys):
                r_d_sql(schema_name=df_foreign_keys.loc[row,'upper_schema'],table_name=df_foreign_keys.loc[row,'upper_table'],st_conn=st_conn,expand_column=False)
    except:
        st.write("No foreign keys")

    st.subheader(f'upload {schema_name}.{table_name}')
    df_set_default_values = get_default_value(schema_name,table_name,st_conn)

    st.subheader(f'select what you want to apply default')
    exclude_columns=[]
    for dk in df_set_default_values.index:
        if st.checkbox(f'{dk}',value=True,key=f'{schema_name}.{table_name}.{dk}'):
            exclude_columns.append( dk )

    for fk in list_foreign_keys:
        if st.checkbox(f'{fk}',value=True,key=f'{schema_name}.{table_name}.{fk}'):
            exclude_columns.append( fk )
    
    st.write(exclude_columns)

    #st.write(list_foreign_keys,df_set_default_values)

    result_to_append = result.copy()
    result_to_append = result_to_append.drop(labels=result.index,axis=0)
    result_to_append = result_to_append.reset_index(drop=True)
    result_to_append = result_to_append.drop(labels=exclude_columns,axis=1)
    
    #categorize foreign keys
    config_append_col = {}
    for foreign_key in df_foreign_keys.index:
        us = df_foreign_keys.at[foreign_key,'upper_schema']
        ut = df_foreign_keys.at[foreign_key,'upper_table']

        result_fk = read_from_server(schema_name=us,table_name=ut,st_conn=st_conn)
        result_fk['_display']=result_fk.apply(lambda columns:" ".join(list(map(str,columns))),axis=1)

        config_append_col[foreign_key] = st.column_config.SelectboxColumn(options=result_fk.index)

    result_to_append
    result_to_append = st.data_editor(result_to_append,num_rows="dynamic",column_config=config_append_col,)
    if st.button(f'upload {schema_name}.{table_name}'):
        result_to_append.to_sql(name=table_name,con=st_conn.connect(),schema=schema_name,index=False,if_exists='append')
        st.rerun()

@dataclass
class TableInput:
    schema : str
    table : str

def table_selection(st_conn,label:str):
    '''
    table selection by using streamlit library.
    ## Parameters:
    st_conn : SQLconnection
    (arg_description).
    ## Examples:
    import streamlit as st

    st_conn = st.connection(name='postgresql',type='sql')

    with st.sidebar:
        input = table_selection(st_conn)
    '''
    df_list=get_table_list(st_conn)
    st.dataframe(df_list)

    
    schema = st.selectbox(label=f'{label} of schema',options=df_list['table_schema'].unique())
    table = st.selectbox(label=f"{label} of table",options=df_list['table_name'][df_list['table_schema']==schema])
    return TableInput(schema,table)