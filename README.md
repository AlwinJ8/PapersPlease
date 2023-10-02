# PapersPlease

This repository provides a REST API for discovering new papers. Provide a topic and the API handles the rest :) The endpoint functionalities include:
- Generating a map of foundational knowledge for learning a topic and a curated list of learning resources for each baseline topic
- Finding important papers on a topic along with a brief summary of their abstracts
- Discovering new research ideas for a topic and viewing research already done in those areas, along with a summary of their abstracts

Built using GPT and the [Metaphor API](https://metaphor.systems/).

# Usage
Install the dependencies and run the API locally to get started:

```
pip install -r requirements.txt
uvicorn backend:app --reload
```

Replace the placeholder API keys with your own keys. You can then make a POST request to one of the three endpoints `("/learn", "/discover", "/explore")`, passing the topic in the request body:
```
{
   "topic": "knowledge distillation"
}
```

Sample responses for the endpoints with topic "knowledge distillation" can be found in the respective txt files.

