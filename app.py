#!/usr/bin/env python3
"""Phil's Baseball Card Finder - Full Featured App"""
import streamlit as st
import sqlite3
import os
import re
import json
import csv
import io
import base64
import pandas as pd
from datetime import datetime

# Load API key - check Streamlit secrets, then axiom .env, then env var
def load_api_key():
    # Streamlit Cloud secrets
    try:
        key = st.secrets.get("ANTHROPIC_API_KEY", "")
        if key: return key
    except: pass
    # Local axiom .env
    env_path = os.path.expanduser("~/axiom/.env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if line.startswith("ANTHROPIC_API_KEY="):
                    return line.strip().split("=", 1)[1].strip('"').strip("'")
    return os.getenv("ANTHROPIC_API_KEY", "")

API_KEY = load_api_key()
if API_KEY:
    os.environ["ANTHROPIC_API_KEY"] = API_KEY

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "db", "cards.db")

NOTABLE_NAMES = {
    "ted williams","sandy koufax","yogi berra","ernie banks","whitey ford",
    "warren spahn","bob lemon","willie mays","nellie fox","don drysdale",
    "roberto clemente","bob clemente","stan musial","bob gibson","monte irvin",
    "mickey mantle","hank aaron","pete rose","johnny bench","nolan ryan",
    "reggie jackson","mike schmidt","george brett","rickey henderson",
    "robin yount","carl yastrzemski","tom seaver","steve carlton","rod carew",
    "joe morgan","ozzie smith","eddie murray","cal ripken","gary carter",
    "dave winfield","jim palmer","dennis eckersley","rollie fingers",
    "don sutton","phil niekro","gaylord perry","fergie jenkins","ferguson jenkins",
    "willie stargell","harmon killebrew","al kaline","brooks robinson",
    "frank robinson","billy williams","wade boggs","ryne sandberg",
    "barry bonds","mark mcgwire","kirby puckett","dale murphy","andre dawson",
    "tim raines","paul molitor","jack morris","bert blyleven","bruce sutter",
    "tony gwynn","barry larkin","dave parker","carlton fisk","don mattingly",
    "dwight gooden","darryl strawberry","willie mccovey","juan marichal",
    "hoyt wilhelm","ron santo","tony oliva","dave concepcion","jim rice",
    "fred lynn","dwight evans","steve garvey","alan trammell","lou whitaker",
    "lance parrish","kirk gibson","jack clark","tony perez","eric davis",
    "jose canseco","will clark","roger clemens","bo jackson","don larsen",
    "honus wagner","pie traynor","walter johnson","ty cobb","lou gehrig",
    "thurman munson","red schoendienst","enos slaughter","richie ashburn",
    "curt flood","dick groat","bill skowron","elston howard","ken boyer",
    "harvey kuenn","minnie minoso","bobby murcer","tony conigliaro",
    "frank viola","bret saberhagen","kent hrbek","joe carter","lee smith",
    "orel hershiser","fernando valenzuela","cecil cooper","bob horner",
    "buddy bell","graig nettles","tommy john","luis aparicio",
    "rafael palmeiro","keith hernandez","george foster","joe torre",
    "sparky anderson","tommy lasorda","earl weaver","whitey herzog","bobby cox",
    "billy martin","lou piniella","mark fidrych","dave kingman",
    "rich gossage","ron guidry","dan quisenberry","dave righetti",
    "bill madlock","ron cey","harold baines","mookie wilson","len dykstra",
    "kevin mitchell","jose cruz","cesar cedeno","j. r. richard",
    "bobby bonilla","andres galarraga","ted simmons","ben oglivie",
    "ken griffey","cecil fielder","felipe alou","willie wilson",
    "tony armas","joe charboneau","mickey klutts",
}

