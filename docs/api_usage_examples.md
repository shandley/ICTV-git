# ICTV-git API Usage Examples

> **Note**: We've significantly upgraded our API! For the complete REST API documentation with 30+ endpoints, see [api_reference.md](api_reference.md).

## Starting the API Server

```bash
# Create virtual environment (if not already done)
python3 -m venv ictv_api_env
source ictv_api_env/bin/activate

# Install dependencies
pip install -r requirements_api.txt

# Start the production API server
python scripts/run_api_server.py --dev

# API will be available at:
# http://localhost:8000
# Interactive docs: http://localhost:8000/docs
```

## New API Features

Our production REST API now includes:
- **30+ endpoints** across 4 modules (Taxonomy, Historical, AI, Search)
- **AI-powered natural language queries** - Ask questions in plain English
- **20-year historical tracking** - All MSL releases from 2005-2024
- **Advanced search** with faceted filtering
- **Auto-generated documentation** at `/docs`

## Quick Examples

### Natural Language Query
```bash
curl -X POST http://localhost:8000/ai/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What happened to Caudovirales in 2019?"}'
```

### Search with Filters
```bash
curl -X POST http://localhost:8000/search/species \
  -H "Content-Type: application/json" \
  -d '{"query": "coronavirus", "family_filter": "Coronaviridae", "limit": 10}'
```

### Historical Comparison
```bash
curl http://localhost:8000/historical/compare/MSL35/MSL40
```

For complete API documentation, see [api_reference.md](api_reference.md).

---

## Legacy API Examples (for reference)

### 1. Get Available Versions

```bash
# List all available MSL versions with statistics
curl http://localhost:8000/api/v1/versions
```

Response:
```json
[
  {
    "version": "MSL36",
    "total_species": 9110,
    "total_genera": 2224,
    "total_families": 233,
    "total_orders": 65,
    "total_realms": 6,
    "year": 2021
  },
  ...
]
```

### 2. Get Species Information

```bash
# Get specific species by name
curl http://localhost:8000/api/v1/species/MSL38/Severe%20acute%20respiratory%20syndrome-related%20coronavirus
```

Response:
```json
{
  "scientific_name": "Severe acute respiratory syndrome-related coronavirus",
  "classification": {
    "realm": "Riboviria",
    "kingdom": "Orthornavirae",
    "phylum": "Pisuviricota",
    "class": "Pisoniviricetes",
    "order": "Nidovirales",
    "family": "Coronaviridae",
    "genus": "Betacoronavirus"
  },
  "genome": {
    "type": "ssRNA(+)",
    "size": "29903 bp"
  },
  "hosts": ["Homo sapiens", "Rhinolophus affinis"]
}
```

### 3. Search Species

```bash
# Search for species by name
curl "http://localhost:8000/api/v1/search?q=coronavirus&version=MSL38&limit=5"

# Search by family
curl "http://localhost:8000/api/v1/search?q=Coronaviridae&version=MSL38&field=family"

# Search by host
curl "http://localhost:8000/api/v1/search?q=human&version=MSL38&field=host"
```

### 4. Get Taxonomic Groups

```bash
# Get all species in a family
curl http://localhost:8000/api/v1/taxonomy/MSL38/family/Coronaviridae

# Get all species in a genus
curl http://localhost:8000/api/v1/taxonomy/MSL38/genus/Betacoronavirus

# Get all species in a realm
curl http://localhost:8000/api/v1/taxonomy/MSL38/realm/Riboviria
```

### 5. Compare Versions

```bash
# Get comparison summary
curl http://localhost:8000/api/v1/compare/MSL37/MSL38

# Get detailed comparison
curl http://localhost:8000/api/v1/compare/MSL37/MSL38/details

# Get only reclassified species
curl "http://localhost:8000/api/v1/compare/MSL37/MSL38/details?change_type=reclassified"
```

### 6. Species History

```bash
# Get complete history of a species across all versions
curl http://localhost:8000/api/v1/history/Tobacco%20mosaic%20virus
```

### 7. Generate Citations

```bash
# Generate standard citation for a species
curl -X POST "http://localhost:8000/api/v1/citation" \
  -H "Content-Type: application/json" \
  -d '{"species_name": "Tobacco mosaic virus", "version": "MSL38", "format": "standard"}'

# Generate BibTeX citation
curl -X POST "http://localhost:8000/api/v1/citation" \
  -H "Content-Type: application/json" \
  -d '{"species_name": "Tobacco mosaic virus", "version": "MSL38", "format": "bibtex"}'

# Generate citation for taxonomic group
curl -X POST "http://localhost:8000/api/v1/citation" \
  -H "Content-Type: application/json" \
  -d '{
    "taxonomic_group": {"rank": "family", "name": "Coronaviridae"},
    "version": "MSL38",
    "format": "standard"
  }'
```

