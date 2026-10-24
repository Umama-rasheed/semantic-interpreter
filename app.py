from flask import Flask, render_template, request, jsonify
import re

app = Flask(__name__)


# ============================================================
# 1. DICTIONARIES  (the system's "knowledge base")
# ============================================================

# Normalized action -> list of verb forms it recognizes
VERBS = {
    "OPEN":    ["open", "opens", "opened", "opening"],
    "CLOSE":   ["close", "closes", "closed", "closing"],
    "SUBMIT":  ["submit", "submits", "submitted", "submitting"],
    "EXPLAIN": ["explain", "explains", "explained", "explaining"],
    "WRITE":   ["write", "writes", "wrote", "written", "writing"],
    "READ":    ["read", "reads", "reading"],
    "BUY":     ["buy", "buys", "bought", "buying"],
    "SELL":    ["sell", "sells", "sold", "selling"],
    "CLEAN":   ["clean", "cleans", "cleaned", "cleaning"],
    "FIX":     ["fix", "fixes", "fixed", "fixing"],
    "WATCH":   ["watch", "watches", "watched", "watching"],
    "EAT":     ["eat", "eats", "ate", "eaten", "eating"],
    "DRINK":   ["drink", "drinks", "drank", "drunk", "drinking"],
    "PLAY":    ["play", "plays", "played", "playing"],
    "SEND":    ["send", "sends", "sent", "sending"],
    "BREAK":   ["break", "breaks", "broke", "broken", "breaking"],
    "BUILD":   ["build", "builds", "built", "building"],
    "CARRY":   ["carry", "carries", "carried", "carrying"],
    "CATCH":   ["catch", "catches", "caught", "catching"],
    "CUT":     ["cut", "cuts", "cutting"],
    "DRAW":    ["draw", "draws", "drew", "drawn", "drawing"],
    "DRIVE":   ["drive", "drives", "drove", "driven", "driving"],
    "FIND":    ["find", "finds", "found", "finding"],
    "FLY":     ["fly", "flies", "flew", "flown", "flying"],
    "FORGET":  ["forget", "forgets", "forgot", "forgotten"],
    "GIVE":    ["give", "gives", "gave", "given", "giving"],
    "GO":      ["go", "goes", "went", "gone", "going"],
    "HEAR":    ["hear", "hears", "heard", "hearing"],
    "HELP":    ["help", "helps", "helped", "helping"],
    "HIDE":    ["hide", "hides", "hid", "hidden", "hiding"],
    "HOLD":    ["hold", "holds", "held", "holding"],
    "KEEP":    ["keep", "keeps", "kept", "keeping"],
    "KNOW":    ["know", "knows", "knew", "known", "knowing"],
    "LEARN":   ["learn", "learns", "learned", "learnt", "learning"],
    "LEAVE":   ["leave", "leaves", "left", "leaving"],
    "LEND":    ["lend", "lends", "lent", "lending"],
    "LOSE":    ["lose", "loses", "lost", "losing"],
    "MAKE":    ["make", "makes", "made", "making"],
    "MEET":    ["meet", "meets", "met", "meeting"],
    "PAY":     ["pay", "pays", "paid", "paying"],
    "PUT":     ["put", "puts", "putting"],
    "RIDE":    ["ride", "rides", "rode", "ridden", "riding"],
    "RING":    ["ring", "rings", "rang", "rung", "ringing"],
    "RUN":     ["run", "runs", "ran", "running"],
    "SAY":     ["say", "says", "said", "saying"],
    "SEE":     ["see", "sees", "saw", "seen", "seeing"],
    "SIGN":    ["sign", "signs", "signed", "signing"],
    "SING":    ["sing", "sings", "sang", "sung", "singing"],
    "SIT":     ["sit", "sits", "sat", "sitting"],
    "SLEEP":   ["sleep", "sleeps", "slept", "sleeping"],
    "SPEAK":   ["speak", "speaks", "spoke", "spoken", "speaking"],
    "SPEND":   ["spend", "spends", "spent", "spending"],
    "STAND":   ["stand", "stands", "stood", "standing"],
    "STEAL":   ["steal", "steals", "stole", "stolen", "stealing"],
    "SWIM":    ["swim", "swims", "swam", "swum", "swimming"],
    "TAKE":    ["take", "takes", "took", "taken", "taking"],
    "TEACH":   ["teach", "teaches", "taught", "teaching"],
    "TELL":    ["tell", "tells", "told", "telling"],
    "THINK":   ["think", "thinks", "thought", "thinking"],
    "THROW":   ["throw", "throws", "threw", "thrown", "throwing"],
    "UNDERSTAND": ["understand", "understands", "understood", "understanding"],
    "WAKE":    ["wake", "wakes", "woke", "woken", "waking"],
    "WEAR":    ["wear", "wears", "wore", "worn", "wearing"],
    "WIN":     ["win", "wins", "won", "winning"],
}

