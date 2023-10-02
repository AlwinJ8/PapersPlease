from metaphor_python import Metaphor
from fastapi import FastAPI, Request
import openai
import json
from datetime import datetime
from dateutil.relativedelta import relativedelta

app = FastAPI()
metaphor = Metaphor(api_key="<METAPHOR_KEY")

openai.organization = '<OPENAI_ORG>'
openai.api_key = '<OPENAI_KEY>'

# Given a JSON {"topic": "<topic>"} returns a list of topics needed to learn the topic along with resources
@app.post("/learn")
async def learn(request: Request):
    request_body = await request.json()
    topic = request_body['topic']

    learning_completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": "give very few broad research topics that form a roadmap of the prerequisite knowledge needed for " + str(topic) + " with titles only in JSON format. Please give in the following format: \{\"number\": \"topic\"\}."}
        ]
    )

    learning_topics = json.loads(learning_completion.choices[0].message.content)
    learning_topics_resources = []

    for topic in learning_topics.values():
        metaphor_response = metaphor.search(
            "learning resources for " + str(topic),
            num_results=5,
            use_autoprompt=True
        )

        resource_list = []
        for result in metaphor_response.results:
            resource_dict = {}
            resource_dict['title'] = result.title
            resource_dict['link'] = result.url
            resource_dict['date'] = result.published_date
            resource_list.append(resource_dict)
        
        learning_topic_resources_entry = {}
        learning_topic_resources_entry["topic"] = topic
        learning_topic_resources_entry["resources"] = resource_list
        learning_topics_resources.append(learning_topic_resources_entry)

    return learning_topics_resources

# Given a JSON {"topic": "<topic>"} returns a list of foundational papers and summaries of their abstracts for the topic
@app.post("/explore")
async def explore(request: Request):
    request_body = await request.json()
    topic = request_body['topic']

    metaphor_response = metaphor.search(
        "Here is a paper about: " + str(topic),
        num_results=10,
        use_autoprompt=True,
    )

    papers_list = []
    for result in metaphor_response.results:
        resource_dict = {}
        resource_dict['title'] = result.title
        resource_dict['link'] = result.url
        resource_dict['date'] = result.published_date
        resource_dict['author'] = result.author

        # Get abstract and summarize using gpt
        abstract = metaphor.get_contents(result.id)
        abstract_completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Given this abstract from the contents of a website: " + abstract.contents[0].extract + " summarize the paper in two sentences briefly."}
            ]
        )

        resource_dict['abstract summary'] = abstract_completion.choices[0].message.content
        papers_list.append(resource_dict)
    
    return papers_list

# Given a JSON {"topic": "<topic>"} returns a list of further exploration topics for the topic, and papers with summaries for each
@app.post("/discover")
async def discover(request: Request):
    request_body = await request.json()
    topic = request_body['topic']

    discover_completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": "give five very specific research ideas for new research exploration in " + str(topic) + " with titles only in JSON format. Please give in the following format: \{\"number\": \"topic\"\}."}
        ]
    )

    discovery_topics = json.loads(discover_completion.choices[0].message.content)
    learning_topics_resources = []

    one_year_ago = datetime.now() - relativedelta(years=1)

    for topic in discovery_topics.values():
        metaphor_response = metaphor.search(
            "Here is a paper about: " + str(topic),
            num_results=3,
            start_published_date=one_year_ago.strftime("%Y-%m-%d"),
            use_autoprompt=True
        )

        resource_list = []
        for result in metaphor_response.results:
            resource_dict = {}
            resource_dict['title'] = result.title
            resource_dict['link'] = result.url
            resource_dict['date'] = result.published_date
            resource_dict['author'] = result.author

            # Get abstract and summarize using gpt
            abstract = metaphor.get_contents(result.id)
            abstract_completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": "Given this abstract from the contents of a website: " + abstract.contents[0].extract + " summarize the paper in two sentences briefly."}
                ]
            )

            resource_dict['abstract summary'] = abstract_completion.choices[0].message.content

            resource_list.append(resource_dict)
        
        learning_topic_resources_entry = {}
        learning_topic_resources_entry["topic"] = topic
        learning_topic_resources_entry["resources"] = resource_list
        learning_topics_resources.append(learning_topic_resources_entry)

    return learning_topics_resources