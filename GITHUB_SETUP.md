# GitHub Repository Setup

To use this website, you'll need to create a GitHub repository with your blog content. Here's the structure your repository should have:

## Repository Structure

```
your-blog-repo/
├── content/
│   ├── blog/
│   │   ├── index.yaml
│   │   ├── my-first-post.md
│   │   └── another-post.md
│   └── projects/
│       └── index.yaml
```

## Blog Setup

### 1. Create `content/blog/index.yaml`

```yaml
- title: "My First Blog Post"
  filename: "my-first-post.md"
  date: "2024-01-15"
  excerpt: "This is a short description of my first blog post."

- title: "Another Great Post"
  filename: "another-post.md"
  date: "2024-01-20"
```

### 2. Create blog post files (e.g., `content/blog/my-first-post.md`)

You can use frontmatter in your markdown files:

```markdown
---
title: "My First Blog Post"
date: "2024-01-15"
excerpt: "A short description that will appear on the blog listing page"
---

# My First Blog Post

This is the content of my blog post written in **markdown**.

## Subheading

- List item 1
- List item 2

```python
def hello_world():
    print("Hello, world!")
```

More content here...
```

## Portfolio Setup

### Create `content/projects/index.yaml`

```yaml
- name: "Personal Website"
  description: "A clean, minimalist personal website built with Flask"
  url: "https://yourwebsite.com"
  github: "https://github.com/yourusername/website"

- name: "Task Manager App"
  description: "A productivity app built with React and Node.js"
  github: "https://github.com/yourusername/task-manager"
```

## Configuration

Update the GitHub configuration in `app.py`:

```python
GITHUB_USER = 'your-github-username'
GITHUB_REPO = 'your-blog-repo-name'
```

## Next Steps

1. Create a public GitHub repository
2. Add the content structure above
3. Update `app.py` with your repository details
4. Deploy to PythonAnywhere or your preferred host

Your website will automatically fetch and display content from your GitHub repository!