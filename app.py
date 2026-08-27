

import re
import json
import math
import string
import datetime
import collections
from flask import Flask, request, jsonify, send_from_directory


#  APP SETUP

app = Flask(__name__, static_folder='.')

SERVER_PORT      = 5000
MIN_TEXT_LENGTH  = 20
MAX_TEXT_LENGTH  = 10000


#  WORD LISTS  –  core of the detection engine


# Words that fake news uses to grab attention and create emotional reactions
SENSATIONALIST_WORDS = [
    "shocking", "bombshell", "explosive", "unbelievable", "incredible",
    "mind-blowing", "jaw-dropping", "stunning", "outrageous", "scandalous",
    "massive", "terrifying", "horrifying", "devastating", "catastrophic",
    "apocalyptic", "earth-shattering", "breaking", "urgent", "alert",
    "warning", "conspiracy", "coverup", "cover-up", "exposed", "revealed",
    "secret", "hidden", "banned", "suppressed", "censored", "leaked",
    "exclusive", "insider", "whistleblower", "miracle", "cure", "magic",
    "instant", "overnight", "guaranteed", "plandemic", "scamdemic",
    "hoax", "fake pandemic", "crisis actor", "deep state", "new world order",
    "wake up", "sheeple", "agenda", "propaganda", "brainwashed",
    "illuminati", "globalist", "microchip", "satanic", "cabal",
]

# Words designed to make readers feel fear, anger, or disgust
EMOTIONAL_TRIGGER_WORDS = [
    "disgusting", "revolting", "sickening", "appalling", "outraged",
    "furious", "enraged", "hateful", "vile", "evil", "wicked", "demonic",
    "corrupt", "criminal", "traitor", "treason", "betrayal", "shame",
    "shameful", "disgrace", "pathetic", "stupid", "idiot", "moron",
    "lunatic", "insane", "crazy", "delusional", "liar", "lies", "lying",
    "deceiving", "deceptive", "manipulative", "destroy", "obliterate",
    "annihilate", "slaughter", "massacre", "genocide", "eliminate",
    "they are lying", "do your research", "open your eyes", "wake up people",
    "snowflake", "libtard", "commie", "fascist", "puppet",
]

# Phrases that fake news uses instead of naming real sources
VAGUE_SOURCE_PHRASES = [
    "sources say", "sources claim", "insiders say", "insiders claim",
    "experts say", "experts believe", "experts warn", "doctors say",
    "scientists say", "researchers say", "studies show", "a study shows",
    "research shows", "according to sources", "many people say",
    "people are saying", "some say", "some believe", "it is believed",
    "it is said", "it is claimed", "it has been reported", "reports suggest",
    "anonymous sources", "unnamed officials", "high-level sources",
    "a government insider", "a reliable source", "we are told",
    "everyone knows", "obviously", "it is well known",
]

# Phrases found in properly sourced, credible news articles
CREDIBLE_SOURCE_INDICATORS = [
    "according to", "said in a statement", "told reporters", "confirmed by",
    "verified by", "published in", "released by", "announced", "stated",
    "declared", "reported by", "university", "institute", "department",
    "ministry", "government", "official", "spokesperson", "press release",
    "report", "study", "journal", "published", "peer-reviewed", "research",
    "professor", "doctor", "senator", "minister", "director", "secretary",
    "statistics", "data", "percent", "survey", "poll",
    "the report found", "the study found", "findings show",
    "in a statement to", "in an interview with", "speaking to",
    "told the press", "told journalists",
]

# Patterns that identify specific verifiable facts in the text
FACT_INDICATOR_PATTERNS = [
    r'\b\d{4}\b',                                         # Years: 2023
    r'\b\d+(\.\d+)?\s*%',                                 # Percentages: 45%
    r'\b\d+\s*(million|billion|thousand|hundred)\b',      # Large numbers
    r'\$\s*\d+',                                          # Dollar amounts
    r'\b(january|february|march|april|may|june|july|'
    r'august|september|october|november|december)\s+\d+', # Specific dates
    r'\b\d{1,2}:\d{2}\s*(am|pm)\b',                      # Times: 3:45 pm
]

