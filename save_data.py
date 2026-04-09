"""Save Phil's card data directly into SQLite from hardcoded notable values."""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "db", "cards.db")

# Pre-researched values for notable cards
KNOWN_VALUES = {
    # (year, company_contains, player_contains, card_num): (raw, psa8, psa9, psa10, source)
    # 1952 Bowman
    (1952, "bowman", "monte irvin", "162"): ("$35-85", "$150+", "$500+", "$1,000+", "web search 2026"),
    # 1956 Topps (T.C.G.)
    (1956, "t.c.g", "ted williams", "5"): ("$250+", "$500+", "$1,500+", "$5,000+", "web search 2026"),
    (1956, "t.c.g", "sandy koufax", "79"): ("$475+", "$1,000+", "$3,000+", "$10,000+", "web search 2026"),
    (1956, "t.c.g", "yogi berra", "110"): ("$130+", "$300+", "$800+", "$3,000+", "web search 2026"),
    (1956, "t.c.g", "ernie banks", "15"): ("$100+", "$250+", "$600+", "$2,000+", "web search 2026"),
    (1956, "t.c.g", "whitey ford", "240"): ("$97+", "$200+", "$500+", "$2,000+", "web search 2026"),
    (1956, "t.c.g", "bob lemon", "255"): ("$75", "$150+", "$400+", "$1,500+", "web search 2026"),
    (1956, "t.c.g", "warren spahn", "10"): ("$50+", "$100+", "$300+", "$1,000+", "web search 2026"),
    (1956, "t.c.g", "enos slaughter", "109"): ("$20+", "$50+", "$150+", "$500+", "web search 2026"),
    (1956, "t.c.g", "early wynn", "187"): ("$24", "$50+", "$150+", "$500+", "web search 2026"),
    (1956, "t.c.g", "bill skowron", "61"): ("$15+", "$40+", "$100+", "$400+", "web search 2026"),
    (1956, "t.c.g", "red schoendienst", "165"): ("$15+", "$40+", "$100+", "$400+", "web search 2026"),
    (1956, "t.c.g", "harvey kuenn", "155"): ("$10+", "$25+", "$75+", "$300+", "web search 2026"),
    (1956, "t.c.g", "dick groat", "24"): ("$10+", "$25+", "$75+", "$300+", "web search 2026"),
    (1956, "t.c.g", "minnie minoso", "125"): ("$15+", "$40+", "$100+", "$400+", "web search 2026"),
    # 1957 Topps
    (1957, "t.c.g", "willie mays", "10"): ("$200+", "$500+", "$1,500+", "$5,000+", "web search 2026"),
    (1957, "t.c.g", "nellie fox", "38"): ("$30+", "$75+", "$200+", "$600+", "web search 2026"),
    # 1958 Topps
    (1958, "t.c.g", "willie mays", "5"): ("$150+", "$400+", "$1,000+", "$4,000+", "web search 2026"),
    (1958, "t.c.g", "don drysdale", "25"): ("$50+", "$100+", "$300+", "$1,000+", "web search 2026"),
    # 1960 Topps
    (1960, "t.c.g", "bob clemente", "326"): ("$169", "$400+", "$1,000+", "$5,000+", "web search 2026"),
    (1960, "t.c.g", "stan musial", "250"): ("$149", "$300+", "$800+", "$3,000+", "web search 2026"),
    (1960, "t.c.g", "sandy koufax", "343"): ("$350", "$700+", "$2,000+", "$8,000+", "web search 2026"),
    (1960, "t.c.g", "bob gibson", "73"): ("$35", "$80+", "$200+", "$800+", "web search 2026"),
    (1960, "t.c.g", "whitey ford", "35"): ("$25+", "$60+", "$150+", "$600+", "web search 2026"),
    (1960, "t.c.g", "nellie fox", "100"): ("$25", "$60+", "$150+", "$600+", "web search 2026"),
    (1960, "t.c.g", "don larsen", "353"): ("$70", "$150+", "$400+", "$1,500+", "web search 2026"),
    (1960, "t.c.g", "luis aparicio", "240"): ("$15+", "$40+", "$100+", "$400+", "web search 2026"),
    (1960, "t.c.g", "richie ashburn", "305"): ("$10+", "$25+", "$75+", "$300+", "web search 2026"),
    (1960, "t.c.g", "curt flood", "275"): ("$11", "$25+", "$75+", "$300+", "web search 2026"),
    (1960, "t.c.g", "felipe alou", "287"): ("$3-5", "$15+", "$40+", "$150+", "web search 2026"),
    # 1970 Topps
    (1970, "t.c.g", "johnny bench", "660"): ("$50+", "$150+", "$400+", "$2,000+", "web search 2026"),
    (1970, "t.c.g", "carl yastrzemski", "10"): ("$10", "$25+", "$75+", "$300+", "web search 2026"),
    (1970, "t.c.g", "brooks robinson", "230"): ("$15+", "$40+", "$100+", "$400+", "web search 2026"),
    (1970, "t.c.g", "hoyt wilhelm", "17"): ("$35", "$75+", "$200+", "$600+", "web search 2026"),
    (1970, "t.c.g", "phil niekro", "160"): ("$10", "$25+", "$60+", "$200+", "web search 2026"),
    (1970, "t.c.g", "juan marichal", "210"): ("$6", "$15+", "$40+", "$150+", "web search 2026"),
    (1970, "t.c.g", "lou piniella", "321"): ("$3+", "$10+", "$25+", "$100+", "web search 2026"),
    # 1971 Topps
    (1971, "t.c.g", "pete rose", "100"): ("$30+", "$75+", "$200+", "$800+", "web search 2026"),
    (1971, "t.c.g", "al kaline", "180"): ("$15+", "$40+", "$100+", "$400+", "web search 2026"),
    (1971, "t.c.g", "phil niekro", "30"): ("$4", "$10+", "$25+", "$100+", "web search 2026"),
    (1971, "t.c.g", "rollie fingers", "384"): ("$3+", "$10+", "$25+", "$100+", "web search 2026"),
    (1971, "t.c.g", "steve garvey", "341"): ("$20+", "$50+", "$150+", "$500+", "web search 2026"),
    (1971, "t.c.g", "joe torre", "370"): ("$4", "$10+", "$25+", "$100+", "web search 2026"),
    (1971, "t.c.g", "paul blair", "53"): ("$60", "$100+", "$250+", "$800+", "web search 2026"),
    (1971, "t.c.g", "sal bando", "285"): ("$2", "$5+", "$15+", "$50+", "web search 2026"),
    (1971, "t.c.g", "ron santo", "220"): ("$5+", "$15+", "$40+", "$150+", "web search 2026"),
    (1971, "t.c.g", "juan marichal", "325"): ("$5+", "$15+", "$40+", "$150+", "web search 2026"),
    (1971, "t.c.g", "tony oliva", "290"): ("$3+", "$10+", "$25+", "$100+", "web search 2026"),
    (1971, "t.c.g", "hoyt wilhelm", "248"): ("$3+", "$10+", "$25+", "$100+", "web search 2026"),
    # 1972 Topps
    (1972, "t.c.g", "carl yastrzemski", "37"): ("$10+", "$25+", "$75+", "$300+", "web search 2026"),
    (1972, "t.c.g", "roberto clemente", "309"): ("$50+", "$150+", "$400+", "$2,000+", "web search 2026"),
    (1972, "t.c.g", "jim palmer", "270"): ("$15+", "$40+", "$100+", "$400+", "web search 2026"),
    (1972, "t.c.g", "lou brock", "200"): ("$15+", "$40+", "$100+", "$400+", "web search 2026"),
    (1972, "t.c.g", "bob gibson", "130"): ("$15+", "$40+", "$100+", "$400+", "web search 2026"),
    (1972, "t.c.g", "george foster", "256"): ("$3+", "$10+", "$25+", "$100+", "web search 2026"),
    # 1973 Topps
    (1973, "t.c.g", "roberto clemente", "50"): ("$300", "$500+", "$1,500+", "$5,000+", "web search 2026 - memorial card"),
    (1973, "t.c.g", "reggie jackson", "255"): ("$100", "$200+", "$500+", "$2,000+", "web search 2026"),
    (1973, "t.c.g", "harmon killebrew", "170"): ("$123", "$200+", "$500+", "$2,000+", "web search 2026"),
    (1973, "t.c.g", "joe morgan", "230"): ("$40", "$75+", "$200+", "$600+", "web search 2026"),
    (1973, "t.c.g", "steve carlton", "300"): ("$25", "$50+", "$150+", "$500+", "web search 2026"),
    (1973, "t.c.g", "bobby murcer", "240"): ("$40", "$75+", "$200+", "$600+", "web search 2026"),
    (1973, "t.c.g", "don sutton", "10"): ("$4", "$10+", "$25+", "$100+", "web search 2026"),
    (1973, "t.c.g", "gaylord perry", "400"): ("$5", "$15+", "$40+", "$150+", "web search 2026"),
    (1973, "t.c.g", "bobby bonds", "145"): ("$8", "$20+", "$50+", "$200+", "web search 2026"),
    (1973, "t.c.g", "dave concepcion", "554"): ("$15", "$30+", "$75+", "$300+", "web search 2026"),
    (1973, "t.c.g", "frank robinson", "175"): ("$3+", "$10+", "$25+", "$100+", "web search 2026"),
    # 1974 Topps
    (1974, "t.c.g", "hank aaron", "1"): ("$20+", "$50+", "$150+", "$500+", "web search 2026"),
    (1974, "t.c.g", "mike schmidt", "283"): ("$100+", "$200+", "$600+", "$2,500+", "web search 2026"),
    (1974, "t.c.g", "reggie jackson", "130"): ("$15+", "$40+", "$100+", "$400+", "web search 2026"),
    (1974, "t.c.g", "jim palmer", "40"): ("$5+", "$15+", "$40+", "$150+", "web search 2026"),
    (1974, "t.c.g", "tom seaver", "80"): ("$10+", "$25+", "$75+", "$300+", "web search 2026"),
    (1974, "t.c.g", "harmon killebrew", "400"): ("$50", "$100+", "$300+", "$1,000+", "web search 2026"),
    (1974, "t.c.g", "dave concepcion", "435"): ("$125", "$200+", "$500+", "$1,500+", "web search 2026"),
    (1974, "t.c.g", "carlton fisk", "105"): ("$10+", "$25+", "$75+", "$300+", "web search 2026"),
    (1974, "t.c.g", "willie mccovey", "250"): ("$5+", "$15+", "$40+", "$150+", "web search 2026"),
    # 1975 Topps
    (1975, "topps", "robin yount", "223"): ("$83", "$150+", "$400+", "$1,500+", "web search 2026 - RC"),
    (1975, "topps", "nolan ryan", "500"): ("$50+", "$100+", "$300+", "$1,000+", "web search 2026"),
    (1975, "topps", "jim palmer", "335"): ("$10", "$25+", "$75+", "$300+", "web search 2026"),
    (1975, "topps", "tom seaver", "370"): ("$15", "$30+", "$75+", "$300+", "web search 2026"),
    (1975, "topps", "bob gibson", "150"): ("$22", "$50+", "$100+", "$400+", "web search 2026"),
    (1975, "topps", "fergie jenkins", "60"): ("$29", "$50+", "$100+", "$400+", "web search 2026"),
    (1975, "topps", "rollie fingers", "21"): ("$4+", "$10+", "$25+", "$100+", "web search 2026"),
    (1975, "topps", "harmon killebrew", "640"): ("$5", "$15+", "$40+", "$150+", "web search 2026"),
    # 1978 Topps
    (1978, "t.c.g", "nolan ryan", "400"): ("$30+", "$75+", "$200+", "$800+", "web search 2026"),
    (1978, "topps", "paul molitor", "707"): ("$30+", "$75+", "$200+", "$800+", "web search 2026 - dual RC"),
    # 1980 Topps
    (1980, "t.c.g", "rickey henderson", "482"): ("$50+", "$150+", "$400+", "$2,000+", "web search 2026 - RC"),
    (1980, "topps", "rickey henderson", "482"): ("$50+", "$150+", "$400+", "$2,000+", "web search 2026 - RC"),
    # 1981 Donruss
    (1981, "donruss", "ozzie smith", "1"): ("$1-5", "$20+", "$47", "$150+", "web search 2026"),
    (1981, "donruss", "mike schmidt", "11"): ("$2-6", "$15+", "$20+", "$100+", "web search 2026"),
    (1981, "donruss", "steve carlton", "33"): ("$1-3", "$15+", "$23", "$61", "web search 2026"),
    (1981, "donruss", "rod carew", "49"): ("$1-3", "$10+", "$15+", "$60+", "web search 2026"),
    (1981, "donruss", "johnny bench", "62"): ("$1-3", "$11", "$8", "$50", "web search 2026"),
    (1981, "donruss", "george foster", "65"): ("$0.75", "", "", "", "web search 2026"),
    (1981, "donruss", "keith hernandez", "67"): ("$0.75", "", "", "", "web search 2026"),
    (1981, "donruss", "gary carter", "90"): ("$1-2", "$7+", "$20", "$42", "web search 2026"),
    (1981, "donruss", "carl yastrzemski", "94"): ("$1-5", "$10+", "$20+", "$58", "web search 2026"),
    (1981, "donruss", "dennis eckersley", "96"): ("$1", "$5+", "$10+", "$40+", "web search 2026"),
    (1981, "donruss", "george brett", "100"): ("$2-6", "$15+", "$30+", "$260", "web search 2026"),
    (1981, "donruss", "eddie murray", "112"): ("$1-2", "$7+", "$21", "$57", "web search 2026"),
    (1981, "donruss", "rickey henderson", "119"): ("$5-15", "$50+", "$48", "$1,264", "web search 2026"),
    (1981, "donruss", "jack morris", "127"): ("$1", "$5+", "$10+", "$27+", "web search 2026"),
    (1981, "donruss", "pete rose", "131"): ("$3.50", "$10+", "$25+", "$80+", "web search 2026"),
    (1981, "donruss", "willie stargell", "132"): ("$3", "$8+", "$20+", "$68", "web search 2026"),
    (1981, "donruss", "bert blyleven", "135"): ("$2", "$5+", "$10+", "$40+", "web search 2026"),
    (1981, "donruss", "ferguson jenkins", "146"): ("$0.75", "$3+", "$10+", "$40+", "web search 2026"),
    (1981, "donruss", "joe morgan", "18"): ("$1-2", "$5+", "$10+", "$32", "web search 2026"),
    (1981, "donruss", "rollie fingers", "2"): ("$0.75", "$3+", "$10+", "$30+", "web search 2026"),
    (1981, "donruss", "don sutton", "58"): ("$0.60", "$3+", "$8+", "$35+", "web search 2026"),
    (1981, "donruss", "dave winfield", "364"): ("$2+", "$8+", "$20+", "$80+", "web search 2026"),
    (1981, "donruss", "reggie jackson", "228"): ("$2+", "$8+", "$20+", "$80+", "web search 2026"),
    (1981, "donruss", "tim raines", "538"): ("$5+", "$25+", "$50+", "$200+", "web search 2026"),
    (1981, "donruss", "andre dawson", "212"): ("$1+", "$5+", "$15+", "$50+", "web search 2026"),
    (1981, "donruss", "paul molitor", "203"): ("$2+", "$8+", "$20+", "$80+", "web search 2026"),
    (1981, "donruss", "robin yount", "323"): ("$2+", "$8+", "$20+", "$80+", "web search 2026"),
    (1981, "donruss", "tom seaver", "422"): ("$2+", "$8+", "$20+", "$60+", "web search 2026"),
    (1981, "donruss", "nolan ryan", ""): ("$3+", "$10+", "$30+", "$100+", "web search 2026"),
    (1981, "donruss", "sparky anderson", "370"): ("$1+", "$3+", "$10+", "$40+", "web search 2026"),
    (1981, "donruss", "bruce sutter", "560"): ("$1+", "$3+", "$10+", "$40+", "web search 2026"),
    # 1983 cards
    (1983, "donruss", "nolan ryan", "23"): ("$10+", "$25+", "$75+", "$300+", "web search 2026"),
    (1983, "donruss", "cal ripken", "52"): ("$10+", "$25+", "$75+", "$300+", "web search 2026"),
    (1983, "fleer", "wade boggs", "179"): ("$10", "$25+", "$50+", "$200+", "web search 2026 - RC"),
    (1983, "fleer", "cal ripken", "70"): ("$15", "$30+", "$75+", "$300+", "web search 2026"),
    (1983, "topps", "ryne sandberg", "83"): ("$15+", "$40+", "$100+", "$400+", "web search 2026"),
    (1983, "topps", "wade boggs", "498"): ("$5+", "$15+", "$40+", "$150+", "web search 2026"),
    (1983, "topps", "tony gwynn", "482"): ("$10+", "$25+", "$75+", "$300+", "web search 2026"),
    (1983, "topps", "cal ripken", "163"): ("$10+", "$25+", "$75+", "$300+", "web search 2026"),
    (1983, "topps", "nolan ryan", "360"): ("$3+", "$10+", "$25+", "$100+", "web search 2026"),
    # 1987 Topps
    (1987, "topps", "barry bonds", "320"): ("$100", "$200+", "$500+", "$2,000+", "web search 2026 - RC"),
    (1987, "topps", "mark mcgwire", "366"): ("$5+", "$15+", "$40+", "$150+", "web search 2026 - RC"),
    (1987, "topps", "barry larkin", "648"): ("$5+", "$15+", "$40+", "$150+", "web search 2026 - RC"),
    (1987, "topps", "bo jackson", "170"): ("$3+", "$10+", "$25+", "$100+", "web search 2026 - RC"),
    (1987, "topps", "jose canseco", "620"): ("$3+", "$10+", "$25+", "$100+", "web search 2026"),
    (1987, "topps", "rafael palmeiro", "634"): ("$2+", "$8+", "$20+", "$80+", "web search 2026 - RC"),
    (1987, "topps", "roger clemens", "340"): ("$3+", "$10+", "$25+", "$100+", "web search 2026"),
    (1987, "topps", "don mattingly", "500"): ("$3+", "$10+", "$25+", "$100+", "web search 2026"),
    (1987, "topps", "kirby puckett", "450"): ("$2+", "$8+", "$20+", "$80+", "web search 2026"),
    (1987, "topps", "will clark", "420"): ("$2+", "$8+", "$20+", "$60+", "web search 2026 - RC"),
    (1987, "topps", "bobby bonilla", "184"): ("$1+", "$5+", "$15+", "$50+", "web search 2026 - RC"),
    # 1982 Topps/Fleer
    (1982, "topps", "cal ripken", "21"): ("$20+", "$50+", "$150+", "$600+", "web search 2026 - RC"),
    (1982, "fleer", "cal ripken", "176"): ("$15+", "$40+", "$100+", "$400+", "web search 2026 - RC"),
    # 1985 Topps
    (1985, "topps", "kirby puckett", "536"): ("$5+", "$15+", "$40+", "$150+", "web search 2026 - RC"),
    (1985, "topps", "don mattingly", "665"): ("$5+", "$15+", "$40+", "$150+", "web search 2026"),
    (1985, "topps", "dwight gooden", "620"): ("$3+", "$10+", "$25+", "$100+", "web search 2026 - RC"),
    (1985, "fleer", "dwight gooden", "82"): ("$3+", "$10+", "$25+", "$100+", "web search 2026"),
    (1985, "topps", "roger clemens", ""): ("$5+", "$15+", "$40+", "$150+", "web search 2026 - RC"),
    # 1984 Topps
    (1984, "topps", "don mattingly", "8"): ("$15+", "$40+", "$100+", "$400+", "web search 2026 - RC"),
    (1984, "topps", "darryl strawberry", "182"): ("$3+", "$10+", "$25+", "$100+", "web search 2026 - RC"),
    # 1977 Kelloggs
    (1977, "kellogg", "thurman munson", "23"): ("$10+", "$25+", "", "", "web search 2026"),
    (1977, "kellogg", "dave parker", "19"): ("$3+", "$8+", "", "", "web search 2026"),
    # 1978 Kelloggs
    (1978, "kellogg", "lou brock", "7"): ("$5+", "$10+", "", "", "web search 2026"),
    # 1976 Hostess
    (1976, "hostess", "nolan ryan", "79"): ("$20+", "$50+", "", "", "web search 2026"),
    # 1979 Hostess
    (1979, "hostess", "johnny bench", "128"): ("$5+", "$10+", "", "", "web search 2026"),
    (1979, "hostess", "pete rose", "144"): ("$5+", "$10+", "", "", "web search 2026"),
}

