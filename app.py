import streamlit as st
import pandas as pd

# Page Config - Phone Friendly
st.set_page_config(page_title="MAYA v43.0", layout="wide")

# Custom CSS for Mobile Optimization
st.markdown("""
    <style>
    html, body, [class*="ViewContainer"] { font-size: 14px !important; }
    .stTable { font-size: 12px !important; }
    .target-grid { 
        display: grid; grid-template-columns: repeat(5, 1fr); 
        gap: 6px; width: 100%; margin: 0 auto; 
    }
    .target-item { 
        background-color: #f0fdf4; color: #166534; padding: 8px; 
        border-radius: 6px; font-size: 16px; font-weight: bold; 
        text-align: center; border: 1px solid #bbf7d0;
    }
    .ank-circle {
        display: inline-block; width: 32px; height: 32px; line-height: 32px;
        border-radius: 50%; background: #fee2e2; color: #b91c1c;
        text-align: center; font-weight: bold; margin: 2px; font-size: 14px; border: 1px solid #fecaca;
    }
    .status-pass { color: #28a745; font-weight: bold; }
    .status-fail { color: #dc3545; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎯 MAYA v43.0 (Compact UI)")

def get_logic_v43(df, idx, shift):
    flow = {'FB': 'DS', 'GB': 'FB', 'GL': 'GB', 'DS': 'GL', 'SG': 'DB', 'DB': 'GL'}
    base_col = flow.get(shift, 'DS')
    
    # 1. Base Find
    val = 0
    for i in range(1, 15):
        t_idx = idx - i
        if t_idx >= 0:
            raw = df.iloc[t_idx].get(base_col, 0)
            if str(raw).isdigit() and int(raw) > 0:
                val = int(raw); break
    
    d1, d2 = val // 10, val % 10
    pa = (d1 + 1) % 10 if d1 != d2 else (d1 + 5) % 10
    pb = (d2 + 1) % 10
    ra, rb = (pa + 5) % 10, (pb + 5) % 10
    
    a_final, b_final = {pa, ra}, {pb, rb}
    
    # Worst Gaps (Adding to make it 5x5)
    for g in [3, 5, 7]:
        if len(a_final) < 5 and (idx-g) >= 0:
            v = df.iloc[idx-g].get(base_col, 0)
            if str(v).isdigit(): a_final.add(int(v)//10)
        if len(b_final) < 5 and (idx-g) >= 0:
            v = df.iloc[idx-g].get(base_col, 0)
            if str(v).isdigit(): b_final.add(int(v)%10)
            
    # Final padding if sets are still small
    for i in range(10):
        if len(a_final) < 5: a_final.add(i)
        if len(b_final) < 5: b_final.add(i)

    blocked = set()
    for a in a_final:
        for i in range(10): blocked.add(str(a) + str(i))
    for b in b_final:
        for i in range(10): blocked.add(str(i) + str(b))
        
    target = [str(i).zfill(2) for i in range(100) if str(i).zfill(2) not in blocked]
    return sorted(list(a_final)), sorted(list(b_final)), target

uploaded_file = st.file_uploader("📂 Upload File", type=["xlsx", "csv"])

if uploaded_file:
    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
    df.columns = [str(c).strip().upper() for c in df.columns]
    df = df.rename(columns={'FD': 'FB', 'GD': 'GB', 'FBD': 'FB', 'GZB': 'GB'})
    
    sel_date = st.selectbox("📅 Date:", options=df['DATE'].astype(str).unique().tolist()[::-1])
    target_s = st.selectbox("🎰 Shift:", options=['DS', 'FB', 'GB', 'GL', 'DB', 'SG'])
    
    idx = df[df['DATE'].astype(str) == sel_date].index[0]
    fa, fb, target_jodis = get_logic_v43(df, idx, target_s)

    # UI: Compact Elimination
    st.write("**🚫 Hata Diye (A/B):**")
    html_e = "".join([f'<span class="ank-circle">{a}</span>' for a in fa]) + " | " + "".join([f'<span class="ank-circle">{b}</span>' for b in fb])
    st.markdown(html_e, unsafe_allow_html=True)

    # UI: 25 Jodis Grid
    st.write(f"**✅ Target ({len(target_jodis)}):**")
    grid_html = '<div class="target-grid">'
    for jodi in target_jodis:
        grid_html += f'<div class="target-item">{jodi}</div>'
    grid_html += '</div>'
    st.markdown(grid_html, unsafe_allow_html=True)

    # UI: Fixed History with Pass/Fail
    st.subheader("📜 Live History (10 Days)")
    hist_list = []
    for i in range(idx - 10, idx + 1):
        if i < 0: continue
        _, _, h_target = get_logic_v43(df, i, target_s)
        res_raw = str(df.iloc[i].get(target_s, "XX")).split('.')[0]
        
        status = "⏳"
        if res_raw.isdigit():
            res_val = str(int(res_raw)).zfill(2)
            status = "✅ PASS" if res_val in h_target else "❌ FAIL"
            
        hist_list.append({"Date": df.iloc[i]['DATE'], "Result": res_raw, "Status": status})
    
    st.table(pd.DataFrame(hist_list))
        
