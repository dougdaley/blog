"""
Enhanced Flask application with EditorJS support and database integration
"""
import os
import requests
from flask import Flask, render_template, abort, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import markdown
import json
import yaml
from datetime import datetime
import re
# Simple slugify function
def slugify(text):
    import re
    return re.sub(r'[^\w\s-]', '', text.lower()).strip().replace(' ', '-')

# Import configuration
from config import config

# Import models
from models.article import db, Article, Tag
from models.business import BusinessProcess, Control, Role, MaturityAssessment

# Import services
from services.content_converter import EditorJSConverter


def create_app(config_name=None):
    """Application factory pattern"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    
    # Content converter
    converter = EditorJSConverter()
    
    # Configure markdown with extensions for better formatting
    md = markdown.Markdown(extensions=[
        'markdown.extensions.fenced_code',
        'markdown.extensions.codehilite',
        'markdown.extensions.toc',
        'markdown.extensions.tables'
    ])
    
    # Legacy content fetching functions (for backward compatibility)
    def fetch_github_file(path):
        """Fetch a file from the GitHub repository or local file system"""
        local_path = os.path.join('.', path)
        if os.path.exists(local_path):
            try:
                with open(local_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except IOError as e:
                print(f"Error reading local file {local_path}: {e}")
        
        url = app.config['RAW_BASE'] + path
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
        """Fetch blog posts - first try database, then fall back to GitHub"""
        # Try database first
        try:
            articles = Article.query.filter_by(status='published').order_by(Article.published_at.desc()).all()
            if articles:
                posts = []
                for article in articles:
                    post_data = article.to_dict()
                    post_data['filename'] = f"{article.slug}.md"
                    post_data['content'] = article.render_html()
                    posts.append(post_data)
                return posts
        except Exception as e:
            print(f"Database query failed: {e}")
        
        # Fall back to GitHub method
        posts_index = fetch_github_file(f'{app.config["BLOG_PATH"]}/index.yaml')
        if not posts_index:
            return []
        
        try:
            posts = yaml.safe_load(posts_index) or []
        except yaml.YAMLError:
            return []
        
        for post in posts:
            if 'filename' in post:
                content = fetch_github_file(f"{app.config['BLOG_PATH']}/{post['filename']}")
                if content:
                    metadata, body = extract_frontmatter(content)
                    post.update(metadata)
                    post['content'] = md.convert(body)
                    
                    if 'excerpt' not in post and body:
                        paragraphs = body.split('\\n\\n')
                        if paragraphs:
                            excerpt = re.sub(r'[#*`\\[\\]()_]', '', paragraphs[0])
                            post['excerpt'] = excerpt[:200] + '...' if len(excerpt) > 200 else excerpt
        
        posts.sort(key=lambda x: x.get('date', ''), reverse=True)
        return posts

    def fetch_projects():
        """Fetch projects from GitHub repository"""
        projects_index = fetch_github_file(f'{app.config["PROJECTS_PATH"]}/index.yaml')
        if not projects_index:
            return []
        
        try:
            projects = yaml.safe_load(projects_index) or []
        except yaml.YAMLError:
            return []
        
        return projects

    def fetch_tom_method():
        """Fetch TOM Method structure and content"""
        method_index = fetch_github_file(f'{app.config["TOM_METHOD_PATH"]}/index.md')
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
        # Try EditorJS JSON first
        json_filename = article_filename.replace('.md', '.json')
        json_path = f"{app.config['TOM_METHOD_PATH']}/{chapter_folder}/{json_filename}"
        json_content = fetch_github_file(json_path)
        if json_content:
            try:
                from services.content_converter import EditorJSConverter
                converter = EditorJSConverter()
                editorjs_data = json.loads(json_content)
                html_content = converter.to_html(editorjs_data)
                # Use metadata from markdown if available, else fallback
                metadata = editorjs_data.get('metadata', {})
                return {
                    'content': html_content,
                    'metadata': metadata,
                    'body': editorjs_data
                }
            except Exception as e:
                print(f"Error rendering EditorJS article: {e}")
                # fallback to markdown below
        # Fallback to markdown
        article_path = f"{app.config['TOM_METHOD_PATH']}/{chapter_folder}/{article_filename}"
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

    # Routes
    @app.route('/')
    def home():
        return render_template('home.html')

    @app.route('/blog')
    def blog():
        posts = fetch_blog_posts()
        return render_template('blog.html', posts=posts)

    @app.route('/blog/<slug>')
    def blog_post(slug):
        # Try database first
        try:
            article = Article.query.filter_by(slug=slug, status='published').first()
            if article:
                return render_template('blog_post.html', post=article.to_dict(include_content=True))
        except Exception as e:
            print(f"Database query failed: {e}")
        
        # Fall back to legacy method
        posts = fetch_blog_posts()
        post = None
        for p in posts:
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
        if not article_filename.endswith('.md'):
            article_filename += '.md'
        
        method_data = fetch_tom_method()
        if not method_data:
            abort(404)
        
        article = fetch_tom_method_article(chapter_folder, article_filename)
        if not article:
            abort(404)
        
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
        
        combined_article = {
            'title': article['metadata'].get('title', 'Untitled Article'),
            'subtitle': article['metadata'].get('subtitle', ''),
            'reading_time': article['metadata'].get('reading_time', ''),
            'content': article['content'],
            'chapter': chapter_meta,
            'metadata': article['metadata']
        }
        
        return render_template('tom_method_article.html', article=combined_article, method=method_data)

    # Admin routes
    @app.route('/admin')
    def admin_dashboard():
        """Admin dashboard"""
        return render_template('admin/dashboard.html')

    @app.route('/admin/articles')
    def admin_articles():
        """List all articles"""
        try:
            articles = Article.query.order_by(Article.updated_at.desc()).all()
            return render_template('admin/articles.html', articles=articles)
        except Exception as e:
            print(f"Error fetching articles: {e}")
            return render_template('admin/articles.html', articles=[])

    @app.route('/admin/articles/new')
    def admin_new_article():
        """Create new article"""
        return render_template('admin/article_edit.html', article=None)

    @app.route('/admin/articles/<int:article_id>')
    def admin_edit_article(article_id):
        """Edit existing article"""
        try:
            article = Article.query.get_or_404(article_id)
            return render_template('admin/article_edit.html', article=article)
        except Exception as e:
            print(f"Error fetching article: {e}")
            abort(404)

    # API routes
    @app.route('/api/articles', methods=['GET', 'POST'])
    def api_articles():
        """API endpoint for articles"""
        if request.method == 'GET':
            try:
                articles = Article.query.all()
                return jsonify([article.to_dict() for article in articles])
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        elif request.method == 'POST':
            try:
                data = request.get_json()
                
                article = Article(
                    title=data.get('title', ''),
                    slug=data.get('slug') or slugify(data.get('title', '')),
                    subtitle=data.get('subtitle', ''),
                    excerpt=data.get('excerpt', ''),
                    author=data.get('author', ''),
                    status=data.get('status', 'draft')
                )
                
                # Set content based on type
                if data.get('content_type') == 'editorjs':
                    article.set_content_from_editorjs(data.get('content', {}))
                else:
                    article.set_content_from_markdown(data.get('content', ''))
                
                db.session.add(article)
                db.session.commit()
                
                return jsonify(article.to_dict(include_content=True)), 201
                
            except Exception as e:
                db.session.rollback()
                return jsonify({'error': str(e)}), 500

    @app.route('/api/articles/<int:article_id>', methods=['GET', 'PUT', 'DELETE'])
    def api_article(article_id):
        """API endpoint for single article"""
        try:
            article = Article.query.get_or_404(article_id)
            
            if request.method == 'GET':
                return jsonify(article.to_dict(include_content=True))
            
            elif request.method == 'PUT':
                data = request.get_json()
                
                article.title = data.get('title', article.title)
                article.subtitle = data.get('subtitle', article.subtitle)
                article.excerpt = data.get('excerpt', article.excerpt)
                article.author = data.get('author', article.author)
                article.status = data.get('status', article.status)
                
                if 'slug' in data:
                    article.slug = data['slug']
                
                # Update content
                if data.get('content_type') == 'editorjs':
                    article.set_content_from_editorjs(data.get('content', {}))
                elif 'content' in data:
                    article.set_content_from_markdown(data.get('content', ''))
                
                db.session.commit()
                return jsonify(article.to_dict(include_content=True))
            
            elif request.method == 'DELETE':
                db.session.delete(article)
                db.session.commit()
                return '', 204
                
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    @app.route('/api/content/save', methods=['POST'])
    def api_save_content():
        """Save EditorJS content"""
        try:
            data = request.get_json()
            content = data.get('content', {})
            article_id = data.get('id')
            
            if article_id:
                article = Article.query.get_or_404(article_id)
                article.set_content_from_editorjs(content)
                db.session.commit()
                
                return jsonify({
                    'success': True,
                    'message': 'Content saved successfully'
                })
            else:
                return jsonify({'error': 'Article ID required'}), 400
                
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('500.html'), 500

    # CLI commands
    @app.cli.command()
    def init_db():
        """Initialize the database"""
        db.create_all()
        print('Database initialized.')

    @app.cli.command()
    def create_sample_data():
        """Create sample data for testing"""
        # Create sample article
        article = Article(
            title="Welcome to the Enhanced Blog",
            slug="welcome-enhanced-blog",
            subtitle="A demonstration of the new EditorJS integration",
            excerpt="This is a sample article created with the new EditorJS system.",
            author="System",
            status="published"
        )
        
        # Sample EditorJS content
        sample_content = {
            "time": datetime.now().timestamp() * 1000,
            "blocks": [
                {
                    "type": "paragraph",
                    "data": {
                        "text": "Welcome to the enhanced blog system! This article demonstrates the new EditorJS integration with custom business blocks."
                    }
                },
                {
                    "type": "header",
                    "data": {
                        "text": "New Features",
                        "level": 2
                    }
                },
                {
                    "type": "list",
                    "data": {
                        "style": "unordered",
                        "items": [
                            "Rich text editing with EditorJS",
                            "Custom business documentation blocks",
                            "Database-backed content management",
                            "Backward compatibility with existing content"
                        ]
                    }
                }
            ],
            "version": "2.28.2"
        }
        
        article.set_content_from_editorjs(sample_content)
        article.publish()
        
        db.session.add(article)
        db.session.commit()
        
        print('Sample data created.')

    return app

# Create app instance
app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=8000)