def is_notable(player, year, description=""):
    if not player: return False
    name = player.lower().strip()
    for n in NOTABLE_NAMES:
        if n in name or name in n: return True
    if year and year < 1965: return True
    dl = (description or "").lower()
    if any(k in dl for k in ["rookie","record break","all star","all-star","mvp","future star","highlight"]): return True
    return False

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS cards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        card_number TEXT, quantity INTEGER DEFAULT 1,
        year INTEGER, team TEXT, position TEXT, player TEXT,
        description TEXT, company TEXT, location TEXT,
        value_raw TEXT, value_psa8 TEXT, value_psa9 TEXT, value_psa10 TEXT,
        value_source TEXT, is_notable INTEGER DEFAULT 0,
        notes TEXT, last_updated TEXT
    )""")
    conn.commit()
    conn.close()

def get_db():
    init_db()
    return sqlite3.connect(DB_PATH)

def import_tsv_data(text_data):
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM cards")
    count = notable_count = 0
    for line in text_data.strip().split('\n'):
        line = line.rstrip()
        if not line or line.startswith("Phil's") or line.startswith("No."): continue
        parts = line.split('\t')
        if len(parts) < 3: parts = re.split(r'\s{4,}', line)
        if len(parts) < 3: continue
        while len(parts) < 11: parts.append("")
        try: qty = int(parts[1].strip() or "1")
        except: qty = 1
        try: year = int(parts[2].strip() or "0")
        except: year = 0
        team, pos, player = parts[3].strip(), parts[4].strip(), parts[5].strip()
        desc, company, loc = parts[6].strip(), parts[7].strip(), parts[8].strip()
        value = parts[9].strip() if len(parts) > 9 else ""
        if not player and not team and not desc and not company: continue
        notable = is_notable(player, year, desc)
        if notable: notable_count += 1
        c.execute("""INSERT INTO cards (card_number,quantity,year,team,position,player,
            description,company,location,value_raw,is_notable)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (parts[0].strip(), qty, year, team, pos, player, desc, company, loc, value, 1 if notable else 0))
        count += 1
    conn.commit(); conn.close()
    return count, notable_count

def get_stats():
    conn = get_db(); c = conn.cursor()
    total = c.execute("SELECT COUNT(*) FROM cards").fetchone()[0]
    notable = c.execute("SELECT COUNT(*) FROM cards WHERE is_notable=1").fetchone()[0]
    with_values = c.execute("SELECT COUNT(*) FROM cards WHERE value_raw!='' AND value_raw IS NOT NULL").fetchone()[0]
    years = [str(y[0]) for y in c.execute("SELECT DISTINCT year FROM cards WHERE year>0 ORDER BY year").fetchall()]
    companies = [r[0] for r in c.execute("SELECT DISTINCT company FROM cards WHERE company!='' ORDER BY company").fetchall()]
    teams = [r[0] for r in c.execute("SELECT DISTINCT team FROM cards WHERE team!='' ORDER BY team").fetchall()]
    total_qty = c.execute("SELECT COALESCE(SUM(quantity),0) FROM cards").fetchone()[0]
    conn.close()
    return {"total":total,"total_qty":total_qty,"notable":notable,"with_values":with_values,"years":years,"companies":companies,"teams":teams}

# ── PSA Grade Visual Guide (SVG) ────────────────────────────────────────────

