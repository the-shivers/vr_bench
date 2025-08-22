# VR Bench - Simple Version

Run visual reasoning questions on models. No bullshit.

## Setup

```bash
pip3 install -r requirements.txt
cp .env.example .env
# Edit .env and add your API key
```

## Run

```bash
python3 run.py
```

That's it.

## Config

Edit these sections in `run.py`:

```python
# Add/remove models
MODELS = [
    {
        "name": "gemini-2.5-pro",
        "model": "google/gemini-2.5-pro", 
        "reasoning": {"effort": "medium"},
        "max_tokens": 2000
    }
]

# Filter questions  
MAX_QUESTIONS = 3  # None for all
QUESTION_TYPE = "Photo"  # None for all types
```

API key comes from `.env` file (safe for git).

## Data

- `questions.json` - 511 questions with images
- `images/` - all the images
- `results.json` - output after running