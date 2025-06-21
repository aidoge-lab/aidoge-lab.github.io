-- Extract AI model parameters vs training dataset size data
-- This query retrieves data for scatter plot visualization
SELECT 
    model,
    parameters,
    training_dataset_size_datapoints,
    domain,
    organization,
    publication_date,
    confidence
FROM ai_models 
WHERE parameters IS NOT NULL 
  AND training_dataset_size_datapoints IS NOT NULL
  AND parameters > 0 
  AND training_dataset_size_datapoints > 0
ORDER BY parameters ASC; 