# Patterns used in clickbait headlines and fake news articles
CLICKBAIT_PATTERNS = [
    r"you won'?t believe",
    r"what happened next",
    r"this will shock you",
    r"they don'?t want you to know",
    r"the truth about",
    r"exposed[:\!]",
    r"warning[:\!]",
    r"must (read|see|watch)",
    r"share before (it'?s|this is) deleted",
    r"going viral",
    r"breaking[:\!]",
    r"(secret|hidden|suppressed) (truth|cure|method)",
    r"mainstream media (won'?t|doesn'?t|refuses to)",
    r"they are (hiding|lying|covering up)",
    r"do your (own )?research",
    r"wake up (people|america|sheeple)",
    r"[\!\?]{2,}",      # !! or ??? etc.
    r"[A-Z]{5,}",       # WORDS IN ALL CAPS
]

# Words that show strong political bias in writing
BIASED_LANGUAGE_LEFT = [
    "capitalist pig", "fascist agenda", "white supremacist", "racist bigot",
    "corporate shill", "wall street greed", "billionaire elite",
]

BIASED_LANGUAGE_RIGHT = [
    "fake news media", "mainstream media lies", "deep state", "globalist agenda",
    "socialist agenda", "radical left", "open borders invasion",
    "libtard", "snowflake triggered", "cancel culture", "woke agenda",
]

# Words that indicate professional, formal journalism
FORMAL_LANGUAGE_WORDS = [
    "furthermore", "moreover", "additionally", "consequently", "subsequently",
    "nevertheless", "nonetheless", "however", "therefore", "thus", "hence",
    "accordingly", "meanwhile", "previously", "recently", "currently",
    "approximately", "estimated", "projected", "attributed", "designated",
    "established", "implemented", "legislation", "regulation", "administration",
    "committee", "investigation", "prosecution", "testimony", "evidence",
    "spokesperson", "representative", "official", "authority", "jurisdiction",
    "constitutional", "parliamentary", "judicial",
]

# Well-known credible news organisations
CREDIBLE_NEWS_SOURCES = [
    "reuters", "associated press", "ap news", "bbc", "the guardian",
    "new york times", "washington post", "the economist", "financial times",
    "npr", "pbs", "abc news", "cbs news", "nbc news", "the atlantic",
    "time magazine", "forbes", "bloomberg", "cnbc", "al jazeera",
    "france 24", "dw news", "deutsche welle", "the independent",
    "nature", "science magazine", "the lancet", "new england journal",
    "world health organization", "who", "united nations", "world bank",
    "imf", "cdc", "centers for disease control", "fda",
]

# Known unreliable or conspiracy-spreading websites
UNRELIABLE_SOURCE_NAMES = [
    "infowars", "natural news", "gateway pundit", "beforeitsnews",
    "yournewswire", "collective evolution", "activistpost",
    "globalresearch", "veteranstoday", "whatreallyhappened",
]

# ---------------------------------------------------------------------------
#  TEXT PREPROCESSING
# ---------------------------------------------------------------------------

def clean_text(raw):
    """Remove extra whitespace and non-printable characters."""
    text = raw.strip()
    text = re.sub(r'  +', ' ', text)
    text = re.sub(r'\n\n+', '\n', text)
    text = text.replace('\t', ' ')
    text = ''.join(ch for ch in text if ch.isprintable())
    return text

def to_lower(text):
    """Convert text to all lowercase."""
    return text.lower()

def get_words(text):
    """Split text into a list of lowercase words without punctuation."""
    return re.findall(r'\b[a-zA-Z]{2,}\b', text.lower())

def get_sentences(text):
    """Split text into sentences."""
    parts = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
    return [s.strip() for s in parts if s.strip()] or [text]

def word_count(text):
    return len(get_words(text))

def sentence_count(text):
    return max(len(get_sentences(text)), 1)

def count_uppercase_words(text):
    """Count words written in ALL CAPS (3+ letters)."""
    return len(re.findall(r'\b[A-Z]{3,}\b', text))

def count_exclamations(text):
    return text.count('!')

def count_questions(text):
    return text.count('?')

def avg_sentence_length(text):
    return word_count(text) / sentence_count(text)

