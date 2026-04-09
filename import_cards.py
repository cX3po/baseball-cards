#!/usr/bin/env python3
"""Import Phil's baseball card spreadsheet into SQLite."""
import sqlite3
import os
import csv

DB_PATH = os.path.join(os.path.dirname(__file__), "db", "cards.db")

def create_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS cards")
    c.execute("""
        CREATE TABLE cards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            card_number TEXT,
            quantity INTEGER DEFAULT 1,
            year INTEGER,
            team TEXT,
            position TEXT,
            player TEXT,
            description TEXT,
            company TEXT,
            location TEXT,
            value_raw TEXT,
            value_psa8 TEXT,
            value_psa9 TEXT,
            value_psa10 TEXT,
            value_source TEXT,
            is_notable INTEGER DEFAULT 0,
            notes TEXT,
            last_updated TEXT
        )
    """)
    conn.commit()
    return conn

# Notable players/cards that deserve value lookups
NOTABLE_PLAYERS = {
    "ted williams", "sandy koufax", "yogi berra", "ernie banks", "whitey ford",
    "warren spahn", "bob lemon", "willie mays", "nellie fox", "don drysdale",
    "roberto clemente", "bob clemente", "stan musial", "bob gibson", "monte irvin",
    "mickey mantle", "hank aaron", "pete rose", "johnny bench", "nolan ryan",
    "reggie jackson", "mike schmidt", "george brett", "rickey henderson",
    "robin yount", "carl yastrzemski", "tom seaver", "steve carlton", "rod carew",
    "joe morgan", "ozzie smith", "eddie murray", "cal ripken", "cal ripken jr.",
    "gary carter", "dave winfield", "jim palmer", "dennis eckersley", "rollie fingers",
    "don sutton", "phil niekro", "gaylord perry", "fergie jenkins", "ferguson jenkins",
    "willie stargell", "harmon killebrew", "al kaline", "brooks robinson",
    "frank robinson", "luis aparicio", "billy williams", "wade boggs",
    "ryne sandberg", "barry bonds", "mark mcgwire", "kirby puckett",
    "dale murphy", "andre dawson", "tim raines", "paul molitor", "jack morris",
    "bert blyleven", "bruce sutter", "tony gwynn", "barry larkin", "dave parker",
    "carlton fisk", "don mattingly", "dwight gooden", "darryl strawberry",
    "willie mccovey", "juan marichal", "hoyt wilhelm", "ron santo",
    "tony oliva", "keith hernandez", "george foster", "cecil cooper",
    "joe carter", "lee smith", "orel hershiser", "fernando valenzuela",
    "lou brock", "billy martin", "sparky anderson", "tommy lasorda",
    "earl weaver", "joe torre", "bobby cox", "whitey herzog",
    "dave concepcion", "jim rice", "fred lynn", "dwight evans",
    "steve garvey", "bob horner", "buddy bell", "alan trammell",
    "lou whitaker", "lance parrish", "kirk gibson", "jack clark",
    "tony perez", "willie wilson", "cecil fielder", "bobby valentine",
    "eric davis", "jose canseco", "will clark", "roger clemens",
    "greg maddux", "john smoltz", "frank viola", "bret saberhagen",
    "kent hrbek", "sid fernandez", "rick sutcliffe", "bo jackson",
    "don larsen", "honus wagner", "pie traynor", "walter johnson",
    "ty cobb", "lou gehrig", "thurman munson", "red schoendienst",
    "enos slaughter", "richie ashburn", "curt flood", "dick groat",
    "bill skowron", "elston howard", "ken boyer", "harvey kuenn",
    "minnie minoso", "bobby murcer", "joe pepitone", "tony conigliaro",
}

def parse_tsv_line(line):
    """Parse a tab-separated line from the spreadsheet."""
    parts = line.split('\t')
    while len(parts) < 10:
        parts.append("")

    card_num = parts[0].strip()
    qty_str = parts[1].strip()
    year_str = parts[2].strip()
    team = parts[3].strip()
    position = parts[4].strip()
    player = parts[5].strip()
    description = parts[6].strip()
    company = parts[7].strip()
    location = parts[8].strip()
    value_str = parts[9].strip() if len(parts) > 9 else ""

    # Parse quantity
    try:
        qty = int(qty_str)
    except (ValueError, TypeError):
        qty = 1

    # Parse year
    try:
        year = int(year_str)
    except (ValueError, TypeError):
        year = 0

    return {
        "card_number": card_num,
        "quantity": qty,
        "year": year,
        "team": team,
        "position": position,
        "player": player,
        "description": description,
        "company": company,
        "location": location,
        "value_raw": value_str,
    }

def is_notable(player, year, card_num, description, company):
    """Check if a card is notable and worth a value lookup."""
    if not player:
        return False
    name_lower = player.lower().strip()

    # Check against notable players list
    if name_lower in NOTABLE_PLAYERS:
        return True

    # Check for partial matches
    for notable in NOTABLE_PLAYERS:
        if notable in name_lower or name_lower in notable:
            return True

    # Pre-1960 cards are generally notable
    if year and year < 1960:
        return True

    # Cards with existing values are notable
    if description and any(kw in description.lower() for kw in ["rookie", "record breaker", "all star", "all-star", "mvp", "future star"]):
        return True

    return False

def import_data(conn, filepath):
    c = conn.cursor()
    count = 0
    notable_count = 0

    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            line = line.rstrip('\n\r')
            if not line.strip():
                continue

            # Skip header lines
            if line.startswith("Phil's") or line.startswith("No.\t"):
                continue

            data = parse_tsv_line(line)

            # Skip if no useful data
            if not data["player"] and not data["team"] and not data["description"]:
                continue

            notable = is_notable(
                data["player"], data["year"], data["card_number"],
                data["description"], data["company"]
            )
            if notable:
                notable_count += 1

            c.execute("""
                INSERT INTO cards (card_number, quantity, year, team, position, player,
                    description, company, location, value_raw, is_notable)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data["card_number"], data["quantity"], data["year"],
                data["team"], data["position"], data["player"],
                data["description"], data["company"], data["location"],
                data["value_raw"], 1 if notable else 0
            ))
            count += 1

    conn.commit()
    return count, notable_count

if __name__ == "__main__":
    data_file = os.path.join(os.path.dirname(__file__), "data", "phils_cards.tsv")
    if not os.path.exists(data_file):
        print(f"Data file not found: {data_file}")
        print("Please save the spreadsheet as phils_cards.tsv first.")
        exit(1)

    conn = create_db()
    total, notable = import_data(conn, data_file)
    conn.close()
    print(f"Imported {total} cards ({notable} notable/valuable)")
    print(f"Database saved to {DB_PATH}")
