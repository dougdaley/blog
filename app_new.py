"""
Enhanced Flask application with EditorJS support and database integration
"""
import os
from flask import Flask, render_template, abort, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
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
from models.navigation import NavigationItem

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

    def ensure_schema():
        """Ensure database has latest columns/tables without relying on migrations."""
        from sqlalchemy import inspect, text

        with app.app_context():
            engine = db.engine
            inspector = inspect(engine)

            # Ensure navigation_items table exists
            NavigationItem.__table__.create(bind=engine, checkfirst=True)

            columns = {col['name'] for col in inspector.get_columns('articles')}
            alter_statements = []

            if 'section' not in columns:
                alter_statements.append(text("ALTER TABLE articles ADD COLUMN section VARCHAR(50) DEFAULT 'blog'"))
            if 'subsection' not in columns:
                alter_statements.append(text("ALTER TABLE articles ADD COLUMN subsection VARCHAR(100)"))
            if 'chapter_slug' not in columns:
                alter_statements.append(text("ALTER TABLE articles ADD COLUMN chapter_slug VARCHAR(100)"))
            if 'chapter_order' not in columns:
                alter_statements.append(text("ALTER TABLE articles ADD COLUMN chapter_order INTEGER"))
            if 'featured_order' not in columns:
                alter_statements.append(text("ALTER TABLE articles ADD COLUMN featured_order INTEGER"))

            with engine.connect() as conn:
                for statement in alter_statements:
                    try:
                        conn.execute(statement)
                    except Exception:
                        pass

                try:
                    conn.execute(text("UPDATE articles SET section='blog' WHERE section IS NULL OR section = ''"))
                except Exception:
                    pass

    ensure_schema()
    
    # Content converter
    converter = EditorJSConverter()
    
    # Legacy content fetching functions (for backward compatibility)
    def fetch_blog_posts():
        """Fetch published blog articles from the database."""
        try:
            articles = Article.query \
                .filter_by(status='published', section='blog') \
                .order_by(db.func.coalesce(Article.featured_order, 9999), Article.published_at.desc()) \
                .all()
        except Exception as exc:
            print(f"Error fetching blog posts: {exc}")
            return []

        posts = []
        for article in articles:
            data = article.to_dict(include_content=True)
            data['html'] = article.render_html()
            data['display_date'] = article.published_at.strftime('%B %d, %Y') if article.published_at else None
            data['url'] = f"/blog/{article.slug}"
            posts.append(data)
        return posts

    def fetch_portfolio_items():
        """Fetch published portfolio entries."""
        try:
            entries = Article.query \
                .filter_by(status='published', section='portfolio') \
                .order_by(db.func.coalesce(Article.featured_order, 9999), Article.published_at.desc()) \
                .all()
        except Exception as exc:
            print(f"Error fetching portfolio items: {exc}")
            return []

        projects = []
        for article in entries:
            data = article.to_dict(include_content=True)
            data['html'] = article.render_html()
            data['url'] = f"/portfolio/{article.slug}"
            projects.append(data)
        return projects

    def fetch_tom_method():
        """Build TOM Method landing data from published articles."""
        try:
            hero_article = Article.query \
                .filter_by(status='published', section='tom_method', subsection='hero') \
                .order_by(db.func.coalesce(Article.featured_order, 9999), Article.published_at.desc()) \
                .first()

            guiding_article = Article.query \
                .filter_by(status='published', section='tom_method', subsection='guiding') \
                .order_by(db.func.coalesce(Article.featured_order, 9999), Article.published_at.desc()) \
                .first()

            chapter_articles = Article.query \
                .filter_by(status='published', section='tom_method', subsection='chapter') \
                .order_by(db.func.coalesce(Article.featured_order, 9999), Article.title.asc()) \
                .all()
        except Exception as exc:
            print(f"Error fetching TOM method data: {exc}")
            return None

        if not hero_article:
            return None

        def roman_numeral(n):
            numerals = [
                (1000, 'M'), (900, 'CM'), (500, 'D'), (400, 'CD'),
                (100, 'C'), (90, 'XC'), (50, 'L'), (40, 'XL'),
                (10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I')
            ]
            result = ''
            for value, numeral in numerals:
                while n >= value:
                    result += numeral
                    n -= value
            return result

        chapters = []
        for index, chapter in enumerate(chapter_articles, start=1):
            chapter_children = Article.query \
                .filter_by(status='published', section='tom_method', chapter_slug=chapter.slug) \
                .order_by(db.func.coalesce(Article.chapter_order, 9999), Article.title.asc()) \
                .all()

            chapter_dict = {
                'number': roman_numeral(index),
                'title': chapter.title,
                'slug': chapter.slug,
                'excerpt': chapter.excerpt,
                'rendered': chapter.render_html(),
                'articles': []
            }

            for child in chapter_children:
                chapter_dict['articles'].append({
                    'title': child.title,
                    'slug': child.slug,
                    'chapter_slug': child.chapter_slug,
                    'excerpt': child.excerpt,
                    'reading_time': child.reading_time,
                    'url': f"/tom-method/{child.chapter_slug}/{child.slug}"
                })

            chapters.append(chapter_dict)

        return {
            'title': hero_article.title,
            'subtitle': hero_article.subtitle,
            'hero_html': hero_article.render_html(),
            'guiding_html': guiding_article.render_html() if guiding_article else None,
            'guiding_title': guiding_article.title if guiding_article else None,
            'chapters': chapters
        }


    def resolve_active_pattern(item):
        """Derive the URL prefix used to highlight the active nav state."""
        if item.section == 'home':
            return '/'
        if item.section == 'blog':
            return '/blog'
        if item.section == 'tom_method':
            return '/tom-method'
        if item.section == 'portfolio':
            return '/portfolio'
        if item.url:
            return item.url
        return '/'

    @app.context_processor
    def inject_navigation():
        try:
            items = NavigationItem.query.filter_by(is_visible=True).order_by(NavigationItem.position.asc(), NavigationItem.id.asc()).all()
        except Exception:
            items = []
        nav_links = []
        for item in items:
            try:
                href = item.effective_url()
            except Exception:
                href = item.url or '/'
            nav_links.append({
                'id': item.id,
                'label': item.label,
                'url': href,
                'section': item.section,
                'is_external': item.is_external,
                'active_pattern': resolve_active_pattern(item)
            })
        return {'navigation_items': nav_links}

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
        try:
            article = Article.query.filter_by(slug=slug, section='blog', status='published').first()
        except Exception as exc:
            print(f"Error fetching blog article: {exc}")
            article = None

        if not article:
            abort(404)

        return render_template('article_page.html', article=article)

    @app.route('/portfolio')
    def portfolio():
        projects = fetch_portfolio_items()
        return render_template('portfolio.html', projects=projects)

    @app.route('/portfolio/<slug>')
    def portfolio_detail(slug):
        try:
            article = Article.query.filter_by(slug=slug, section='portfolio', status='published').first()
        except Exception as exc:
            print(f"Error fetching portfolio article: {exc}")
            article = None

        if not article:
            abort(404)

        return render_template('article_page.html', article=article)

    @app.route('/tom-method')
    def tom_method():
        method_data = fetch_tom_method()
        if not method_data:
            abort(404)
        return render_template('tom_method.html', method=method_data)

    @app.route('/tom-method/<chapter_folder>/<article_filename>')
    def tom_method_article(chapter_folder, article_filename):
        slug = article_filename.replace('.md', '')
        try:
            article = Article.query.filter_by(slug=slug, section='tom_method', status='published').first()
        except Exception as exc:
            print(f"Error fetching TOM article: {exc}")
            article = None

        if not article:
            abort(404)

        if article.chapter_slug and article.chapter_slug != chapter_folder:
            abort(404)

        method_data = fetch_tom_method()

        chapter_meta = None
        if method_data and article.chapter_slug:
            for chapter in method_data['chapters']:
                if chapter['slug'] == article.chapter_slug:
                    chapter_meta = {
                        'number': chapter['number'],
                        'title': chapter['title'],
                        'excerpt': chapter.get('excerpt')
                    }
                    break

        return render_template('tom_method_article.html', article=article, method=method_data, chapter_meta=chapter_meta)

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

    @app.route('/admin/navigation')
    def admin_navigation():
        """Navigation management dashboard"""
        try:
            items = NavigationItem.query.order_by(NavigationItem.position.asc(), NavigationItem.id.asc()).all()
        except Exception:
            items = []
        serialized = []
        for item in items:
            try:
                resolved = item.effective_url()
            except Exception:
                resolved = item.url or '/'
            data = item.to_dict()
            data['resolved_url'] = resolved
            serialized.append(data)
        return render_template('admin/navigation.html', items=items, items_json=serialized)

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
                data = request.get_json() or {}

                def parse_optional_int(value):
                    try:
                        return int(value)
                    except (TypeError, ValueError):
                        return None

                section = (data.get('section') or 'blog').strip()
                subsection = (data.get('subsection') or '').strip() or None
                chapter_slug = (data.get('chapter_slug') or '').strip() or None
                chapter_order = parse_optional_int(data.get('chapter_order'))
                featured_order = parse_optional_int(data.get('featured_order'))

                article = Article(
                    title=data.get('title', ''),
                    slug=data.get('slug') or slugify(data.get('title', '')),
                    subtitle=data.get('subtitle', ''),
                    excerpt=data.get('excerpt', ''),
                    author=data.get('author', ''),
                    status=data.get('status', 'draft'),
                    section=section or 'blog',
                    subsection=subsection,
                    chapter_slug=chapter_slug,
                    chapter_order=chapter_order,
                    featured_order=featured_order
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
                data = request.get_json() or {}

                def parse_optional_int(value):
                    try:
                        return int(value)
                    except (TypeError, ValueError):
                        return None

                article.title = data.get('title', article.title)
                article.subtitle = data.get('subtitle', article.subtitle)
                article.excerpt = data.get('excerpt', article.excerpt)
                article.author = data.get('author', article.author)
                article.status = data.get('status', article.status)

                if 'slug' in data:
                    article.slug = data['slug']

                if 'section' in data:
                    section_value = (data.get('section') or 'blog').strip()
                    article.section = section_value or 'blog'
                if 'subsection' in data:
                    subsection_value = (data.get('subsection') or '').strip() or None
                    article.subsection = subsection_value
                if 'chapter_slug' in data:
                    article.chapter_slug = (data.get('chapter_slug') or '').strip() or None
                if 'chapter_order' in data:
                    article.chapter_order = parse_optional_int(data.get('chapter_order'))
                if 'featured_order' in data:
                    article.featured_order = parse_optional_int(data.get('featured_order'))

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

    @app.route('/api/articles/sections', methods=['GET'])
    def api_article_sections():
        try:
            query = db.session.query(Article.section).filter(Article.section.isnot(None)).distinct()
            sections = sorted([row[0] for row in query if row[0]])
            return jsonify(sections)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/navigation', methods=['GET', 'POST'])
    def api_navigation():
        """API endpoint for navigation collection"""
        if request.method == 'GET':
            items = NavigationItem.query.order_by(NavigationItem.position.asc(), NavigationItem.id.asc()).all()
            return jsonify([item.to_dict() | {'resolved_url': item.effective_url()} for item in items])

        data = request.get_json() or {}
        try:
            max_position = db.session.query(db.func.max(NavigationItem.position)).scalar() or 0
            item = NavigationItem(
                label=data.get('label', '').strip() or 'Untitled',
                slug=(data.get('slug') or '').strip() or None,
                url=(data.get('url') or '').strip() or None,
                section=(data.get('section') or '').strip() or None,
                is_external=bool(data.get('is_external')),
                is_visible=data.get('is_visible', True),
                position=data.get('position', max_position + 1)
            )
            db.session.add(item)
            db.session.commit()
            return jsonify(item.to_dict() | {'resolved_url': item.effective_url()}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    @app.route('/api/navigation/<int:item_id>', methods=['PUT', 'DELETE'])
    def api_navigation_item(item_id):
        try:
            item = NavigationItem.query.get_or_404(item_id)

            if request.method == 'DELETE':
                db.session.delete(item)
                db.session.commit()
                return '', 204

            data = request.get_json() or {}

            for field in ['label', 'slug', 'url', 'section']:
                if field in data:
                    value = data[field]
                    setattr(item, field, value.strip() if isinstance(value, str) else value)

            if 'is_external' in data:
                item.is_external = bool(data['is_external'])
            if 'is_visible' in data:
                item.is_visible = bool(data['is_visible'])
            if 'position' in data and data['position'] is not None:
                try:
                    item.position = int(data['position'])
                except (TypeError, ValueError):
                    pass

            db.session.commit()
            return jsonify(item.to_dict() | {'resolved_url': item.effective_url()})
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