def unique_word_ratio(text):
    words = get_words(text)
    if not words:
        return 0.0
    return len(set(words)) / len(words)

# ---------------------------------------------------------------------------
#  SCORING FUNCTIONS  –  each returns a 0-100 score
# ---------------------------------------------------------------------------

def score_sensationalism(lower):
    """
    Count sensationalist and emotional trigger words.
    More of these words = higher fake probability.
    """
    found = []
    for w in SENSATIONALIST_WORDS:
        if w in lower:
            found.append(w)
    for w in EMOTIONAL_TRIGGER_WORDS:
        if w in lower and w not in found:
            found.append(w)

    total = max(word_count(lower), 1)
    density = (len(found) / total) * 100
    score   = min(density * 20, 100)

    # ALL CAPS and exclamation marks also raise this score
    score += count_uppercase_words(lower.upper()) * 3
    score += count_exclamations(lower) * 5
    score  = min(score, 100)

    return round(score, 1), found


def score_source_credibility(lower):
    """
    Check for credible vs vague source attribution.
    High credibility score = less likely to be fake.
    """
    pts  = 0
    good = []
    bad  = []

    for phrase in CREDIBLE_SOURCE_INDICATORS:
        if phrase in lower:
            pts += 5
            good.append(phrase)

    for src in CREDIBLE_NEWS_SOURCES:
        if src in lower:
            pts += 10
            good.append(src)

    for phrase in VAGUE_SOURCE_PHRASES:
        if phrase in lower:
            pts -= 8
            bad.append(phrase)

    for src in UNRELIABLE_SOURCE_NAMES:
        if src in lower:
            pts -= 15
            bad.append(src)

    # Named person patterns like "Dr. Smith said" or "Minister John stated"
    named_persons = re.findall(
        r'\b(dr|mr|mrs|ms|prof|senator|minister|director|general)\b\s+[a-z]+',
        lower
    )
    pts += len(named_persons) * 6

    score = max(0, min(pts, 100))

    if score >= 70:
        desc = "Good — named and verifiable sources cited"
    elif score >= 40:
        desc = "Moderate — some sources mentioned, not all specific"
    elif score >= 20:
        desc = "Low — mostly vague, unattributed sources"
    else:
        desc = "Very Low — no credible sources found"

    return score, desc, good, bad


def score_bias(lower):
    """
    Detect strong political or ideological bias in the writing.
    High bias score = more one-sided = more likely fake.
    """
    left_count  = 0
    right_count = 0
    found       = []

    for w in BIASED_LANGUAGE_LEFT:
        if w in lower:
            left_count += 1
            found.append(w)

    for w in BIASED_LANGUAGE_RIGHT:
        if w in lower:
            right_count += 1
            found.append(w)

    total_bias  = left_count + right_count
    total_words = max(word_count(lower), 1)
    density     = (total_bias / total_words) * 100
    raw_score   = min(density * 25, 100)

    # Formal language reduces bias score
    formal_count = sum(1 for w in FORMAL_LANGUAGE_WORDS if w in lower)
    score        = max(0, raw_score - formal_count * 3)

    if left_count > right_count and total_bias > 0:
        direction = "Left-leaning political bias detected"
    elif right_count > left_count and total_bias > 0:
        direction = "Right-leaning political bias detected"
    elif total_bias > 0:
        direction = "Mixed political bias detected"
    else:
        direction = "No strong political bias detected"

    return round(score, 1), direction, found


def score_fact_density(lower, original):
    """
    Count specific verifiable facts (dates, numbers, names, quotes).
    High fact density = more like real journalism.
    """
    count = 0

    for pattern in FACT_INDICATOR_PATTERNS:
        count += len(re.findall(pattern, lower, re.IGNORECASE))

    # Proper nouns (capitalised words) from the original text
    proper_nouns = re.findall(r'\b[A-Z][a-z]{2,}\b', original)
    noun_freq    = collections.Counter(proper_nouns)
    meaningful   = [w for w, c in noun_freq.items() if len(w) > 3]
    count       += len(meaningful)

    # Direct quotes are strong fact indicators
    direct_quotes = re.findall(r'"[^"]{10,}"', original)
    count        += len(direct_quotes) * 3

    # Standalone numbers
    count += len(re.findall(r'\b\d{2,}\b', original))

    total   = max(word_count(lower), 1)
    density = (count / total) * 100
    score   = min(density * 5, 100)

    if score >= 70:
        desc = "High — many specific facts, numbers and names found"
    elif score >= 45:
        desc = "Moderate — some specific facts present"
    elif score >= 20:
        desc = "Low — few specific or verifiable facts"
    else:
        desc = "Very Low — almost no verifiable facts"

    return round(score, 1), desc, count


