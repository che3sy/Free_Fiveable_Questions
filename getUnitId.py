import requests
import json

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
                topic_ids_list = resource.get("topicIds")
                topic_name = resource.get("title")
                
                if topic_name and topic_ids_list and len(topic_ids_list) > 0:
                    topic_id = topic_ids_list[0]
                    navigation_data[unit_id]["topics"].append({
                        "id": topic_id,
                        "name": topic_name
                    })

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching data for slug '{slug}': {e}")
    except json.JSONDecodeError:
        print(f"Failed to parse JSON response for slug '{slug}'.")
        
    return navigation_data
