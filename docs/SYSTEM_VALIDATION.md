# System Validation Guide for ICTV-git

## Overview

This guide explains how to validate ICTV-git system output and distinguish between real taxonomic changes and potential system errors.

## Validation Framework

### Automated Validation Checks

The system performs several automated validation checks on every taxonomic change:

#### 1. Hierarchy Consistency
```python
# Check that lower ranks have appropriate higher ranks
if genus exists: family must exist
if subfamily exists: family must exist  
if family exists: order should exist (warning if missing)
```

#### 2. Data Completeness
```python
# Essential data validation
species_name must not be empty
if classification exists: at least genus should be present
```

#### 3. Biological Plausibility
```python
# Check for impossible transitions
realm changes are extremely rare (warning)
kingdom changes within realm are unusual (warning)
```

#### 4. Consistency Checks
```python
# Cross-validation
family changes should typically involve genus changes
genus staying same while family changes is unusual (warning)
```

### Manual Validation Procedures

#### Quality Score Interpretation

**Quality Score = (Valid + 0.5×Warning) / Total**

| Score | Interpretation | Action Required |
|-------|---------------|-----------------|
| 95-100% | Excellent | Proceed with confidence |
| 85-94% | Good | Spot check warnings |
| 70-84% | Moderate | Review all warnings |
| 50-69% | Poor | Manual review required |
| <50% | Critical | Do not use, investigate errors |

#### Error Triage Process

1. **ERRORS (Fix required)**
   ```
   Priority: Critical
   Examples: Missing species names, hierarchy violations
   Action: Must be resolved before proceeding
   ```

2. **WARNINGS (Review required)**
   ```
   Priority: High  
   Examples: Unusual change patterns, incomplete data
   Action: Manual verification recommended
   ```

3. **VALID (No action needed)**
   ```
   Priority: None
   Examples: Standard reclassifications, expected patterns
   Action: Proceed normally
   ```

## Common Validation Scenarios

### Scenario 1: Major Taxonomic Reorganization

**Example**: Caudovirales restructuring (MSL36→MSL37)

**Expected patterns**:
- High warning count due to rank removal
- Many "restructure:rank_removal" changes
- Quality score may be lower due to unusual patterns

**Validation steps**:
1. Verify against ICTV proposals
2. Check that biological relationships preserved
3. Confirm systematic pattern across related species

**Red flags**:
- Species moving to unrelated families
- Inconsistent patterns within groups
- Missing proposal documentation

### Scenario 2: New Species Additions

**Example**: Large number of newly discovered viruses

**Expected patterns**:
- Many "added" status changes
- Quality score should remain high
- New species follow existing naming conventions

**Validation steps**:
1. Check addition rate is reasonable
2. Verify new species have complete classifications
3. Confirm naming follows ICTV conventions

**Red flags**:
- Massive sudden additions without documentation
- New species with incomplete classifications
- Inconsistent naming patterns

### Scenario 3: Data Format Changes

**Example**: MSL file structure evolution

**Expected patterns**:
- Parsing warnings due to column changes
- Some missing data for new fields
- Quality score may temporarily decrease

**Validation steps**:
1. Compare MSL file structures
2. Update parser for new format
3. Re-run analysis after parser updates

**Red flags**:
- Complete loss of data for major ranks
- Species names becoming corrupted
- Systematic hierarchy errors

## Validation Tools

### 1. Quality Assessment Script

```bash
# Run quality assessment
python scripts/enhanced_caudovirales_analysis.py

# Check output for:
# - Overall quality score
# - Validation status distribution  
# - Common issues list
```

### 2. Change Pattern Analysis

```bash
# Analyze specific change patterns
python scripts/taxonomy_lookup.py --species "Virus name" --history

# Look for:
# - Consistent change patterns
# - Logical progression through versions
# - Proper change classification
```

### 3. Cross-Version Validation

```bash
# Compare multiple version pairs
python scripts/migrate_dataset.py --export-tables

# Verify:
# - Consistency across version transitions
# - No contradictory changes
# - Proper change tracking
```

## Error Investigation Process

### Step 1: Identify Error Type

**Data Collection Error**:
- MSL file parsing failure
- Column mapping incorrect
- Character encoding issues

**System Logic Error**:
- Classification algorithm bug
- Validation rule incorrect
- Mapping logic failure

**Source Data Issue**:
- ICTV data inconsistency
- MSL file corruption
- Documentation mismatch

### Step 2: Trace Error Source

```bash
# Enable debug logging
export PYTHONPATH=$PWD/src
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from src.utils.taxonomy_diff import TaxonomyDiff
# Run analysis with verbose output
"
```

### Step 3: Validate Fix

After resolving issues:

1. **Re-run analysis**: Confirm error resolved
2. **Check quality score**: Should improve
3. **Spot check results**: Manual verification
4. **Document fix**: Update validation procedures

## Performance Benchmarks

### Expected Processing Times

| Operation | Small Dataset (1K species) | Large Dataset (10K species) | Full MSL (10K+ species) |
|-----------|----------------------------|------------------------------|--------------------------|
| Parse MSL | <5 seconds | 10-30 seconds | 30-60 seconds |
| Compare versions | <10 seconds | 30-60 seconds | 1-3 minutes |
| Generate report | <5 seconds | 10-20 seconds | 20-40 seconds |

### Memory Usage

| Dataset Size | Expected RAM | Peak RAM |
|--------------|--------------|----------|
| 1K species | <100 MB | <200 MB |
| 10K species | <500 MB | <1 GB |
| 50K species | <2 GB | <4 GB |

### Quality Thresholds

| MSL Transition | Expected Quality Score | Typical Warning Rate |
|----------------|------------------------|---------------------|
| Minor update (MSL37→MSL38) | >90% | <5% |
| Major reorganization (MSL36→MSL37) | 70-85% | 10-30% |
| Format change | 60-80% | 20-40% |

## Continuous Validation

### Automated Monitoring

Set up automated checks for new MSL releases:

```bash
# Daily check for new MSL files
# Run validation pipeline
# Alert on quality score drops
# Generate comparison reports
```

### Quality Metrics Dashboard

Track key metrics over time:
- Quality scores by MSL version
- Error rate trends
- Processing performance
- User feedback patterns

### Validation Test Suite

Maintain test cases for:
- Known good transitions
- Historical problem cases
- Edge case scenarios
- Performance benchmarks

## Reporting Issues

### Bug Reports

Include in bug reports:
- MSL versions involved
- Quality scores and validation output
- Specific species examples
- Expected vs. actual behavior
- System configuration details

### Data Quality Issues

Report to ICTV if system reveals:
- Consistent data inconsistencies
- Possible MSL file errors
- Missing documentation
- Contradictory information

### Enhancement Requests

Suggest improvements for:
- New validation checks
- Better error messages
- Performance optimizations
- Additional analysis features

## Best Practices Summary

1. **Always check quality scores** before using results
2. **Review warnings manually** for important analyses  
3. **Cross-validate** against ICTV documentation
4. **Test with known data** before production use
5. **Monitor performance** and quality trends
6. **Document** any manual validation steps
7. **Report issues** to help improve the system

Remember: The goal is to distinguish real biological changes from system artifacts, ensuring researchers can trust the taxonomic change analysis.