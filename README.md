# FiveableQuestionExploit
Allows anyone to get all of [Fiveable](https://fiveable.me/) questions for free

# If you don't care on how this works
(make sure python is installed and you have the following packages: requests, json, csv, and os)     
1. Download the release (fiveable.zip).
2. Extract the folder. 
3. Open the fiveable folder
4. Open the folder, right-click anywhere in the folder, and press Open in Terminal
5. Run this command: ``python main.py`` (make sure Python is installed) OR click on the main python file and run it 
6. Follow the prompts
7. The csv with all the questions will be saved in the fiveable folder :) 

# Else (you care how it works): 
___

## Step 0 - intro:
Fivable uses a [Apollo](https://www.apollographql.com/graphos) graphql server, at https://prod.fiveable.me/api//graphql 

They cleary don't provide any documentation on their api, but we can work back by looking at the network requests the webstie makes. First we need to get "slugs" for each subject, its like a id that the api uses to figure out what section we are looking at, then we need the unit. From here we can basically get any question we want and query for diffculty.  

## Step 1 - get slugs:
All the slugs of the database are stored at this url: https://library.fiveable.me/_next/data/H6rl5wshOljn2Oaxn4Hbn/index.json 

We can use a simple script to extract all the slugs from here, the file which does that is [getSlug.py](getSlug.py)
Here is the core logic:
```python
url = "https://library.fiveable.me/_next/data/H6rl5wshOljn2Oaxn4Hbn/index.json"
response = requests.get(url)
data = response.json()

all_slugs = set()

# 1. Get slugs from the main subjects list
subjects_by_branch = data["pageProps"]["subjectsByCategoryBranch"]
for branch in subjects_by_branch:
    for subject in branch.get("subjects", []):
        slug = subject.get("slug")
        if slug:
            all_slugs.add(slug)

# 2. Get slugs from the stats branches
stats_branches = data["pageProps"]["stats"]["countSubjectsByCategoryBranch"]
for item in stats_branches:
    slug = item.get("slug")
    if slug:
        all_slugs.add(slug)

# 3. Get slugs from the stats sub-branches
stats_sub_branches = data["pageProps"]["stats"]["countSubjectsByCategorySubBranch"]
for item in stats_sub_branches:
    slug = item.get("slug")
    if slug:
        all_slugs.add(slug)
```

## Step 2 - get Unit ids:
Now we can get the units in a subject, using this endpoint: https://library.fiveable.me/api/subjects/{slug}/getAllNavigationData ({slug} is the respective slug) 

Here is an example response for ap-calc:
```json
{
  "getNavigationSubject": {
    "id": "ap-calculus",
    "name": "AP Calculus AB/BC",
    "emoji": "♾️",
    "active": true,
    "slug": "ap-calc", //matches our slug
    "keyTermsActive": null,
    "category": "Math & Computer Science",
    "hasCalculators": true,
    "hasKeyTerms": true,
    "hasPracticeQuestions": true,
    "units": [
      {
        "id": "i3gyeoce2fMjzN88", //Unit ID
        "name": "Unit 1 – Limits and Continuity", //Unit 
        "slug": "unit-1",
        "order": null,
        "active": true,
        "description": null,
        "emoji": "👑",
        "h1": null,
        "hasResources": true,
        "publicId": "i3gyeoce2fMjzN88",
        "resources": [
          {
            "id": "HVxTuBB73RiPPODABBib", //Unit ID
            "title": "1.12 Confirming Continuity over an Interval", //Topic
            "slug": "confirming-continuity-over-an-interval",
            "type": "STUDY_GUIDE",
            "date": null,
            "topicIds": [
              "BqSoSwBjYurktMAwvEXua" //ID for that specfic topic 
            ]
          },...
```

We can make a simple function to get this and put it in a simple data structure. The file responsible for this is [getUnitId.py](getUnitId.py)
```python
def get_subject_navigation(slug: str) -> dict:
    url = f"https://library.fiveable.me/api/subjects/{slug}/getAllNavigationData"
    navigation_data = {}
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        
        subject_data = data.get("getNavigationSubject")

        for unit in subject_data.get("units", []):
            unit_id = unit.get("id")
            unit_name = unit.get("name")
            
            if not unit_id:
                continue

            navigation_data[unit_id] = {
                "name": unit_name,
                "topics": []
            }
            
            for resource in unit.get("resources", []):
                topic_id = resource.get("id")
                topic_name = resource.get("title")
                
                if topic_id and topic_name:
                    navigation_data[unit_id]["topics"].append({
                        "id": topic_id,
                        "name": topic_name
                    })

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching data for slug '{slug}': {e}")
    except json.JSONDecodeError:
        print(f"Failed to parse JSON response for slug '{slug}'.")
        
    return navigation_data
```

## Step 3 - get the questions:
Here is the final URL we will use to fetch the questions: https://library.fiveable.me/api/practice-questions
We add three things to the request:
- subjectId = the slug
- unitId = the unit
- limit = the amount
- type (optional) = CLAUDE_3_7 or SINGLE_ANSWER

[getQuestions.py](getQuestions.py) Has a function which does this

```python
def get_practice_questions(subject_slug: str, unit_id: str, topic_id: str, limit: int = 1, question_type: str = None) -> list:
    """
    Fetches practice questions from the Fiveable API.

    Args:
        subject_slug: The slug for the subject (e.g., "ap-calc").
        unit_id: The ID of the unit.
        topic_id: The ID of the topic.
        limit: The number of questions to fetch (1-40).
        question_type: Optional. Can be "CLAUDE_3_7", "SINGLE_ANSWER", etc.

    Returns:
        A list of dictionaries, each containing a question, answers, the correct answer, and an explanation.
    """
    base_url = "https://library.fiveable.me/api/practice-questions"
    params = {
        "subjectId": subject_slug,
        "unitId": unit_id,
        "topicId": topic_id,
        "limit": limit
    }
    if question_type:
        params["type"] = question_type
    
    processed_questions = []
    try:
        response = requests.get(base_url, params=params,  timeout=15)
        response.raise_for_status()
        data = response.json()

        questions_list = data.get("data", {}).get("practiceQuestionsByTopic", [])
        
        for q_data in questions_list:
            correct_answer = ""
            all_answers = []
            for ans in q_data.get("answers", []):
                all_answers.append(ans.get("answer"))
                if ans.get("type") == "CORRECT":
                    correct_answer = ans.get("answer")
            
            processed_questions.append({
                "question": q_data.get("question"),
                "answers": all_answers,
                "correct_answer": correct_answer,
                "explanation": q_data.get("explanation")
            })

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching questions: {e}")
    except json.JSONDecodeError:
        print("Failed to parse JSON response for questions.")
        
    return processed_questions
```

That's It! 










