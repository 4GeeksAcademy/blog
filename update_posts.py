import json
import os
from datetime import datetime
import re

def get_slug_from_filename(filename):
    # Remove the language suffix and .md extension
    base_name = re.sub(r'(\.(us|es))?\.md$', '', filename)
    return base_name

def get_lang_from_filename(filename):
    if '.es.md' in filename:
        return 'es'
    return 'us'

def create_excerpt(title):
    # Create a simple excerpt from the title
    return f"Learn about {title} with 4Geeks Academy. Get expert insights and guidance for your tech career."

def validate_posts_json(posts):
    required_fields = ['slug', 'fileName', 'status', 'authors', 'title', 'date', 'lang', 'translations', 'excerpt']
    valid_langs = ['us', 'es']
    errors = []

    if not isinstance(posts, list):
        return ["posts.json must contain a list of posts"]

    for i, post in enumerate(posts):
        # Check required fields
        for field in required_fields:
            if field not in post:
                errors.append(f"Post at index {i} is missing required field: {field}")
                continue

        # Validate field types
        if not isinstance(post['slug'], str):
            errors.append(f"Post at index {i} has invalid slug type: {type(post['slug'])}")
        if not isinstance(post['fileName'], str):
            errors.append(f"Post at index {i} has invalid fileName type: {type(post['fileName'])}")
        if not isinstance(post['status'], str):
            errors.append(f"Post at index {i} has invalid status type: {type(post['status'])}")
        if post['authors'] is not None and not isinstance(post['authors'], list):
            errors.append(f"Post at index {i} has invalid authors type: {type(post['authors'])}")
        if not isinstance(post['title'], str):
            errors.append(f"Post at index {i} has invalid title type: {type(post['title'])}")
        if not isinstance(post['date'], str):
            errors.append(f"Post at index {i} has invalid date type: {type(post['date'])}")
        if not isinstance(post['lang'], str):
            errors.append(f"Post at index {i} has invalid lang type: {type(post['lang'])}")
        if not isinstance(post['translations'], list):
            errors.append(f"Post at index {i} has invalid translations type: {type(post['translations'])}")
        if not isinstance(post['excerpt'], str):
            errors.append(f"Post at index {i} has invalid excerpt type: {type(post['excerpt'])}")

        # Validate date format
        try:
            datetime.strptime(post['date'], "%Y-%m-%dT%H:%M:%S+00:00")
        except ValueError:
            errors.append(f"Post at index {i} has invalid date format: {post['date']}")

        # Validate language
        if post['lang'] not in valid_langs:
            errors.append(f"Post at index {i} has invalid language: {post['lang']}")

    return errors

def update_posts_json():
    # Read existing posts.json
    with open('api/posts.json', 'r', encoding='utf-8') as f:
        posts = json.load(f)

    # Validate posts.json format
    errors = validate_posts_json(posts)
    if errors:
        print("Error: posts.json has format issues:")
        for error in errors:
            print(f"- {error}")
        return

    # Get existing filenames
    existing_filenames = {post['fileName'] for post in posts}

    # Get all .md files from blog directory
    blog_files = [f for f in os.listdir('blog') if f.endswith('.md')]

    # Find missing files
    missing_files = [f for f in blog_files if f not in existing_filenames]

    # Create new entries for missing files
    for filename in missing_files:
        slug = get_slug_from_filename(filename)
        lang = get_lang_from_filename(filename)
        
        # Create a title from the filename
        title = ' '.join(slug.split('-')).title()
        
        new_post = {
            "slug": slug,
            "fileName": filename,
            "status": "published",
            "authors": None,
            "title": title,
            "date": datetime.now().strftime("%Y-%m-%dT%H:%M:%S+00:00"),
            "lang": lang,
            "translations": [],
            "excerpt": create_excerpt(title)
        }
        posts.append(new_post)

    # Sort posts by date
    posts.sort(key=lambda x: x['date'], reverse=True)

    # Write updated posts.json
    with open('api/posts.json', 'w', encoding='utf-8') as f:
        json.dump(posts, f, indent=2, ensure_ascii=False)
    
    print("Success: posts.json has been updated successfully!")
    if missing_files:
        print(f"Added {len(missing_files)} new entries to posts.json")

if __name__ == "__main__":
    update_posts_json() 