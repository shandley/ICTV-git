"""
Configuration Settings for ICTV Interactive Dashboard

Default parameters, themes, and application settings.
"""

# Default risk factor weights (must sum to 1.0)
DEFAULT_RISK_WEIGHTS = {
    'size_factor': 0.30,        # Family size impact
    'growth_rate': 0.25,        # Species addition rate
    'host_breadth': 0.20,       # Host diversity impact
    'genome_complexity': 0.15,  # Genome diversity
    'phylogenetic_coherence': 0.10  # Phylogenetic consistency
}

# Default intervention thresholds (species counts)
DEFAULT_THRESHOLDS = {
    'review': 50,      # Trigger committee review
    'concern': 100,    # Structural concerns
    'crisis': 500      # Immediate intervention needed
}

# Risk category definitions
RISK_CATEGORIES = {
    'Low Risk': {
        'min_score': 0.0,
        'max_score': 3.0,
        'color': '#4caf50',
        'description': 'Stable family structure'
    },
    'Medium Risk': {
        'min_score': 3.0,
        'max_score': 5.0,
        'color': '#ffc107',
        'description': 'Monitor for changes'
    },
    'High Risk': {
        'min_score': 5.0,
        'max_score': 7.0,
        'color': '#ff9800',
        'description': 'Review and possible restructuring'
    },
    'Crisis': {
        'min_score': 7.0,
        'max_score': 10.0,
        'color': '#f44336',
        'description': 'Immediate intervention required'
    }
}

# Intervention type mapping
INTERVENTION_TYPES = {
    'Monitor': {
        'description': 'Regular observation',
        'urgency': 'Low',
        'estimated_effort': '1-2 committee hours',
        'color': '#4caf50'
    },
    'Review': {
        'description': 'Detailed assessment',
        'urgency': 'Medium',
        'estimated_effort': '4-8 committee hours',
        'color': '#ffc107'
    },
    'Split': {
        'description': 'Family reorganization',
        'urgency': 'High',
        'estimated_effort': '20-40 committee hours',
        'color': '#ff9800'
    },
    'Emergency': {
        'description': 'Immediate restructuring',
        'urgency': 'Critical',
        'estimated_effort': '40+ committee hours',
        'color': '#f44336'
    }
}

# Dashboard appearance settings
DASHBOARD_CONFIG = {
    'page_title': 'ICTV Family Risk Dashboard',
    'page_icon': '🦠',
    'layout': 'wide',
    'sidebar_state': 'expanded',
    'theme': {
        'primary_color': '#1f77b4',
        'background_color': '#ffffff',
        'secondary_background': '#f0f2f6',
        'text_color': '#262730'
    }
}

# Model configuration
MODEL_CONFIG = {
    'prediction_accuracy': 0.85,  # 85% accuracy from validation
    'confidence_threshold': 0.7,
    'forecast_horizon_years': 3,
    'update_frequency': 'quarterly'
}

# Export settings
EXPORT_CONFIG = {
    'formats': ['json', 'csv', 'pdf'],
    'include_metadata': True,
    'timestamp_format': '%Y-%m-%d_%H-%M-%S'
}

# API endpoints (for future integration)
API_CONFIG = {
    'base_url': 'http://localhost:8000',  # Future API integration
    'endpoints': {
        'families': '/api/families',
        'assessments': '/api/assessments',
        'interventions': '/api/interventions'
    }
}

# Performance settings
PERFORMANCE_CONFIG = {
    'cache_timeout': 300,  # 5 minutes
    'max_families': 1000,
    'chart_update_delay': 100,  # milliseconds
    'data_refresh_interval': 3600  # 1 hour
}

# Validation rules
VALIDATION_RULES = {
    'family_size': {
        'min': 1,
        'max': 10000,
        'type': 'integer'
    },
    'growth_rate': {
        'min': 0.0,
        'max': 2.0,  # 200% annual growth max
        'type': 'float'
    },
    'host_breadth': {
        'min': 1,
        'max': 100,
        'type': 'integer'
    },
    'genome_complexity': {
        'min': 0.0,
        'max': 1.0,
        'type': 'float'
    },
    'phylogenetic_coherence': {
        'min': 0.0,
        'max': 1.0,
        'type': 'float'
    }
}

# Help text for UI elements
HELP_TEXT = {
    'size_weight': "Impact of family size on instability risk. Larger families are harder to manage coherently.",
    'growth_weight': "Impact of rapid species addition on stability. Fast growth often indicates unclear boundaries.",
    'host_weight': "Impact of diverse host ranges on classification difficulty. More hosts = more complexity.",
    'complexity_weight': "Impact of genome diversity on family coherence. Higher diversity challenges classification.",
    'coherence_weight': "Impact of phylogenetic inconsistency. Poor phylogenetic support indicates classification problems.",
    'review_threshold': "Family size that triggers routine committee review and monitoring.",
    'concern_threshold': "Family size indicating potential structural problems requiring attention.",
    'crisis_threshold': "Family size requiring immediate intervention to prevent classification breakdown."
}

# Feature flags for phased rollout
FEATURE_FLAGS = {
    'real_time_updates': True,
    'parameter_adjustment': True,
    'family_comparison': True,
    'intervention_planning': False,  # Phase 2
    'historical_trends': False,     # Phase 2
    'automated_alerts': False,      # Phase 2
    'committee_workflow': False,    # Phase 2
    'api_integration': False        # Phase 3
}