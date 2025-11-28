"""
Relevance classification module using ML and heuristics.
"""
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
from pathlib import Path
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class RelevanceClassifier:
    """Classify section relevance using ML and heuristic scoring."""
    
    def __init__(self, model_dir: str = './models'):
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(exist_ok=True)
        
        self.model: Optional[RandomForestClassifier] = None
        self.scaler: Optional[StandardScaler] = None
        self.feature_names: List[str] = []
        self.trained = False
        
        # Load existing model if available
        self._load_model()
        
        # Feature weights for heuristic scoring
        self.feature_weights = {
            'word_count': 0.05,
            'digit_ratio': 0.15,
            'currency_count': 0.10,
            'percentage_count': 0.08,
            'number_count': 0.10,
            'date_count': 0.08,
            'entity_count': 0.12,
            'person_count': 0.05,
            'org_count': 0.05,
            'location_count': 0.03,
            'has_table': 0.15,
            'bullet_list_count': 0.08,
            'numbered_list_count': 0.08,
            'text_density': 0.05,
        }
    
    def score_section(self, features: Dict) -> float:
        """
        Score a section's relevance.
        
        Args:
            features: Dictionary of extracted features
            
        Returns:
            Relevance score between 0.0 and 1.0
        """
        if self.trained and self.model:
            return self._ml_score(features)
        else:
            return self._heuristic_score(features)
    
    def _heuristic_score(self, features: Dict) -> float:
        """Calculate relevance score using heuristics."""
        score = 0.0
        
        # Normalize and weight features
        for feature, weight in self.feature_weights.items():
            value = features.get(feature, 0)
            
            # Normalize different feature types
            if feature == 'word_count':
                # Optimal word count around 100-500
                normalized = min(value / 200.0, 1.0)
            elif feature == 'has_table':
                normalized = 1.0 if value else 0.0
            elif feature == 'text_density':
                # Prefer density between 0.6 and 0.9
                if 0.6 <= value <= 0.9:
                    normalized = 1.0
                else:
                    normalized = max(0, 1.0 - abs(value - 0.75) * 2)
            elif feature in ['digit_ratio']:
                # Already a ratio
                normalized = min(value * 5, 1.0)  # Scale up
            else:
                # Count-based features
                normalized = min(value / 5.0, 1.0)
            
            score += normalized * weight
        
        # Penalize very short sections
        if features.get('word_count', 0) < 20:
            score *= 0.3
        
        # Boost sections with multiple indicators
        indicator_count = sum([
            features.get('has_table', False),
            features.get('number_count', 0) > 3,
            features.get('entity_count', 0) > 2,
            features.get('bullet_list_count', 0) > 0,
            features.get('date_count', 0) > 0,
        ])
        
        if indicator_count >= 3:
            score *= 1.2
        
        # Clamp to [0, 1]
        return min(max(score, 0.0), 1.0)
    
    def _ml_score(self, features: Dict) -> float:
        """Calculate relevance score using trained ML model."""
        try:
            # Extract feature vector
            feature_vector = self._extract_feature_vector(features)
            
            # Scale features
            feature_vector_scaled = self.scaler.transform([feature_vector])
            
            # Predict probability
            proba = self.model.predict_proba(feature_vector_scaled)[0]
            
            # Return probability of relevant class (assuming 1 is relevant)
            return float(proba[1])
        except Exception as e:
            logger.warning(f"ML scoring failed, falling back to heuristics: {e}")
            return self._heuristic_score(features)
    
    def train(self, training_data: List[Dict]):
        """
        Train the classifier on labeled data.
        
        Args:
            training_data: List of dicts with 'features' and 'is_relevant' keys
        """
        if len(training_data) < 10:
            logger.warning("Insufficient training data. Need at least 10 examples.")
            return
        
        # Extract features and labels
        X = []
        y = []
        
        for sample in training_data:
            features = sample['features']
            label = 1 if sample['is_relevant'] else 0
            
            feature_vector = self._extract_feature_vector(features)
            X.append(feature_vector)
            y.append(label)
        
        X = np.array(X)
        y = np.array(y)
        
        # Initialize scaler and model
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            class_weight='balanced'
        )
        
        self.model.fit(X_scaled, y)
        self.trained = True
        
        # Save model
        self._save_model()
        
        logger.info(f"Model trained on {len(training_data)} examples")
    
    def add_feedback(self, features: Dict, is_relevant: bool):
        """
        Add a single feedback example for incremental learning.
        
        Args:
            features: Feature dictionary
            is_relevant: Whether the section is relevant
        """
        # Store feedback for batch retraining
        feedback_file = self.model_dir / 'feedback.joblib'
        
        try:
            if feedback_file.exists():
                feedback_data = joblib.load(feedback_file)
            else:
                feedback_data = []
            
            feedback_data.append({
                'features': features,
                'is_relevant': is_relevant
            })
            
            joblib.dump(feedback_data, feedback_file)
            
            # Retrain if we have enough new feedback
            if len(feedback_data) >= 10:
                self.train(feedback_data)
                # Clear feedback after training
                feedback_data = []
                joblib.dump(feedback_data, feedback_file)
        
        except Exception as e:
            logger.error(f"Error saving feedback: {e}")
    
    def _extract_feature_vector(self, features: Dict) -> List[float]:
        """Extract feature vector for ML model."""
        # Define feature order
        if not self.feature_names:
            self.feature_names = [
                'word_count', 'sentence_count', 'char_count', 'line_count',
                'digit_count', 'digit_ratio', 'currency_count', 'percentage_count',
                'number_count', 'date_count', 'email_count', 'url_count',
                'phone_count', 'has_table', 'bullet_list_count', 'numbered_list_count',
                'text_density', 'entity_count', 'person_count', 'org_count',
                'location_count', 'money_count', 'date_entity_count',
                'avg_word_length', 'avg_sentence_length'
            ]
        
        vector = []
        for name in self.feature_names:
            value = features.get(name, 0)
            # Convert boolean to int
            if isinstance(value, bool):
                value = 1 if value else 0
            vector.append(float(value))
        
        return vector
    
    def _save_model(self):
        """Save trained model to disk."""
        if not self.trained:
            return
        
        try:
            model_file = self.model_dir / 'relevance_model.joblib'
            scaler_file = self.model_dir / 'scaler.joblib'
            
            joblib.dump(self.model, model_file)
            joblib.dump(self.scaler, scaler_file)
            
            logger.info(f"Model saved to {model_file}")
        except Exception as e:
            logger.error(f"Error saving model: {e}")
    
    def _load_model(self):
        """Load trained model from disk."""
        model_file = self.model_dir / 'relevance_model.joblib'
        scaler_file = self.model_dir / 'scaler.joblib'
        
        if model_file.exists() and scaler_file.exists():
            try:
                self.model = joblib.load(model_file)
                self.scaler = joblib.load(scaler_file)
                self.trained = True
                logger.info("Loaded existing model")
            except Exception as e:
                logger.error(f"Error loading model: {e}")
                self.trained = False