def score_clickbait(lower):
    """
    Count clickbait patterns in the text.
    High clickbait score = more likely fake or misleading.
    """
    found   = []
    total   = 0
    for pattern in CLICKBAIT_PATTERNS:
        matches = re.findall(pattern, lower, re.IGNORECASE)
        if matches:
            total += len(matches)
            found.append(pattern)
    score = min(total * 20, 100)
    return round(score, 1), found


def score_language_tone(lower):
    """
    Measure how emotional vs formal the writing style is.
    High tone score = more emotional = more likely fake.
    """
    score = 50

    formal_count     = sum(1 for w in FORMAL_LANGUAGE_WORDS if w in lower)
    exclaim_count    = count_exclamations(lower)
    question_count   = count_questions(lower)
    uppercase_count  = count_uppercase_words(lower.upper())
    avg_sent_len     = avg_sentence_length(lower)

    if avg_sent_len < 10:
        score += 15
    elif avg_sent_len > 20:
        score -= 10

    score -= formal_count    * 2
    score += exclaim_count   * 8
    score += question_count  * 3
    score += uppercase_count * 4

    first_person = len(re.findall(
        r'\b(i|me|my|we|us|our)\b', lower
    ))
    score += first_person * 2

    score = max(0, min(score, 100))

    if score >= 75:
        label = "Highly sensationalist and emotional"
    elif score >= 55:
        label = "Somewhat emotional and informal"
    elif score >= 35:
        label = "Mostly neutral with minor informal elements"
    else:
        label = "Formal and neutral — journalistic style"

    return round(score, 1), label

# ---------------------------------------------------------------------------
#  COMBINE SCORES → FINAL FAKE PROBABILITY
# ---------------------------------------------------------------------------

def combined_fake_score(sens, cred, bias, fact, click, tone):
    """
    Combine six individual scores into one fake-probability score 0-100.
    Weights are based on how strongly each factor predicts fake news.

    Factors that push score UP   (= more fake):  sens, bias, click, tone
    Factors that push score DOWN (= more real):  cred, fact
    """
    WEIGHT_SENS  = 0.25
    WEIGHT_CRED  = 0.25   # inverted: high cred = less fake
    WEIGHT_BIAS  = 0.15
    WEIGHT_FACT  = 0.20   # inverted: high facts = less fake
    WEIGHT_CLICK = 0.10
    WEIGHT_TONE  = 0.05

    fake_part = (
        sens  * WEIGHT_SENS  +
        bias  * WEIGHT_BIAS  +
        click * WEIGHT_CLICK +
        tone  * WEIGHT_TONE
    )
    real_part = (
        (100 - cred) * WEIGHT_CRED +
        (100 - fact) * WEIGHT_FACT
    )

    total = fake_part + real_part
    return round(max(0, min(total, 100)), 1)


