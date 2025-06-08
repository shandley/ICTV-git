"""
AI Classification Suggestions

Machine learning system to predict correct viral classifications and warn about
likely misclassifications based on historical patterns.
"""

import json
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import pickle
import warnings
from datetime import datetime

try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics import accuracy_score, precision_score, recall_score
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import LabelEncoder
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

try:
    import torch
    import torch.nn as nn
    HAS_TORCH = False  # Disable for now - would need proper setup
except ImportError:
    HAS_TORCH = False


@dataclass
class ClassificationPrediction:
    """Result of classification prediction"""
    suggested_family: str
    suggested_genus: Optional[str] = None
    confidence: float = 0.0
    alternative_families: List[Tuple[str, float]] = None
    warnings: List[str] = None
    stability_score: float = 1.0
    reasoning: str = ""
    
    def __post_init__(self):
        if self.alternative_families is None:
            self.alternative_families = []
        if self.warnings is None:
            self.warnings = []


@dataclass
class VirusFeatures:
    """Structured representation of virus features for ML"""
    genome_type: str = "unknown"
    genome_size: Optional[int] = None
    host_type: str = "unknown"
    morphology: str = "unknown"
    blast_top_hit: Optional[str] = None
    blast_similarity: float = 0.0
    discovery_year: Optional[int] = None
    geographic_origin: str = "unknown"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for ML processing"""
        return asdict(self)


class FamilyStabilityAnalyzer:
    """Analyze and predict family stability based on historical data"""
    
    def __init__(self, git_repo_path: str):
        self.git_repo_path = Path(git_repo_path)
        self.stability_scores = {}
        self.reclassification_patterns = {}
        self._load_historical_data()
    
    def _load_historical_data(self):
        """Load historical reclassification data"""
        try:
            # This would load from our stability analysis
            # For now, use example data
            self.stability_scores = {
                'Rhabdoviridae': 0.2,  # Very unstable
                'Picornaviridae': 0.3,  # Unstable
                'Siphoviridae': 0.0,   # Dissolved
                'Coronaviridae': 0.8,  # Stable
                'Virgaviridae': 0.9,   # Very stable
                'Retroviridae': 0.85   # Stable
            }
            
            self.reclassification_patterns = {
                'Siphoviridae': {
                    'dissolved': True,
                    'split_into': ['Drexlerviridae', 'Guelinviridae', 'Iobviridae'],
                    'common_reason': 'Phylogenetic incongruence'
                },
                'Rhabdoviridae': {
                    'common_changes': ['genus_splits', 'new_genera'],
                    'instability_cause': 'Rapid discovery of diverse species'
                }
            }
        except Exception as e:
            print(f"Warning: Could not load historical data: {e}")
    
    def get_family_stability(self, family_name: str) -> float:
        """Get stability score for a family (0-1, higher is more stable)"""
        return self.stability_scores.get(family_name, 0.5)  # Default to moderate
    
    def get_red_flags(self, family_name: str) -> List[str]:
        """Get warning flags for a family"""
        warnings = []
        
        stability = self.get_family_stability(family_name)
        
        if stability < 0.3:
            warnings.append(f"⚠️ {family_name} is highly unstable (stability: {stability:.1f})")
        
        if family_name in self.reclassification_patterns:
            pattern = self.reclassification_patterns[family_name]
            
            if pattern.get('dissolved'):
                warnings.append(f"⚠️ {family_name} was dissolved in recent reorganization")
            
            if 'common_changes' in pattern:
                changes = ', '.join(pattern['common_changes'])
                warnings.append(f"⚠️ {family_name} frequently undergoes: {changes}")
        
        return warnings


class GenomeFeatureExtractor:
    """Extract features from genome sequences and metadata"""
    
    def __init__(self):
        self.genome_type_patterns = {
            'dsDNA': ['double-stranded DNA', 'ds-DNA', 'dsDNA'],
            'ssDNA': ['single-stranded DNA', 'ss-DNA', 'ssDNA'],
            'dsRNA': ['double-stranded RNA', 'ds-RNA', 'dsRNA'],
            'ssRNA(+)': ['positive-sense RNA', 'ssRNA(+)', 'positive'],
            'ssRNA(-)': ['negative-sense RNA', 'ssRNA(-)', 'negative'],
        }
    
    def extract_features(self, 
                        genome_sequence: Optional[str] = None,
                        metadata: Dict[str, Any] = None) -> VirusFeatures:
        """Extract features from genome and metadata"""
        if metadata is None:
            metadata = {}
        
        features = VirusFeatures()
        
        # Extract genome type
        genome_comp = metadata.get('genome_composition', '')
        features.genome_type = self._classify_genome_type(genome_comp)
        
        # Extract genome size
        if genome_sequence:
            features.genome_size = len(genome_sequence)
        elif 'genome_size' in metadata:
            features.genome_size = self._parse_genome_size(metadata['genome_size'])
        
        # Extract host information
        features.host_type = self._classify_host(metadata.get('host', ''))
        
        # Extract other features
        features.morphology = metadata.get('morphology', 'unknown')
        features.discovery_year = metadata.get('discovery_year')
        features.geographic_origin = metadata.get('geographic_origin', 'unknown')
        
        return features
    
    def _classify_genome_type(self, genome_composition: str) -> str:
        """Classify genome type from composition string"""
        comp_lower = genome_composition.lower()
        
        for genome_type, patterns in self.genome_type_patterns.items():
            if any(pattern.lower() in comp_lower for pattern in patterns):
                return genome_type
        
        return 'unknown'
    
    def _parse_genome_size(self, size_str: str) -> Optional[int]:
        """Parse genome size from string like '29903 bp'"""
        try:
            # Extract numbers from string
            import re
            numbers = re.findall(r'\d+', str(size_str))
            if numbers:
                return int(numbers[0])
        except:
            pass
        return None
    
    def _classify_host(self, host_str: str) -> str:
        """Classify host type from host string"""
        host_lower = host_str.lower()
        
        if any(term in host_lower for term in ['human', 'homo sapiens', 'mammal']):
            return 'mammal'
        elif any(term in host_lower for term in ['plant', 'tobacco', 'wheat', 'rice']):
            return 'plant'
        elif any(term in host_lower for term in ['bacteria', 'escherichia', 'streptomyces']):
            return 'bacteria'
        elif any(term in host_lower for term in ['insect', 'drosophila', 'mosquito']):
            return 'insect'
        elif any(term in host_lower for term in ['bird', 'avian', 'chicken']):
            return 'bird'
        else:
            return 'unknown'


class ClassificationPredictor:
    """Machine learning model for classification prediction"""
    
    def __init__(self):
        self.model = None
        self.feature_vectorizer = None
        self.label_encoder = None
        self.is_trained = False
        
        if not HAS_SKLEARN:
            warnings.warn("scikit-learn not available, using rule-based fallback")
    
    def prepare_training_data(self, git_repo_path: str) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare training data from historical classifications"""
        # This would extract features from all species in the git repo
        # For now, create synthetic training data
        
        training_data = []
        training_labels = []
        
        # Example training patterns based on known virus families
        examples = [
            # Coronaviruses
            {'genome_type': 'ssRNA(+)', 'host_type': 'mammal', 'genome_size': 30000, 'label': 'Coronaviridae'},
            {'genome_type': 'ssRNA(+)', 'host_type': 'bird', 'genome_size': 27000, 'label': 'Coronaviridae'},
            
            # Rhabdoviruses  
            {'genome_type': 'ssRNA(-)', 'host_type': 'plant', 'genome_size': 12000, 'label': 'Rhabdoviridae'},
            {'genome_type': 'ssRNA(-)', 'host_type': 'mammal', 'genome_size': 11000, 'label': 'Rhabdoviridae'},
            
            # Picornaviruses
            {'genome_type': 'ssRNA(+)', 'host_type': 'mammal', 'genome_size': 7500, 'label': 'Picornaviridae'},
            {'genome_type': 'ssRNA(+)', 'host_type': 'insect', 'genome_size': 9000, 'label': 'Picornaviridae'},
            
            # Bacteriophages
            {'genome_type': 'dsDNA', 'host_type': 'bacteria', 'genome_size': 50000, 'label': 'Drexlerviridae'},
            {'genome_type': 'dsDNA', 'host_type': 'bacteria', 'genome_size': 170000, 'label': 'Myoviridae'},
        ]
        
        for example in examples:
            features = [
                example['genome_size'] or 0,
                hash(example['genome_type']) % 1000,  # Simple encoding
                hash(example['host_type']) % 1000
            ]
            training_data.append(features)
            training_labels.append(example['label'])
        
        return np.array(training_data), np.array(training_labels)
    
    def train(self, git_repo_path: str):
        """Train the classification model"""
        if not HAS_SKLEARN:
            print("Training skipped - scikit-learn not available")
            return
        
        X, y = self.prepare_training_data(git_repo_path)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train model
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"Model trained with accuracy: {accuracy:.2f}")
        self.is_trained = True
    
    def predict(self, features: VirusFeatures) -> ClassificationPrediction:
        """Predict classification for virus features"""
        if not self.is_trained or not HAS_SKLEARN:
            return self._rule_based_prediction(features)
        
        # Convert features to model input
        feature_vector = np.array([[
            features.genome_size or 0,
            hash(features.genome_type) % 1000,
            hash(features.host_type) % 1000
        ]])
        
        # Get prediction and confidence
        prediction = self.model.predict(feature_vector)[0]
        probabilities = self.model.predict_proba(feature_vector)[0]
        confidence = max(probabilities)
        
        # Get alternative predictions
        class_names = self.model.classes_
        alternatives = [(class_names[i], prob) for i, prob in enumerate(probabilities)]
        alternatives = sorted(alternatives, key=lambda x: x[1], reverse=True)[1:4]  # Top 3 alternatives
        
        return ClassificationPrediction(
            suggested_family=prediction,
            confidence=confidence,
            alternative_families=alternatives,
            reasoning=f"Predicted based on genome type: {features.genome_type}, host: {features.host_type}"
        )
    
    def _rule_based_prediction(self, features: VirusFeatures) -> ClassificationPrediction:
        """Fallback rule-based prediction when ML is not available"""
        # Simple rule-based classification
        family = "Unknown"
        confidence = 0.5
        reasoning = "Rule-based prediction"
        
        if features.genome_type == 'ssRNA(+)':
            if features.host_type == 'mammal' and features.genome_size and features.genome_size > 25000:
                family = "Coronaviridae"
                confidence = 0.7
                reasoning = "Large positive-sense RNA virus infecting mammals"
            elif features.genome_size and features.genome_size < 10000:
                family = "Picornaviridae"
                confidence = 0.6
                reasoning = "Small positive-sense RNA virus"
        
        elif features.genome_type == 'ssRNA(-)':
            if features.host_type in ['plant', 'mammal']:
                family = "Rhabdoviridae"
                confidence = 0.6
                reasoning = "Negative-sense RNA virus"
        
        elif features.genome_type == 'dsDNA':
            if features.host_type == 'bacteria':
                if features.genome_size and features.genome_size > 100000:
                    family = "Myoviridae"
                    confidence = 0.5
                    reasoning = "Large DNA bacteriophage"
                else:
                    family = "Drexlerviridae"
                    confidence = 0.5
                    reasoning = "DNA bacteriophage"
        
        return ClassificationPrediction(
            suggested_family=family,
            confidence=confidence,
            reasoning=reasoning
        )


