from flask import Flask, render_template, request, jsonify
import re

app = Flask(__name__)

# ============================================================
# 1. DICTIONARIES  (The system's expanded knowledge base)
# ============================================================

VERBS = {
    "ACCEPT": ["accept", "accepts", "accepted", "accepting"], "ADD": ["add", "adds", "added", "adding"],
    "AGREE": ["agree", "agrees", "agreed", "agreeing"], "ALLOW": ["allow", "allows", "allowed", "allowing"],
    "ANSWER": ["answer", "answers", "answered", "answering"], "APPEAR": ["appear", "appears", "appeared", "appearing"],
    "ASK": ["ask", "asks", "asked", "asking"], "BAKE": ["bake", "bakes", "baked", "baking"],
    "BECOME": ["become", "becomes", "became", "becoming"], "BEGIN": ["begin", "begins", "began", "begun", "beginning"],
    "BELIEVE": ["believe", "believes", "believed", "believing"], "BRING": ["bring", "brings", "brought", "bringing"],
    "BUILD": ["build", "builds", "built", "building"], "BUY": ["buy", "buys", "bought", "buying"],
    "CALL": ["call", "calls", "called", "calling"], "CARRY": ["carry", "carries", "carried", "carrying"],
    "CATCH": ["catch", "catches", "caught", "catching"], "CHOOSE": ["choose", "chooses", "chose", "chosen", "choosing"],
    "CLEAN": ["clean", "cleans", "cleaned", "cleaning"], "CLOSE": ["close", "closes", "closed", "closing"],
    "COME": ["come", "comes", "came", "coming"], "COOK": ["cook", "cooks", "cooked", "cooking"],
    "COST": ["cost", "costs", "costing"], "CUT": ["cut", "cuts", "cutting"],
    "DANCE": ["dance", "dances", "danced", "dancing"], "DECIDE": ["decide", "decides", "decided", "deciding"],
    "DRAW": ["draw", "draws", "drew", "drawn", "drawing"], "DRINK": ["drink", "drinks", "drank", "drunk", "drinking"],
    "DRIVE": ["drive", "drives", "drove", "driven", "driving"], "EAT": ["eat", "eats", "ate", "eaten", "eating"],
    "ENJOY": ["enjoy", "enjoys", "enjoyed", "enjoying"], "EXPLAIN": ["explain", "explains", "explained", "explaining"],
    "FALL": ["fall", "falls", "fell", "fallen", "falling"], "FEEL": ["feel", "feels", "felt", "feeling"],
    "FIGHT": ["fight", "fights", "fought", "fighting"], "FIND": ["find", "finds", "found", "finding"],
    "FIX": ["fix", "fixes", "fixed", "fixing"], "FLY": ["fly", "flies", "flew", "flown", "flying"],
    "FORGET": ["forget", "forgets", "forgot", "forgotten"], "GET": ["get", "gets", "got", "gotten", "getting"],
    "GIVE": ["give", "gives", "gave", "given", "giving"], "GO": ["go", "goes", "went", "gone", "going"],
    "GROW": ["grow", "grows", "grew", "grown", "growing"], "HAPPEN": ["happen", "happens", "happened", "happening"],
    "HAVE": ["have", "has", "had", "having"], "HEAR": ["hear", "hears", "heard", "hearing"],
    "HELP": ["help", "helps", "helped", "helping"], "HIDE": ["hide", "hides", "hid", "hidden", "hiding"],
    "HIT": ["hit", "hits", "hitting"], "HOLD": ["hold", "holds", "held", "holding"],
    "HOPE": ["hope", "hopes", "hoped", "hoping"], "JUMP": ["jump", "jumps", "jumped", "jumping"],
    "KEEP": ["keep", "keeps", "kept", "keeping"], "KILL": ["kill", "kills", "killed", "killing"],
    "KNOW": ["know", "knows", "knew", "known", "knowing"], "LAUGH": ["laugh", "laughs", "laughed", "laughing"],
    "LEARN": ["learn", "learns", "learned", "learnt", "learning"], "LEAVE": ["leave", "leaves", "left", "leaving"],
    "LEND": ["lend", "lends", "lent", "lending"], "LISTEN": ["listen", "listens", "listened", "listening"],
    "LIVE": ["live", "lives", "lived", "living"], "LOOK": ["look", "looks", "looked", "looking"],
    "LOSE": ["lose", "loses", "lost", "losing"], "LOVE": ["love", "loves", "loved", "loving"],
    "MAKE": ["make", "makes", "made", "making"], "MEET": ["meet", "meets", "met", "meeting"],
    "MOVE": ["move", "moves", "moved", "moving"], "NEED": ["need", "needs", "needed", "needing"],
    "OPEN": ["open", "opens", "opened", "opening"], "PAINT": ["paint", "paints", "painted", "painting"],
    "PAY": ["pay", "pays", "paid", "paying"], "PLAY": ["play", "plays", "played", "playing"],
    "PULL": ["pull", "pulls", "pulled", "pulling"], "PUSH": ["push", "pushes", "pushed", "pushing"],
    "PUT": ["put", "puts", "putting"], "READ": ["read", "reads", "reading"],
    "REMEMBER": ["remember", "remembers", "remembered", "remembering"], "RIDE": ["ride", "rides", "rode", "ridden", "riding"],
    "RING": ["ring", "rings", "rang", "rung", "ringing"], "RUN": ["run", "runs", "ran", "running"],
    "SAY": ["say", "says", "said", "saying"], "SEE": ["see", "sees", "saw", "seen", "seeing"],
    "SELL": ["sell", "sells", "sold", "selling"], "SEND": ["send", "sends", "sent", "sending"],
    "SIGN": ["sign", "signs", "signed", "signing"], "SING": ["sing", "sings", "sang", "sung", "singing"],
    "SIT": ["sit", "sits", "sat", "sitting"], "SLEEP": ["sleep", "sleeps", "slept", "sleeping"],
    "SMILE": ["smile", "smiles", "smiled", "smiling"], "SPEAK": ["speak", "speaks", "spoke", "spoken", "speaking"],
    "SPEND": ["spend", "spends", "spent", "spending"], "STAND": ["stand", "stands", "stood", "standing"],
    "START": ["start", "starts", "started", "starting"], "STAY": ["stay", "stays", "stayed", "staying"],
    "STEAL": ["steal", "steals", "stole", "stolen", "stealing"], "STOP": ["stop", "stops", "stopped", "stopping"],
    "STUDY": ["study", "studies", "studied", "studying"], "SUBMIT": ["submit", "submits", "submitted", "submitting"],
    "SWIM": ["swim", "swims", "swam", "swum", "swimming"], "TAKE": ["take", "takes", "took", "taken", "taking"],
    "TALK": ["talk", "talks", "talked", "talking"], "TEACH": ["teach", "teaches", "taught", "teaching"],
    "TELL": ["tell", "tells", "told", "telling"], "THINK": ["think", "thinks", "thought", "thinking"],
    "THROW": ["throw", "throws", "threw", "thrown", "throwing"], "TOUCH": ["touch", "touches", "touched", "touching"],
    "TRY": ["try", "tries", "tried", "trying"], "UNDERSTAND": ["understand", "understands", "understood", "understanding"],
    "USE": ["use", "uses", "used", "using"], "WAIT": ["wait", "waits", "waited", "waiting"],
    "WAKE": ["wake", "wakes", "woke", "woken", "waking"], "WALK": ["walk", "walks", "walked", "walking"],
    "WANT": ["want", "wants", "wanted", "wanting"], "WASH": ["wash", "washes", "washed", "washing"],
    "WATCH": ["watch", "watches", "watched", "watching"], "WEAR": ["wear", "wears", "wore", "worn", "wearing"],
    "WIN": ["win", "wins", "won", "winning"], "WORK": ["work", "works", "worked", "working"],
    "WRITE": ["write", "writes", "wrote", "written", "writing"], "YELL": ["yell", "yells", "yelled", "yelling"],
}