def make_verdict(fake_score):
    """Convert fake score to FAKE / REAL / UNCERTAIN + confidence."""
    if fake_score >= 60:
        verdict    = "FAKE"
        confidence = int(fake_score)
        if fake_score >= 85:
            prefix = (
                "This text shows very strong signs of fake news. Multiple "
                "serious red flags were detected including highly "
                "sensationalist language, emotional manipulation, and a "
                "lack of credible named sources. "
            )
        elif fake_score >= 72:
            prefix = (
                "This text shows several significant indicators commonly "
                "found in fake news articles. The writing is emotional "
                "and exaggerated, and sources are vague or missing. "
            )
        else:
            prefix = (
                "This text shows notable characteristics of fake news. "
                "The combination of language patterns, missing sources, "
                "and low fact density suggests the content may not be "
                "reliable. "
            )
    elif fake_score >= 40:
        verdict    = "UNCERTAIN"
        confidence = int(abs(50 - fake_score) + 50)
        if fake_score >= 52:
            prefix = (
                "This text has a mixed credibility profile. It shows some "
                "concerning language patterns and lacks strong source "
                "attribution, but cannot be conclusively labelled fake. "
            )
        else:
            prefix = (
                "This text could not be confidently classified as real or "
                "fake from language analysis alone. Some positive and some "
                "negative credibility signals were found. "
            )
    else:
        verdict    = "REAL"
        confidence = int(100 - fake_score)
        if fake_score <= 15:
            prefix = (
                "This text shows strong indicators of credible professional "
                "journalism. The language is formal and neutral, specific "
                "named sources are cited, and verifiable facts are present. "
            )
        elif fake_score <= 25:
            prefix = (
                "This text shows mostly positive credibility signals. "
                "The writing is largely professional and factual with "
                "reasonable source attribution. "
            )
        else:
            prefix = (
                "This text shows more credibility signals than red flags, "
                "suggesting it is probably reliable. Some minor concerns "
                "were noted but do not outweigh the positive signals. "
            )

    return verdict, confidence, prefix


# ---------------------------------------------------------------------------
#  BUILD EXPLANATION PARAGRAPH
# ---------------------------------------------------------------------------

def build_explanation(verdict, prefix, sens, cred, fact, bias, wc):
    """Build the plain-English explanation shown in the result panel."""
    text = prefix

    if sens >= 60 and verdict in ("FAKE", "UNCERTAIN"):
        text += (
            "The most notable red flag is the highly sensationalist and "
            "emotional language used throughout, which is a well-documented "
            "feature of misleading content. "
        )
    elif cred >= 60 and verdict == "REAL":
        text += (
            "The strongest positive signal is the presence of specific, "
            "named, and verifiable sources, indicating proper journalistic "
            "practice. "
        )
    elif fact <= 20 and verdict in ("FAKE", "UNCERTAIN"):
        text += (
            "The text contains very few specific facts, numbers, or named "
            "sources that could be independently verified — a common feature "
            "of fabricated or misleading articles. "
        )
    elif fact >= 60 and verdict == "REAL":
        text += (
            "The article contains a high density of specific facts including "
            "dates, statistics, proper names, and direct quotes — all "
            "characteristics of credible reporting. "
        )

    if verdict == "FAKE":
        text += (
            "We recommend not sharing this content without first verifying "
            "it through a credible news source or fact-checking site such "
            "as Reuters, BBC, or FactCheck.org."
        )
    elif verdict == "UNCERTAIN":
        text += (
            "Please cross-reference this content with multiple credible news "
            "sources before forming an opinion or sharing it."
        )
    else:
        text += (
            "As always, it is good practice to check important news with "
            "at least two or three independent sources."
        )

    return text


# ---------------------------------------------------------------------------
#  BUILD INDICATOR LIST
# ---------------------------------------------------------------------------

