#!/usr/bin/env python3
"""
Import Phil's cards from stdin (tab-separated).
Usage: paste spreadsheet data | python import_from_conversation.py
Or: python import_from_conversation.py < data/phils_cards.tsv
"""
import sqlite3
import sys
import os
import re

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "db", "cards.db")

NOTABLE_NAMES = {
    "ted williams", "sandy koufax", "yogi berra", "ernie banks", "whitey ford",
    "warren spahn", "bob lemon", "willie mays", "nellie fox", "don drysdale",
    "roberto clemente", "bob clemente", "stan musial", "bob gibson", "monte irvin",
    "mickey mantle", "hank aaron", "pete rose", "johnny bench", "nolan ryan",
    "reggie jackson", "mike schmidt", "george brett", "rickey henderson",
    "robin yount", "carl yastrzemski", "tom seaver", "steve carlton", "rod carew",
    "joe morgan", "ozzie smith", "eddie murray", "cal ripken", "gary carter",
    "dave winfield", "jim palmer", "dennis eckersley", "rollie fingers",
    "don sutton", "phil niekro", "gaylord perry", "fergie jenkins", "ferguson jenkins",
    "willie stargell", "harmon killebrew", "al kaline", "brooks robinson",
    "frank robinson", "billy williams", "wade boggs", "ryne sandberg",
    "barry bonds", "mark mcgwire", "kirby puckett", "dale murphy", "andre dawson",
    "tim raines", "paul molitor", "jack morris", "bert blyleven", "bruce sutter",
    "tony gwynn", "barry larkin", "dave parker", "carlton fisk", "don mattingly",
    "dwight gooden", "darryl strawberry", "willie mccovey", "juan marichal",
    "hoyt wilhelm", "ron santo", "tony oliva", "dave concepcion", "jim rice",
    "fred lynn", "dwight evans", "steve garvey", "alan trammell", "lou whitaker",
    "lance parrish", "kirk gibson", "jack clark", "tony perez", "cecil fielder",
    "eric davis", "jose canseco", "will clark", "roger clemens", "bo jackson",
    "don larsen", "honus wagner", "pie traynor", "walter johnson", "ty cobb",
    "lou gehrig", "thurman munson", "red schoendienst", "enos slaughter",
    "richie ashburn", "curt flood", "dick groat", "bill skowron", "elston howard",
    "ken boyer", "harvey kuenn", "minnie minoso", "bobby murcer", "joe pepitone",
    "tony conigliaro", "frank viola", "bret saberhagen", "kent hrbek", "joe carter",
    "lee smith", "orel hershiser", "fernando valenzuela", "willie wilson",
    "keith hernandez", "george foster", "cecil cooper", "bob horner",
    "buddy bell", "jim sundberg", "graig nettles", "tommy john",
    "luis aparicio", "roberto alomar", "johnny ray", "john franco",
    "rafael palmeiro", "mike greenwell", "greg maddux", "john smoltz",
    "sid fernandez", "rick sutcliffe", "roger maris", "joe torre",
    "sparky anderson", "tommy lasorda", "earl weaver", "whitey herzog",
    "bobby cox", "billy martin", "lou piniella", "dave kingman",
    "richie zisk", "al oliver", "ted simmons", "bill madlock",
    "tony pena", "johnny ray", "kent tekulve", "ron cey", "steve sax",
    "harold baines", "ron guidry", "rich gossage", "dan quisenberry",
    "jesse orosco", "dave righetti", "cecil cooper", "ben oglivie",
    "gorman thomas", "lou brock", "willie wilson", "vince coleman",
    "bobby bonilla", "andres galarraga", "bip roberts", "john kruk",
    "steve yeager", "mookie wilson", "wally backman", "len dykstra",
    "kevin mitchell", "manny trillo", "mike scott", "bob knepper",
    "jose cruz", "cesar cedeno", "nolan ryan", "j. r. richard",
    "mike lum", "billy martin", "yogi berra", "joe dimaggio",
    "dan ford", "mark fidrych", "dave rozema", "mickey klutts",
    "joe charboneau", "tony armas", "rickey henderson",
}

def is_notable(player, year, description=""):
    if not player:
        return False
    name = player.lower().strip()
    for n in NOTABLE_NAMES:
        if n in name or name in n:
            return True
    if year and year < 1965:
        return True
    desc_lower = (description or "").lower()
    if any(kw in desc_lower for kw in ["rookie", "record break", "all star", "all-star", "mvp", "future star", "highlight"]):
        return True
    return False

def import_stdin():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Create table if not exists
    c.execute("DROP TABLE IF EXISTS cards")
    c.execute("""
        CREATE TABLE cards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            card_number TEXT, quantity INTEGER DEFAULT 1,
            year INTEGER, team TEXT, position TEXT, player TEXT,
            description TEXT, company TEXT, location TEXT,
            value_raw TEXT, value_psa8 TEXT, value_psa9 TEXT, value_psa10 TEXT,
            value_source TEXT, is_notable INTEGER DEFAULT 0,
            notes TEXT, last_updated TEXT
        )
    """)

    count = 0
    notable_count = 0

    for line in sys.stdin:
        line = line.rstrip('\n\r')
        if not line.strip():
            continue
        if line.startswith("Phil's") or line.startswith("No.\t") or line.startswith("No.    "):
            continue

        # Split on tabs or multiple spaces (handle both)
        parts = line.split('\t')
        if len(parts) < 3:
            # Try splitting on 4+ spaces
            parts = re.split(r'\s{4,}', line)
        if len(parts) < 3:
            continue

        while len(parts) < 11:
            parts.append("")

        card_num = parts[0].strip()
        try:
            qty = int(parts[1].strip())
        except:
            qty = 1
        try:
            year = int(parts[2].strip())
        except:
            year = 0
        team = parts[3].strip()
        pos = parts[4].strip()
        player = parts[5].strip()
        desc = parts[6].strip()
        company = parts[7].strip()
        location = parts[8].strip()
        value = parts[9].strip() if len(parts) > 9 else ""

        if not player and not team and not desc:
            # Still import if we have card_num and company
            if not card_num and not company:
                continue

        notable = is_notable(player, year, desc)
        if notable:
            notable_count += 1

        c.execute("""
            INSERT INTO cards (card_number, quantity, year, team, position, player,
                description, company, location, value_raw, is_notable)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (card_num, qty, year, team, pos, player, desc, company, location, value, 1 if notable else 0))
        count += 1

    conn.commit()
    conn.close()
    print(f"Imported {count} cards ({notable_count} notable)")
    return count

if __name__ == "__main__":
    import_stdin()