# Reverse lookup: "opened" -> "OPEN"
VERB_LOOKUP = {form: norm for norm, forms in VERBS.items() for form in forms}

# Auxiliary verbs used to detect passive voice
AUX_PASSIVE = {"was", "were", "is", "are", "been", "be", "being"}

# Temporal words
TIME_WORDS = {
    "yesterday", "today", "tomorrow", "morning", "afternoon",
    "evening", "night", "now", "later", "soon", "recently",
    "monday", "tuesday", "wednesday", "thursday", "friday",
    "saturday", "sunday", "week", "month", "year",
    "always", "never", "sometimes", "often"
}

# Prepositions that introduce a place
PLACE_PREPS = {"in", "at", "on", "inside", "outside", "near", "under",
               "beside", "above", "below", "behind", "into", "onto"}

# Common place nouns — recognized even without a preposition
PLACE_NOUNS = {
    "classroom", "office", "market", "park", "school", "library",
    "kitchen", "garden", "hospital", "station", "shop", "store",
    "restaurant", "cafe", "hotel", "airport", "temple", "church",
    "museum", "theatre", "theater", "college", "university",
    "home", "house", "room", "hall", "ground", "field"
}

# Pronouns — valid subjects without needing a dictionary noun
PRONOUNS = {"i", "you", "he", "she", "it", "we", "they",
            "him", "her", "them", "us", "me"}

# Common adjectives — attached to the noun they modify
ADJECTIVES = {
    "red", "blue", "green", "yellow", "black", "white", "orange",
    "big", "small", "large", "tiny", "huge", "little",
    "old", "new", "young", "tall", "short", "long",
    "happy", "sad", "angry", "beautiful", "ugly", "smart",
    "fast", "slow", "hot", "cold", "warm", "cool",
    "good", "bad", "great", "nice", "interesting", "boring"
}

# Words to ignore when picking subject/object
STOPWORDS = {
    "the", "a", "an", "to", "of", "is", "was", "were", "and",
    "with", "by", "for", "from", "that", "this", "these", "those",
    "been", "being", "be"
}


# ============================================================
# 2. TOKENIZATION
# ============================================================

def tokenize(sentence):
    """
    Split sentence into lowercase words, stripping punctuation.
    Example: "Rahul opened the door." -> ["rahul", "opened", "the", "door"]
    """
    clean = re.sub(r"[^\w\s]", "", sentence.lower())
    return clean.split()


# ============================================================
# 3. PASSIVE DETECTION
# ============================================================

def is_passive(tokens):
    """
    Heuristic: passive if an auxiliary verb appears AND 'by' appears.
    Example: "The door was opened by Rahul" -> True
    """
    return any(t in AUX_PASSIVE for t in tokens) and "by" in tokens


# ============================================================
# 4. HELPERS
# ============================================================

def _first_content_word(words):
    """Return first non-stopword, non-adjective, non-time word."""
    for w in words:
        if w not in STOPWORDS and w not in ADJECTIVES and w not in TIME_WORDS:
            return w.capitalize()
    return None


def _find_adjacent_adjective(words, target):
    """If the word immediately before 'target' is an adjective, return it."""
    try:
        idx = words.index(target)
        if idx > 0 and words[idx - 1] in ADJECTIVES:
            return words[idx - 1]
    except ValueError:
        pass
    return None