def update_values():
    """Update known values in the database."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    updated = 0
    for (year, company_hint, player_hint, card_num), (raw, psa8, psa9, psa10, source) in KNOWN_VALUES.items():
        query = "UPDATE cards SET value_psa8=?, value_psa9=?, value_psa10=?, value_source=? WHERE year=?"
        params = [psa8, psa9, psa10, source, year]

        conditions = " AND year=?"
        if company_hint:
            conditions += " AND LOWER(company) LIKE ?"
            params.append(f"%{company_hint}%")
        if player_hint:
            conditions += " AND LOWER(player) LIKE ?"
            params.append(f"%{player_hint}%")
        if card_num:
            conditions += " AND card_number=?"
            params.append(card_num)

        full_query = f"UPDATE cards SET value_psa8=?, value_psa9=?, value_psa10=?, value_source=? WHERE year=?{conditions[len(' AND year=?'):]}"
        params_full = [psa8, psa9, psa10, source] + params[1:]

        c.execute(full_query, params_full)
        updated += c.rowcount

        # Also update raw value if not already set
        if raw:
            raw_query = f"UPDATE cards SET value_raw=COALESCE(NULLIF(value_raw,''), ?) WHERE year=?{conditions[len(' AND year=?'):]}"
            raw_params = [raw] + params[1:]
            c.execute(raw_query, raw_params)

    conn.commit()
    conn.close()
    print(f"Updated {updated} card value entries")

if __name__ == "__main__":
    update_values()
