# ICTV-git REST API Reference

## Overview

The ICTV-git REST API provides comprehensive programmatic access to 20 years of viral taxonomy history with 30+ endpoints across four main modules:

- **Taxonomy API**: Core taxonomic data access
- **Historical API**: 20-year evolution tracking
- **AI API**: Natural language queries and ML features
- **Search API**: Advanced search and filtering

## Quick Start

```bash
# Start the API server
python scripts/run_api_server.py --dev

# API available at
http://localhost:8000

# Interactive documentation
http://localhost:8000/docs
```

## Authentication

Currently, the API does not require authentication for read operations. This may change in future versions.

## Base URL

All API endpoints are relative to:
```
http://localhost:8000
```

## API Modules

### 1. Taxonomy API

Core endpoints for accessing taxonomic data.

#### Get Species Information
```http
GET /taxonomy/species/{scientific_name}
```

**Example:**
```bash
curl http://localhost:8000/taxonomy/species/Tobacco%20Mosaic%20Virus
```

**Response:**
```json
{
  "scientific_name": "Tobacco Mosaic Virus",
  "taxonomy": {
    "family": "Virgaviridae",
    "genus": "Tobamovirus"
  },
  "classification": {
    "msl_version": "MSL40",
    "msl_year": 2024
  }
}
```

#### Get Family Data
```http
GET /taxonomy/family/{family_name}
```

Returns complete family hierarchy including all genera and species.

#### List All Families
```http
GET /taxonomy/families
```

#### Get Taxonomy Hierarchy
```http
GET /taxonomy/hierarchy
```

Returns complete taxonomy tree structure with statistics.

#### Validate Classification
```http
POST /taxonomy/validate
```

**Request Body:**
```json
{
  "scientific_name": "Test Virus",
  "taxonomy": {
    "family": "Virgaviridae",
    "genus": "Tobamovirus"
  }
}
```

### 2. Historical API

Track taxonomic changes across 20 years (2005-2024).

#### List All MSL Releases
```http
GET /historical/releases
```

Returns all 18 MSL releases with metadata.

#### Get Release Details
```http
GET /historical/releases/{msl_version}
```

**Example:**
```bash
curl http://localhost:8000/historical/releases/MSL40
```

#### Compare Releases
```http
GET /historical/compare/{from_version}/{to_version}
```

**Example:**
```bash
curl http://localhost:8000/historical/compare/MSL35/MSL40
```

Shows detailed comparison including added, deleted, and modified files.

#### Species History
```http
GET /historical/species/{scientific_name}/history
```

Track a species across all releases.

#### Family Evolution
```http
GET /historical/family/{family_name}/evolution
```

Monitor family changes over time.

#### Caudovirales Dissolution
```http
GET /historical/caudovirales-dissolution
```

Detailed information about the historic 2019 reorganization.

#### Timeline Summary
```http
GET /historical/timeline
```

High-level 20-year overview with major milestones.

### 3. AI API

AI-powered features for advanced analysis.

#### Natural Language Query
```http
POST /ai/query
```

**Request Body:**
```json
{
  "query": "What happened to Caudovirales in 2019?",
  "use_cache": true
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/ai/query \
  -H "Content-Type: application/json" \
  -d '{"query": "How many families exist?"}'
```

#### AI Classification
```http
POST /ai/classify
```

**Request Body:**
```json
{
  "organism_name": "Novel RNA Virus",
  "metadata": {
    "genome_type": "RNA",
    "genome_size": "12kb",
    "host": "plants"
  }
}
```

#### Family Stability Score
```http
GET /ai/stability/{family_name}
```

Get stability analysis based on historical changes.

#### Available AI Features
```http
GET /ai/features
```

#### AI Health Check
```http
GET /ai/health
```

#### Example Queries
```http
GET /ai/examples
```

### 4. Search API

Advanced search capabilities with faceted filtering.

#### Search Species
```http
POST /search/species
```

**Request Body:**
```json
{
  "query": "coronavirus",
  "family_filter": "Coronaviridae",
  "genus_filter": null,
  "exact_match": false,
  "limit": 100
}
```

#### Get Search Facets
```http
GET /search/facets
```

Returns available filters with counts.

#### Faceted Search
```http
POST /search/faceted
```

**Request Body:**
```json
{
  "family": "virgaviridae",
  "msl_version": "MSL40"
}
```

#### Family Summary
```http
GET /search/family/{family_name}/summary
```

Comprehensive family statistics and species list.

#### Advanced Search
```http
POST /search/advanced
```

**Request Body:**
```json
{
  "query": "tobacco",
  "filters": {
    "family": "virgaviridae",
    "era": "AI Era"
  },
  "sort_by": "alphabetical",
  "limit": 50
}
```

#### Search Statistics
```http
GET /search/statistics
```

## Response Formats

All responses are in JSON format. Successful responses have HTTP status 200.

### Error Responses

```json
{
  "error": "Error message",
  "detail": "Detailed error information",
  "type": "ErrorType"
}
```

**Status Codes:**
- `200`: Success
- `404`: Resource not found
- `422`: Validation error
- `500`: Internal server error

## Python Client Example

```python
import requests
import json

# Base URL
BASE_URL = "http://localhost:8000"

# Natural language query
response = requests.post(
    f"{BASE_URL}/ai/query",
    json={"query": "How has Coronaviridae changed since COVID?"}
)
print(response.json()['response'])

# Search species
response = requests.post(
    f"{BASE_URL}/search/species",
    json={
        "query": "coronavirus",
        "family_filter": "Coronaviridae",
        "limit": 10
    }
)
results = response.json()
print(f"Found {results['total_matches']} species")

# Compare releases
response = requests.get(f"{BASE_URL}/historical/compare/MSL35/MSL40")
comparison = response.json()
print(f"Total changes: {comparison['changes']['total_changes']}")

# Get family evolution
response = requests.get(f"{BASE_URL}/historical/family/siphoviridae/evolution")
evolution = response.json()
for event in evolution['major_events']:
    print(f"{event['msl_version']}: {event['description']}")
```

## JavaScript/TypeScript Example

```javascript
// Using fetch API
const BASE_URL = 'http://localhost:8000';

// Natural language query
async function askQuestion(query) {
  const response = await fetch(`${BASE_URL}/ai/query`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ query, use_cache: true }),
  });
  const data = await response.json();
  return data.response;
}

// Search species
async function searchSpecies(query, family = null) {
  const response = await fetch(`${BASE_URL}/search/species`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query,
      family_filter: family,
      limit: 100,
    }),
  });
  return response.json();
}

// Usage
(async () => {
  const answer = await askQuestion('What is the largest viral family?');
  console.log(answer);
  
  const results = await searchSpecies('virus', 'Coronaviridae');
  console.log(`Found ${results.total_matches} species`);
})();
```

## Rate Limiting

Currently, there are no rate limits. For production deployment, we recommend:
- Caching responses locally
- Using bulk endpoints for large datasets
- Implementing exponential backoff for retries

## Best Practices

1. **Use specific endpoints**: Choose the most specific endpoint for your needs
2. **Cache responses**: Especially for historical data that doesn't change
3. **Handle errors gracefully**: Check status codes and parse error messages
4. **Use the search index**: For performance, use search endpoints rather than iterating
5. **Batch requests**: When possible, use bulk operations

## Upcoming Features

- WebSocket support for real-time updates
- GraphQL endpoint
- Authentication and API keys
- Rate limiting
- Additional export formats

## Support

- **Documentation**: http://localhost:8000/docs (when server running)
- **GitHub Issues**: https://github.com/shandley/ICTV-git/issues
- **API Status**: http://localhost:8000/health