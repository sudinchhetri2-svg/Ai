# 🛡️ FakeShield

### Fake News Detection System using Python + Flask

FakeShield is a **rule-based fake news detection web application** developed using **Python and Flask**. It analyzes the language and structure of a news article and estimates whether the content is **REAL, FAKE, or UNCERTAIN**.

The system does not use machine learning or external AI APIs. Instead, it uses a collection of linguistic rules, keyword lists, regular expressions, source indicators, and weighted scoring techniques to analyze submitted text.

> **Author:** Sudin
> **Program:** BIT — 4th Semester
> **Technology:** Python + Flask
> **Detection Method:** Rule-based NLP

---

## ✨ Features

* 📰 Fake news analysis from article text
* 🛡️ REAL / FAKE / UNCERTAIN classification
* 📊 Confidence score
* 🎭 Sensationalism detection
* 😡 Emotional language detection
* 📰 Source credibility analysis
* ⚖️ Political bias detection
* 📚 Fact-density analysis
* 🚨 Clickbait pattern detection
* ✍️ Language tone analysis
* 🔠 ALL-CAPS and excessive punctuation detection
* 💡 Human-readable explanation of the result
* 📋 List of detected credibility indicators
* ❤️ Health-check API endpoint
* 🌐 Flask web interface
* 📡 JSON API for frontend integration
* 🚫 No external AI API required

---

## 🧠 How FakeShield Works

FakeShield analyzes submitted text using six major scoring categories:

### 1. Sensationalism

The system searches for words and phrases commonly associated with sensationalist or exaggerated content.

Examples include:

* `shocking`
* `bombshell`
* `explosive`
* `breaking`
* `urgent`
* `secret`
* `exposed`
* `miracle`
* `conspiracy`

A high concentration of these words increases the fake-news score.

---

### 2. Source Credibility

FakeShield looks for evidence that an article provides identifiable and credible sources.

Examples of positive indicators:

* according to
* verified by
* published in
* official
* government
* university
* research
* study
* statistics
* Reuters
* BBC
* Associated Press

It also detects vague source descriptions such as:

* `sources say`
* `insiders claim`
* `experts say`
* `anonymous sources`
* `everyone knows`

Credible sources decrease the fake-news score, while vague or unreliable sources increase it.

---

### 3. Political Bias

The system checks for strongly ideological or politically biased phrases.

It maintains separate lists for left-leaning and right-leaning expressions.

For example:

```text
"fascist agenda"
"capitalist pig"
"radical left"
"deep state"
"fake news media"
"woke agenda"
```

The system reports whether strong political bias is detected.

---

### 4. Fact Density

FakeShield looks for specific information that can potentially be verified, including:

* Years
* Dates
* Percentages
* Numbers
* Monetary values
* Names
* Direct quotations
* Specific factual statements

For example:

```text
In 2025, the unemployment rate decreased by 4.2%.
```

contains several identifiable factual elements.

Higher fact density generally produces a more credible result.

---

### 5. Clickbait Detection

The system detects common clickbait patterns such as:

```text
You won't believe what happened!
What happened next...
They don't want you to know
This will shock you
Share before it's deleted
Going viral
The truth about...
```

Excessive punctuation and ALL-CAPS words are also considered potential warning signs.

---

### 6. Language Tone

The system analyzes whether the article uses:

* Formal language
* Neutral language
* Emotional language
* Excessive exclamation marks
* Excessive question marks
* ALL-CAPS words
* First-person language
* Short or unusually structured sentences

Professional journalism generally uses a more neutral and formal tone.

---

# 📊 Scoring System

FakeShield combines six individual scores into one overall fake-news probability.

| Factor             | Weight | Effect                                 |
| ------------------ | -----: | -------------------------------------- |
| Sensationalism     |    25% | Increases fake score                   |
| Source credibility |    25% | High credibility decreases fake score  |
| Political bias     |    15% | Increases fake score                   |
| Fact density       |    20% | High fact density decreases fake score |
| Clickbait          |    10% | Increases fake score                   |
| Language tone      |     5% | Emotional tone increases fake score    |

The final score ranges from:

```text
0 - 100
```

### Verdict thresholds

|  Score | Verdict      |
| -----: | ------------ |
|   0–39 | 🟢 REAL      |
|  40–59 | 🟡 UNCERTAIN |
| 60–100 | 🔴 FAKE      |

The result also includes a confidence percentage and an explanation describing the detected signals.

---

# 🛠️ Technologies Used

### Backend

* Python
* Flask

### Python Libraries

FakeShield primarily uses Python's standard libraries:

* `re`
* `json`
* `math`
* `string`
* `datetime`
* `collections`

The Flask framework is used to create the web server and API.

### NLP Approach

The project uses:

> **Rule-Based Natural Language Processing (NLP)**

It does not require:

* Machine learning models
* TensorFlow
* PyTorch
* OpenAI API
* External NLP models
* Database systems

---

# 📁 Project Structure

