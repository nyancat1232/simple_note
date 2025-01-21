import streamlit as st
import pandas as pd

def lim(n):
    ret = n+1
    if ret>9:
        return None
    else:
        return ret

wowow = {
    'ref' : [lim(n) for n in range(10)]
}

df = pd.DataFrame(wowow,index=[n for n in range(10)])
#df = pd.DataFrame({'ref':['dog','cat',None,'dog']},index=['bird','dog','cat','rabbit'])
df

"referencing"
def epoch_recurse(ser_reference:pd.Series,ser_origin:pd.Series)->pd.Series:
    def recurse(row):
        try:
            return ser_origin[row]
        except:
            return None
    return ser_reference.apply(lambda val:recurse(val))

#def generate_recurse(df:pd.DataFrame,col:str,count:int=0):
#    if count < 1:
#        col_with_epoch = f'{col}'
#    else:
#        col_with_epoch = f'{col}_{count-1}'
#    ret = epoch_recurse(df[col_with_epoch],df[f'{col}'])
#    df[f'{col}_{count}']= ret
#    if ret.any():
#        generate_recurse(df,col,count+1)
#    else:
#        df

def temp(ser_0:pd.Series,ser_piv:pd.Series):
    ser_1=epoch_recurse(ser_0,ser_piv)
    ser_1.name=ser_1.name + '_rec'
    st.dataframe(ser_1)
    if ser_1.any():
        return pd.concat([ser_0,temp(ser_1,ser_piv)],axis=1)
    else:
        return ser_0
df.aggregate
vvv=temp(df['ref'],df['ref'])
vvv
