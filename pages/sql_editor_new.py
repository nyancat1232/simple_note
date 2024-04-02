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


def creation(type:Literal['bool','str'],rows,cols)->pd.DataFrame:
    match type:
        case 'bool':
            return pd.DataFrame({col:[False for _ in rows] for col in cols}).set_index(rows)
        case 'str':
            return pd.DataFrame({col:[None for _ in rows] for col in cols}).set_index(rows)

def get_foreign_id_from_value(readd:pd.DataFrame,expand:pd.DataFrame,row,column):
    '''
        a.b c.d
    30  3   4

    get_foreign_id_from_value(.., .., 30, a.b)
    result : the foreign id of (30,a.b)
    '''
    def id_repeat(readd:pd.DataFrame,expand:pd.DataFrame):
        df_copy = readd.copy()
        col_sub = {col:col[:col.find('.')] for col in expand.columns if col.find('.')!=-1}
        for col in col_sub:
            df_copy[col] = df_copy[col_sub[col]]
        return df_copy
    df_repeat=id_repeat(readd,expand)
    return df_repeat.loc[row,column]

def get_mode_by_compare_table(df_compare:pd.DataFrame):
    df_mode = creation('str',df_compare.index,filter_new(df_compare).columns)
    for row in df_compare.index:
        for column in df_compare.columns:
            v = df_compare.loc[row,column[0]]
            na_new = v.loc['new'] is pd.NA
            na_old = v.loc['old'] is pd.NA
            if not na_new and not na_old:
                df_mode.loc[row,column[0]]='U'
            elif not na_new and na_old:
                df_mode.loc[row,column[0]]='A'
            elif na_new and not na_old:
                df_mode.loc[row,column[0]]='D'
    return df_mode

def get_mode(comp:pd.DataFrame,readd:pd.DataFrame,expand:pd.DataFrame)->pd.DataFrame:
    df_new_ids = creation('str',comp.index,comp.columns)
    for ind in df_new_ids.index:
        for col in df_new_ids.columns:
            val_comp = comp.loc[ind,col]
            foreign_id = get_foreign_id_from_value(readd,expand,ind,col)
            if val_comp is not pd.NA:
                if foreign_id is pd.NA:
                    df_new_ids.loc[ind,col] = 'A'
                else:
                    df_new_ids.loc[ind,col] = 'U'
    return df_new_ids


def get_mode_points(df_mode:pd.DataFrame)->list[dict]:
    df_temp = df_mode
    split=df_temp.to_dict(orient='split')
    temp = [
            [
                {
                    'row':split['index'][ind],'col':split['columns'][col],'mode':val
                }
                for col,val in enumerate(line) if val is not None
            ] 
            for ind,line in enumerate(split['data'])
        ]
    ret = []
    for dim0 in temp:
        ret += dim0

    return ret

def get_vals(l:list[dict],df:pd.DataFrame)->list[dict]:
    cp = l.copy()
    for point in cp:
        point['val'] = df.loc[point['row'],point['col']]
    return cp

def col_to_colinf(l:list[dict])->list[dict]:
    cp = l.copy()
    for di in cp:
        di['col'] = get_column_address(di['col'])
    return cp

def get_column_address(col_name:str)->dict:
    return {'address':col_name.split(".")[:-1], 'column_name':col_name.split(".")[-1]}

df_read = first_ts.read()
df_expanded = first_ts.read_expand()
index_expanded = df_expanded.index
df_edited = st.data_editor(df_expanded.reset_index(drop=True),num_rows='dynamic')
index_edited = df_edited.index
if len(index_edited)==len(index_expanded):
    st.subheader('edit mode')
    df_edited_with_index = df_edited.copy()
    df_edited_with_index.index = index_expanded

    df_compare2=df_edited_with_index.compare(df_expanded,keep_equal=False,result_names=('new','old'))
    
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
else:
    st.subheader('append mode')

