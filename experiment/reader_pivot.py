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
        compress = st.checkbox('compress columns',value=False)
    with tp.value:
        valuees= st.dataframe(df,on_select='rerun',selection_mode='multi-column',key='reader_pivot_value')['selection']['columns']
    df_pivot = df.pivot_table(index=indexs,columns=columns,values=valuees,aggfunc=agg_func,margins=True)
    column_configs={}
    if compress:
        df_pivot = df_pivot.fillna(0.)
        buffer = {}
        for super_col in valuees:
            vvvv = df_pivot[super_col].apply(lambda row:[val for val in row],axis=1)
            buffer[super_col]=vvvv
            column_configs[super_col]=st.column_config.LineChartColumn(f'{super_col}')
        df_pivot = pd.DataFrame(buffer)
    st.dataframe(df_pivot,column_config=column_configs)

processing(df)