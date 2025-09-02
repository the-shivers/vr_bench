# Everyday Visual Reasoning Benchmark

Homemade benchmark to assess how good LLMs are at everyday visual reasoning tasks including counting, identifying objects, and multi-step reasoning.

You're welcome to run this yourself (apologies about the code: there's a lot of Claudeslop), or you can just look at the results.

I made a Twitter/X thread about it [here](https://x.com/thinkingshivers/status/1962768039994073375).

## Running

Install the requirements. 
Then comment/uncomment whatever models you want to run from run.py. 
Make sure you update MAX_QUESTIONS in run.py as well.
Make sure you have an OpenRouter and XAI API key in an .env to be loaded.

```bash
python3 run.py
```

That's it.

## Key Files

- `questions.json` - 500+ questions
- `images/` - all the images
- `results.json` - raw output after running
- `results_cleaned.tsv` - Manually cleaned results to guarantee accuracy. Was able to catch a few questions with incorrect answers in this review. Please use this file rather than results.json if you want to analyze the data.
- `create_tsv.py` - Creates a .tsv from the results.json.
- `analyze_cleaned_results.py` - Outputs summary statistics by model, according to command line parameters.

## Notes

This was a fun project, but it was also a lot of work. The annoying thing about manually creating all these questions, indexing all the images, etc. is that you can't outsource it to an LLM! Because you know, it's their ability to do that that we're testing.

If you do decide to dig into the results, you'll notice that there's actually two sets of results for GPT-5 and Grok. The first time I ran the test, I didn't configure any image detail level parameters. As a result, even though GPT-5's first run went quite well, Grok's first run went terribly. It seems like it was ingesting low-res (low-token) versions of each image, and so it wasn't able to answer questions about them very well. I did another batch of runs for both GPT-5 and Grok 4 with the image detail parameter set explicitly to high instead of auto. Grok's score improved greatly. GPT-5's somehow fell slightly. I didn't want to list both sets of results since it would require confusing footnotes for all the graphs. Ultimately I decided to go with the explicitly-set high-detail runs. Even though this portrays GPT-5 as slightly worse, I think the general story is still the same. Plus, it's a good reminder that there's going to be
some level of variation in these results, the same model may not always give the same answer, even with temperature set to 0.