VERB_LOOKUP = {form: norm for norm, forms in VERBS.items() for form in forms}

AUX_PASSIVE = {"was", "were", "is", "are", "been", "be", "being", "am", "has", "have", "had"}

TIME_WORDS = {
    "yesterday", "today", "tomorrow", "morning", "afternoon", "evening", "night", "midnight", "noon",
    "now", "later", "soon", "recently", "currently", "previously", "always", "never", "sometimes", "often",
    "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
    "january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december",
    "week", "month", "year", "decade", "century", "hour", "minute", "second", "time", "day"
}

PLACE_PREPS = {
    "in", "at", "on", "inside", "outside", "near", "under", "over", "beside", "above", "below", 
    "behind", "into", "onto", "through", "across", "along", "around", "between", 
    "among", "against", "towards", "toward", "upon", "within", "without", "beyond", "past"
}

PLACE_NOUNS = {
    "classroom", "office", "market", "park", "school", "library", "kitchen", "garden", "hospital", 
    "station", "shop", "store", "restaurant", "cafe", "hotel", "airport", "temple", "church", "mosque", 
    "museum", "theatre", "theater", "college", "university", "home", "house", "room", "hall", "ground", 
    "field", "stadium", "gym", "pool", "beach", "river", "lake", "ocean", "sea", "mountain", "hill", 
    "forest", "jungle", "desert", "city", "town", "village", "street", "road", "highway", "bridge", 
    "bank", "mall", "factory", "farm", "zoo", "prison", "court", "studio", "lab", "laboratory"
}

