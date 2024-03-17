import streamlit as st
import pandas as pd
import pyplus.streamlit as stp


from pre import ex,conn
ex()

tab_name = ['new','open']
file_tab = st.tabs(tab_name)
with file_tab[0]:

    new_df_dtype = pd.DataFrame(columns=['name','dtype','index'])
    new_df_dtype['index'] = new_df_dtype['index'].astype("boolean")
    #all_dtype=pd.read_html("https://pandas.pydata.org/docs/user_guide/basics.html#basics-dtypes")[3]["String Aliases"]
    #all_dtype = all_dtype.apply(lambda s:s.split(",")).apply(lambda l:[s.strip("'`") for s in l])
    #all_dtype
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
    new_df_dtype_column_config = {
        "dtype": st.column_config.SelectboxColumn(
            label="Set dtype",
            options=all_dtype
        )
    }
    new_df_dtype = st.data_editor(new_df_dtype,num_rows="dynamic",hide_index=True, column_config=new_df_dtype_column_config)
    

    new_df = pd.DataFrame({a:pd.Series([],dtype=b) for a,b in zip(new_df_dtype['name'],new_df_dtype['dtype'])})
    new_df=st.data_editor(new_df,num_rows="dynamic")
    try:
        column_for_index = new_df_dtype[new_df_dtype['index']==True]['name'].to_list()
        column_for_index
        new_df = new_df.set_index(column_for_index)
    except:
        pass
    st.dataframe(new_df)
    filename = st.text_input(label='filename',value='out')
    st.download_button(label='download parquet (new)',data=new_df.to_parquet(),file_name=f'{filename}.parquet')

with file_tab[1]:
    new_df=None
    try:
        file = st.file_uploader('parquet test',type='parquet')
        file_df = pd.read_parquet(path=file,)
    except:
        pass
    try:
        file_df=st.data_editor(file_df,num_rows="dynamic")
    except:
        "No file"
    st.markdown("---")


    process = st.tabs(['drop','rename','set_index','dtype'])

    with process[0]:
        try:
            input = stp.list_checkbox(*file_df.columns.values)
            remove_select = [key for key,value in input.items() if value==True]
            file_df = file_df.drop(remove_select,axis=1)
        except:
            pass

    with process[1]:
        try:
            changer = stp.list_text_input_by_vals(*file_df.columns.values)
            changer = {key : value for key,value in changer.items() if len(value)>0 }
            changer
            file_df = file_df.rename(mapper=changer,axis=1)
        except:
            pass
    
    with process[2]:
        try:
            index = st.text_input('setting index')
            file_df = file_df.set_index([index])
        except:
            st.error("Index error")

    st.dataframe(file_df)
    st.download_button(label=f'download parquet',data=file_df.to_parquet(),file_name='out.parquet')