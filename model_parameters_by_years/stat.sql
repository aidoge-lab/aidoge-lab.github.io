-- Statistical Analysis for Chart Design
-- This SQL provides statistical insights for axis ranges and series design

-- 1. Year Range Analysis
SELECT 
    'Year Range' as metric,
    MIN(CAST(strftime('%Y', publication_date) AS INTEGER)) as min_value,
    MAX(CAST(strftime('%Y', publication_date) AS INTEGER)) as max_value,
    COUNT(*) as total_count
FROM ai_models 
WHERE publication_date IS NOT NULL;

-- 2. Parameter Range Analysis (with log scale)
SELECT 
    'Parameter Range' as metric,
    MIN(parameters) as min_value,
    MAX(parameters) as max_value,
    AVG(parameters) as avg_value,
    MIN(LOG10(parameters)) as min_log_value,
    MAX(LOG10(parameters)) as max_log_value,
    AVG(LOG10(parameters)) as avg_log_value,
    COUNT(*) as total_count
FROM ai_models 
WHERE parameters IS NOT NULL AND parameters > 0;

-- 3. Domain Distribution Analysis
SELECT 
    'Domain Distribution' as analysis_type,
    CASE 
        WHEN domain LIKE '%Language%' THEN 'Language'
        WHEN domain LIKE '%Vision%' THEN 'Vision' 
        WHEN domain LIKE '%Multimodal%' THEN 'Multimodal'
        WHEN domain LIKE '%Audio%' THEN 'Audio'
        WHEN domain LIKE '%Video%' THEN 'Video'
        WHEN domain LIKE '%Mathematics%' THEN 'Mathematics'
        WHEN domain LIKE '%Code%' THEN 'Code'
        WHEN domain LIKE '%Reasoning%' THEN 'Reasoning'
        ELSE 'Other'
    END as primary_domain,
    COUNT(*) as model_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM ai_models WHERE domain IS NOT NULL), 2) as percentage
FROM ai_models 
WHERE domain IS NOT NULL
GROUP BY primary_domain
ORDER BY model_count DESC;

-- 4. Year-wise Model Count Distribution
SELECT 
    'Models Per Year' as analysis_type,
    CAST(strftime('%Y', publication_date) AS INTEGER) as year,
    COUNT(*) as model_count,
    AVG(parameters) as avg_parameters,
    MIN(parameters) as min_parameters,
    MAX(parameters) as max_parameters
FROM ai_models 
WHERE publication_date IS NOT NULL 
    AND parameters IS NOT NULL 
    AND parameters > 0
GROUP BY year
ORDER BY year;

-- 5. Parameter Size Categories
SELECT 
    'Parameter Categories' as analysis_type,
    CASE 
        WHEN parameters < 1000000 THEN 'Small (<1M)'
        WHEN parameters < 1000000000 THEN 'Medium (1M-1B)'
        WHEN parameters < 100000000000 THEN 'Large (1B-100B)'
        WHEN parameters < 1000000000000 THEN 'Very Large (100B-1T)'
        ELSE 'Ultra Large (>1T)'
    END as size_category,
    COUNT(*) as model_count,
    MIN(parameters) as min_params,
    MAX(parameters) as max_params
FROM ai_models 
WHERE parameters IS NOT NULL AND parameters > 0
GROUP BY size_category
ORDER BY MIN(parameters); 