PRONOUNS = {
    "i", "me", "my", "mine", "myself", "you", "your", "yours", "yourself", "yourselves",
    "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself",
    "we", "us", "our", "ours", "ourselves", "they", "them", "their", "theirs", "themselves",
    "this", "that", "these", "those", "who", "whom", "whose", "which", "what", "someone",
    "somebody", "something", "anyone", "anybody", "anything", "everyone", "everybody", 
    "everything", "no one", "nobody", "nothing", "each", "either", "neither", "both", 
    "few", "many", "several", "all", "some", "none", "any"
}

ADJECTIVES = {
    "red", "blue", "green", "yellow", "orange", "purple", "pink", "brown", "black", "white", "gray", "grey",
    "big", "small", "large", "tiny", "huge", "gigantic", "massive", "little", "mini", "giant",
    "old", "new", "young", "ancient", "modern", "tall", "short", "long", "wide", "narrow", "thick", "thin",
    "happy", "sad", "angry", "mad", "excited", "bored", "tired", "sleepy", "hungry", "thirsty", "scared",
    "beautiful", "ugly", "pretty", "handsome", "cute", "smart", "stupid", "clever", "dumb", "wise",
    "fast", "slow", "quick", "rapid", "hot", "cold", "warm", "cool", "freezing", "boiling",
    "good", "bad", "great", "terrible", "nice", "mean", "kind", "cruel", "interesting", "boring",
    "easy", "hard", "difficult", "simple", "complex", "expensive", "cheap", "rich", "poor", "strong", "weak",
    "delicious", "tasty", "sweet", "sour", "bitter", "salty", "spicy", "famous", "popular", "successful",
    "healthy", "sick", "ill", "clean", "dirty", "noisy", "quiet", "loud", "soft", "hard", "bright", "dark"
}

ADVERBS = {
    "quickly", "slowly", "loudly", "quietly", "happily", "sadly", "angrily", "carefully",
    "carelessly", "easily", "hardly", "barely", "completely", "totally", "absolutely",
    "definitely", "probably", "possibly", "certainly", "surely", "really", "very", "quite",
    "too", "so", "well", "badly", "fast", "hard", "early", "late", "soon", "later", "now",
    "then", "always", "never", "sometimes", "often", "rarely", "usually", "normally"
}

STOPWORDS = {
    "the", "a", "an", "to", "of", "is", "was", "were", "and", "or", "but", "if", "then", "else",
    "with", "for", "from", "that", "this", "these", "those", "been", "being", "be", "have", "has", "had",
    "do", "does", "did", "will", "would", "shall", "should", "can", "could", "may", "might", "must",
    "am", "are", "as", "at", "by", "in", "into", "on", "onto", "over", "under", "up", "down", 
    "so", "than", "too", "just", "only", "also", "however", "therefore", "thus", "hence"
}


# ============================================================
# 2. TOKENIZATION & HELPERS
# ============================================================

def tokenize(sentence):
    clean = re.sub(r"[^\w\s]", "", sentence.lower())
    return clean.split()

def is_passive(tokens):
    return any(t in AUX_PASSIVE for t in tokens) and "by" in tokens

def _first_content_word(words):
    for w in words:
        if w not in STOPWORDS and w not in ADJECTIVES and w not in TIME_WORDS and w not in ADVERBS:
            return w.capitalize()
    return None

