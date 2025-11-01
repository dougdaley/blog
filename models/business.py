from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from typing import Dict, Any, List, Optional
from models.article import db

class BusinessProcess(db.Model):
    """Business Process model for structured business documentation"""
    
    __tablename__ = 'business_processes'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    description = db.Column(db.Text)
    
    # Process details
    process_owner = db.Column(db.String(100))
    department = db.Column(db.String(100))
    frequency = db.Column(db.String(50))  # daily, weekly, monthly, etc.
    estimated_time = db.Column(db.String(50))  # "2-4 hours", "30 minutes", etc.
    
    # Process steps (stored as JSON)
    steps = db.Column(db.JSON)  # [{"step": 1, "title": "...", "description": "...", "responsible": "..."}]
    
    # Dependencies and relationships
    inputs = db.Column(db.JSON)  # [{"name": "...", "source": "...", "format": "..."}]
    outputs = db.Column(db.JSON)  # [{"name": "...", "destination": "...", "format": "..."}]
    
    # Status and metadata
    status = db.Column(db.String(20), default='active')  # active, deprecated, draft
    version = db.Column(db.String(20), default='1.0')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    controls = db.relationship('Control', secondary='process_controls', back_populates='processes')
    roles = db.relationship('Role', secondary='process_roles', back_populates='processes')
    
    def __repr__(self):
        return f'<BusinessProcess {self.name}>'
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'process_owner': self.process_owner,
            'department': self.department,
            'frequency': self.frequency,
            'estimated_time': self.estimated_time,
            'steps': self.steps or [],
            'inputs': self.inputs or [],
            'outputs': self.outputs or [],
            'status': self.status,
            'version': self.version,
            'controls': [control.to_dict() for control in self.controls],
            'roles': [role.to_dict() for role in self.roles]
        }


class Control(db.Model):
    """Control model for risk management and compliance"""
    
    __tablename__ = 'controls'
    
    id = db.Column(db.Integer, primary_key=True)
    control_id = db.Column(db.String(50), unique=True, nullable=False)  # e.g., "CTRL-001"
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Control details
    control_type = db.Column(db.String(50))  # preventive, detective, corrective
    control_category = db.Column(db.String(50))  # manual, automated, hybrid
    risk_rating = db.Column(db.String(20))  # low, medium, high, critical
    
    # Implementation details
    control_procedure = db.Column(db.Text)
    testing_procedure = db.Column(db.Text)
    frequency = db.Column(db.String(50))
    responsible_party = db.Column(db.String(100))
    
    # Evidence and documentation
    evidence_required = db.Column(db.JSON)  # [{"type": "...", "description": "...", "retention": "..."}]
    documentation_links = db.Column(db.JSON)  # [{"title": "...", "url": "...", "type": "..."}]
    
    # Status and compliance
    status = db.Column(db.String(20), default='active')
    last_tested = db.Column(db.DateTime)
    next_test_due = db.Column(db.DateTime)
    compliance_status = db.Column(db.String(20), default='compliant')  # compliant, non-compliant, not_tested
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    processes = db.relationship('BusinessProcess', secondary='process_controls', back_populates='controls')
    
    def __repr__(self):
        return f'<Control {self.control_id}: {self.name}>'
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'control_id': self.control_id,
            'name': self.name,
            'description': self.description,
            'control_type': self.control_type,
            'control_category': self.control_category,
            'risk_rating': self.risk_rating,
            'control_procedure': self.control_procedure,
            'testing_procedure': self.testing_procedure,
            'frequency': self.frequency,
            'responsible_party': self.responsible_party,
            'evidence_required': self.evidence_required or [],
            'documentation_links': self.documentation_links or [],
            'status': self.status,
            'compliance_status': self.compliance_status,
            'last_tested': self.last_tested.isoformat() if self.last_tested else None,
            'next_test_due': self.next_test_due.isoformat() if self.next_test_due else None
        }


class Role(db.Model):
    """Role model for organizational roles and responsibilities"""
    
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    title = db.Column(db.String(150))
    department = db.Column(db.String(100))
    
    # Role details
    summary = db.Column(db.Text)
    responsibilities = db.Column(db.JSON)  # [{"category": "...", "items": [...]}]
    required_skills = db.Column(db.JSON)  # [{"skill": "...", "level": "...", "required": true/false}]
    preferred_qualifications = db.Column(db.JSON)  # [{"qualification": "...", "type": "..."}]
    
    # Reporting and relationships
    reports_to = db.Column(db.String(100))
    manages = db.Column(db.JSON)  # ["role1", "role2", ...]
    collaborates_with = db.Column(db.JSON)  # ["role1", "role2", ...]
    
    # Employment details
    employment_type = db.Column(db.String(50))  # full-time, part-time, contract, consultant
    location = db.Column(db.String(100))
    salary_range = db.Column(db.String(50))
    
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    processes = db.relationship('BusinessProcess', secondary='process_roles', back_populates='roles')
    
    def __repr__(self):
        return f'<Role {self.name}>'
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'title': self.title,
            'department': self.department,
            'summary': self.summary,
            'responsibilities': self.responsibilities or [],
            'required_skills': self.required_skills or [],
            'preferred_qualifications': self.preferred_qualifications or [],
            'reports_to': self.reports_to,
            'manages': self.manages or [],
            'collaborates_with': self.collaborates_with or [],
            'employment_type': self.employment_type,
            'location': self.location,
            'salary_range': self.salary_range,
            'status': self.status
        }


class MaturityAssessment(db.Model):
    """Maturity assessment model for capability evaluation"""
    
    __tablename__ = 'maturity_assessments'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    description = db.Column(db.Text)
    
    # Assessment framework
    framework = db.Column(db.String(100))  # e.g., "CMMI", "Custom", "ISO"
    version = db.Column(db.String(20), default='1.0')
    
    # Maturity levels and criteria
    levels = db.Column(db.JSON)  # [{"level": 1, "name": "...", "description": "...", "criteria": [...]}]
    domains = db.Column(db.JSON)  # [{"name": "...", "weight": 0.2, "criteria": [...]}]
    
    # Scoring configuration
    scoring_method = db.Column(db.String(50), default='weighted_average')
    max_score = db.Column(db.Integer, default=5)
    
    # Recommendations
    improvement_recommendations = db.Column(db.JSON)  # [{"level_from": 1, "level_to": 2, "recommendations": [...]}]
    
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<MaturityAssessment {self.name}>'
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'framework': self.framework,
            'version': self.version,
            'levels': self.levels or [],
            'domains': self.domains or [],
            'scoring_method': self.scoring_method,
            'max_score': self.max_score,
            'improvement_recommendations': self.improvement_recommendations or [],
            'status': self.status
        }


# Association tables
process_controls = db.Table('process_controls',
    db.Column('process_id', db.Integer, db.ForeignKey('business_processes.id'), primary_key=True),
    db.Column('control_id', db.Integer, db.ForeignKey('controls.id'), primary_key=True)
)

process_roles = db.Table('process_roles',
    db.Column('process_id', db.Integer, db.ForeignKey('business_processes.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True)
)