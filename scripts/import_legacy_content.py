"""One-off importer that migrates legacy markdown/JSON content into the database."""

import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path

import yaml
import markdown

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app_new import create_app
from models.article import db, Article


MARKDOWN_CONVERTER = markdown.Markdown(extensions=['extra', 'sane_lists'])


def slugify(value: str) -> str:
    return re.sub(r'[^a-z0-9-]+', '-', value.lower()).strip('-')


def markdown_to_html(text: str) -> str:
    html = MARKDOWN_CONVERTER.convert(text)
    MARKDOWN_CONVERTER.reset()
    if html.startswith('<p>') and html.endswith('</p>'):
        html = html[3:-4]
    return html


def markdown_to_editorjs(markdown_text: str) -> dict:
    blocks = []
    lines = markdown_text.splitlines()
    i = 0

    def collect_paragraph(start_index):
        buffer = []
        idx = start_index
        while idx < len(lines):
            current = lines[idx]
            if not current.strip():
                break
            if re.match(r'^(#{1,6})\s+', current) or current.startswith('```') or re.match(r'^[-*]\s+', current) or re.match(r'^\d+\.\s+', current):
                break
            buffer.append(current)
            idx += 1
        html = markdown_to_html('\n'.join(buffer).strip())
        if html:
            blocks.append({'type': 'paragraph', 'data': {'text': html}})
        return idx

    while i < len(lines):
        line = lines[i].rstrip()
        if not line.strip():
            i += 1
            continue

        if line.startswith('```'):
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].startswith('```'):
                code_lines.append(lines[i])
                i += 1
            blocks.append({'type': 'code', 'data': {'code': '\n'.join(code_lines)}})
            i += 1  # skip closing ```
            continue

        heading_match = re.match(r'^(#{1,6})\s+(.*)', line)
        if heading_match:
            level = len(heading_match.group(1))
            text = heading_match.group(2).strip()
            blocks.append({'type': 'header', 'data': {'text': text, 'level': level}})
            i += 1
            continue

        list_match = re.match(r'^([-*])\s+(.*)', line)
        ordered_match = re.match(r'^(\d+)\.\s+(.*)', line)
        if list_match or ordered_match:
            is_ordered = bool(ordered_match)
            items = []
            pattern = r'^([-*])\s+(.*)' if not is_ordered else r'^(\d+)\.\s+(.*)'
            while i < len(lines):
                current = lines[i]
                match = re.match(pattern, current)
                if not match:
                    break
                items.append(markdown_to_html(match.group(2).strip()))
                i += 1
            blocks.append({'type': 'list', 'data': {'style': 'ordered' if is_ordered else 'unordered', 'items': items}})
            continue

        i = collect_paragraph(i)

    return {
        'time': int(time.time() * 1000),
        'blocks': blocks,
        'version': '2.28.2'
    }


def upsert_article(slug: str, defaults: dict, editorjs_content: dict):
    article = Article.query.filter_by(slug=slug).first()
    if not article:
        article = Article(slug=slug)
        db.session.add(article)

    for key, value in defaults.items():
        setattr(article, key, value)

    article.set_content_from_editorjs(editorjs_content)
    if defaults.get('status') == 'published' and not article.published_at:
        article.publish()
    return article


def import_blog(content_root: Path):
    index_path = content_root / 'blog' / 'index.yaml'
    if not index_path.exists():
        return

    posts = yaml.safe_load(index_path.read_text(encoding='utf-8')) or []
    for entry in posts:
        filename = entry.get('filename')
        if not filename:
            continue
        post_path = content_root / 'blog' / filename
        if not post_path.exists():
            continue

        markdown_body = post_path.read_text(encoding='utf-8')
        editorjs = markdown_to_editorjs(markdown_body)
        slug = slugify(entry.get('slug') or filename.replace('.md', ''))
        title = entry.get('title') or slug.replace('-', ' ').title()
        excerpt = entry.get('excerpt')
        if not excerpt and editorjs['blocks']:
            first_block = editorjs['blocks'][0]
            if first_block['type'] == 'paragraph':
                excerpt = re.sub('<[^<]+?>', '', first_block['data']['text'])[:200]

        published_at = None
        if entry.get('date'):
            try:
                published_at = datetime.fromisoformat(entry['date'])
            except ValueError:
                pass

        defaults = {
            'title': title,
            'subtitle': entry.get('subtitle', ''),
            'excerpt': excerpt,
            'author': entry.get('author', ''),
            'reading_time': entry.get('reading_time', ''),
            'section': 'blog',
            'status': 'published'
        }

        article = upsert_article(slug, defaults, editorjs)
        if published_at:
            article.published_at = published_at


def import_portfolio(content_root: Path):
    index_path = content_root / 'projects' / 'index.yaml'
    if not index_path.exists():
        return

    projects = yaml.safe_load(index_path.read_text(encoding='utf-8')) or []
    for entry in projects:
        name = entry.get('name')
        if not name:
            continue
        slug = slugify(entry.get('slug') or name)
        description = entry.get('description', '')
        url = entry.get('url', '')

        blocks = [
            {'type': 'header', 'data': {'text': name, 'level': 2}},
            {'type': 'paragraph', 'data': {'text': markdown_to_html(description) if description else ''}}
        ]
        if url:
            blocks.append({'type': 'paragraph', 'data': {'text': f'<a href="{url}" target="_blank" rel="noopener">Project URL</a>'}})

        editorjs = {
            'time': int(time.time() * 1000),
            'blocks': blocks,
            'version': '2.28.2'
        }

        defaults = {
            'title': name,
            'excerpt': description,
            'section': 'portfolio',
            'status': 'published',
            'meta_description': description,
        }

        article = upsert_article(slug, defaults, editorjs)
        article.reading_time = entry.get('reading_time') or ''
        article.subsection = entry.get('category')