def build_indicators(
    verdict, cls,
    sens, sens_found,
    cred, good_src, bad_src,
    fact, fact_count,
    bias, bias_dir, bias_words,
    tone, tone_label,
    wc, sc, avg_sl,
    caps, excl
):
    """Build 4-6 human-readable signal strings shown under the verdict."""
    items = []

    # Sensationalism
    if sens >= 50:
        sample = ', '.join(sens_found[:3]) if sens_found else 'multiple dramatic phrases'
        items.append(
            f"High sensationalism — emotional or exaggerated words found: {sample}"
        )
    elif sens >= 20:
        items.append("Moderate sensationalism — some dramatic words used but not excessive")
    else:
        items.append("Low sensationalism — writing style is calm and measured")

    # Source credibility
    if cred >= 60:
        sample = good_src[0] if good_src else "named sources"
        items.append(f"Good source credibility — verifiable sources cited including: {sample}")
    elif cred >= 30:
        items.append("Moderate source credibility — some sources mentioned but not all specific")
    else:
        sample = bad_src[0] if bad_src else "no named sources"
        items.append(f"Poor source credibility — vague phrases used such as: '{sample}'")

    # Fact density
    if fact >= 60:
        items.append(
            f"High fact density — {fact_count} specific facts, numbers, "
            f"dates and names found in {wc} words"
        )
    elif fact >= 30:
        items.append(
            f"Moderate fact density — {fact_count} factual elements found; "
            "more would improve credibility"
        )
    else:
        items.append(
            f"Low fact density — only {fact_count} specific facts in {wc} words; "
            "mostly vague, unverifiable claims"
        )

    # Bias
    if bias >= 50:
        sample = bias_words[0] if bias_words else "biased phrasing"
        items.append(f"Strong bias — {bias_dir}; example: '{sample}'")
    elif bias >= 20:
        items.append(f"Mild bias — {bias_dir}")
    else:
        items.append("Minimal bias — writing is largely balanced and neutral")

    # Tone / formatting
    if caps >= 3 or excl >= 3:
        items.append(
            f"Unprofessional formatting — {caps} ALL-CAPS words and "
            f"{excl} exclamation marks; professional journalism avoids these"
        )
    elif tone >= 60:
        items.append(
            f"Emotional writing tone — {tone_label.lower()}; "
            "real journalism aims for neutral factual language"
        )
    else:
        items.append(
            f"Professional tone — {tone_label.lower()}; "
            f"average sentence length is {avg_sl:.0f} words"
        )

    return items[:6]


# ---------------------------------------------------------------------------
#  MAIN ANALYSIS ORCHESTRATOR
# ---------------------------------------------------------------------------

def analyse(raw_text):
    """
    Run the full fake news analysis on the submitted text.
    Returns a dictionary ready to be sent as JSON to the browser.
    """
    # 1. Preprocess
    clean   = clean_text(raw_text)
    if len(clean) > MAX_TEXT_LENGTH:
        clean = clean[:MAX_TEXT_LENGTH]
    lower   = to_lower(clean)

    # 2. Basic statistics
    wc      = word_count(clean)
    sc      = sentence_count(clean)
    avg_sl  = avg_sentence_length(clean)
    caps    = count_uppercase_words(clean)
    excl    = count_exclamations(clean)

    # 3. Individual scores
    sens,  sens_found                    = score_sensationalism(lower)
    cred,  cred_desc, good_src, bad_src  = score_source_credibility(lower)
    bias,  bias_dir, bias_words          = score_bias(lower)
    fact,  fact_desc, fact_count         = score_fact_density(lower, clean)
    click, click_found                   = score_clickbait(lower)
    tone,  tone_label                    = score_language_tone(lower)

    # 4. Combined fake score and verdict
    fake_s              = combined_fake_score(sens, cred, bias, fact, click, tone)
    verdict, conf, pfx  = make_verdict(fake_s)
    cls                 = verdict.lower() if verdict != "UNCERTAIN" else "uncertain"

    # 5. Build human-readable outputs
    explanation = build_explanation(verdict, pfx, sens, cred, fact, bias, wc)
    indicators  = build_indicators(
        verdict, cls,
        sens, sens_found,
        cred, good_src, bad_src,
        fact, fact_count,
        bias, bias_dir, bias_words,
        tone, tone_label,
        wc, sc, avg_sl,
        caps, excl
    )

    # 6. Bias level description
    if bias >= 60:
        bias_label = f"High — {bias_dir}"
    elif bias >= 30:
        bias_label = f"Moderate — {bias_dir}"
    else:
        bias_label = "Low — writing appears balanced"

    return {
        "verdict"           : verdict,
        "confidence"        : conf,
        "languageTone"      : tone_label,
        "sourceCredibility" : cred_desc,
        "biasLevel"         : bias_label,
        "factDensity"       : fact_desc,
        "explanation"       : explanation,
        "indicators"        : indicators,
    }


# ---------------------------------------------------------------------------
#  INPUT VALIDATION
# ---------------------------------------------------------------------------

def validate(text):
    """Return (ok, error_string). ok=True means text is ready to analyse."""
    if not text or not text.strip():
        return False, "No text was submitted. Please paste a news article."
    stripped = text.strip()
    if len(stripped) < MIN_TEXT_LENGTH:
        return False, (
            f"Text is too short. Please provide at least "
            f"{MIN_TEXT_LENGTH} characters (you gave {len(stripped)})."
        )
    letter_count = sum(1 for ch in stripped if ch.isalpha())
    if letter_count < 10:
        return False, "Please paste an actual news article — not just numbers or symbols."
    return True, None


