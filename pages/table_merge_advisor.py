import streamlit as st
from pre import ex,conn,table_selector,types
ex()

"If tables are 1:1 like"
one_one={'fruit':['apple','banana','cherry'],'fruit_id':[1,2,3],'fruit_id.color':['red','yellow','red']}
st.dataframe(one_one)
"Then merge foreign tables"