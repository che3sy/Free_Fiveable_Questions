import requests
import csv
import os
csv_file_path="all_slugs.csv"

def refresh_slugs():
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

    sorted_slugs = sorted(list(all_slugs))

    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        for slug in sorted_slugs:
            writer.writerow([slug])

def load_slugs() -> list:
    if not os.path.exists(csv_file_path):
        print(f"'{csv_file_path}' not found. Running initial fetch...")
        return refresh_slugs()
    
    with open(csv_file_path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        return [row[0] for row in reader]