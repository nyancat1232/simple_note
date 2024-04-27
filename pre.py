import streamlit as st
import pyplus.streamlit as stp
import pyplus.sql as sqlp

def ex():
    if not stp.check_password():
        st.stop()
if 'conn' not in st.session_state:
    st.session_state['conn'] = st.connection('myaddress',type='sql')

conn = st.session_state['conn']
types=['bigint','double precision','text','timestamp with time zone','boolean','url','image_url','text_with_tag']
title = 'Simple note'
sn_config_table={'schema':'sn_config','table':'configs'}

def init_schema():
    lists=sqlp.get_table_list(conn.engine)
    return st.selectbox('select a schema',['public']+lists['table_schema'].unique().tolist())

def table_selector(label:str):
    '''
    Show a selector for selecting schema and table.
    
    Parameters
    ----------
    label : str
        A short label explaining to the user what this select widget is for. The label can optionally contain Markdown and supports the following
        elements: Bold, Italics, Strikethroughs, Inline Code, Emojis, and Links.

        This also supports:

        Emoji shortcodes, such as and. For a list of all supported codes, see https://share.streamlit.io/streamlit/emoji-shortcodes.

        LaTeX expressions, by wrapping them in "$" or "$$" (the "$$" must be on their own lines). Supported LaTeX functions are listed at https://katex.org/docs/supported.html.

        Colored text, using the syntax :color[text to be colored], where color needs to be replaced with any of the following supported colors: blue, green, orange, red, violet, gray/grey, rainbow.

        Unsupported elements are unwrapped so only their children (text contents) render. Display unsupported elements as literal characters by backslash-escaping them. E.g. 1\. Not an ordered list.
    
    Returns
    --------
    tuple
        schema,table
    
    Examples
    --------
    
    >>> with st.sidebar:
    >>>     schema,table=table_selector('select table')
    >>> first_ts = sqlp.TableStructure(schema,table,conn.engine)

    '''
    df_list=sqlp.get_table_list(conn.engine)

    np_schemas=df_list['table_schema'].unique()
    schema = st.selectbox(label=f'{label} of schema',options=np_schemas)

    np_tables=df_list['table_name'][df_list['table_schema']==schema]
    table = st.selectbox(label=f"{label} of table",options=np_tables)
    return schema, table