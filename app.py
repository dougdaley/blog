import os
import requests
from flask import Flask, render_template, abort
import markdown
import yaml
from datetime import datetime
import re

app = Flask(__name__)

# Configure markdown with extensions for better formatting
md = markdown.Markdown(extensions=[
    'markdown.extensions.fenced_code',
    'markdown.extensions.codehilite',
    'markdown.extensions.toc',
    'markdown.extensions.tables'
])

# Configuration: Set your GitHub repo details here

# Configured for dougdaley/blog.git
GITHUB_USER = 'dougdaley'
GITHUB_REPO = 'blog'
BLOG_PATH = 'content/blog'  # folder in repo for blog posts
PROJECTS_PATH = 'content/projects'  # folder in repo for projects
TOM_METHOD_PATH = 'content/tom-method'  # folder for TOM Method content

RAW_BASE = f'https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/main/'


def fetch_github_file(path):
    """Fetch a file from the GitHub repository or local file system"""
    # First try to read from local file system (for development)
    local_path = os.path.join('.', path)
    if os.path.exists(local_path):
        try:
            with open(local_path, 'r', encoding='utf-8') as f:
                return f.read()
        except IOError as e:
            print(f"Error reading local file {local_path}: {e}")
    
    # Fall back to GitHub if local file not found
    url = RAW_BASE + path
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return r.text
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
    return None


def extract_frontmatter(content):
    """Extract YAML frontmatter from markdown content"""
    if not content.startswith('---'):
        return {}, content
    
    try:
        _, frontmatter, body = content.split('---', 2)
        metadata = yaml.safe_load(frontmatter.strip())
        return metadata or {}, body.strip()
    except (ValueError, yaml.YAMLError):
        return {}, content


def fetch_blog_posts():
    """Fetch blog posts from GitHub repository"""
    posts_index = fetch_github_file(f'{BLOG_PATH}/index.yaml')
    if not posts_index:
        return []
    
    try:
        posts = yaml.safe_load(posts_index) or []
    except yaml.YAMLError:
        return []
    
    for post in posts:
        if 'filename' in post:
            content = fetch_github_file(f"{BLOG_PATH}/{post['filename']}")
            if content:
                metadata, body = extract_frontmatter(content)
                # Merge index metadata with frontmatter (index takes precedence)
                post.update(metadata)
                post['content'] = md.convert(body)
                
                # Generate excerpt if not provided
                if 'excerpt' not in post and body:
                    # Extract first paragraph as excerpt
                    paragraphs = body.split('\n\n')
                    if paragraphs:
                        # Strip markdown formatting for excerpt
                        excerpt = re.sub(r'[#*`\[\]()_]', '', paragraphs[0])
                        post['excerpt'] = excerpt[:200] + '...' if len(excerpt) > 200 else excerpt
    
    # Sort by date if available
    posts.sort(key=lambda x: x.get('date', ''), reverse=True)
    return posts


def fetch_projects():
    """Fetch projects from GitHub repository"""
    projects_index = fetch_github_file(f'{PROJECTS_PATH}/index.yaml')
    if not projects_index:
        return []
    
    try:
        projects = yaml.safe_load(projects_index) or []
    except yaml.YAMLError:
        return []
    
    return projects


def fetch_tom_method():
    """Fetch TOM Method structure and content"""
    method_index = fetch_github_file(f'{TOM_METHOD_PATH}/index.md')
    if not method_index:
        return None
    
    try:
        metadata, body = extract_frontmatter(method_index)
        method_content = md.convert(body)
        
        return {
            'title': metadata.get('title', 'The TOM Method'),
            'subtitle': metadata.get('subtitle', ''),
            'content': method_content,
            'metadata': metadata
        }
    except Exception as e:
        print(f"Error processing TOM method index: {e}")
        return None


def fetch_tom_method_article(chapter_folder, article_filename):
    """Fetch a specific TOM Method article"""
    article_path = f"{TOM_METHOD_PATH}/{chapter_folder}/{article_filename}"
    content = fetch_github_file(article_path)
    if not content:
        return None
    
    metadata, body = extract_frontmatter(content)
    article_content = md.convert(body)
    
    return {
        'content': article_content,
        'metadata': metadata,
        'body': body
    }


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/blog')
def blog():
    posts = fetch_blog_posts()
    return render_template('blog.html', posts=posts)


@app.route('/blog/<slug>')
def blog_post(slug):
    posts = fetch_blog_posts()
    # Find post by matching filename or create slug from title
    post = None
    for p in posts:
        # Create slug from filename (remove .md extension)
        post_slug = p.get('filename', '').replace('.md', '').lower().replace(' ', '-')
        if post_slug == slug:
            post = p
            break
    
    if not post:
        abort(404)
    
    return render_template('blog_post.html', post=post)


@app.route('/portfolio')
def portfolio():
    projects = fetch_projects()
    return render_template('portfolio.html', projects=projects)


@app.route('/tom-method')
def tom_method():
    method_data = fetch_tom_method()
    if not method_data:
        abort(404)
    return render_template('tom_method.html', method=method_data)


@app.route('/tom-method/<chapter_folder>/<article_filename>')
def tom_method_article(chapter_folder, article_filename):
    # Remove .md extension if present in URL
    if not article_filename.endswith('.md'):
        article_filename += '.md'
    
    method_data = fetch_tom_method()
    if not method_data:
        abort(404)
    
    article = fetch_tom_method_article(chapter_folder, article_filename)
    if not article:
        abort(404)
    
    # Create chapter info from folder name
    chapter_names = {
        '01-foundation': {'number': 'I', 'title': 'Foundation & Principles'},
        '02-strategy': {'number': 'II', 'title': 'Strategy & Vision'},
        '03-operating-model': {'number': 'III', 'title': 'Operating Model Design'},
        '04-process-architecture': {'number': 'IV', 'title': 'Process Architecture'},
        '05-technology-integration': {'number': 'V', 'title': 'Technology Integration'},
        '06-people-change': {'number': 'VI', 'title': 'People & Change'},
        '07-performance-evolution': {'number': 'VII', 'title': 'Performance & Evolution'}
    }
    
    chapter_meta = chapter_names.get(chapter_folder, {'number': '', 'title': 'Unknown Chapter'})
    
    # Combine metadata from article frontmatter
    combined_article = {
        'title': article['metadata'].get('title', 'Untitled Article'),
        'subtitle': article['metadata'].get('subtitle', ''),
        'reading_time': article['metadata'].get('reading_time', ''),
        'content': article['content'],
        'chapter': chapter_meta,
        'metadata': article['metadata']
    }
    
    return render_template('tom_method_article.html', article=combined_article, method=method_data)


if __name__ == '__main__':
    app.run(debug=True)
