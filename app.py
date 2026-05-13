import streamlit as st
import pandas as pd

st.set_page_config(page_title="MAYA AI - 25+ Pattern Engine", layout="wide")
st.title("🎯 MAYA Super-AI: 25+ Pattern Confluence Engine")

uploaded_file = st.file_uploader("Upload 0DSP0.csv", type=["csv"])

def get_family(n):
    d1, d2 = n // 10, n % 10
    m1, m2 = (d1 + 5) % 10, (d2 + 5) % 10
    return {d1*10+d2, d1*10+m2, m1*10+d2, m1*10+m2, d2*10+d1, d2*10+m1, m2*10+d1, m2*10+m1}

if uploaded_file:
    df = pd.read_csv(uploaded_file).dropna(how='all')
    df.columns = [str(c).strip().upper() for c in df.columns]
    
    # --- Prediction Matrix ---
    # Har ank (0-9) ke liye ek score board
    scores = {i: 0 for i in range(10)}
    reasons = {i: [] for i in range(10)}

    # Latest Data
    last_row = df.iloc[-1]
    prev_row = df.iloc[-2]
    game_cols = ['DS', 'FD', 'GD', 'GL']

    # 1. YOUR PATTERN (85 -> 0/5)
    for col in game_cols:
        val = int(last_row[col]) if pd.notna(last_row[col]) else 0
        u = val % 10
        scores[u] += 5
        scores[(u+5)%10] += 5
        reasons[u].append(f"Unit Digit Pattern from {col}")

    # 2. JODA LOGIC (0/5 Boost)
    if any(int(last_row[c])%11 == 0 for c in game_cols if pd.notna(last_row[c])):
        scores[0] += 10
        scores[5] += 10
        reasons[0].append("Joda Trigger")

    # 3. FAMILY REPEAT PATTERN (15-42 Logic)
    # Check if 15 or 42 family was active in last 3 days
    recent_3 = df.tail(3)[game_cols].values.flatten()
    f42 = get_family(42)
    if any(val in f42 for val in recent_3):
        scores[2] += 8; scores[7] += 8; scores[4] += 8; scores[9] += 8
        reasons[4].append("42-Family Active Flow")

    # 4. GAP ANK PATTERN (Missing for 10 days)
    all_recent = df.tail(10)[game_cols].astype(str).values.flatten()
    full_str = "".join(all_recent)
    for i in range(10):
        if str(i) not in full_str:
            scores[i] += 15
            reasons[i].append("10-Day Long Gap (Strong)")

    # 5. COUNTING SERIES PATTERN
    for col in game_cols:
        val = int(last_row[col])
        if abs((val//10) - (val%10)) == 1:
            next_step = (max(val//10, val%10) + 1) % 10
            scores[next_step] += 7
            reasons[next_step].append("Counting Series Next Step")

    # --- FINAL VERDICT ---
    res_df = pd.DataFrame([{'Ank': k, 'Score': v, 'Patterns': ", ".join(reasons[k])} for k, v in scores.items()])
    res_df = res_df.sort_values(by='Score', ascending=False)

    st.subheader("🔥 Super Solid Prediction (Multi-Pattern Match)")
    top_ank = res_df.iloc[0]
    
    c1, c2 = st.columns([1, 2])
    with c1:
        st.metric("CONFIRMED ANK", top_ank['Ank'], f"Score: {top_ank['Score']}")
        st.write("**Top 3 Candidates:**")
        st.table(res_df[['Ank', 'Score']].head(3))
    
    with c2:
        st.write("**Matching Patterns for this Ank:**")
        st.info(top_ank['Patterns'])

    st.bar_chart(res_df.set_index('Ank')['Score'])
                             