A basic project structure is:

```text
project/
│
├── app.py
├── index.html
├── .gitignore
└── README.md
```

### `app.py`

Contains the Flask backend and the complete FakeShield detection engine.

### `index.html`

Provides the frontend interface where users can enter news articles and view the analysis.

### `.gitignore`

Prevents unnecessary files such as macOS `.DS_Store` files from being committed to Git.

### `README.md`

Project documentation.

---

# 🚀 Installation

## 1. Clone the repository

```bash
git clone https://github.com/sudinchhetri2-svg/Ai.git
```

Then enter the project directory:

```bash
cd Ai
```

---

## 2. Create a virtual environment

Recommended:

```bash
python3 -m venv venv
```

Activate it on macOS/Linux:

```bash
source venv/bin/activate
```

On Windows:

```bash
venv\Scripts\activate
```

---

## 3. Install Flask

```bash
pip install flask
```

---

# ▶️ Running the Application

Start the Flask server:

```bash
python3 app.py
```

You should see:

```text
==========================================================
   🛡️   F A K E S H I E L D   🛡️
   Fake News Detector — Python + Flask
   Author : Sudin  |  BIT 4th Semester
==========================================================
   Server starting on http://localhost:5000
==========================================================
```

Open your browser and visit:

```text
http://localhost:5000
```

---

# 🔌 API Documentation

FakeShield provides a REST API endpoint for analyzing text.

## POST `/analyse`

Send a JSON request containing the article text.

### Request

```json
{
  "text": "Your news article goes here..."
}
```

### Example using cURL

```bash
curl -X POST http://localhost:5000/analyse \
-H "Content-Type: application/json" \
-d '{"text":"Your news article goes here with enough content to analyze."}'
```

### Response

A successful request returns JSON containing information such as:

```json
{
  "verdict": "UNCERTAIN",
  "confidence": 55,
  "languageTone": "Somewhat emotional and informal",
  "sourceCredibility": "Moderate — some sources mentioned, not all specific",
  "biasLevel": "Low — writing appears balanced",
  "factDensity": "Moderate — some specific facts present",
  "explanation": "...",
  "indicators": [
    "Moderate sensationalism — some dramatic words used but not excessive",
    "Moderate source credibility — some sources mentioned but not all specific"
  ]
}
```

---

# ❤️ Health Check

The application also provides a health-check endpoint:

```text
GET /health
```

You can test it using:

```bash
curl http://localhost:5000/health
```

Example response:

```json
{
  "status": "ok",
  "server": "FakeShield",
  "time": "2026-08-27T..."
}
```

---

# 🔐 Input Validation

FakeShield validates submitted text before analysis.

The minimum required text length is:

```text
20 characters
```

The application also rejects content containing fewer than 10 alphabetic characters.

The maximum analyzed text length is:

```text
10,000 characters
```

This prevents extremely large submissions from being processed unnecessarily.

---

# 🧪 Example

A sensationalist article containing phrases such as:

```text
BREAKING! SHOCKING discovery exposed!

They don't want you to know the truth. Sources say
this unbelievable discovery could change everything!
Share before this story is deleted!
```

would likely receive a higher fake-news score because it contains:

* Sensationalist language
* Clickbait patterns
* Vague sourcing
* Excessive punctuation
* ALL-CAPS text
* Emotional language
* Lack of specific verifiable facts

---

# ⚠️ Important Limitations

FakeShield is a **rule-based linguistic analysis tool**, not a professional fact-checking system.

It does **not actually verify whether a claim is true**.

For example, an article can contain:

* Specific dates
* Numbers
* Named people
* Formal language
* Professional vocabulary

and still contain completely false information.

Similarly, a legitimate breaking-news article may use emotional or urgent language and therefore receive a higher fake-news score.

The system should therefore be considered an **educational and analytical tool**, not an authoritative source of truth.

For important claims, users should verify information using multiple independent and trustworthy sources.

---

# 🎓 Academic Purpose

FakeShield was developed as an academic project for studying:

* Natural Language Processing
* Text classification
* Rule-based systems
* Web application development
* Python programming
* Flask
* Regular expressions
* Text preprocessing
* Heuristic scoring
* API development

The project demonstrates how linguistic characteristics can be combined to create a simple fake-news detection system without machine learning.

---

# 🔮 Future Improvements

Possible future improvements include:

* Machine-learning-based classification
* Transformer/NLP models
* Real-time fact checking
* News API integration
* Source reputation verification
* URL analysis
* Multilingual fake-news detection
* Database storage of analyzed articles
* User accounts
* Analysis history
* More sophisticated sentiment analysis
* Named Entity Recognition
* Claim extraction
* Automated fact verification
* Browser extension
* Improved confidence calibration

---

# 📜 License

This project is intended primarily for educational and academic purposes.

You are free to modify and improve the project for learning and experimentation.

---

# 👨‍💻 Author

**Sudin**

BIT — 4th Semester

### FakeShield


