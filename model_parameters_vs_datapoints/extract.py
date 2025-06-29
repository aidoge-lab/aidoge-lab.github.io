#!/usr/bin/env python3
"""
Data extraction script for AI model parameters vs training dataset size analysis.
This script executes SQL queries and generates ECharts-compatible JSON data.

Usage:
    python extract.py [database_path]
    
Default database path: ../../db/ai_insights.db
"""

import sqlite3
import json
import math
import os
import sys
from pathlib import Path

def execute_sql_file(cursor, sql_file_path):
    """Execute SQL queries from a file and return results."""
    with open(sql_file_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # For single queries, execute directly
    if 'UNION ALL' not in sql_content:
        cursor.execute(sql_content)
        return cursor.fetchall()
    
    # For UNION ALL queries, execute as a single statement
    try:
        cursor.execute(sql_content)
        return cursor.fetchall()
    except Exception as e:
        # If UNION ALL fails, try splitting and executing separately
        print(f"Trying alternative execution method due to: {e}")
        queries = [query.strip() for query in sql_content.split('UNION ALL')]
        all_results = []
        for query in queries:
            if query.strip():
                cursor.execute(query)
                all_results.extend(cursor.fetchall())
        return all_results

def generate_echarts_data(raw_data):
    """Convert raw SQL data to ECharts scatter plot format."""
    
    # Group data by era
    era_data = {}
    
    for row in raw_data:
        model, org, params, dataset_size, pub_date, era, params_real, dataset_real = row
        
        if era not in era_data:
            era_data[era] = []
        
        # Calculate log10 values for plotting
        try:
            log_params = math.log10(params_real) if params_real and params_real > 0 else None
            log_dataset = math.log10(dataset_real) if dataset_real and dataset_real > 0 else None
            
            if log_params is not None and log_dataset is not None:
                era_data[era].append({
                    'value': [log_params, log_dataset],
                    'name': model,
                    'organization': org,
                    'parameters': int(params_real),
                    'dataset_size': int(dataset_real),
                    'publication_date': pub_date
                })
        except (ValueError, TypeError):
            # Skip invalid data points
            continue
    
    # Convert to ECharts series format
    series_data = []
    colors = {
        'Era 1: Classical ML (Before 2012)': '#5470c6',
        'Era 2: Deep Learning (2012-2017)': '#91cc75', 
        'Era 3: Transformer (2017+)': '#fac858',
        'Unknown Era': '#ee6666'
    }
    
    for era, data_points in era_data.items():
        if data_points:  # Only include eras with data
            series_data.append({
                'name': era,
                'type': 'scatter',
                'data': data_points,
                'itemStyle': {
                    'color': colors.get(era, '#73c0de')
                },
                'symbolSize': 8,
                'emphasis': {
                    'itemStyle': {
                        'borderColor': '#000',
                        'borderWidth': 1
                    }
                }
            })
    
    # Create complete ECharts configuration
    echarts_config = {
        'title': {
            'text': 'AI Model Parameters vs Training Dataset Size',
            'subtext': 'Logarithmic scale comparison across different eras',
            'left': 'center'
        },
                 'tooltip': {
             'trigger': 'item',
             'formatter': 'function(params) { const data = params.data; const params_formatted = (data.parameters / 1e9).toFixed(1) + "B"; const dataset_formatted = (data.dataset_size / 1e12).toFixed(1) + "T"; return data.name + "<br/>" + "Organization: " + (data.organization || "Unknown") + "<br/>" + "Parameters: " + params_formatted + "<br/>" + "Dataset Size: " + dataset_formatted + " tokens<br/>" + "Date: " + (data.publication_date || "Unknown"); }'
         },
        'legend': {
            'data': [era for era in era_data.keys() if era_data[era]],
            'top': '8%'
        },
                 'xAxis': {
             'type': 'log',
             'name': 'Model Parameters (log10)',
             'nameLocation': 'center',
             'nameGap': 35,
             'axisLabel': {
                 'formatter': 'function(value) { return Math.pow(10, value).toExponential(0); }'
             },
             'splitLine': {
                 'show': True
             }
         },
         'yAxis': {
             'type': 'log', 
             'name': 'Training Dataset Size (log10)',
             'nameLocation': 'center',
             'nameGap': 50,
             'axisLabel': {
                 'formatter': 'function(value) { return Math.pow(10, value).toExponential(0); }'
             },
             'splitLine': {
                 'show': True
             }
         },
        'series': series_data,
        'grid': {
            'left': '12%',
            'right': '8%',
            'bottom': '15%',
            'top': '20%'
        }
    }
    
    return echarts_config

def main():
    # Determine database path
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    else:
        script_dir = Path(__file__).parent
        db_path = script_dir / "../../db/ai_insights.db"
    
    if not os.path.exists(db_path):
        print(f"Error: Database file not found at {db_path}")
        sys.exit(1)
    
    # File paths
    script_dir = Path(__file__).parent
    extract_sql_path = script_dir / "extract.sql"
    stat_sql_path = script_dir / "stat.sql"
    data_json_path = script_dir / "data.json"
    stat_json_path = script_dir / "stat.json"
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Execute extract SQL
        print("Executing extract SQL...")
        raw_data = execute_sql_file(cursor, extract_sql_path)
        print(f"Retrieved {len(raw_data)} records")
        
        # Generate ECharts data
        print("Generating ECharts data...")
        echarts_data = generate_echarts_data(raw_data)
        
        # Save data.json
        with open(data_json_path, 'w', encoding='utf-8') as f:
            json.dump(echarts_data, f, indent=2, ensure_ascii=False)
        print(f"Data saved to {data_json_path}")
        
        # Execute statistics SQL
        print("Executing statistics SQL...")
        stat_results = execute_sql_file(cursor, stat_sql_path)
        
        # Convert statistics to JSON format
        stat_data = []
        for row in stat_results:
            stat_data.append({
                'analysis_type': row[0],
                'total_count': row[1],
                'min_value': row[2],
                'max_value': row[3],
                'avg_value': row[4],
                'min_log10': row[5] if len(row) > 5 else None,
                'max_log10': row[6] if len(row) > 6 else None,
                'avg_log10': row[7] if len(row) > 7 else None
            })
        
        # Save stat.json
        with open(stat_json_path, 'w', encoding='utf-8') as f:
            json.dump(stat_data, f, indent=2, ensure_ascii=False)
        print(f"Statistics saved to {stat_json_path}")
        
        # Print summary
        print("\n=== Extraction Summary ===")
        print(f"Total data points: {len(raw_data)}")
        series_count = len([s for s in echarts_data['series'] if s['data']])
        print(f"Series count: {series_count}")
        for series in echarts_data['series']:
            print(f"  {series['name']}: {len(series['data'])} points")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main() 