class ClassificationAI:
    """Main interface for AI-powered classification suggestions"""
    
    def __init__(self, git_repo_path: str):
        self.git_repo_path = git_repo_path
        self.feature_extractor = GenomeFeatureExtractor()
        self.stability_analyzer = FamilyStabilityAnalyzer(git_repo_path)
        self.predictor = ClassificationPredictor()
        
        # Train model if data available
        try:
            self.predictor.train(git_repo_path)
        except Exception as e:
            print(f"Model training failed: {e}, using rule-based fallback")
    
    def suggest_classification(self,
                             genome_sequence: Optional[str] = None,
                             metadata: Dict[str, Any] = None,
                             blast_results: Optional[pd.DataFrame] = None) -> ClassificationPrediction:
        """
        Suggest classification for a new virus
        
        Args:
            genome_sequence: Viral genome sequence (optional)
            metadata: Dictionary with virus metadata
            blast_results: BLAST search results (optional)
        
        Returns:
            ClassificationPrediction with suggestions and warnings
        """
        if metadata is None:
            metadata = {}
        
        # Extract features
        features = self.feature_extractor.extract_features(genome_sequence, metadata)
        
        # Add BLAST information if available
        if blast_results is not None and not blast_results.empty:
            top_hit = blast_results.iloc[0]
            features.blast_top_hit = top_hit.get('subject_id', '')
            features.blast_similarity = top_hit.get('percent_identity', 0.0) / 100.0
        
        # Get prediction
        prediction = self.predictor.predict(features)
        
        # Add stability analysis
        prediction.stability_score = self.stability_analyzer.get_family_stability(prediction.suggested_family)
        
        # Add warnings
        family_warnings = self.stability_analyzer.get_red_flags(prediction.suggested_family)
        prediction.warnings.extend(family_warnings)
        
        # Add confidence-based warnings
        if prediction.confidence < 0.6:
            prediction.warnings.append("⚠️ Low confidence prediction - consider getting more data")
        
        if features.blast_similarity > 0 and features.blast_similarity < 0.7:
            prediction.warnings.append("⚠️ Low sequence similarity to known viruses - novel family possible")
        
        return prediction
    
    def batch_predict(self, virus_list: List[Dict[str, Any]]) -> List[ClassificationPrediction]:
        """Predict classifications for multiple viruses"""
        results = []
        
        for virus_data in virus_list:
            prediction = self.suggest_classification(
                genome_sequence=virus_data.get('genome_sequence'),
                metadata=virus_data.get('metadata', {}),
                blast_results=virus_data.get('blast_results')
            )
            results.append(prediction)
        
        return results
    
    def save_model(self, filepath: str):
        """Save trained model to file"""
        if self.predictor.is_trained:
            with open(filepath, 'wb') as f:
                pickle.dump(self.predictor, f)
    
    def load_model(self, filepath: str):
        """Load trained model from file"""
        with open(filepath, 'rb') as f:
            self.predictor = pickle.load(f)


# For testing
if __name__ == "__main__":
    # Test the classification AI
    ai = ClassificationAI("output/git_taxonomy")
    
    # Test virus
    test_virus = {
        'genome_composition': 'ssRNA(+)',
        'host': 'Homo sapiens',
        'genome_size': '29903 bp',
        'discovery_year': 2020
    }
    
    prediction = ai.suggest_classification(metadata=test_virus)
    
    print(f"Suggested family: {prediction.suggested_family}")
    print(f"Confidence: {prediction.confidence:.2f}")
    print(f"Stability score: {prediction.stability_score:.2f}")
    print(f"Reasoning: {prediction.reasoning}")
    
    if prediction.warnings:
        print("Warnings:")
        for warning in prediction.warnings:
            print(f"  {warning}")