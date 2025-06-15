# AI Model Insights Analysis Template

## Data Source 
`data/models/notable_ai_models.sql` is the data format definition, and the database file is located in `db/ai_insights.db`.

## Insight Mining Requirements
I want to extract comprehensive model insights:
- Analyze all AI models with a scatter plot where:
  - X-axis: Model release year
  - Y-axis: Model parameter count (trainable parameters) 
  - Y-axis scale: Logarithmic (log10) to handle the wide range of parameter sizes
  - domain as series differentiation (The primary domain(s) the model is designed for)

folder_name=insights/model_size
Implementation approach divided into four stages:

## Stage 1: Data Extraction
Create an analysis script to extract the required information and save it as `$folder_name/extract.py`

## Stage 2: Data Processing  
Execute the extraction script to generate processed data and output results to `$folder_name/data.json`

## Stage 3: Visualization Development
Generate `$folder_name/index.html` with the following specifications:
- Utilize ECharts visualization library
- Please refer to the visual effects in the components, layouts, and styles directories under the `template` directory
- Select appropriate chart type for professional data presentation
- Load data dynamically from `$folder_name/data.json`
- Apply modern, tech-focused styling that conveys scientific rigor
- Ensure responsive design and interactive features

## Stage 4: Standalone Deployment
Create `index_standalone.html` based on `index.html` and `data.json`:
- Embed data directly into the HTML file, using `insights/create_standalone.py` tool
- Ensure complete self-contained functionality
- Optimize for direct viewing without external dependencies

# General Notes

- The X and Y axis ranges of the chart should be adaptive. (by analyze the data rage)
- Language: English
- Please write the HTML according to the styles provided in the template directory
