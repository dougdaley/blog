# Personal Website (Blog & Portfolio)

This is a Python Flask project for a personal website that serves as both a blog and a portfolio. Blog posts and project data are read from files stored in a GitHub repository.

## Features
- Homepage
- Blog section (reads posts from GitHub)
- Portfolio/projects section (reads project data from GitHub)

## Deployment
- Designed for easy deployment to PythonAnywhere or similar low-cost hosts.

---

## Setup Instructions
1. Clone this repository.
2. Create and activate a virtual environment: `uv venv && source .venv/bin/activate`
3. Install dependencies: `uv pip install flask requests PyYAML markdown`
4. Set up your GitHub data source (see below).
5. Run the Flask app: `python app.py`

## Data Source
- Blog posts and project data should be stored in a public GitHub repository as markdown or JSON files.
- The Flask app will fetch and render this data.

## Deployment
- See the end of this README for PythonAnywhere deployment instructions.
