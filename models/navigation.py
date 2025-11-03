from datetime import datetime

from models.article import db


class NavigationItem(db.Model):
    """Configurable top-level navigation item"""

    __tablename__ = 'navigation_items'

    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(120), unique=True, index=True)
    url = db.Column(db.String(255))
    section = db.Column(db.String(50), index=True)  # e.g., blog, tom_method, portfolio
    is_external = db.Column(db.Boolean, default=False)
    is_visible = db.Column(db.Boolean, default=True)
    position = db.Column(db.Integer, default=0, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<NavigationItem {self.label}>'

    def effective_url(self):
        """Determine the URL to use when rendering the nav item."""
        if self.url:
            return self.url
        if self.section:
            return self._section_to_url(self.section)
        return '#'

    @staticmethod
    def _section_to_url(section):
        mapping = {
            'home': '/',
            'blog': '/blog',
            'tom_method': '/tom-method',
            'portfolio': '/portfolio',
        }
        return mapping.get(section, '/')

    def to_dict(self):
        return {
            'id': self.id,
            'label': self.label,
            'slug': self.slug,
            'url': self.url,
            'section': self.section,
            'is_external': self.is_external,
            'is_visible': self.is_visible,
            'position': self.position,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
