"""Baseball card specific prompts for the identifier engine."""

CARD_IDENTIFIER = """You are an expert baseball card identifier and grader. Look at this photo of a baseball card and provide a detailed analysis.

Identify:
- player_name: the player on the card
- year: the year printed on the card or estimated year
- card_set: the set name (e.g. "Topps", "Donruss", "Fleer", "Bowman", "Upper Deck")
- card_number: the card number if visible
- manufacturer: card manufacturer
- variant: any variant info (error card, rookie card, all-star, etc.)

Condition Assessment (PSA-style 1-10 scale):
- centering: rate 1-10 (check if image is centered equally on all sides)
- corners: rate 1-10 (sharp corners = 10, rounded/dinged = lower)
- edges: rate 1-10 (clean edges = 10, chipping/wear = lower)
- surface: rate 1-10 (clean surface = 10, scratches/stains = lower)
- overall_grade: estimated PSA grade 1-10 based on above
- condition_notes: describe any specific flaws you see

Value Assessment:
- estimated_value: estimated value in USD based on card + condition (integer, or null if unknown)
- value_source: "AI estimate based on card identification"
- value_confidence: high, medium, or low
- IMPORTANT: If you are not confident in the value, set estimated_value to null and say so. Never invent a price.

Return ONLY a JSON object, no markdown, no explanation. Example:
{"player_name": "Ken Griffey Jr.", "year": 1989, "card_set": "Upper Deck", "card_number": "1", "manufacturer": "Upper Deck", "variant": "Star Rookie", "centering": 8, "corners": 7, "edges": 8, "surface": 9, "overall_grade": 7, "condition_notes": "Slight corner wear on top-left, good centering, clean surface", "estimated_value": 50, "value_source": "AI estimate based on card identification", "value_confidence": "medium"}"""


CARD_CONDITION_ONLY = """You are an expert PSA card grader. Look at this photo and grade ONLY the physical condition of this card.

Rate each on PSA's 1-10 scale:
- centering: how well centered is the image? (10 = perfect 50/50 on all sides)
- corners: how sharp are the corners? (10 = razor sharp, no wear)
- edges: how clean are the edges? (10 = no chipping, no rough spots)
- surface: how clean is the surface? (10 = no scratches, stains, or print defects)
- overall_grade: your best PSA grade estimate combining all factors
- condition_notes: specific observations about flaws or quality

Tips for accurate grading:
- Look at ALL FOUR corners carefully
- Check for print lines, dots, or roller marks on the surface
- Note any wax stains, gum stains, or rubber band marks
- Check if there's any bowing, warping, or creasing
- Look for any writing, stamps, or marks

Return ONLY a JSON object:
{"centering": 8, "corners": 7, "edges": 8, "surface": 9, "overall_grade": 7, "condition_notes": "description of what you see"}"""


CARD_MULTI_ANGLE = """You are an expert PSA card grader examining multiple photos of the same card. The images show different angles/sides of the card.

For each angle you can see, assess:
- Front: centering, surface quality, print quality
- Back: centering, surface quality, any damage
- Corners (close-up): sharpness of each corner
- Edges: any chipping, whitening, or damage

Provide a comprehensive grade:
- centering_front: 1-10
- centering_back: 1-10
- corners: 1-10 (average of all 4 corners)
- corner_details: brief note on each corner if visible
- edges: 1-10
- surface_front: 1-10
- surface_back: 1-10
- overall_grade: estimated PSA grade 1-10
- condition_notes: detailed description of condition
- grade_confidence: high, medium, or low

Return ONLY a JSON object, no markdown."""
