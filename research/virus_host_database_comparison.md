# Virus Host Range Database Comparison for Phase 6 Analysis

## Database Options Evaluation

### 1. Viral Host Range Database (Pasteur)
- **URL**: https://viralhostrangedb.pasteur.cloud
- **API**: https://hub.pages.pasteur.fr/viralhostrangedb/api.html
- **Last Updated**: February 19, 2025 (very recent!)
- **Pros**:
  - Recently updated (not dated as initially thought)
  - Has REST API for programmatic access
  - Focuses specifically on experimental host range data
  - Curated from literature
- **Cons**:
  - May have limited species coverage
  - Focuses on experimental data only
- **Best for**: Verified experimental host relationships

### 2. NCBI Virus
- **URL**: https://www.ncbi.nlm.nih.gov/labs/virus/vssi/
- **Pros**:
  - Comprehensive sequence-based data
  - Constantly updated with new submissions
  - Links to GenBank/RefSeq
  - Includes metadata from sequence submissions
- **Cons**:
  - Host data often from isolation source, not full host range
  - May include unverified host associations
  - No dedicated API for host range queries
- **Best for**: Large-scale sequence-linked host data

### 3. ICTV MSL Host Column (What we have)
- **Source**: Master Species List Excel files
- **Coverage**: All ICTV-recognized species
- **Pros**:
  - Directly matches our taxonomy data
  - Authoritative for recognized species
  - We already have it parsed
- **Cons**:
  - Limited detail (often just major host groups)
  - Not comprehensive host range
  - Variable formatting across MSL versions
- **Best for**: Basic host categorization aligned with taxonomy

### 4. ViralZone (ExPASy)
- **URL**: https://viralzone.expasy.org/
- **Pros**:
  - Well-curated host information
  - Good coverage of major viral families
  - Clear host categories
- **Cons**:
  - No API
  - Manual extraction needed
  - May not cover all ICTV species
- **Best for**: Reference validation

### 5. GIDEON (Global Infectious Diseases and Epidemiology Network)
- **Pros**:
  - Clinical/epidemiological focus
  - Geographic distribution data
- **Cons**:
  - Subscription required
  - Limited to pathogens
  - Not comprehensive for all viruses
- **Best for**: Human/animal pathogen data

## Recommended Approach for Phase 6

Given our research question "Do generalist viruses have unstable taxonomy?", I recommend a **hybrid approach**:

1. **Primary Source**: ICTV MSL host data (already available)
   - Use this as our taxonomic baseline
   - Parse and categorize host breadth from MSL files

2. **Enrichment Source**: Viral Host Range Database API
   - Use to get experimental host range counts
   - Validate and expand MSL host categories
   - Recent update (Feb 2025) makes it current

3. **Validation Source**: NCBI Virus (spot checks)
   - Use for specific validation cases
   - Check emerging host associations

## Data Integration Strategy

```python
# Proposed approach
1. Parse MSL host columns → categorize as specialist/intermediate/generalist
2. Query VHRdb API for species with experimental host data
3. Combine to create host breadth scores
4. Analyze correlation with taxonomic stability from our MSL version tracking
```

## Key Metrics We Can Calculate

1. **Host Breadth Score**: 
   - Specialist (1 host species/genus)
   - Intermediate (2-5 hosts or 1 family)
   - Generalist (>5 hosts or >1 family)

2. **Taxonomic Stability**:
   - Number of reclassifications across MSL versions
   - Family changes
   - Name changes

3. **Correlation Analysis**:
   - Host breadth vs. reclassification frequency
   - Host breadth vs. family stability
   - Time to first reclassification

## Next Steps

1. Start with MSL host data parsing (immediate)
2. Design VHRdb API integration (if needed for enrichment)
3. Create host breadth categorization algorithm
4. Run stability correlation analysis

This approach maximizes use of our existing ICTV data while leveraging external sources only where necessary for enrichment.