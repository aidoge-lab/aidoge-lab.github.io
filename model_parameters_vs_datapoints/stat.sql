-- Statistical analysis for AI model parameters vs training dataset size
-- This query provides insights for chart design

-- Basic statistics for parameters
SELECT 
    'parameters' as metric,
    COUNT(*) as total_count,
    CAST(MIN(parameters) as INTEGER) as min_value,
    CAST(MAX(parameters) as INTEGER) as max_value,
    CAST(AVG(parameters) as INTEGER) as avg_value,
    0 as median_value
FROM ai_models 
WHERE parameters IS NOT NULL 
  AND training_dataset_size_datapoints IS NOT NULL
  AND parameters > 0 
  AND training_dataset_size_datapoints > 0

UNION ALL

-- Basic statistics for training dataset size
SELECT 
    'training_dataset_size_datapoints' as metric,
    COUNT(*) as total_count,
    CAST(MIN(training_dataset_size_datapoints) as INTEGER) as min_value,
    CAST(MAX(training_dataset_size_datapoints) as INTEGER) as max_value,
    CAST(AVG(training_dataset_size_datapoints) as INTEGER) as avg_value,
    0 as median_value
FROM ai_models 
WHERE parameters IS NOT NULL 
  AND training_dataset_size_datapoints IS NOT NULL
  AND parameters > 0 
  AND training_dataset_size_datapoints > 0

UNION ALL

-- Domain distribution
SELECT 
    'domain_distribution' as metric,
    COUNT(*) as total_count,
    COUNT(DISTINCT domain) as min_value,
    0 as max_value,
    0 as avg_value,
    0 as median_value
FROM ai_models 
WHERE parameters IS NOT NULL 
  AND training_dataset_size_datapoints IS NOT NULL
  AND parameters > 0 
  AND training_dataset_size_datapoints > 0

-- Domain breakdown query (separate from main stats)
-- This will run as a separate query to avoid issues with mixed result sets 