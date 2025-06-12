#!/usr/bin/env python3
"""
AI Model Size Analysis - Data Extraction Script

This script extracts AI model data for size vs. year analysis with domain differentiation.
It generates a scatter plot dataset where:
- X-axis: Model release year
- Y-axis: Model parameter count (trainable parameters)
- Series: Domain (for color differentiation)
"""

import json
import logging
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelSizeExtractor:
    """Extract model size and year data for visualization."""

    def __init__(self, db_path: str):
        """Initialize with database path."""
        self.db_path = db_path
        try:
            self.conn = sqlite3.connect(db_path)
            self.conn.row_factory = sqlite3.Row
            logger.info(f"Connected to database: {db_path}")
        except sqlite3.Error as e:
            logger.error(f"Failed to connect to database: {e}")
            raise

    def __del__(self):
        """Close database connection."""
        if hasattr(self, "conn"):
            self.conn.close()

    def extract_model_data(self) -> List[Dict[str, Any]]:
        """Extract model data with year, parameters, and domain."""
        query = """
        SELECT 
            model,
            organization,
            publication_date,
            parameters,
            domain,
            frontier_model,
            notability_criteria
        FROM ai_models 
        WHERE parameters IS NOT NULL 
          AND publication_date IS NOT NULL
          AND parameters > 0
        ORDER BY publication_date ASC
        """
        
        cursor = self.conn.cursor()
        cursor.execute(query)
        raw_data = [dict(row) for row in cursor.fetchall()]
        
        logger.info(f"Extracted {len(raw_data)} models with parameter and date information")
        
        # Process the data
        processed_data = []
        for row in raw_data:
            try:
                # Extract year from publication_date
                pub_date = row['publication_date']
                if pub_date:
                    if isinstance(pub_date, str):
                        # Handle different date formats
                        try:
                            if len(pub_date) == 4:  # Just year
                                year = int(pub_date)
                            else:
                                # Try to parse full date
                                date_obj = datetime.strptime(pub_date[:10], '%Y-%m-%d')
                                year = date_obj.year
                        except ValueError:
                            logger.warning(f"Could not parse date '{pub_date}' for model {row['model']}")
                            continue
                    else:
                        # Assume it's already a datetime object
                        year = pub_date.year
                
                # Clean domain information
                domain = row['domain'] or 'Unknown'
                domain = domain.strip()
                
                # Group similar domains
                if 'language' in domain.lower() or 'nlp' in domain.lower() or 'text' in domain.lower():
                    domain_group = 'Language'
                elif 'vision' in domain.lower() or 'image' in domain.lower() or 'visual' in domain.lower():
                    domain_group = 'Vision'
                elif 'multimodal' in domain.lower() or 'multi-modal' in domain.lower():
                    domain_group = 'Multimodal'
                elif 'speech' in domain.lower() or 'audio' in domain.lower():
                    domain_group = 'Speech/Audio'
                elif 'code' in domain.lower() or 'programming' in domain.lower():
                    domain_group = 'Code'
                elif 'game' in domain.lower() or 'rl' in domain.lower() or 'reinforcement' in domain.lower():
                    domain_group = 'RL/Games'
                elif 'science' in domain.lower() or 'scientific' in domain.lower():
                    domain_group = 'Science'
                else:
                    domain_group = domain if domain != 'Unknown' else 'Other'
                
                processed_data.append({
                    'model_name': row['model'],
                    'organization': row['organization'],
                    'year': year,
                    'parameters': row['parameters'],
                    'domain': domain_group,
                    'original_domain': row['domain'],
                    'is_frontier': bool(row['frontier_model']),
                    'notability': row['notability_criteria']
                })
                
            except Exception as e:
                logger.warning(f"Error processing model {row['model']}: {e}")
                continue
        
        logger.info(f"Successfully processed {len(processed_data)} models")
        return processed_data

    def generate_chart_data(self, models_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate chart-ready data structure."""
        
        # Group by domain
        domain_series = {}
        domains = set(model['domain'] for model in models_data)
        
        for domain in domains:
            domain_models = [model for model in models_data if model['domain'] == domain]
            domain_series[domain] = {
                'name': domain,
                'data': [{
                    'x': model['year'],
                    'y': model['parameters'],
                    'model_name': model['model_name'],
                    'organization': model['organization'],
                    'is_frontier': model['is_frontier'],
                    'notability': model['notability']
                } for model in domain_models]
            }
        
        # Calculate statistics
        years = [model['year'] for model in models_data]
        parameters = [model['parameters'] for model in models_data]
        
        stats = {
            'total_models': len(models_data),
            'year_range': {
                'min': min(years),
                'max': max(years)
            },
            'parameter_range': {
                'min': min(parameters),
                'max': max(parameters)
            },
            'domains': list(domains),
            'domain_counts': {domain: len(domain_series[domain]['data']) for domain in domains}
        }
        
        chart_data = {
            'series': list(domain_series.values()),
            'stats': stats,
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'title': 'AI Model Size vs. Release Year',
                'x_axis_title': 'Release Year',
                'y_axis_title': 'Parameters (Log Scale)',
                'description': 'Scatter plot showing the relationship between AI model parameter count and release year, grouped by domain'
            }
        }
        
        return chart_data

    def save_data(self, data: Dict[str, Any], output_path: str) -> None:
        """Save data to JSON file."""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Data saved to: {output_file}")


def main():
    """Main extraction function."""
    # Database path
    db_path = Path(__file__).parent.parent.parent / "db" / "ai_insights.db"
    
    if not db_path.exists():
        logger.error(f"Database not found: {db_path}")
        sys.exit(1)
    
    try:
        # Initialize extractor
        extractor = ModelSizeExtractor(str(db_path))
        
        # Extract data
        logger.info("Starting data extraction...")
        models_data = extractor.extract_model_data()
        
        if not models_data:
            logger.error("No data extracted. Check database content.")
            sys.exit(1)
        
        # Generate chart data
        logger.info("Generating chart data...")
        chart_data = extractor.generate_chart_data(models_data)
        
        # Save to JSON
        output_path = Path(__file__).parent / "data.json"
        extractor.save_data(chart_data, str(output_path))
        
        # Print summary
        print(f"\n✅ Data extraction completed successfully!")
        print(f"📊 Total models: {chart_data['stats']['total_models']}")
        print(f"📅 Year range: {chart_data['stats']['year_range']['min']} - {chart_data['stats']['year_range']['max']}")
        print(f"🔢 Parameter range: {chart_data['stats']['parameter_range']['min']:,} - {chart_data['stats']['parameter_range']['max']:,}")
        print(f"🎯 Domains: {', '.join(chart_data['stats']['domains'])}")
        print(f"💾 Data saved to: {output_path}")
        
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 