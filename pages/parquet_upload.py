import streamlit as st
from pre import ex,conn,table_selector
ex()

import pandas as pd
import pyplus.streamlit as stp
import pyplus.sql as sqlp
from datetime import datetime


with st.sidebar:
    fe = stp.FileExecutor()
    fe += "^[A-Za-z0-9_]+.parquet$",pd.read_parquet
    
    dfs = fe()
    current_timezone = st.text_input('input time zone')


for key in dfs:
    schema,table = table_selector(label='input')

    df_from = dfs[key]
    if st.checkbox('Reverse index of the file'):
        df_from = df_from[::-1]
    df_from = df_from.reset_index()

    ts_to = sqlp.TableStructure(schema_name=schema,table_name=table,engine=conn.engine)
    df_to = ts_to.read().reset_index()

    stp.write_columns(df_from,df_to)

    
    df_direction = pd.DataFrame({'from':df_from.columns,
                                 'to':pd.Categorical([None for _ in df_from],categories=df_to.columns)})

    st.subheader('Select a column')
    df_direction=st.data_editor(df_direction,disabled=['from'])
    df_direction=df_direction.dropna()

    df_foreign = ts_to.get_foreign_table()
    df_foreign


    df_converted = df_from[df_direction['from']]
    for column_from,column_to in zip(df_direction['from'],df_direction['to']):
        if column_to in df_foreign.index:
            inf = df_foreign.loc[column_to].to_dict()
            ts_foreign = sqlp.TableStructure(schema_name=inf['upper_schema'],table_name=inf['upper_table'],engine=conn.engine)
            df_from_foreign = ts_foreign.read()
            target = st.selectbox(f'convert {column_to} to ',df_from_foreign.columns.to_list())
            convert_table = ts_to.get_foreign_direction(column_to,target)
            convert_table

            df_converted[column_from] = df_converted[column_from].apply(lambda v:convert_table[v])

        if df_converted.dtypes[column_from] == 'datetime64[ns]':
            df_converted[column_from] = df_converted[column_from].dt.tz_localize(current_timezone)
    renamer={d['from']:d['to'] for d in df_direction.to_dict('records')}
    df_converted = df_converted.rename(columns=renamer)
    df_converted

    if st.button('upload'):
        for row in df_converted.index:
            if row%100 == 0:
                st.toast(df_converted.loc[row])
            ts_to.upload_append(**df_converted.loc[row].to_dict())