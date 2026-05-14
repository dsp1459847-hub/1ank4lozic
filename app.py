import streamlit as st
import pandas as pd

# Page Setup
st.set_page_config(page_title="MAYA v33.0 - Smart Scanner", layout="wide")

# Custom UI Styling
st.markdown("""
    <style>
    .formula-container { display: flex; align-items: center; justify-content: center; gap: 15px; margin-bottom: 20px; }
    .box-wrapper { display: flex; flex-direction: column; align-items: center; }
    .box { width: 95px; height: 95px; display: flex; align-items: center; justify-content: center; 
           font-size: 45px; font-weight: bold; border-radius: 15px; color: white; border: 3px solid #555; }
    .plus-equal { font-size: 55px; font-weight: bold; color: #fff; padding-top: 15px; }
    .green { background-color: #28a745 !important; box-shadow: 0 0 20px #28a745; }
    .yellow { background-color: #ffc107 !important; color: black !important; box-shadow: 0 0 20px #ffc107; }
    .red { background-color: #dc3545 !important; }
    .gray { background-color: #333 !important; border: 3px dashed #666; }
    .label-top { font-size: 16px; margin-bottom: 5px; font-weight: bold; color: #bbb; }
    .label-rashi { font-size: 18px; margin-top: 8px; font-weight: bold; color: #ffc107; background: #111; padding: 4px 12px; border-radius: 6px; }
    .best-frame { background: #1e1e1e; padding: 10px; border-left: 5px solid #28a745; margin-bottom: 20px; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎯 MAYA v33.0 (Smart Timeframe Scanner)")

# --- LOGIC CORE ---
def get_prediction_by_gap(df, idx, col, gap):
    """Specific gap timeframe se prediction nikalna"""
    target_idx = idx - gap
    if target_idx < 0: return None, None
    
    val = df.iloc[target_idx].get(col, "XX")
    try:
        base_val = int(float(str(val).split('.')[0]))
        if base_val == 0: return None, None
    except: return None, None

    d1, d2 = base_val // 10, base_val % 10
    s_a, s_b = {i: 0 for i in range(10)}, {i: 0 for i in range(10)}
    
    # Pattern Logic
    if d1 == d2: s_a[0]+=20; s_a[5]+=20
    elif abs(d1-d2)==1: s_a[(max(d1,d2)+1)%10]+=18; s_b[(max(d1,d2)+6)%10]+=15
    else: s_a[d2]+=15; s_b[(d2+5)%10]+=12
    
    return max(s_a, key=s_a.get), max(s_b, key=s_b.get)

def auto_scan_best_timeframe(df, idx, shift):
    """Sare timeframes scan karke sabse best accuracy wala chunna"""
    timeframes = {
        "Yesterday (1-Day)": 1,
        "Day Before (2-Day)": 2,
        "Step Gap (3-Day)": 3,
        "Jump Gap (5-Day)": 5,
        "Weekly (7-Day)": 7
    }
    
    best_frame = "Yesterday (1-Day)"
    max_score = -1
    final_pred = (0, 5)

    for name, gap in timeframes.items():
        score = 0
        # Pichle 10 records par test run
        for check_idx in range(idx-10, idx):
            if check_idx < 10: continue
            pa, pb = get_prediction_by_gap(df, check_idx, shift, gap)
            if pa is None: continue
            
            act = str(df.iloc[check_idx].get(shift, "XX")).split('.')[0]
            if act.isdigit():
                v = int(act); aa, ab = v//10, v%10
                if aa == pa and ab == pb: score += 10 # Direct
                elif aa in [pa, (pa+5)%10] and ab in [pb, (pb+5)%10]: score += 5 # Family
        
        if score > max_score:
            max_score = score
            best_frame = name
            current_pa, current_pb = get_prediction_by_gap(df, idx, shift, gap)
            if current_pa is not None:
                final_pred = (current_pa, current_pb)

    return best_frame, final_pred

# --- INTERFACE ---
uploaded_file = st.file_uploader("📂 Upload 0DSP0 File", type=["csv", "xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
    df.columns = [str(c).strip().upper() for c in df.columns]
    df = df.rename(columns={'FD': 'FB', 'GD': 'GB', 'FBD': 'FB', 'GZB': 'GB'})
    df['DATE'] = df['DATE'].astype(str).str.strip()

    c1, c2, c3 = st.columns([2, 2, 2])
    with c1: sel_date = st.selectbox("📅 Date:", options=df['DATE'].unique().tolist()[::-1])
    with c2: target_s = st.selectbox("🎰 Shift:", options=['DS', 'FB', 'GB', 'GL', 'DB', 'SG'])
    
    idx = df[df['DATE'] == sel_date].index[0]
    
    # Run Auto-Scanner
    best_name, (p_a, p_b) = auto_scan_best_timeframe(df, idx, target_s)
    r_a, r_b = (p_a + 5) % 10, (p_b + 5) % 10

    with c3:
        st.markdown(f'<div class="best-frame"><b>Best Timeframe:</b><br>{best_name}</div>', unsafe_allow_html=True)

    # UI Result
    actual_val = df.iloc[idx].get(target_s, "XX")
    clean_act = str(actual_val).split('.')[0] if pd.notna(actual_val) and str(actual_val).upper() != 'XX' else "XX"
    
    act_a, act_b = None, None
    if clean_act.isdigit():
        v = int(clean_act); act_a, act_b = v // 10, v % 10

    c_a = "green" if act_a == p_a else ("yellow" if act_a == r_a else "red")
    c_b = "green" if act_b == p_b else ("yellow" if act_b == r_b else "red")
    if clean_act == "XX" or clean_act == "0": c_a = c_b = "gray"

    st.divider()

    st.markdown(f"""
    <div class="formula-container">
        <div class="box-wrapper"><div class="label-top">ANDAR (A)</div><div class="box {c_a}">{p_a}</div><div class="label-rashi">R: {r_a}</div></div>
        <div class="plus-equal">+</div>
        <div class="box-wrapper"><div class="label-top">BAHAR (B)</div><div class="box {c_b}">{p_b}</div><div class="label-rashi">R: {r_b}</div></div>
        <div class="plus-equal">=</div>
        <div class="box-wrapper"><div class="label-top">JODI</div><div class="box {'green' if c_a=='green' and c_b=='green' else ('yellow' if 'yellow' in [c_a, c_b] else ('red' if c_a!='gray' else 'gray'))}">{p_a}{p_b}</div><div class="label-rashi">F: {r_a}{r_b}</div></div>
    </div>
    """, unsafe_allow_html=True)

    # Backtest History
    st.subheader(f"📜 {target_s} Scanner Backtest (Based on {best_name})")
    history = []
    gap_val = {"Yesterday (1-Day)": 1, "Day Before (2-Day)": 2, "Step Gap (3-Day)": 3, "Jump Gap (5-Day)": 5, "Weekly (7-Day)": 7}[best_name]
    
    for i in range(idx - 10, idx + 1):
        if i < 10: continue
        ha, hb = get_prediction_by_gap(df, i, target_s, gap_val)
        if ha is None: continue
        h_act = str(df.iloc[i][target_s]).split('.')[0]
        try:
            if h_act.isdigit():
                hv = int(h_act); ha_act, hb_act = hv//10, hv%10
                ra, rb = (ha+5)%10, (hb+5)%10
                if ha_act == ha and hb_act == hb: s = "💎 DIRECT"
                elif (ha_act in [ha, ra]) and (hb_act in [hb, rb]): s = "👪 FAMILY"
                elif (ha_act in [ha, ra]) or (hb_act in [hb, rb]): s = "🎯 ANK"
                else: s = "❌"
            else: s = "⏳"
        except: s = "⏳"
        history.append({"Date": df.iloc[i]['DATE'], "Result": h_act, "AI Pred": f"{ha}+{hb}", "Status": s})
    st.table(pd.DataFrame(history))
            
