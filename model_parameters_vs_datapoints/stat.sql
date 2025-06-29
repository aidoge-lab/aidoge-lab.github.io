-- Statistical analysis for model parameters vs training dataset size
-- This query provides insights for chart design (axis ranges, series counts, etc.)

-- Combined statistics including era-based distribution
SELECT 
    CASE 
        WHEN publication_date < '2012-01-01' OR publication_date IS NULL THEN 'Era 1: Classical ML (Before 2012)'
        WHEN publication_date >= '2012-01-01' AND publication_date < '2017-01-01' THEN 'Era 2: Deep Learning (2012-2017)'
        WHEN publication_date >= '2017-01-01' THEN 'Era 3: Transformer (2017+)'
        ELSE 'Unknown Era'
    END as analysis_type,
    COUNT(*) as total_count,
    MIN(parameters) as min_parameters,
    MAX(parameters) as max_parameters,
    AVG(CAST(parameters AS REAL)) as avg_parameters,
    MIN(LOG10(CAST(parameters AS REAL))) as min_log10_parameters,
    MAX(LOG10(CAST(parameters AS REAL))) as max_log10_parameters,
    AVG(LOG10(CAST(parameters AS REAL))) as avg_log10_parameters
FROM ai_models 
WHERE parameters IS NOT NULL 
    AND parameters > 0
    AND training_dataset_size_datapoints IS NOT NULL 
    AND training_dataset_size_datapoints > 0
GROUP BY 
    CASE 
        WHEN publication_date < '2012-01-01' OR publication_date IS NULL THEN 'Era 1: Classical ML (Before 2012)'
        WHEN publication_date >= '2012-01-01' AND publication_date < '2017-01-01' THEN 'Era 2: Deep Learning (2012-2017)'
        WHEN publication_date >= '2017-01-01' THEN 'Era 3: Transformer (2017+)'
        ELSE 'Unknown Era'
    END
ORDER BY analysis_type; 