# ============================================================
# 5. CORE: SEMANTIC COMPONENT EXTRACTION
# ============================================================

def extract_components(tokens):
    """
    Given a tokenized sentence, return a dict with:
      subject, action, object, time, place, predicate, params
    """
    subject = action = obj = time = place = None
    verb_index = -1

    # --- 1. Find the verb ---
    for i, word in enumerate(tokens):
        if word in VERB_LOOKUP:
            action = VERB_LOOKUP[word]   # normalized form, e.g. "OPEN"
            verb_index = i
            break

    if verb_index == -1:
        # No recognized verb -> cannot interpret
        return {
            "subject": None, "action": None, "object": None,
            "time": None, "place": None,
            "predicate": None, "params": [], "passive": False
        }

    # --- 2. Check for passive voice ---
    passive = is_passive(tokens)

    # --- 3. Split tokens around the verb ---
    before = tokens[:verb_index]
    after = tokens[verb_index + 1:]

    # --- 4. Handle PASSIVE case ---
    if passive and "by" in after:
        # "The window was broken by the boy in the room yesterday"
        by_index = after.index("by")
        patient_words = before
        agent_words = after[by_index + 1:]

        obj = _first_content_word(patient_words)
        
        # Grab the agent (the first word after "by")
        for word in agent_words:
            if word not in STOPWORDS and word not in ADJECTIVES:
                subject = word.capitalize()
                break
        
        # Now scan the REST of the sentence for Time and Place
        place_mode = False
        for word in agent_words:
            if word in TIME_WORDS:
                time = word.capitalize()
            elif word in PLACE_PREPS:
                place_mode = True
            elif place_mode and word not in STOPWORDS:
                place = word.capitalize()
                place_mode = False
            elif word in PLACE_NOUNS:
                place = word.capitalize()

    # --- 5. Handle PASSIVE with no agent ---
    elif passive:
        # "The window was broken yesterday"
        obj = _first_content_word(before)
        subject = None

    # --- 6. Handle ACTIVE case ---
    else:
        # Subject: last non-stopword, non-adjective word before verb
        for word in reversed(before):
            if word in PRONOUNS:
                subject = word.capitalize()
                break
            if word in ADJECTIVES:
                continue
            if word not in STOPWORDS and word not in TIME_WORDS:
                adj = _find_adjacent_adjective(before, word)
                subject = (adj + " " + word).capitalize() if adj else word.capitalize()
                break

        # Scan after verb for object / place / time
        place_mode = False
        for word in after:
            if word in TIME_WORDS:
                time = word.capitalize()
            elif word in PLACE_PREPS:
                place_mode = True
            elif place_mode and word not in STOPWORDS:
                adj = _find_adjacent_adjective(after, word)
                place = (adj + " " + word).capitalize() if adj else word.capitalize()
                place_mode = False
            elif word in PLACE_NOUNS:
                place = word.capitalize()
            elif word == "by":
                continue
            elif obj is None and word not in STOPWORDS and word not in TIME_WORDS \
                    and word not in ADJECTIVES:
                adj = _find_adjacent_adjective(after, word)
                obj = (adj + " " + word).capitalize() if adj else word.capitalize()

    # --- 7. Time and place can also appear before the verb in passive ---
    if passive:
        for word in before:
            if word in TIME_WORDS and time is None:
                time = word.capitalize()
        for word in after:
            if word in TIME_WORDS and time is None:
                time = word.capitalize()

    # --- 8. Build params for the predicate formula ---
    params = [p for p in [subject, obj, place, time] if p]

    return {
        "subject": subject,
        "action": action,
        "object": obj,
        "time": time,
        "place": place,
        "predicate": action,
        "params": params,
        "passive": passive
    }


# ============================================================
# 6. FLASK ROUTES
# ============================================================

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/interpret", methods=["POST"])
def interpret():
    """JSON API called by frontend via fetch()."""
    data = request.get_json(silent=True) or {}
    sentence = (data.get("sentence") or "").strip()

    if not sentence:
        return jsonify({"error": "Empty sentence"}), 400

    tokens = tokenize(sentence)
    result = extract_components(tokens)
    result["tokens"] = tokens
    result["original"] = sentence
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)