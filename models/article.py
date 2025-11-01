from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
import markdown
from typing import Dict, Any, Optional

db = SQLAlchemy()

class Article(db.Model):
    """Enhanced article model supporting both Markdown and EditorJS content"""
    
    __tablename__ = 'articles'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    subtitle = db.Column(db.Text)
    
    # Content fields
    content_type = db.Column(db.String(20), default='markdown')  # 'markdown' or 'editorjs'
    content_json = db.Column(db.JSON)  # For EditorJS blocks
    content_markdown = db.Column(db.Text)  # For Markdown content
    
    # Metadata
    excerpt = db.Column(db.Text)
    reading_time = db.Column(db.String(20))
    author = db.Column(db.String(100))
    
    # Publishing
    status = db.Column(db.String(20), default='draft')  # 'draft', 'published', 'archived'
    published_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # SEO
    meta_description = db.Column(db.Text)
    meta_keywords = db.Column(db.Text)
    
    # Relationships
    tags = db.relationship('Tag', secondary='article_tags', back_populates='articles')
    
    def __repr__(self):
        return f'<Article {self.title}>'
    
    def render_html(self) -> str:
        """Convert content to HTML based on content type"""
        if self.content_type == 'editorjs' and self.content_json:
            from services.content_converter import EditorJSConverter
            converter = EditorJSConverter()
            return converter.to_html(self.content_json)
        elif self.content_type == 'markdown' and self.content_markdown:
            md = markdown.Markdown(extensions=[
                'markdown.extensions.fenced_code',
                'markdown.extensions.codehilite',
                'markdown.extensions.toc',
                'markdown.extensions.tables'
            ])
            return md.convert(self.content_markdown)
        return ''
    
    def get_content_data(self) -> Dict[str, Any]:
        """Get content data for editor"""
        if self.content_type == 'editorjs':
            return self.content_json or {'blocks': [], 'version': '2.28.2'}
        return {
            'blocks': [
                {
                    'type': 'paragraph',
                    'data': {'text': self.content_markdown or ''}
                }
            ],
            'version': '2.28.2'
        }
    
    def set_content_from_editorjs(self, data: Dict[str, Any]):
        """Set content from EditorJS data"""
        self.content_type = 'editorjs'
        self.content_json = data
        self.content_markdown = None
        
        # Auto-generate excerpt from first paragraph
        if not self.excerpt and data.get('blocks'):
            for block in data['blocks']:
                if block.get('type') == 'paragraph' and block.get('data', {}).get('text'):
                    self.excerpt = block['data']['text'][:200] + '...'
                    break
    
    def set_content_from_markdown(self, markdown_content: str):
        """Set content from Markdown"""
        self.content_type = 'markdown'
        self.content_markdown = markdown_content
        self.content_json = None
        
        # Auto-generate excerpt
        if not self.excerpt and markdown_content:
            lines = markdown_content.split('\n')
            for line in lines:
                if line.strip() and not line.startswith('#'):
                    self.excerpt = line[:200] + '...'
                    break
    
    def publish(self):
        """Publish the article"""
        self.status = 'published'
        self.published_at = datetime.utcnow()
    
    def unpublish(self):
        """Unpublish the article"""
        self.status = 'draft'
        self.published_at = None
    
    @property
    def is_published(self):
        return self.status == 'published'
    
    def to_dict(self, include_content=False) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        data = {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'subtitle': self.subtitle,
            'excerpt': self.excerpt,
            'reading_time': self.reading_time,
            'author': self.author,
            'status': self.status,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'content_type': self.content_type,
            'tags': [tag.name for tag in self.tags]
        }
        
        if include_content:
            data['content'] = self.get_content_data()
            data['html'] = self.render_html()
        
        return data


class Tag(db.Model):
    """Tag model for categorizing articles"""
    
    __tablename__ = 'tags'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    slug = db.Column(db.String(50), unique=True, nullable=False)
    color = db.Column(db.String(7), default='#6B7280')  # Hex color
    
    articles = db.relationship('Article', secondary='article_tags', back_populates='tags')
    
    def __repr__(self):
        return f'<Tag {self.name}>'


# Association table for many-to-many relationship
article_tags = db.Table('article_tags',
    db.Column('article_id', db.Integer, db.ForeignKey('articles.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True)
)