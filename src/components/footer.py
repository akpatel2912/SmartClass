import streamlit as st

def footer_home():

    st.markdown("""
        <div style="
            margin-top: 3rem;
            text-align: center;
            font-weight:bold;
        ">
            <p>
                Created with 
                <span style="color: #B01E28;">&#x2665;</span> 
                by Akshat
            </p>
        </div>
    """, unsafe_allow_html=True)

def footer_dashboard():

    st.markdown("""
        <div style="
            margin-top: 3rem;
            text-align: center;
            font-weight:bold;
            color:#000000;
        ">
            <p>
                Created with 
                <span style="color: #B01E28 ;">&#x2665;</span> 
                by Akshat
            </p>
        </div>
    """, unsafe_allow_html=True)