PHOTO_GUIDE_SVG = """
<svg viewBox="0 0 500 400" xmlns="http://www.w3.org/2000/svg" style="max-width:500px;font-family:sans-serif;">
  <!-- Card outline -->
  <rect x="150" y="30" width="200" height="280" rx="8" fill="#f5f0e1" stroke="#333" stroke-width="2"/>
  <text x="250" y="170" text-anchor="middle" font-size="14" fill="#666">CARD FRONT</text>

  <!-- Corner callouts -->
  <circle cx="150" cy="30" r="12" fill="none" stroke="#e74c3c" stroke-width="2"/>
  <line x1="138" y1="22" x2="100" y2="10" stroke="#e74c3c" stroke-width="1.5"/>
  <text x="30" y="14" font-size="10" fill="#e74c3c">Corner 1 - Sharp?</text>

  <circle cx="350" cy="30" r="12" fill="none" stroke="#e74c3c" stroke-width="2"/>
  <line x1="362" y1="22" x2="400" y2="10" stroke="#e74c3c" stroke-width="1.5"/>
  <text x="370" y="14" font-size="10" fill="#e74c3c">Corner 2</text>

  <circle cx="150" cy="310" r="12" fill="none" stroke="#e74c3c" stroke-width="2"/>
  <line x1="138" y1="318" x2="90" y2="340" stroke="#e74c3c" stroke-width="1.5"/>
  <text x="10" y="344" font-size="10" fill="#e74c3c">Corner 3 - Wear?</text>

  <circle cx="350" cy="310" r="12" fill="none" stroke="#e74c3c" stroke-width="2"/>
  <line x1="362" y1="318" x2="410" y2="340" stroke="#e74c3c" stroke-width="1.5"/>
  <text x="380" y="344" font-size="10" fill="#e74c3c">Corner 4</text>

  <!-- Centering arrows -->
  <line x1="170" y1="20" x2="330" y2="20" stroke="#3498db" stroke-width="1" stroke-dasharray="4"/>
  <text x="250" y="16" text-anchor="middle" font-size="9" fill="#3498db">CENTERING - equal borders?</text>

  <!-- Edge callout -->
  <line x1="145" y1="170" x2="80" y2="170" stroke="#2ecc71" stroke-width="1.5"/>
  <text x="10" y="168" font-size="10" fill="#2ecc71">Edge - chips?</text>
  <text x="10" y="180" font-size="10" fill="#2ecc71">whitening?</text>

  <!-- Surface callout -->
  <line x1="250" y1="200" x2="250" y2="240" stroke="#9b59b6" stroke-width="1" stroke-dasharray="3"/>
  <text x="250" y="255" text-anchor="middle" font-size="10" fill="#9b59b6">Surface - scratches?</text>
  <text x="250" y="267" text-anchor="middle" font-size="10" fill="#9b59b6">stains? creases?</text>

  <!-- Camera icon -->
  <rect x="200" y="355" width="100" height="35" rx="5" fill="#333"/>
  <circle cx="250" cy="372" r="10" fill="none" stroke="white" stroke-width="2"/>
  <circle cx="250" cy="372" r="4" fill="white"/>
  <text x="250" y="400" text-anchor="middle" font-size="11" fill="#333">Take photo flat, good light</text>

  <!-- Photo tips -->
  <text x="250" y="330" text-anchor="middle" font-size="11" font-weight="bold" fill="#333">Photo Tips for Best Grading:</text>
</svg>
"""

# ── AI Chat Helper ───────────────────────────────────────────────────────────

def chat_with_ax(message, context="", history=None, app_type="baseball"):
    """Send a chat message to AX - Phil's family AI assistant."""
    import requests
    if not API_KEY:
        return "No API key found. Add your ANTHROPIC_API_KEY in the app settings."

    personas = {
        "baseball": """You are AX, a friendly and knowledgeable AI assistant for the family.
You're an expert in baseball cards - identification, pricing, grading, history, and selling.
You help with card values, condition grading advice, collection management, and market trends.
Be warm and helpful - you're talking to family members who may not be card experts.
If asked about a specific card value, be honest about uncertainty. Never invent prices.
If someone asks how to sell, give practical eBay/auction house advice.""",
        "trains": """You are AX, a friendly and knowledgeable AI assistant for the family.
You're an expert in model trains and railroadiana - identification, pricing, brands, scales, and selling.
You know Lionel, American Flyer, HO scale, N scale, O gauge, G scale, brass models, vintage tinplate.
Help identify trains from photos, estimate values, and advise on selling via auction houses or eBay.
Be warm and helpful - you're talking to family members.""",
        "general": """You are AX, a friendly and knowledgeable AI assistant for the family.
You help with collectibles, identification, pricing, and selling advice.
Be warm, practical, and honest about what you know and don't know."""
    }

    system = personas.get(app_type, personas["general"])
    if context:
        system += f"\n\nContext: {context}"

    messages = []
    if history:
        for msg in history[-10:]:  # Last 10 messages for context
            messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": message})

    try:
        resp = requests.post("https://api.anthropic.com/v1/messages",
            headers={"x-api-key": API_KEY, "anthropic-version": "2023-06-01", "content-type": "application/json"},
            json={"model": "claude-haiku-4-5-20251001", "max_tokens": 1024,
                  "system": system, "messages": messages},
            timeout=30)
        if resp.ok:
            return resp.json()["content"][0]["text"]
        return f"API error: {resp.status_code}"
    except Exception as e:
        return f"Error: {e}"

