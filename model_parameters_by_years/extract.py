#!/usr/bin/env python3
"""
AI Model Insights Data Extraction Script
Executes SQL queries and outputs ECharts-compatible JSON data
"""

import sqlite3
import json
import sys
import os
from pathlib import Path

def execute_sql_file(db_path: str, sql_file_path: str) -> list:
    """Execute SQL file and return results as list of dictionaries"""
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # This enables column access by name
        cursor = conn.cursor()
        
        # Read SQL file
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Execute SQL (handle multiple statements if needed)
        results = []
        for statement in sql_content.split(';'):
            statement = statement.strip()
            if statement:
                cursor.execute(statement)
                # Fetch results and convert to list of dicts
                rows = cursor.fetchall()
                if rows:
                    results.extend([dict(row) for row in rows])
        
        conn.close()
        return results
        
    except Exception as e:
        print(f"Error executing SQL file {sql_file_path}: {e}")
        return []

def convert_to_echarts_format(data: list) -> dict:
    """Convert raw data to ECharts scatter plot format"""
    
    # Group data by primary domain for series
    series_data = {}
    
    for row in data:
        domain = row.get('primary_domain', 'Other')
        if domain not in series_data:
            series_data[domain] = []
        
        # ECharts scatter format: [x, y, extra_info]
        point = [
            row.get('release_year'),
            row.get('log_parameters'),  # Use log scale for Y-axis
            {
                'model': row.get('model'),
                'organization': row.get('organization'),
                'parameters': row.get('parameters'),
                'domain': row.get('domain'),
                'confidence': row.get('confidence'),
                'frontier_model': row.get('frontier_model')
            }
        ]
        series_data[domain].append(point)
    
    # Convert to ECharts series format
    echarts_series = []
    colors = [
        '#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', 
        '#3ba272', '#fc8452', '#9a60b4', '#ea7ccc', '#dd6b66'
    ]
    
    for i, (domain, points) in enumerate(series_data.items()):
        series = {
            'name': domain,
            'type': 'scatter',
            'data': points,
            'itemStyle': {
                'color': colors[i % len(colors)]
            }
        }
        echarts_series.append(series)
    
    return {
        'series': echarts_series,
        'legend': {
            'data': list(series_data.keys())
        }
    }

def convert_stats_to_json(stats_data: list) -> dict:
    """Convert statistics data to structured JSON"""
    stats_result = {
        'year_range': {},
        'parameter_range': {},
        'domain_distribution': [],
        'models_per_year': [],
        'parameter_categories': []
    }
    
    for row in stats_data:
        metric = row.get('metric', '')
        analysis_type = row.get('analysis_type', '')
        
        if metric == 'Year Range':
            stats_result['year_range'] = {
                'min': row.get('min_value'),
                'max': row.get('max_value'),
                'total_count': row.get('total_count')
            }
        elif metric == 'Parameter Range':
            stats_result['parameter_range'] = {
                'min': row.get('min_value'),
                'max': row.get('max_value'),
                'avg': row.get('avg_value'),
                'min_log': row.get('min_log_value'),
                'max_log': row.get('max_log_value'),
                'avg_log': row.get('avg_log_value'),
                'total_count': row.get('total_count')
            }
        elif analysis_type == 'Domain Distribution':
            stats_result['domain_distribution'].append({
                'domain': row.get('primary_domain'),
                'count': row.get('model_count'),
                'percentage': row.get('percentage')
            })
        elif analysis_type == 'Models Per Year':
            stats_result['models_per_year'].append({
                'year': row.get('year'),
                'count': row.get('model_count'),
                'avg_parameters': row.get('avg_parameters'),
                'min_parameters': row.get('min_parameters'),
                'max_parameters': row.get('max_parameters')
            })
        elif analysis_type == 'Parameter Categories':
            stats_result['parameter_categories'].append({
                'category': row.get('size_category'),
                'count': row.get('model_count'),
                'min_params': row.get('min_params'),
                'max_params': row.get('max_params')
            })
    
    return stats_result

def main():
    """Main execution function"""
    if len(sys.argv) != 2:
        print("Usage: python extract.py <database_path>")
        sys.exit(1)
    
    db_path = sys.argv[1]
    script_dir = Path(__file__).parent
    
    # SQL file paths
    extract_sql_path = script_dir / 'extract.sql'
    stat_sql_path = script_dir / 'stat.sql'
    
    # Output paths
    data_json_path = script_dir / 'data.json'
    stat_json_path = script_dir / 'stat.json'
    
    # Check if files exist
    if not os.path.exists(db_path):
        print(f"Database file not found: {db_path}")
        sys.exit(1)
    
    if not extract_sql_path.exists():
        print(f"Extract SQL file not found: {extract_sql_path}")
        sys.exit(1)
    
    if not stat_sql_path.exists():
        print(f"Statistics SQL file not found: {stat_sql_path}")
        sys.exit(1)
    
    print("Extracting model data...")
    # Execute extract SQL
    extract_data = execute_sql_file(db_path, str(extract_sql_path))
    if not extract_data:
        print("No data extracted from extract.sql")
        sys.exit(1)
    
    print("Extracting statistics...")
    # Execute statistics SQL
    stats_data = execute_sql_file(db_path, str(stat_sql_path))
    
    print("Converting to ECharts format...")
    # Convert to ECharts format
    echarts_data = convert_to_echarts_format(extract_data)
    
    print("Converting statistics...")
    # Convert statistics
    stats_json = convert_stats_to_json(stats_data)
    
    print("Saving data files...")
    # Save data.json
    with open(data_json_path, 'w', encoding='utf-8') as f:
        json.dump(echarts_data, f, indent=2, ensure_ascii=False)
    
    # Save stat.json  
    with open(stat_json_path, 'w', encoding='utf-8') as f:
        json.dump(stats_json, f, indent=2, ensure_ascii=False)
    
    print(f"Data extraction completed!")
    print(f"- ECharts data saved to: {data_json_path}")
    print(f"- Statistics saved to: {stat_json_path}")
    print(f"- Total models processed: {len(extract_data)}")
    print(f"- Domains found: {len(echarts_data['legend']['data'])}")

if __name__ == "__main__":
    main() 