### 8. Bulk Data Download

```bash
# Download all species in JSON format
curl http://localhost:8000/api/v1/bulk/species/MSL38 -o msl38_all_species.json

# Download as CSV
curl "http://localhost:8000/api/v1/bulk/species/MSL38?format=csv" -o msl38_all_species.csv

# Download filtered by family
curl "http://localhost:8000/api/v1/bulk/species/MSL38?format=csv&family=Coronaviridae" \
  -o coronaviridae_species.csv

# Download filtered by realm
curl "http://localhost:8000/api/v1/bulk/species/MSL38?format=json&realm=Riboviria" \
  -o riboviria_species.json
```

### 9. Diversity Statistics

```bash
# Get comprehensive diversity statistics for a version
curl http://localhost:8000/api/v1/stats/diversity/MSL38
```

Response includes:
- Total species count
- Number of taxa at each rank
- Genome type distribution
- Host distribution (top 20)
- Largest families
- Most diverse genera

## Python Client Examples

```python
import requests

# Base URL for the API
BASE_URL = "http://localhost:8000"

# Get all versions
response = requests.get(f"{BASE_URL}/api/v1/versions")
versions = response.json()
print(f"Available versions: {[v['version'] for v in versions]}")

# Search for species
params = {
    "q": "coronavirus",
    "version": "MSL38",
    "field": "all",
    "limit": 10
}
response = requests.get(f"{BASE_URL}/api/v1/search", params=params)
results = response.json()
print(f"Found {results['total_results']} species matching 'coronavirus'")

# Get species history
species_name = "Tobacco mosaic virus"
response = requests.get(f"{BASE_URL}/api/v1/history/{species_name}")
history = response.json()
print(f"First appearance: {history['first_appearance']}")
print(f"Last appearance: {history['last_appearance']}")

# Compare versions
response = requests.get(f"{BASE_URL}/api/v1/compare/MSL37/MSL38")
comparison = response.json()
print(f"Species added: {comparison['species_added']}")
print(f"Species reclassified: {comparison['species_reclassified']}")

# Generate citation
citation_data = {
    "species_name": "Severe acute respiratory syndrome-related coronavirus",
    "version": "MSL38",
    "format": "bibtex"
}
response = requests.post(f"{BASE_URL}/api/v1/citation", json=citation_data)
citation = response.json()
print(citation['citation'])
```

## R Client Example

```r
library(httr)
library(jsonlite)

# Base URL
base_url <- "http://localhost:8000"

# Get versions
versions <- GET(paste0(base_url, "/api/v1/versions")) %>%
  content(as = "text") %>%
  fromJSON()

# Search for species
search_results <- GET(
  paste0(base_url, "/api/v1/search"),
  query = list(
    q = "coronavirus",
    version = "MSL38",
    limit = 10
  )
) %>%
  content(as = "text") %>%
  fromJSON()

# Get all species in a family
family_species <- GET(
  paste0(base_url, "/api/v1/taxonomy/MSL38/family/Coronaviridae")
) %>%
  content(as = "text") %>%
  fromJSON()

# Download bulk data as CSV
download.file(
  paste0(base_url, "/api/v1/bulk/species/MSL38?format=csv&family=Coronaviridae"),
  destfile = "coronaviridae_species.csv"
)
```

## Rate Limiting and Best Practices

1. **Bulk Downloads**: For large datasets, use the bulk download endpoints rather than making individual requests
2. **Caching**: Cache responses locally to avoid repeated requests
3. **Versioning**: Always specify the MSL version in your requests for reproducibility
4. **Error Handling**: Check response status codes and handle errors appropriately
5. **Citation**: Use the citation endpoint to generate proper citations for your research

## Error Responses

The API returns standard HTTP status codes:

- `200`: Success
- `404`: Resource not found (e.g., invalid version or species name)
- `400`: Bad request (e.g., invalid parameters)
- `422`: Validation error (e.g., missing required fields)
- `500`: Internal server error

Error responses include a detail message:
```json
{
  "detail": "Version MSL99 not found"
}
```