def _find_adjacent_adjective(words, target):
    try:
        idx = words.index(target)
        if idx > 0 and words[idx - 1] in ADJECTIVES:
            return words[idx - 1]
    except ValueError:
        pass
    return None


# ============================================================
# 3. CORE: SEMANTIC COMPONENT EXTRACTION
# ============================================================

def extract_components(tokens):
    subject = action = obj = time = place = None
    verb_index = -1

    for i, word in enumerate(tokens):
        if word in VERB_LOOKUP:
            action = VERB_LOOKUP[word]
            verb_index = i
            break

    if verb_index == -1:
        return {"subject": None, "action": None, "object": None, "time": None, "place": None, "predicate": None, "params": [], "passive": False}

    passive = is_passive(tokens)
    before = tokens[:verb_index]
    after = tokens[verb_index + 1:]

    if passive and "by" in after:
        by_index = after.index("by")
        patient_words = before
        agent_words = after[by_index + 1:]

        obj = _first_content_word(patient_words)
        for word in agent_words:
            if word not in STOPWORDS and word not in ADJECTIVES and word not in ADVERBS:
                subject = word.capitalize()
                break
        
        place_mode = False
        for word in agent_words:
            if word in TIME_WORDS: time = word.capitalize()
            elif word in PLACE_PREPS: place_mode = True
            elif place_mode and word not in STOPWORDS: place = word.capitalize(); place_mode = False
            elif word in PLACE_NOUNS: place = word.capitalize()

    elif passive:
        obj = _first_content_word(before)
        subject = None

    else:
        for word in reversed(before):
            if word in ADVERBS: continue 
            if word in PRONOUNS: subject = word.capitalize(); break
            if word in ADJECTIVES: continue
            if word not in STOPWORDS and word not in TIME_WORDS:
                adj = _find_adjacent_adjective(before, word)
                subject = (adj + " " + word).capitalize() if adj else word.capitalize()
                break

        place_mode = False
        for word in after:
            if word in ADVERBS: continue 
            if word in TIME_WORDS: time = word.capitalize()
            elif word in PLACE_PREPS: place_mode = True
            elif place_mode and word not in STOPWORDS:
                adj = _find_adjacent_adjective(after, word)
                place = (adj + " " + word).capitalize() if adj else word.capitalize()
                place_mode = False
            elif word in PLACE_NOUNS: place = word.capitalize()
            elif word == "by": continue
            elif obj is None and word not in STOPWORDS and word not in TIME_WORDS and word not in ADJECTIVES:
                adj = _find_adjacent_adjective(after, word)
                obj = (adj + " " + word).capitalize() if adj else word.capitalize()

    if passive:
        for word in before:
            if word in TIME_WORDS and time is None: time = word.capitalize()
        for word in after:
            if word in TIME_WORDS and time is None: time = word.capitalize()

    params = [p for p in [subject, obj, place, time] if p]
    return {"subject": subject, "action": action, "object": obj, "time": time, "place": place, "predicate": action, "params": params, "passive": passive}


# ============================================================
# 4. FLASK ROUTES
# ============================================================

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/interpret", methods=["POST"])
def interpret():
    data = request.get_json(silent=True) or {}
    sentence = (data.get("sentence") or "").strip()

    if not sentence:
        return jsonify({"error": "Empty sentence"}), 400

    tokens = tokenize(sentence)
    result = extract_components(tokens)
    result["tokens"] = tokens
    result["original"] = sentence
    
    # --- UPGRADED POS TAGGER ---
    tagged_tokens = []
    for word in tokens:
        if word in STOPWORDS: tag = "DET"
        elif word in ADVERBS: tag = "ADV"
        elif word in ADJECTIVES: tag = "ADJ"
        elif word in VERB_LOOKUP: tag = "VERB"
        elif word in TIME_WORDS: tag = "TIME"
        elif word in PLACE_PREPS or word == "by": tag = "PREP"
        elif word in PRONOUNS: tag = "PRON"
        elif word in PLACE_NOUNS: tag = "NOUN"
        else: tag = "NOUN"
        
        tagged_tokens.append({"word": word, "tag": tag})
        
    result["tagged_tokens"] = tagged_tokens
    return jsonify(result)

if __name__ == "__main__":
    app.run()