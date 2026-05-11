import pandas as pd
import streamlit as st
import io

# --- 1. SETTINGS & STYLING ---
st.set_page_config(layout="wide", page_title="MAYA MATRIX v38.6")

st.markdown("""
    <style>
    .header-info { background: #000; color: gold; padding: 10px; border-radius: 8px; text-align: center; border: 2px solid gold; margin-bottom: 10px; font-weight: bold; }
    .result-box { border: 2px solid gold; padding: 15px; border-radius: 12px; text-align: center; margin-bottom: 15px; background: #111; color: white; }
    .pass-tag { color: #00FF00; font-weight: 900; font-size: 22px; }
    .compact-grid { display:grid; grid-template-columns: repeat(5, 1fr); gap: 4px; }
    .item-box { font-size: 14px; padding: 8px; text-align: center; border-radius: 5px; font-weight: 900; border: 1px solid #444; }
    .hit-border { border: 2px solid #00FF00 !important; box-shadow: 0px 0px 10px #00FF00; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GLOBAL LOGIC ---
def clean(v):
    if pd.isna(v): return ""
    s = "".join(filter(str.isdigit, str(v)))
    return s.zfill(2)[-2:] if s else ""

# --- 3. SIDEBAR ---
with st.sidebar:
    st.header("⚙️ MATRIX CONTROLS")
    uploaded_file = st.file_uploader("Upload 0DSP0.xlsx", type=['xlsx', 'csv'])
    t_date = st.date_input("Select Target Date")

# --- 4. EXECUTION ---
if uploaded_file:
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    df['DATE'] = pd.to_datetime(df['DATE'])
    
    st.markdown(f"<div class='header-info'>⚡ MATRIX ENGINE v38.6 | {t_date.strftime('%d-%b-%Y')}</div>", unsafe_allow_html=True)
    
    shifts = ["DS", "FD", "GD", "GL", "DB", "SG"]
    tabs = st.tabs(shifts)

    for idx, s_name in enumerate(shifts):
        with tabs[idx]:
            # A. Actual Result
            row = df[df['DATE'] == pd.to_datetime(t_date)]
            actual = clean(row[s_name].values[0]) if not row.empty else ""
            
            # Dummy Predictions (Yahan aapka run_engine logic aayega)
            ss_picks = ["10", "62"] 
            p33 = ["10", "15", "20", "25", "27"] # Example with a match
            p24 = ["62", "67", "72", "77"]

            # B. Check for PASS ✅
            is_hit_any = (actual in ss_picks or actual in p33 or actual in p24)
            pass_status = f"<span class='pass-tag'>PASS ✅</span>" if (actual != "" and is_hit_any) else ""
            
            st.markdown(f"<div class='result-box'><h2>{s_name} Result: {actual if actual else '--'} {pass_status}</h2></div>", unsafe_allow_html=True)

            # C. Single Shot Section
            st.markdown("### 🚀 Matrix Single Shot")
            ss_cols = st.columns(max(len(ss_picks), 1))
            for i, p in enumerate(ss_picks):
                is_hit = (p == actual and actual != "")
                ss_cols[i].markdown(f"<div style='background:#1A237E; color:white; padding:15px; text-align:center; border-radius:10px; border:2px solid gold; font-weight:bold; font-size:20px; {'border:4px solid #00FF00;' if is_hit else ''}'>{p}{' ✅' if is_hit else ''}</div>", unsafe_allow_html=True)

            # D. Parallel Grids
            c1, c2 = st.columns(2)
            with c1:
                st.write("**v33 Platinum Grid**")
                h = "<div class='compact-grid'>"
                for p in p33:
                    is_hit = (p == actual and actual != "")
                    h += f"<div class='item-box {'hit-border' if is_hit else ''}' style='background:#FFD600; color:black;'>{p}{' ✅' if is_hit else ''}</div>"
                h += "</div>"
                st.markdown(h, unsafe_allow_html=True)
            with c2:
                st.write("**v24 Audit Grid**")
                h = "<div class='compact-grid'>"
                for p in p24:
                    is_hit = (p == actual and actual != "")
                    h += f"<div class='item-box {'hit-border' if is_hit else ''}' style='background:#1B5E20; color:white;'>{p}{' ✅' if is_hit else ''}</div>"
                h += "</div>"
                st.markdown(h, unsafe_allow_html=True)

            # E. FIXED HISTORY TABLE (No more AttributeError)
            st.markdown("---")
            st.subheader(f"📋 {s_name} Deep Audit (Color Coded)")
            hist_df = df[df['DATE'] < pd.to_datetime(t_date)].tail(15).copy()
            hist_df['DATE'] = hist_df['DATE'].dt.strftime('%d-%b') # Date format clean
            
            # Resetting index to avoid style mismatch
            display_df = hist_df[['DATE', s_name]].reset_index(drop=True)

            def apply_color_logic(val):
                v = clean(val)
                if v == "": return ""
                if v in ss_picks: return 'background-color: #1A237E; color: white; font-weight: bold;'
                if v in p33: return 'background-color: #FFD600; color: black; font-weight: bold;'
                if v in p24: return 'background-color: #1B5E20; color: white; font-weight: bold;'
                return ''

            # Using .map() instead of .applymap() for newer Pandas compatibility
            styled_df = display_df.style.map(apply_color_logic, subset=[s_name])
            st.table(styled_df)

st.info("Legend: 🔵 Blue = Matrix Single Hit | 🟡 Gold = v33 Hit | 🟢 Green = v24 Hit")
