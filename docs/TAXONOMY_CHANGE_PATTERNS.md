# Understanding Taxonomy Change Patterns in ICTV-git

## Overview

This document explains the different types of taxonomic changes captured by ICTV-git and helps distinguish between expected biological patterns and potential system errors.

## Change Types Explained

### 1. RECLASSIFICATION
**What it means**: Species moved to different taxonomic groups based on new biological understanding.

**Subtypes**:
- `family_change`: Species moved to entirely different family (e.g., virus reclassified based on genomic analysis)
- `genus_change`: Species moved to different genus within same family
- `subfamily_change`: Minor reclassification within family
- `high_level_change`: Rare changes at realm/kingdom level

**Expected patterns**:
- ✅ Family change with corresponding genus change
- ✅ Genus change within same family
- ✅ Changes supported by new genomic data

**Warning signs**:
- ⚠️ Family changes but genus stays the same (rare, verify manually)
- ⚠️ Multiple unrelated ranks changing simultaneously

**Examples**:
```
Escherichia virus T4: Myoviridae → Straboviridae (family_change)
Reason: Genomic analysis showed different evolutionary lineage
```

### 2. RESTRUCTURE
**What it means**: Taxonomic hierarchy reorganized without changing species' biological relationships.

**Subtypes**:
- `rank_removal`: Taxonomic rank eliminated (e.g., order Caudovirales removed)
- `rank_addition`: New taxonomic rank added to hierarchy
- `order_class_change`: Reorganization at order/class level

**Expected patterns**:
- ✅ Order removed but family/genus unchanged (hierarchy simplification)
- ✅ New intermediate ranks added for clarity
- ✅ Multiple species affected simultaneously

**The Caudovirales Example**:
```
Before (MSL36): Realm > Kingdom > Phylum > Class > ORDER: Caudovirales > Family: Myoviridae > Genus: Tequatrovirus
After (MSL37):  Realm > Kingdom > Phylum > Class > ∅ > Family: Myoviridae > Genus: Tequatrovirus
```
This is **restructure:rank_removal**, not species reclassification!

### 3. NOMENCLATURE
**What it means**: Name changes without biological reclassification.

**Subtypes**:
- `species_rename`: Species name updated
- `taxon_rename`: Higher-level taxon renamed
- `binomial_adoption`: Switch to binomial nomenclature

**Expected patterns**:
- ✅ Same biological position, new name
- ✅ Systematic name updates across multiple species

## Validation Status Levels

### VALID ✅
- All data consistent and logical
- Changes follow expected patterns
- No hierarchy violations

### WARNING ⚠️
- Unusual but potentially correct patterns
- Requires manual verification
- Common warnings:
  - Family changed but genus unchanged
  - Rank skipping (genus without family)
  - High-level changes (realm/kingdom)

### ERROR ❌
- Clear data inconsistencies
- Hierarchy violations
- Missing required information
- Common errors:
  - Missing species names
  - Subfamily without family
  - Circular hierarchies

## Severity Levels

### MINOR
- Subfamily-level changes
- Cosmetic nomenclature updates
- Low impact on research

### NORMAL
- Genus-level reclassifications
- Order/class restructuring
- Typical taxonomic updates

### MAJOR
- Family-level reclassifications
- Significant biological insights
- High impact on research

### CRITICAL
- Realm/kingdom changes
- Fundamental reorganizations
- Extremely rare events

## Expected vs. Problematic Patterns

### EXPECTED PATTERNS ✅

#### Caudovirales "Dissolution" (MSL36→MSL37)
```
Pattern: restructure:rank_removal
Count: 95 species
Explanation: ICTV removed the order rank but kept species in original families
Impact: Hierarchy simplified, biological relationships unchanged
```

#### Family Splitting Based on Genomics
```
Pattern: reclassification:family_change
Example: Siphoviridae → Multiple new families
Explanation: Genomic analysis revealed distinct evolutionary lineages
Impact: Better reflects biological reality
```

#### Binomial Nomenclature Adoption
```
Pattern: nomenclature:binomial_adoption
Example: "Virus name" → "Genus species"
Explanation: Standardization with biological nomenclature
Impact: Consistency with other organisms
```

### PROBLEMATIC PATTERNS ❌

#### Orphaned Classifications
```
Error: Genus exists without family
Example: Species has genus="Newvirus" but family=""
Cause: Data processing error or incomplete update
```

#### Impossible Transitions
```
Error: Realm changes
Example: Riboviria → Duplodnaviria
Cause: Fundamental biological misclassification or data error
```

#### Missing Species Names
```
Error: Classification exists but species=""
Cause: Data corruption or parsing failure
```

## Quality Assessment

### Data Quality Score
Calculated as: `(valid_changes + 0.5 × warning_changes) / total_changes`

- **>90%**: Excellent data quality
- **70-90%**: Good quality, some manual review needed
- **50-70%**: Moderate quality, significant review required
- **<50%**: Poor quality, major data issues

### Common Issue Patterns

#### Low Quality Score Causes:
1. **Parsing errors**: Species names not extracted correctly
2. **Incomplete updates**: Some ranks updated, others missed
3. **Format changes**: MSL structure changed between versions

#### High Warning Count Causes:
1. **Major reorganizations**: Large-scale taxonomic restructuring
2. **Methodology changes**: New classification criteria adopted
3. **Data model evolution**: ICTV hierarchy structure updated

## Best Practices for Users

### For Researchers
1. **Check change type**: Understand if it's reclassification vs. restructure
2. **Review warnings**: Manual verification for unusual patterns
3. **Use migration tools**: Automated dataset updates with change tracking
4. **Track history**: Follow species through multiple MSL versions

### For Database Maintainers  
1. **Validate before importing**: Check quality scores and error patterns
2. **Implement gradual updates**: Stage changes by severity level
3. **Preserve provenance**: Keep change history and reasoning
4. **Monitor patterns**: Track validation trends across releases

### For Tool Developers
1. **Handle rank removal**: Don't assume all ranks always exist
2. **Validate hierarchies**: Check parent-child relationships
3. **Support versioning**: Allow users to specify MSL version
4. **Provide fallbacks**: Handle missing or changed taxa gracefully

## Troubleshooting Guide

### "Species disappeared"
- **Check**: Renamed rather than removed?
- **Look for**: Similar names in new version
- **Verify**: Change type classification

### "Validation errors"
- **Review**: Error details and notes
- **Cross-check**: Against ICTV documentation
- **Consider**: Reporting data quality issues

### "Unexpected changes"
- **Classify**: Reclassification vs. restructure vs. nomenclature
- **Research**: ICTV proposals and rationale
- **Validate**: Against other trusted sources

## Contributing

Found a pattern not covered here? Please:
1. Document the pattern with examples
2. Classify the change type and severity
3. Determine if it's expected or problematic
4. Submit issues or pull requests with updates

## References

- [ICTV Master Species Lists](https://ictv.global/msl)
- [ICTV Taxonomy Proposals](https://ictv.global/proposals)
- [Viral Taxonomy Guidelines](https://ictv.global/about/code-of-ethics)