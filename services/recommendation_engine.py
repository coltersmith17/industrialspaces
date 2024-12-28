import numpy as np
from sklearn.preprocessing import MinMaxScaler
from typing import List, Dict
from models import Property, BusinessTypePreference

class PropertyRecommendationEngine:
    def __init__(self):
        self.scaler = MinMaxScaler()

    def _calculate_feature_vector(self, property: Property) -> np.ndarray:
        """Convert property features to a numerical vector for comparison"""
        features = [
            float(property.square_feet),
            float(property.ceiling_height or 0),
            float(property.loading_docks or 0),
            float(property.year_built or 0)
        ]
        return np.array(features).reshape(1, -1)

    def _calculate_preference_vector(self, preference: BusinessTypePreference) -> np.ndarray:
        """Convert business preferences to a numerical vector"""
        features = [
            float(preference.min_square_feet or 0),
            float(preference.min_ceiling_height or 0),
            float(preference.min_loading_docks or 0),
            2024  # Current year as reference for building age
        ]
        return np.array(features).reshape(1, -1)

    def calculate_match_score(self, property: Property, preference: BusinessTypePreference) -> float:
        """Calculate how well a property matches business preferences"""
        if not preference:
            return 0.0

        property_vector = self._calculate_feature_vector(property)
        preference_vector = self._calculate_preference_vector(preference)

        # Scale features to [0,1] range
        scaled_features = self.scaler.fit_transform(
            np.vstack([property_vector, preference_vector])
        )

        # Calculate Euclidean distance and convert to similarity score
        distance = np.linalg.norm(scaled_features[0] - scaled_features[1])
        similarity = 1 / (1 + distance)

        # Apply business type bonus if matching
        if property.business_type == preference.business_type:
            similarity *= 1.2

        return float(similarity)

    def get_recommendations(
        self,
        properties: List[Property],
        business_type: str,
        min_square_feet: int = None,
        max_square_feet: int = None
    ) -> List[Dict]:
        """Get property recommendations based on business type and requirements"""
        # Convert None to 0 for min_square_feet and a large number for max_square_feet
        min_square_feet = min_square_feet or 0
        max_square_feet = max_square_feet or float('inf')

        preference = BusinessTypePreference.query.filter_by(
            business_type=business_type
        ).first()

        if not preference:
            preference = BusinessTypePreference(
                business_type=business_type,
                min_square_feet=min_square_feet,
                max_square_feet=max_square_feet
            )

        recommendations = []
        for property in properties:
            # Filter by square footage if specified
            if property.square_feet < min_square_feet:
                continue
            if property.square_feet > max_square_feet:
                continue

            score = self.calculate_match_score(property, preference)
            recommendations.append({
                'property': property,
                'score': score
            })

        # Sort by score descending
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        return recommendations