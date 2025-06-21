-- Extract AI Model Data for Scatter Plot Visualization
-- X-axis: Model release year
-- Y-axis: Model parameter count (trainable parameters) 
-- Series: Primary domain

SELECT 
    model,
    organization,
    CAST(strftime('%Y', publication_date) AS INTEGER) as release_year,
    parameters,
    domain,
    CASE 
        WHEN parameters IS NOT NULL AND parameters > 0 
        THEN LOG10(parameters) 
        ELSE NULL 
    END as log_parameters,
    -- Split domain into primary domain for series grouping
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
    confidence,
    frontier_model
FROM ai_models 
WHERE publication_date IS NOT NULL 
    AND parameters IS NOT NULL 
    AND parameters > 0
    AND strftime('%Y', publication_date) IS NOT NULL
ORDER BY release_year, parameters; 