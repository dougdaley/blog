#!/usr/bin/env python
"""
Database initialization script
Creates the database tables and optionally adds sample data
"""

import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app_new import create_app
from models.article import db, Article, Tag
from models.business import BusinessProcess, Control, Role, MaturityAssessment
from models.navigation import NavigationItem
from datetime import datetime


def init_database():
    """Initialize the database with tables"""
    app = create_app()
    
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("Database tables created successfully!")
        
        # Check if we should add sample data
        existing_articles = Article.query.count()
        if existing_articles == 0:
            print("Adding sample data...")
            create_sample_data()
            print("Sample data added!")
        else:
            print(f"Database already has {existing_articles} articles. Skipping sample data.")


def create_sample_data():
    """Create sample articles and business data"""
    
    # Sample article with EditorJS content
    sample_editorjs_content = {
        "time": int(datetime.now().timestamp() * 1000),
        "blocks": [
            {
                "type": "header",
                "data": {
                    "text": "Welcome to the Enhanced Blog System",
                    "level": 1
                }
            },
            {
                "type": "paragraph",
                "data": {
                    "text": "This is a demonstration of the new <b>EditorJS-powered content management system</b>. You can now create rich, structured content with ease."
                }
            },
            {
                "type": "header",
                "data": {
                    "text": "Key Features",
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
                        "Database-backed content storage",
                        "Backward compatibility with existing markdown",
                        "Sophisticated literary design maintained"
                    ]
                }
            },
            {
                "type": "quote",
                "data": {
                    "text": "The best content management systems are invisible to the content creator, allowing them to focus entirely on their ideas and words.",
                    "caption": "Design Philosophy"
                }
            },
            {
                "type": "delimiter",
                "data": {}
            },
            {
                "type": "paragraph",
                "data": {
                    "text": "This system maintains the sophisticated, literary aesthetic you're familiar with while providing modern content creation tools."
                }
            }
        ],
        "version": "2.28.2"
    }
    
    article1 = Article(
        title="Welcome to the Enhanced Blog System",
        slug="welcome-enhanced-blog",
        subtitle="Introducing EditorJS integration with sophisticated design",
        excerpt="A comprehensive overview of the new content management capabilities.",
        author="System",
        reading_time="5 min read",
        status="published",
        section="blog"
    )
    article1.set_content_from_editorjs(sample_editorjs_content)
    article1.publish()
    
    # Sample markdown article for backward compatibility
    sample_markdown = """# Traditional Markdown Support

This article demonstrates that the system maintains full backward compatibility with existing **Markdown content**.

## Features Still Work

- *Italic* and **bold** text
- `inline code` and code blocks
- Lists and other formatting

```python
def hello_world():
    print("Markdown code blocks work perfectly!")
```

The system seamlessly handles both EditorJS and Markdown content, converting both to beautiful HTML output."""
    
    article2 = Article(
        title="Markdown Compatibility Demo",
        slug="markdown-compatibility",
        subtitle="Demonstrating backward compatibility",
        excerpt="See how existing markdown content continues to work perfectly.",
        author="System",
        reading_time="3 min read",
        status="published",
        section="blog"
    )
    article2.set_content_from_markdown(sample_markdown)
    article2.publish()
    
    # Draft article to show the editing workflow
    article3 = Article(
        title="Draft Article Example",
        slug="draft-example",
        subtitle="This is a work in progress",
        excerpt="An example of a draft article in the system.",
        author="Editor",
        reading_time="2 min read",
        status="draft",
        section="blog"
    )
    
    draft_content = {
        "time": int(datetime.now().timestamp() * 1000),
        "blocks": [
            {
                "type": "paragraph",
                "data": {
                    "text": "This is a draft article that demonstrates the workflow for content creation. It won't appear on the public site until published."
                }
            },
            {
                "type": "header",
                "data": {
                    "text": "Writing Process",
                    "level": 2
                }
            },
            {
                "type": "paragraph",
                "data": {
                    "text": "The admin interface provides a sophisticated editing experience with:"
                }
            },
            {
                "type": "list",
                "data": {
                    "style": "unordered",
                    "items": [
                        "Auto-save functionality",
                        "Rich text editing",
                        "SEO optimization fields",
                        "Publishing workflow"
                    ]
                }
            }
        ],
        "version": "2.28.2"
    }
    
    article3.set_content_from_editorjs(draft_content)
    
    # Add all articles to the session
    db.session.add_all([article1, article2, article3])
    
    # Sample tags
    tags = [
        Tag(name="Technology", slug="technology", color="#3b82f6"),
        Tag(name="Content Management", slug="content-management", color="#10b981"),
        Tag(name="EditorJS", slug="editorjs", color="#8b5cf6"),
        Tag(name="Flask", slug="flask", color="#f59e0b")
    ]
    
    db.session.add_all(tags)
    
    # Associate tags with articles
    article1.tags.extend([tags[0], tags[1], tags[2]])  # Technology, Content Management, EditorJS
    article2.tags.extend([tags[0], tags[3]])  # Technology, Flask
    
    # Sample business process
    process = BusinessProcess(
        name="Content Publishing Workflow",
        slug="content-publishing-workflow",
        description="The process for creating, reviewing, and publishing content in the CMS",
        process_owner="Content Manager",
        department="Marketing",
        frequency="as-needed",
        estimated_time="30-60 minutes",
        steps=[
            {
                "step": 1,
                "title": "Content Creation",
                "description": "Author creates content using the EditorJS interface",
                "responsible": "Content Author"
            },
            {
                "step": 2,
                "title": "Review and Edit",
                "description": "Content is reviewed for quality and accuracy",
                "responsible": "Editor"
            },
            {
                "step": 3,
                "title": "SEO Optimization",
                "description": "Meta tags and SEO elements are optimized",
                "responsible": "SEO Specialist"
            },
            {
                "step": 4,
                "title": "Publication",
                "description": "Content is published and promoted",
                "responsible": "Content Manager"
            }
        ],
        status="active"
    )
    
    # Sample control
    control = Control(
        control_id="CONT-001",
        name="Content Review Control",
        description="All published content must be reviewed by an editor before publication",
        control_type="preventive",
        control_category="manual",
        risk_rating="medium",
        control_procedure="Editor reviews content for accuracy, grammar, and brand compliance",
        testing_procedure="Monthly review of published content to ensure compliance",
        frequency="per-article",
        responsible_party="Content Editor",
        evidence_required=[
            {
                "type": "approval",
                "description": "Editor approval in CMS",
                "retention": "2 years"
            }
        ],
        status="active",
        compliance_status="compliant"
    )
    
    # Sample role
    role = Role(
        name="Content Editor",
        slug="content-editor",
        title="Senior Content Editor",
        department="Marketing",
        summary="Responsible for reviewing and editing all published content",
        responsibilities=[
            {
                "category": "Content Review",
                "items": [
                    "Review articles for accuracy and quality",
                    "Ensure brand voice consistency",
                    "Optimize content for SEO"
                ]
            },
            {
                "category": "Workflow Management",
                "items": [
                    "Manage content publication schedule",
                    "Coordinate with authors and stakeholders"
                ]
            }
        ],
        required_skills=[
            {"skill": "Content Writing", "level": "Expert", "required": True},
            {"skill": "SEO", "level": "Intermediate", "required": True},
            {"skill": "Project Management", "level": "Intermediate", "required": False}
        ],
        employment_type="full-time",
        location="Remote",
        status="active"
    )
    
    db.session.add_all([process, control, role])
    
    # Commit all changes
    db.session.commit()

    # Seed navigation if empty
    if NavigationItem.query.count() == 0:
        navigation_items = [
            NavigationItem(label="Home", slug="home", section="home", position=0),
            NavigationItem(label="Articles", slug="articles", section="blog", position=1),
            NavigationItem(label="The TOM Method", slug="tom-method", section="tom_method", position=2),
            NavigationItem(label="Portfolio", slug="portfolio", section="portfolio", position=3),
        ]
        db.session.add_all(navigation_items)
        db.session.commit()
    print("Sample data creation completed!")


if __name__ == "__main__":
    init_database()
