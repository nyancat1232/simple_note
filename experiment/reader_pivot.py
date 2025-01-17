import streamlit as st
import pyplus.streamlit as stp
import pandas as pd

selected_table = st.session_state['selected_table'] 
df:pd.DataFrame = st.session_state['selected_table_dataframe']

@st.fragment
def processing(df:pd.DataFrame):
    tp = stp.TabsPlus(titles=['index','column','value'],layout='column',hide_titles=False)
    with tp.index:
        indexs= st.dataframe(df,on_select='rerun',selection_mode='multi-column',key='reader_pivot_index')['selection']['columns']
        agg_func = st.selectbox('aggregation',
                                ['count',
                                'sum',
                                'mean',
                                'median',
                                'min',
                                'max',
                                'mode',
                                'abs',
                                'prod',
                                'std',
                                'var',
                                'sem',
                                'skew',
                                'kurt',
                                'quantile',
                                'cumsum',
                                'cumprod',
                                'cummax',
                                'cummin']
                                )
        
    with tp.column:
        columns= st.dataframe(df,on_select='rerun',selection_mode='multi-column',key='reader_pivot_column')['selection']['columns']
    with tp.value:
        valuees= st.dataframe(df,on_select='rerun',selection_mode='multi-column',key='reader_pivot_value')['selection']['columns']
    df_pivot = df.pivot_table(index=indexs,columns=columns,values=valuees,aggfunc=agg_func,margins=True)
    st.dataframe(df_pivot)

processing(df)