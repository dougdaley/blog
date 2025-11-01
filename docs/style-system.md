# Style System Guide

This project aims for a clean, literary aesthetic that remains consistent across the public site and the admin editing experience. All layout and typography primitives are centralized to make it easy for both humans and AI agents to extend the system without breaking the visual language.

## File Anatomy

| File | Purpose |
| --- | --- |
| `static/css/style.css` | Global reset, home/portfolio layouts, and shared utility classes. |
| `static/css/article.css` | Long-form reading experience (typography, tables, article layout, TOC). Imported by both public and admin layouts. |
| `static/css/admin.css` | Admin-specific chrome (studio shell, toolbar, metadata cards). Relies on the shared article stylesheet for previews. |
| `templates/base.html` | Public layout that links the shared stylesheets. |
| `templates/admin/base.html` | Admin layout that imports the same shared CSS before layering on editor-specific styling. |

When adjusting the reading experience, change `article.css` so both the live pages and the editor preview stay in sync.

## Shared Article Layout

`article-shell` and `article-prose` live in `article.css` and drive the composition on `/blog/<slug>` and inside the admin preview.

```css
.article-shell {
    max-width: 1280px;
    margin: 0 auto;
    display: grid;            /* Desktop: article + toc grid */
    grid-template-columns: minmax(0, 1fr) 260px;
}

.article-prose {
    max-width: clamp(68ch, 72vw, 92ch);
    margin: 0 auto;           /* Centers the reading column */
}
```

- The right-aligned table-of-contents (`.article-toc`) is sticky on desktop and automatically collapses on screens below 1024 px.
- Breadcrumb navigation spans the grid by assigning it `grid-column: 1 / -1`.

## Typography System

The core typographic rhythm is defined in `article.css`:

- **Headings (`h1–h4`)** use the sans-serif stack (Inter) with tight letter-spacing and responsive clamp sizing.
- **Body copy (`p`, list items)** uses the serif stack (Charter) at 1.15 rem with 1.85 line height for comfortable reading.
- **Blockquotes** employ a subtle 2 px accent rule and increased margins to create breathing room.
- **Inline code / code blocks** leverage the shared mono stack with softened backgrounds and rounded rectangles.

If you add new text elements, follow this pattern:

1. Choose the appropriate type family (serif for flowing prose, sans for structural UI text).
2. Use rem units and `clamp()` for responsiveness.
3. Maintain generous vertical spacing (≥ 1.5 rem) to preserve the airy feel.

## Tables

Tables follow a literary, information-dense style with zero chrome:

- No shadows, rounded corners, or background fills.
- Collapsed borders with hairline row rules for legibility; no outer frame.
- Header uses a slightly stronger bottom rule only; no gradients.
- Normal-case headings with subtle letter-spacing (no shouty uppercase).
- Compact cell padding to increase data density while maintaining readability.

Key selectors to customize: `.article-prose table`, `.article-prose th`, and `.article-prose td`.

Example (kept in `static/css/article.css`):

```css
.article-prose table { border-collapse: collapse; background: transparent; border: none; }
.article-prose th, .article-prose td { border-bottom: 1px solid rgba(15,15,15,0.14); padding: 0.55rem 0.9rem; }
.article-prose th { border-bottom: 2px solid rgba(15,15,15,0.55); text-transform: none; }
```

Avoid zebra striping and hover shading so tables sit quietly in the flow of prose.

## Keeping Preview & Live in Sync

1. Any long-form styling lives in `static/css/article.css`.
2. Public layout (`templates/blog_post.html`) and admin preview (`templates/admin/article_edit.html`) both wrap article content with `article-prose`.
3. The admin preview updates in real time by reusing the same CSS classes. Avoid redefining typography in `admin.css`.

If you need editor-only visuals (e.g., toolbar adjustments), add them to `admin.css`. If the live article should mirror it, add to `article.css` instead.

## Extending Components

- **New block types** (e.g., callouts, pull quotes) should register their class names in `article.css` and be mirrored in the EditorJS converter (`services/content_converter.py`) so the markup matches the styling.
- **Images** already receive rounded corners and soft shadows. Wrap supplementary content in figure/figcaption to inherit this presentation.
- **TOC / sidebar content** should be placed inside `.article-toc`; use Tailwind utility classes sparingly, as the CSS files carry most of the styling burden.

## Best Practices

1. **Prefer shared CSS** over Tailwind utility classes for anything rendered in both admin and public views.
2. **Measure in ch/rem** instead of px for responsive, typographic scaling.
3. **Audit both contexts** (public page and admin preview) after changes to confirm parity.
4. **Document new patterns** here whenever you introduce a component or significant styling rule, so future contributors (human or AI) can find guidance quickly.

By keeping the article experience centralized and descriptive, future enhancements only require touching one stylesheet and both the live site and editing environment will remain in lockstep.
