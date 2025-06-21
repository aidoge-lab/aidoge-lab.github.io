#!/usr/bin/env python3
"""
AI Model Parameters vs Training Dataset Size Data Extraction
This script executes SQL queries and generates JSON data for ECharts visualization.
"""

import sqlite3
import json
import sys
import os
from pathlib import Path
import math

def read_sql_file(file_path):
    """Read SQL query from file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def execute_query(cursor, query):
    """Execute SQL query and return results"""
    try:
        cursor.execute(query)
        columns = [description[0] for description in cursor.description]
        results = cursor.fetchall()
        return [dict(zip(columns, row)) for row in results]
    except Exception as e:
        print(f"Error executing query: {e}")
        return []

def process_domain(domain_str):
    """Process domain string to get primary domain"""
    if not domain_str:
        return "Unknown"
    # Split by comma and take the first domain
    return domain_str.split(',')[0].strip()

def prepare_echarts_data(raw_data):
    """Convert raw data to ECharts scatter plot format"""
    # Group data by domain
    domain_data = {}
    
    for record in raw_data:
        domain = process_domain(record.get('domain'))
        
        if domain not in domain_data:
            domain_data[domain] = []
        
        # Convert to log10 for both axes
        params = record.get('parameters', 0)
        dataset_size = record.get('training_dataset_size_datapoints', 0)
        
        if params > 0 and dataset_size > 0:
            log_params = math.log10(params)
            log_dataset_size = math.log10(dataset_size)
            
            domain_data[domain].append({
                'value': [log_params, log_dataset_size],
                'name': record.get('model', ''),
                'organization': record.get('organization', ''),
                'parameters': params,
                'training_dataset_size_datapoints': dataset_size,
                'publication_date': record.get('publication_date', ''),
                'confidence': record.get('confidence', '')
            })
    
    # Convert to ECharts series format
    series = []
    for domain, data_points in domain_data.items():
        series.append({
            'name': domain,
            'type': 'scatter',
            'data': data_points
        })
    
    return {
        'series': series,
        'domains': list(domain_data.keys()),
        'total_models': sum(len(data) for data in domain_data.values())
    }

def prepare_stat_data(raw_stat_data):
    """Process statistical data"""
    stats = {}
    domain_breakdown = []
    
    for record in raw_stat_data:
        if 'analysis_type' in record and record['analysis_type'] == 'domain_breakdown':
            domain_breakdown.append(record)
        elif 'metric' in record:
            stats[record['metric']] = {
                'total_count': record.get('total_count', 0),
                'min_value': record.get('min_value', 0),
                'max_value': record.get('max_value', 0),
                'avg_value': record.get('avg_value', 0),
                'median_value': record.get('median_value', 0)
            }
    
    return {
        'basic_stats': stats,
        'domain_breakdown': domain_breakdown
    }

def main():
    """Main execution function"""
    if len(sys.argv) != 2:
        print("Usage: python extract.py <database_path>")
        sys.exit(1)
    
    db_path = sys.argv[1]
    script_dir = Path(__file__).parent
    
    # Define file paths
    extract_sql_path = script_dir / "extract.sql"
    stat_sql_path = script_dir / "stat.sql"
    data_json_path = script_dir / "data.json"
    stat_json_path = script_dir / "stat.json"
    
    # Check if SQL files exist
    if not extract_sql_path.exists():
        print(f"Error: {extract_sql_path} not found")
        sys.exit(1)
    
    if not stat_sql_path.exists():
        print(f"Error: {stat_sql_path} not found")
        sys.exit(1)
    
    # Connect to database
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Read and execute extract query
        extract_query = read_sql_file(extract_sql_path)
        print("Executing data extraction query...")
        raw_data = execute_query(cursor, extract_query)
        print(f"Extracted {len(raw_data)} records")
        
        # Process data for ECharts
        echarts_data = prepare_echarts_data(raw_data)
        
        # Save data.json
        with open(data_json_path, 'w', encoding='utf-8') as f:
            json.dump(echarts_data, f, indent=2, ensure_ascii=False)
        print(f"Data saved to {data_json_path}")
        
        # Read and execute stat query
        stat_query = read_sql_file(stat_sql_path)
        print("Executing statistical analysis query...")
        raw_stat_data = execute_query(cursor, stat_query)
        print(f"Generated {len(raw_stat_data)} statistical records")
        
        # Process statistical data
        stat_data = prepare_stat_data(raw_stat_data)
        
        # Save stat.json
        with open(stat_json_path, 'w', encoding='utf-8') as f:
            json.dump(stat_data, f, indent=2, ensure_ascii=False)
        print(f"Statistics saved to {stat_json_path}")
        
        # Print summary
        print("\nData Extraction Summary:")
        print(f"- Total models: {echarts_data['total_models']}")
        print(f"- Domains found: {len(echarts_data['domains'])}")
        print(f"- Domain list: {', '.join(echarts_data['domains'])}")
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main() 