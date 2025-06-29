-- Extract AI models data for parameters vs training dataset size analysis
-- Generate scatter plot data with model era classification

SELECT 
    model,
    organization,
    parameters,
    training_dataset_size_datapoints,
    publication_date,
    CASE 
        WHEN publication_date < '2012-01-01' OR publication_date IS NULL THEN 'Era 1: Classical ML (Before 2012)'
        WHEN publication_date >= '2012-01-01' AND publication_date < '2017-01-01' THEN 'Era 2: Deep Learning (2012-2017)'
        WHEN publication_date >= '2017-01-01' THEN 'Era 3: Transformer (2017+)'
        ELSE 'Unknown Era'
    END as era,
    -- Log10 values for plotting (will be calculated in Python)
    CAST(parameters AS REAL) as parameters_real,
    CAST(training_dataset_size_datapoints AS REAL) as training_dataset_size_real
FROM ai_models 
WHERE parameters IS NOT NULL 
    AND parameters > 0
    AND training_dataset_size_datapoints IS NOT NULL 
    AND training_dataset_size_datapoints > 0
ORDER BY publication_date ASC, parameters ASC; 