def generate_sell_listing(card_info):
    """Generate an eBay/auction listing for a card."""
    prompt = f"""Create a ready-to-use eBay listing for this baseball card:
{card_info}

Include:
1. **Title** (80 chars max, include year, brand, player, card #, condition keywords)
2. **Description** (detailed, mentions condition, any notable features)
3. **Category suggestion** (eBay category)
4. **Starting price suggestion** (based on the card)
5. **Shipping notes** (how to ship a card safely)
6. **Tags/keywords** for search visibility

Format it so it can be copy-pasted directly into eBay."""
    return chat_with_ax(prompt, app_type="baseball")

# ── Main App ─────────────────────────────────────────────────────────────────

def main():
    st.set_page_config(page_title="Phil's Baseball Cards", page_icon="\u26be", layout="wide")

    # Custom title
    if "app_title" not in st.session_state:
        st.session_state.app_title = "Phil's Baseball Card Collection"

    st.title(st.session_state.app_title)

    init_db()
    stats = get_stats()

    # Sidebar
    with st.sidebar:
        # Editable title
        new_title = st.text_input("Collection Title", st.session_state.app_title)
        if new_title != st.session_state.app_title:
            st.session_state.app_title = new_title
            st.rerun()

        st.markdown("---")
        st.header("Filters")
        search = st.text_input("Search player, team, card #", "")
        notable_only = st.checkbox("Valuable cards only", False)
        year_filter = st.selectbox("Year", ["All"] + stats["years"])
        company_filter = st.selectbox("Company", ["All"] + stats["companies"])
        team_filter = st.selectbox("Team", ["All"] + stats["teams"])

        st.markdown("---")
        st.markdown(f"**Entries:** {stats['total']:,} | **Cards:** {stats['total_qty']:,}")
        st.markdown(f"**Notable:** {stats['notable']:,} | **Priced:** {stats['with_values']:,}")

    # Tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "Collection", "Card Scanner", "Ask AX",
        "Sell Cards", "Valuable Cards", "Stats", "Import/Export"
    ])

    # ── TAB 1: Full Editable Spreadsheet ──
    with tab1:
        conn = get_db()
        query = "SELECT * FROM cards WHERE 1=1"
        params = []
        if search:
            query += " AND (LOWER(player) LIKE ? OR LOWER(team) LIKE ? OR card_number LIKE ? OR LOWER(description) LIKE ?)"
            s = f"%{search.lower()}%"
            params.extend([s, s, f"%{search}%", s])
        if year_filter != "All":
            query += " AND year=?"; params.append(int(year_filter))
        if company_filter != "All":
            query += " AND LOWER(company) LIKE ?"; params.append(f"%{company_filter.lower()}%")
        if team_filter != "All":
            query += " AND LOWER(team) LIKE ?"; params.append(f"%{team_filter.lower()}%")
        if notable_only:
            query += " AND is_notable=1"
        query += " ORDER BY year ASC, card_number ASC"
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()

        if df.empty:
            if stats["total"] == 0:
                st.info("No cards yet. Go to Import/Export to paste your spreadsheet.")
            else:
                st.info("No cards match filters.")
        else:
            st.markdown(f"**{len(df)} cards** | Edit cells directly. Click Save when done.")

            # Column name customization
            if "col_names" not in st.session_state:
                st.session_state.col_names = {
                    "card_number": "#", "quantity": "Qty", "year": "Year",
                    "team": "Team", "position": "Pos", "player": "Player",
                    "description": "Description", "company": "Company",
                    "location": "Location", "value_raw": "Value",
                    "value_psa9": "PSA 9", "value_psa10": "PSA 10",
                    "notes": "Notes"
                }

            with st.expander("Customize Column Names"):
                cols = st.columns(4)
                keys = list(st.session_state.col_names.keys())
                for i, key in enumerate(keys):
                    with cols[i % 4]:
                        st.session_state.col_names[key] = st.text_input(
                            key, st.session_state.col_names[key], key=f"col_{key}")

            # Editable dataframe
            edit_cols = ["id","card_number","quantity","year","team","position","player",
                        "description","company","location","value_raw","value_psa9","value_psa10","notes"]
            avail = [c for c in edit_cols if c in df.columns]
            edit_df = df[avail].copy()

            col_config = {}
            for col in avail:
                label = st.session_state.col_names.get(col, col)
                if col == "id":
                    col_config[col] = st.column_config.NumberColumn("ID", disabled=True, width="small")
                elif col == "year":
                    col_config[col] = st.column_config.NumberColumn(label, min_value=1900, max_value=2030, width="small")
                elif col == "quantity":
                    col_config[col] = st.column_config.NumberColumn(label, min_value=1, max_value=999, width="small")
                else:
                    col_config[col] = st.column_config.TextColumn(label)

            edited = st.data_editor(edit_df, column_config=col_config,
                                   use_container_width=True, height=600,
                                   num_rows="dynamic", key="card_editor")

            col_a, col_b, col_c = st.columns(3)
            with col_a:
                if st.button("Save Changes", type="primary"):
                    conn = get_db()
                    for _, row in edited.iterrows():
                        if pd.notna(row.get("id")):
                            conn.execute("""UPDATE cards SET card_number=?,quantity=?,year=?,team=?,
                                position=?,player=?,description=?,company=?,location=?,
                                value_raw=?,value_psa9=?,value_psa10=?,notes=?,last_updated=?
                                WHERE id=?""",
                                (row.get("card_number",""), row.get("quantity",1), row.get("year",0),
                                 row.get("team",""), row.get("position",""), row.get("player",""),
                                 row.get("description",""), row.get("company",""), row.get("location",""),
                                 row.get("value_raw",""), row.get("value_psa9",""), row.get("value_psa10",""),
                                 row.get("notes",""), datetime.now().isoformat(), row["id"]))
                    conn.commit(); conn.close()
                    st.success("Saved!")

            # Per-card search buttons
            with col_b:
                search_player = st.text_input("Quick value search", placeholder="e.g. 1956 Topps Ted Williams")
                if search_player and st.button("Search Value"):
                    with st.spinner("Searching..."):
                        result = chat_with_ax(
                            f"What is the current market value of a {search_player} baseball card? "
                            f"Give raw ungraded value and PSA 9/10 values if known. Be concise.",
                        )
                        st.markdown(result)

    # ── TAB 2: Card Scanner ──
    with tab2:
        st.subheader("Scan & Grade a Card")

        # Photo guide
        with st.expander("How to photograph your card for best grading", expanded=False):
            st.markdown(PHOTO_GUIDE_SVG, unsafe_allow_html=True)
            st.markdown("""
            **For the best AI condition grading:**
            1. Place card on a **dark, flat surface**
            2. Use **bright, even lighting** (no shadows)
            3. Hold camera **directly above** (not at an angle)
            4. Take **front photo** - shows centering, surface, corners
            5. Take **back photo** - shows back centering, damage
            6. Optional: **close-up of corners** for detailed grading

            **What the AI checks:**
            - **Centering** (red circles) - Are borders equal on all sides?
            - **Corners** (red) - Sharp or rounded/dinged?
            - **Edges** (green) - Any chipping or whitening?
            - **Surface** (purple) - Scratches, stains, creases?
            """)

        uploaded_photos = st.file_uploader(
            "Upload card photo(s)", type=["jpg","jpeg","png","webp"],
            accept_multiple_files=True)

        scan_mode = st.radio("Scan mode",
            ["Identify + Grade + Value", "Condition Grade Only"], horizontal=True)

        if uploaded_photos and st.button("Scan Card", type="primary"):
            if not API_KEY:
                st.error("No API key. Set ANTHROPIC_API_KEY in ~/axiom/.env")
            else:
                with st.spinner("Analyzing card..."):
                    try:
                        from engine import VisionEngine
                        from card_prompts import CARD_IDENTIFIER, CARD_CONDITION_ONLY

                        engine = VisionEngine(provider="haiku")
                        photo = uploaded_photos[0]
                        img_bytes = photo.read()

                        prompt = CARD_IDENTIFIER if scan_mode.startswith("Identify") else CARD_CONDITION_ONLY
                        results = engine.analyze(img_bytes, prompt)

                        if results:
                            r = results[0].raw
                            st.success("Card analyzed!")

                            # Show the uploaded image
                            col1, col2 = st.columns([1, 2])
                            with col1:
                                st.image(img_bytes, width=250)

                            with col2:
                                if "player_name" in r:
                                    st.markdown(f"### {r.get('player_name','Unknown')} - {r.get('year','')} {r.get('card_set','')}")
                                    st.markdown(f"**Card #:** {r.get('card_number','')} | **Set:** {r.get('card_set','')} | **Variant:** {r.get('variant','')}")

                                # Condition grades
                                st.markdown("---")
                                st.markdown("### Condition Assessment")
                                gc = st.columns(5)
                                grade_items = [
                                    ("Centering", r.get("centering", r.get("centering_front","?"))),
                                    ("Corners", r.get("corners","?")),
                                    ("Edges", r.get("edges","?")),
                                    ("Surface", r.get("surface", r.get("surface_front","?"))),
                                    ("Overall", r.get("overall_grade","?")),
                                ]
                                for i, (label, val) in enumerate(grade_items):
                                    with gc[i]:
                                        color = "#2ecc71" if str(val).isdigit() and int(str(val)) >= 8 else "#f39c12" if str(val).isdigit() and int(str(val)) >= 5 else "#e74c3c"
                                        st.markdown(f"<div style='text-align:center'><span style='font-size:28px;color:{color};font-weight:bold'>{val}</span><br/><small>{label}</small></div>", unsafe_allow_html=True)

                                st.markdown(f"**Notes:** {r.get('condition_notes','')}")

                                if r.get("estimated_value"):
                                    st.markdown(f"**Estimated Value:** ${r['estimated_value']} ({r.get('value_confidence','?')} confidence)")
                                    st.caption(r.get("value_source",""))
                                elif "player_name" in r:
                                    st.info("Value not estimated - use the search feature for real market prices.")

                                # Add to collection button
                                if "player_name" in r:
                                    if st.button("Add to Collection"):
                                        conn = get_db()
                                        conn.execute("""INSERT INTO cards (card_number,quantity,year,team,player,
                                            description,company,value_raw,is_notable,notes,last_updated)
                                            VALUES (?,1,?,?,?,?,?,?,?,?,?)""",
                                            (r.get("card_number",""), r.get("year",0), "",
                                             r.get("player_name",""),
                                             f"{r.get('variant','')}",
                                             r.get("card_set",""),
                                             str(r.get("estimated_value","")) if r.get("estimated_value") else "",
                                             1 if is_notable(r.get("player_name",""), r.get("year",0)) else 0,
                                             f"AI Grade: {r.get('overall_grade','?')}/10. {r.get('condition_notes','')}",
                                             datetime.now().isoformat()))
                                        conn.commit(); conn.close()
                                        st.success("Added to collection!")
                        else:
                            st.warning("Could not analyze the image. Try a clearer photo.")
                    except Exception as e:
                        st.error(f"Scan error: {e}")

    # ── TAB 3: Ask AX ──
    with tab3:
        st.subheader("Ask AX")
        st.caption("Your family AI assistant. Ask about cards, values, grading, selling - anything.")

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        # Display chat history
        for msg in st.session_state.chat_history:
            role_name = "AX" if msg["role"] == "assistant" else "You"
            avatar = "\U0001f916" if msg["role"] == "assistant" else "\U0001f9d1"
            with st.chat_message(msg["role"], avatar=avatar):
                st.markdown(msg["content"])

        # Chat input
        if prompt := st.chat_input("Ask AX anything about your cards..."):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user", avatar="\U0001f9d1"):
                st.markdown(prompt)

            with st.chat_message("assistant", avatar="\U0001f916"):
                with st.spinner("AX is thinking..."):
                    context = f"Collection has {stats['total']} cards, spanning {stats['years'][0] if stats['years'] else '?'} to {stats['years'][-1] if stats['years'] else '?'}. Companies: {', '.join(stats['companies'][:5])}."
                    response = chat_with_ax(prompt, context, history=st.session_state.chat_history, app_type="baseball")
                    st.markdown(response)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})

        if st.session_state.chat_history and st.button("Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()

    # ── TAB 4: Sell Cards ──
    with tab4:
        st.subheader("Sell Your Cards")
        st.markdown("Generate ready-to-use eBay listings or auction house submissions.")

        sell_col1, sell_col2 = st.columns([1, 1])

        with sell_col1:
            st.markdown("### Create a Listing")
            sell_method = st.radio("Sell via", ["eBay", "Auction House", "Local Card Shop"], horizontal=True)

            # Manual entry
            sell_player = st.text_input("Player Name", placeholder="e.g. Ken Griffey Jr.")
            sell_scol1, sell_scol2, sell_scol3 = st.columns(3)
            with sell_scol1:
                sell_year = st.text_input("Year", placeholder="1989")
            with sell_scol2:
                sell_set = st.text_input("Card Set", placeholder="Upper Deck")
            with sell_scol3:
                sell_number = st.text_input("Card #", placeholder="1")
            sell_condition = st.selectbox("Condition", ["Mint", "Near Mint", "Excellent", "Good", "Fair", "Poor"])
            sell_notes = st.text_input("Additional notes", placeholder="Rookie card, centered, clean corners")

            if st.button("Generate Listing", type="primary"):
                if sell_player:
                    card_info = f"{sell_year} {sell_set} #{sell_number} {sell_player} - Condition: {sell_condition}. {sell_notes}"
                    with st.spinner("AX is writing your listing..."):
                        if sell_method == "eBay":
                            listing = generate_sell_listing(card_info)
                        elif sell_method == "Auction House":
                            listing = chat_with_ax(
                                f"Write a professional auction house submission letter for this card: {card_info}. "
                                f"Include: item description, provenance (from personal collection), condition notes, "
                                f"and suggest which auction houses specialize in sports cards (Heritage Auctions, "
                                f"Goldin Auctions, REA, Lelands). Format as a ready-to-send email.",
                                app_type="baseball")
                        else:
                            listing = chat_with_ax(
                                f"Write a description card for bringing this to a local card shop: {card_info}. "
                                f"Include what to ask for, what price to expect, and negotiation tips.",
                                app_type="baseball")
                        st.session_state["last_listing"] = listing
                else:
                    st.warning("Enter a player name.")

        with sell_col2:
            st.markdown("### Your Listing")
            if "last_listing" in st.session_state:
                st.markdown(st.session_state["last_listing"])
                st.download_button("Copy as Text File",
                    st.session_state["last_listing"],
                    f"listing_{sell_player}_{sell_year}.txt" if sell_player else "listing.txt",
                    "text/plain")
            else:
                st.info("Fill in the card details and click 'Generate Listing' to create a sell-ready description.")

        st.markdown("---")
        st.markdown("### Sell from Collection")
        st.caption("Select a card from your collection to generate a listing.")
        conn = get_db()
        sellable = pd.read_sql_query(
            "SELECT id, card_number, year, player, company, value_raw FROM cards WHERE player != '' ORDER BY year", conn)
        conn.close()
        if not sellable.empty:
            selected_card = st.selectbox("Pick a card",
                sellable.apply(lambda r: f"#{r['card_number']} {r['year']} {r['company']} {r['player']} ({r['value_raw'] or 'no price'})", axis=1))
            if selected_card and st.button("Generate Listing for This Card"):
                with st.spinner("AX is writing..."):
                    listing = generate_sell_listing(selected_card)
                    st.markdown(listing)

    # ── TAB 5: Valuable Cards ──
    with tab5:
        st.subheader("Notable & Valuable Cards")
        conn = get_db()
        val_df = pd.read_sql_query("""
            SELECT id, card_number as '#', year as Year, team as Team, player as Player,
                   company as Company, description as Desc, quantity as Qty,
                   value_raw as 'Raw Value', value_psa9 as 'PSA 9', value_psa10 as 'PSA 10',
                   notes as Notes
            FROM cards WHERE is_notable=1 ORDER BY year ASC
        """, conn)
        conn.close()

        if val_df.empty:
            st.info("Import cards first - notable cards auto-detected.")
        else:
            st.markdown(f"**{len(val_df)} notable cards** in your collection")
            st.dataframe(val_df.drop(columns=["id"]), use_container_width=True, height=600)

    # ── TAB 6: Stats ──
    with tab6:
        st.subheader("Collection Statistics")
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Entries", f"{stats['total']:,}")
        c2.metric("Total Cards", f"{stats['total_qty']:,}")
        c3.metric("Notable", f"{stats['notable']:,}")
        c4.metric("Priced", f"{stats['with_values']:,}")

        if stats["total"] > 0:
            conn = get_db()
            yd = pd.read_sql_query("SELECT year, SUM(quantity) as cards FROM cards WHERE year>0 GROUP BY year ORDER BY year", conn)
            cd = pd.read_sql_query("SELECT company, COUNT(*) as count FROM cards WHERE company!='' GROUP BY company ORDER BY count DESC LIMIT 10", conn)
            td = pd.read_sql_query("SELECT team, COUNT(*) as count FROM cards WHERE team!='' GROUP BY team ORDER BY count DESC LIMIT 20", conn)
            conn.close()
            if not yd.empty:
                st.subheader("Cards by Year")
                st.bar_chart(yd.set_index("year")["cards"])
            if not cd.empty:
                st.subheader("Cards by Company")
                st.bar_chart(cd.set_index("company")["count"])
            if not td.empty:
                st.subheader("Top Teams")
                st.bar_chart(td.set_index("team")["count"])

    # ── TAB 7: Import/Export ──
    with tab7:
        st.subheader("Import / Export")

        imp_col, exp_col = st.columns(2)

        with imp_col:
            st.markdown("### Import Cards")
            st.markdown("Paste tab-separated data: `No. | Qty | Year | Team | Pos | Player | Desc | Company | Location | Value`")

            paste_data = st.text_area("Paste spreadsheet (tab-separated)", height=200,
                placeholder="162\t1\t1952\tGiants\tLF/RF\tMonte Irvin\t...\tBowman\t...\t")

            if st.button("Import Cards", type="primary"):
                if paste_data.strip():
                    count, notable = import_tsv_data(paste_data)
                    st.success(f"Imported {count} cards ({notable} notable)")
                    st.rerun()
                else: st.warning("Paste data first.")

            uploaded = st.file_uploader("Or upload CSV/TSV", type=["csv","tsv","txt"])
            if uploaded:
                content = uploaded.read().decode('utf-8', errors='replace')
                count, notable = import_tsv_data(content)
                st.success(f"Imported {count} cards ({notable} notable)")
                st.rerun()

        with exp_col:
            st.markdown("### Export Collection")

            if stats["total"] > 0:
                conn = get_db()
                all_df = pd.read_sql_query("SELECT * FROM cards ORDER BY year, card_number", conn)
                conn.close()

                # CSV export
                csv_buf = io.StringIO()
                all_df.to_csv(csv_buf, index=False)
                st.download_button("Download CSV", csv_buf.getvalue(), "baseball_cards.csv", "text/csv")

                # TSV export
                tsv_buf = io.StringIO()
                all_df.to_csv(tsv_buf, index=False, sep='\t')
                st.download_button("Download TSV", tsv_buf.getvalue(), "baseball_cards.tsv", "text/tab-separated-values")

                # JSON export
                json_str = all_df.to_json(orient="records", indent=2)
                st.download_button("Download JSON", json_str, "baseball_cards.json", "application/json")
            else:
                st.info("No cards to export.")

            st.markdown("---")
            st.markdown(f"**Database:** {stats['total']} cards")
            if stats['total'] > 0 and st.button("Clear All Cards"):
                conn = get_db(); conn.execute("DELETE FROM cards"); conn.commit(); conn.close()
                st.success("Cleared."); st.rerun()

if __name__ == "__main__":
    main()
