import streamlit as st
import pandas as pd
import pyplus.streamlit as stp


from pre import ex,conn
ex()

tab_name = ['new','open']
file_tab = stp.TabsPlus(*tab_name)
with file_tab['new']:

    #all_dtype=pd.read_html("https://pandas.pydata.org/docs/user_guide/basics.html#basics-dtypes")[3]["String Aliases"]

    all_dtype=["datetime64[ns]"\
                ,"category"\
                #,"period[<freq>]"\
                #,'Sparse', 'Sparse[int]', 'Sparse[float]'\
                #,'interval', 'Interval[<numpy_dtype>]', 'Interval[datetime64[ns, <tz>]]','Interval[timedelta64[<freq>]]'\
                ,'Int8', 'Int16', 'Int32', 'Int64', 'UInt8', 'UInt16', 'UInt32', 'UInt64'\
                ,'Float32', 'Float64'\
                ,'string'\
                ,'boolean'
                ]
    new_df_dtype = pd.DataFrame({'name':[''],'dtype':pd.Categorical([None],categories=all_dtype),'index':[False]})
    new_df_dtype = st.data_editor(new_df_dtype,num_rows="dynamic",hide_index=True)
    
    new_dict_dtypes = new_df_dtype.to_dict(orient='records')
    new_df = pd.DataFrame({rec['name']:pd.Series([],dtype=rec['dtype']) for rec in new_dict_dtypes })
    new_df=st.data_editor(new_df,num_rows="dynamic")
    new_df=new_df.set_index(new_df_dtype['name'][new_df_dtype['index']==True].to_list())

    st.dataframe(new_df)
    filename = st.text_input(label='filename',value='out')
    st.download_button(label='download parquet (new)',data=new_df.to_parquet(),file_name=f'{filename}.parquet')

with file_tab['open']:
    new_df=None
    
    file = st.file_uploader('parquet test',type='parquet')
    file_df = pd.read_parquet(path=file,)
    file_df=st.data_editor(file_df,num_rows="dynamic")

    st.markdown("---")
    file_df = file_df.reset_index()
    df_dtypes = file_df.dtypes
    df_dtypes = st.data_editor(df_dtypes)
    stp.write_columns(df_dtypes.to_dict())
    for col in df_dtypes.to_dict():
        file_df[col] = file_df[col].astype(df_dtypes[col])
    file_df.dtypes

    if col_for_index := st.selectbox('setting index',file_df.columns.to_list()+[None]):
        file_df = file_df.set_index(col_for_index)

    st.dataframe(file_df)
    st.download_button(label=f'download parquet',data=file_df.to_parquet(),file_name='out.parquet')