# ---------------------------------------------------------------------------
#  SIMPLE LOGGER
# ---------------------------------------------------------------------------

def log(level, msg):
    ts = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {level}: {msg}")


# ---------------------------------------------------------------------------
#  FLASK ROUTES
# ---------------------------------------------------------------------------

@app.route('/', methods=['GET'])
def homepage():
    """Serve the main HTML page."""
    log("INFO", "Serving homepage")
    return send_from_directory('.', 'index.html')


@app.route('/analyse', methods=['POST'])
def analyse_route():
    """
    POST /analyse
    Expects JSON body: { "text": "..." }
    Returns JSON with verdict, confidence, metrics, explanation, indicators.
    """
    # Parse JSON body
    body = request.get_json(silent=True)
    if body is None or 'text' not in body:
        log("WARN", "Bad request — missing JSON body or 'text' field")
        return jsonify({'error': "Please send JSON with a 'text' field."}), 400

    text = body.get('text', '')

    # Validate input
    ok, err = validate(text)
    if not ok:
        log("WARN", f"Validation failed: {err}")
        return jsonify({'error': err}), 400

    # Run analysis
    log("INFO", f"Analysing text ({len(text)} chars)...")
    try:
        result = analyse(text.strip())
    except Exception as e:
        log("ERROR", f"Analysis error: {str(e)}")
        return jsonify({'error': 'Analysis failed. Please try again.'}), 500

    log("INFO", f"Done — verdict={result['verdict']} confidence={result['confidence']}%")
    return jsonify(result), 200


@app.route('/health', methods=['GET'])
def health():
    """Simple health check so you can confirm the server is running."""
    return jsonify({
        'status'   : 'ok',
        'server'   : 'FakeShield',
        'time'     : datetime.datetime.now().isoformat()
    }), 200


# ---------------------------------------------------------------------------
#  ERROR HANDLERS
# ---------------------------------------------------------------------------

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': f"Page '{request.path}' not found."}), 404

@app.errorhandler(405)
def not_allowed(e):
    return jsonify({'error': f"Method '{request.method}' not allowed here."}), 405

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error. Please try again.'}), 500


# ---------------------------------------------------------------------------
#  STARTUP
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    print("")
    print("=" * 58)
    print("   🛡️   F A K E S H I E L D   🛡️")
    print("   Fake News Detector — Python + Flask")
    print("   Author : Sudin  |  BIT 4th Semester")
    print("=" * 58)
    print(f"   Server starting on http://localhost:{SERVER_PORT}")
    print(f"   Open that link in your browser to use the app.")
    print("   Press CTRL+C to stop the server.")
    print("=" * 58)
    print(f"   Word lists loaded:")
    print(f"     Sensationalist words   : {len(SENSATIONALIST_WORDS)}")
    print(f"     Emotional trigger words: {len(EMOTIONAL_TRIGGER_WORDS)}")
    print(f"     Credible source phrases: {len(CREDIBLE_SOURCE_INDICATORS)}")
    print(f"     Vague source phrases   : {len(VAGUE_SOURCE_PHRASES)}")
    print(f"     Fact indicator patterns: {len(FACT_INDICATOR_PATTERNS)}")
    print(f"     Clickbait patterns     : {len(CLICKBAIT_PATTERNS)}")
    print(f"     Known credible sources : {len(CREDIBLE_NEWS_SOURCES)}")
    print(f"     Known bad sources      : {len(UNRELIABLE_SOURCE_NAMES)}")
    print("=" * 58)
    print("   No AI API needed. 100% pure Python NLP.")
    print("=" * 58)
    print("")

    app.run(debug=True, port=SERVER_PORT, host='0.0.0.0')

# =============================================================================
#  END OF FILE  –  FakeShield app.py
#  Pure Python rule-based NLP fake news detector.
#  No machine learning, no AI API, no external NLP library.
#  Only uses: flask, re, json, math, datetime, collections  (all built-in)
# =============================================================================
