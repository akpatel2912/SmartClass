import streamlit as st

def header_home():
    logo_url = "https://png.pngtree.com/png-vector/20250513/ourmid/pngtree-vector-graduation-male-faceless-png-image_16259807.png"

    st.markdown(f"""
        <div style="display:flex; flex-direction:column;align-items:center; justify-content:center; margin-bottom:30px">
            <img src="{logo_url}" style="height:100px;"/>
            <h1 style="text-align:center; color:#E0E3FF;">SMART <br/> CLASS </h1>
        </div>
     """,unsafe_allow_html=True)


def header_dashboard():
    logo_url = "https://png.pngtree.com/png-vector/20250513/ourmid/pngtree-vector-graduation-male-faceless-png-image_16259807.png"

    st.markdown(f"""
        <div style="display:flex;align-items:center; justify-content:center; gap:10px ;">
            <img src="{logo_url}" style="height:60px;"/>
            <h1 style="text-align:left; color:#5865F2 ;">SMART <br/> CLASS </h1>
        </div>
     """,unsafe_allow_html=True)