def parse_tom_index(md_path: Path):
    raw = md_path.read_text(encoding='utf-8')
    if raw.startswith('---'):
        _, frontmatter, body = raw.split('---', 2)
        metadata = yaml.safe_load(frontmatter) or {}
    else:
        metadata, body = {}, raw

    sections = body.split('\n## ')
    intro_section = sections[0]
    remaining = sections[1:]

    if remaining:
        intro_section = intro_section + '\n## ' + remaining[0]
        remaining = remaining[1:]

    intro_content = intro_section.strip()
    guiding_content = ''
    chapter_sections = []

    for section in remaining:
        if section.lower().startswith('guiding principles'):
            guiding_content = section
            continue
        chapter_sections.append(section)

    chapters = []
    chapter_heading_pattern = re.compile(r'^chapter\s+([ivx]+):\s+(.*)$', re.IGNORECASE)
    for chunk in chapter_sections:
        lines = [line for line in chunk.splitlines() if line.strip()]
        if not lines:
            continue
        while lines and lines[0].strip().lower() in {'the method'}:
            lines.pop(0)
        if not lines:
            continue
        heading_match = chapter_heading_pattern.match(lines[0].strip())
        if not heading_match:
            continue
        number = heading_match.group(1).upper()
        title = heading_match.group(2).strip()
        description = ''
        articles = []
        for line in lines[1:]:
            if line.strip().startswith('*') and not description:
                description = line.strip()
            elif line.strip().startswith('-'):
                link_text = line.strip('- ')
                link_match = re.match(r'\*\*\[([^\]]+)\]\(([^)]+)\)\*\*\s*-\s*([^*]+)(\*\(([^)]+)\)\*)?', link_text)
                if link_match:
                    article_title = link_match.group(1).strip()
                    path = link_match.group(2).strip()
                    description_text = link_match.group(3).strip()
                    reading = link_match.group(5).strip() if link_match.group(5) else ''
                    path_obj = Path(path)
                    slug = path_obj.name
                    chapter_folder = path_obj.parent.name
                    articles.append({
                        'title': article_title,
                        'slug': slug,
                        'description': description_text,
                        'reading_time': reading,
                        'chapter_folder': chapter_folder
                    })
                else:
                    articles.append({'title': link_text, 'slug': slugify(link_text), 'description': '', 'reading_time': '', 'chapter_folder': ''})

        chapters.append({
            'number': number,
            'title': title,
            'description': description,
            'articles': articles
        })

    return metadata, intro_content, guiding_content, chapters


def import_tom_method(content_root: Path):
    index_path = content_root / 'tom-method' / 'index.md'
    if not index_path.exists():
        return

    metadata, intro_content, guiding_content, chapters = parse_tom_index(index_path)

    intro_editorjs = markdown_to_editorjs(intro_content)
    hero_defaults = {
        'title': metadata.get('title', 'The Target Operating Model Method'),
        'subtitle': metadata.get('subtitle', ''),
        'section': 'tom_method',
        'subsection': 'hero',
        'featured_order': 1,
        'status': 'published'
    }
    upsert_article('tom-method-intro', hero_defaults, intro_editorjs)

    if guiding_content:
        guiding_editorjs = markdown_to_editorjs('## Guiding Principles\n' + guiding_content)
        guiding_defaults = {
            'title': 'Guiding Principles',
            'section': 'tom_method',
            'subsection': 'guiding',
            'featured_order': 2,
            'status': 'published'
        }
        upsert_article('tom-method-guiding-principles', guiding_defaults, guiding_editorjs)

    # Create chapter summary articles
    for order, chapter in enumerate(chapters, start=1):
        chapter_slug = chapter['articles'][0].get('chapter_folder') if chapter.get('articles') else None
        if not chapter_slug:
            chapter_slug = slugify(chapter['title'])
        description = chapter.get('description', '')
        editorjs = markdown_to_editorjs(description)
        defaults = {
            'title': chapter['title'],
            'excerpt': re.sub('<[^<]+?>', '', markdown_to_html(description)) if description else '',
            'section': 'tom_method',
            'subsection': 'chapter',
            'chapter_slug': chapter_slug,
            'featured_order': order,
            'status': 'published'
        }
        upsert_article(chapter_slug, defaults, editorjs)

    # Import article bodies from JSON files
    tom_root = content_root / 'tom-method'
    for chapter in chapters:
        chapter_slug = slugify(chapter['title'])
        chapter_dir = tom_root / chapter_slug
        if not chapter_dir.exists():
            continue

        for position, article_meta in enumerate(chapter['articles'], start=1):
            slug = article_meta['slug']
            folder = article_meta.get('chapter_folder') or chapter_slug
            json_file = tom_root / folder / f"{slug}.json"
            if not json_file.exists():
                continue

            data = json.loads(json_file.read_text(encoding='utf-8'))
            defaults = {
                'title': article_meta['title'] or slug.replace('-', ' ').title(),
                'excerpt': article_meta.get('description', ''),
                'reading_time': article_meta.get('reading_time', ''),
                'section': 'tom_method',
                'chapter_slug': folder,
                'chapter_order': position,
                'featured_order': position,
                'status': 'published'
            }
            upsert_article(slug, defaults, data)


def main():
    project_root = Path(__file__).resolve().parents[1]
    content_root = project_root / 'content'

    app = create_app('development')
    with app.app_context():
        import_blog(content_root)
        import_portfolio(content_root)
        import_tom_method(content_root)
        db.session.commit()


if __name__ == '__main__':
    main()
