import streamlit as st
import pandas as pd

# Page Configuration
st.set_page_config(page_title="MAYA v36.0 - Purpose Restored", layout="wide")

# Custom UI
st.markdown("""
    <style>
    .formula-container { display: flex; align-items: center; justify-content: center; gap: 15px; margin-bottom: 20px; }
    .box { width: 90px; height: 90px; display: flex; align-items: center; justify-content: center; 
           font-size: 40px; font-weight: bold; border-radius: 12px; color: white; border: 3px solid #444; }
    .plus-equal { font-size: 45px; font-weight: bold; color: #fff; padding-top: 15px; }
    .green { background-color: #28a745 !important; }
    .yellow { background-color: #ffc107 !important; color: black !important; }
    .red { background-color: #dc3545 !important; }
    .gray { background-color: #333 !important; }
    .label-rashi { font-size: 18px; margin-top: 8px; font-weight: bold; color: #ffc107; background: #111; padding: 4px 10px; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎯 MAYA v36.0 (Fixed Single-Shift Isolation)")

# --- CLEAN ENGINE ---
def get_valid_base_v36(df, idx, col):
    # Strictly search back until a real number > 0 is found
    for i in range(1, 20):
        t_idx = idx - i
        if t_idx < 0: break
        val = df.iloc[t_idx].get(col, "XX")
        try:
            num = int(float(str(val).split('.')[0]))
            if num > 0: return num
        except: continue
    return 14 # Static fallback

def calculate_v36(df, idx, shift):
    game_cols = ['DS', 'FB', 'GB', 'GL', 'DB', 'SG']
    flow = {'FB': 'DS', 'GB': 'FB', 'GL': 'GB', 'DS': 'GL', 'SG': 'DB', 'DB': 'GL'}
    base_col = flow.get(shift, 'DS')
    
    base_val = get_valid_base_v36(df, idx, base_col)
    d1, d2 = base_val // 10, base_val % 10
    s_a, s_b = {i: 0 for i in range(10)}, {i: 0 for i in range(10)}
    
    # Original v12.5 Weights
    if d1 == d2:
        s_a[0]+=25; s_a[5]+=25
    elif abs(d1-d2)==1:
        n = (max(d1,d2)+1)%10
        s_a[n]+=20; s_b[(n+5)%10]+=15
    else:
        s_a[d2]+=15; s_b[(d2+5)%10]+=12

    # Gap Variety Fix (Last 15 records)
    pool = "".join([str(x).split('.')[0] for x in df[shift].iloc[:idx].tail(15) if str(x).isdigit()])
    for i in range(10):
        if str(i) not in pool:
            s_a[i]+=10; s_b[i]+=10

    ba, bb = max(s_a, key=s_a.get), max(s_b, key=s_b.get)
    if ba == bb: bb = sorted(s_b, key=s_b.get, reverse=True)[1]
    return ba, bb

uploaded_file = st.file_uploader("📂 Upload Excel", type=["csv", "xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
    df.columns = [str(c).strip().upper() for c in df.columns]
    df = df.rename(columns={'FD': 'FB', 'GD': 'GB', 'FBD': 'FB', 'GZB': 'GB'})
    
    c1, c2 = st.columns(2)
    with c1: sel_date = st.selectbox("📅 Date:", options=df['DATE'].astype(str).unique().tolist()[::-1])
    with c2: target_s = st.selectbox("🎰 Shift:", options=['DS', 'FB', 'GB', 'GL', 'DB', 'SG'])
    
    idx = df[df['DATE'].astype(str) == sel_date].index[0]
    p_a, p_b = calculate_v36(df, idx, target_s)
    r_a, r_b = (p_a + 5) % 10, (p_b + 5) % 10

    # Result logic
    res_raw = df.iloc[idx].get(target_s, "XX")
    res = str(res_raw).split('.')[0] if pd.notna(res_raw) and str(res_raw).upper() != 'XX' else "XX"
    
    c_a = "green" if (res.isdigit() and int(res)//10 == p_a) else ("yellow" if (res.isdigit() and int(res)//10 == r_a) else "red")
    c_b = "green" if (res.isdigit() and int(res)%10 == p_b) else ("yellow" if (res.isdigit() and int(res)%10 == r_b) else "red")
    if res == "XX": c_a = c_b = "gray"

    st.divider()
    st.markdown(f"""
    <div class="formula-container">
        <div><div class="box {c_a}">{p_a}</div><div class="label-rashi">R: {r_a}</div></div>
        <div class="plus-equal">+</div>
        <div><div class="box {c_b}">{p_b}</div><div class="label-rashi">R: {r_b}</div></div>
        <div class="plus-equal">=</div>
        <div class="box {'green' if c_a=='green' and c_b=='green' else 'gray'}">{p_a}{p_b}</div>
    </div>
    """, unsafe_allow_html=True)

    # History
    history = []
    for i in range(idx - 10, idx + 1):
        if i < 0: continue
        ha, hb = calculate_v36(df, i, target_s)
        h_res = str(df.iloc[i][target_s]).split('.')[0]
        s = "✅" if (h_res.isdigit() and (int(h_res)//10 in [ha,(ha+5)%10] or int(h_res)%10 in [hb,(hb+5)%10])) else "❌"
        history.append({"Date": df.iloc[i]['DATE'], "Result": h_res, "AI": f"{ha}+{hb}", "Status": s})
    st.table(pd.DataFrame(history))
    
