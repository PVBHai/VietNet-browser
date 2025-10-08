# Vietnamese Domain-Specific Lexicons

This document describes the 4 domain-specific Vietnamese lexicons created from the main VietNet lexicon.

## 📁 Project Structure

```
vietnet_wn_lmf_project/
├── food/
│   ├── vietnet_food_all.xml                    # Food lexicon (all entries)
│   └── vietnet_food_high_confidence.xml        # Food lexicon (high confidence only)
├── animal/
│   ├── vietnet_animal_all.xml                  # Animal lexicon (all entries)
│   └── vietnet_animal_high_confidence.xml      # Animal lexicon (high confidence only)
└── create_domain_lexicons.py                   # Generator script
```

## 🎯 Lexicon Specifications

### 1. 🍎 **Food Domain Lexicons**

**Root Concept**: `oewn-00021445-n` (food - "any substance that can be metabolized by an animal to give energy and build tissue")

#### **Food (All) - `vietnet_food_all.xml`**
- **Synsets**: 153 Vietnamese food concepts
- **Words**: 309 Vietnamese food-related words
- **Relations**: 220 hypernym/hyponym relations
- **Filter**: All entries (is_same = True/False)
- **Lexicon ID**: `vietnet-food`

#### **Food (High Confidence) - `vietnet_food_high_confidence.xml`**
- **Synsets**: 119 Vietnamese food concepts
- **Words**: 193 Vietnamese food-related words
- **Relations**: 164 hypernym/hyponym relations
- **Filter**: Only high-confidence translations (is_same = True)
- **Lexicon ID**: `vietnet-food-hc`

### 2. 🐾 **Animal Domain Lexicons**

**Root Concept**: `oewn-00015568-n` (animal - "a living organism characterized by voluntary movement")

#### **Animal (All) - `vietnet_animal_all.xml`**
- **Synsets**: 470 Vietnamese animal concepts
- **Words**: 884 Vietnamese animal-related words
- **Relations**: 452 hypernym/hyponym relations
- **Filter**: All entries (is_same = True/False)
- **Lexicon ID**: `vietnet-animal`

#### **Animal (High Confidence) - `vietnet_animal_high_confidence.xml`**
- **Synsets**: 389 Vietnamese animal concepts
- **Words**: 640 Vietnamese animal-related words
- **Relations**: 338 hypernym/hyponym relations
- **Filter**: Only high-confidence translations (is_same = True)
- **Lexicon ID**: `vietnet-animal-hc`

## 📊 Statistics Comparison

| Lexicon | Domain | Confidence | Synsets | Words | Relations |
|---------|--------|------------|---------|-------|-----------|
| Food (All) | 🍎 Food | All | 153 | 309 | 220 |
| Food (HC) | 🍎 Food | High | 119 | 193 | 164 |
| Animal (All) | 🐾 Animal | All | 470 | 884 | 452 |
| Animal (HC) | 🐾 Animal | High | 389 | 640 | 338 |

## 🔗 Relation Types

Each lexicon contains **only hypernym and hyponym relations**:
- **Hypernym**: Broader, more general concepts (e.g., "thức ăn" is hypernym of "cơm")
- **Hyponym**: More specific, narrower concepts (e.g., "cơm" is hyponym of "thức ăn")

## 🇻🇳 Sample Vietnamese Words

### Food Domain
- **General**: thức ăn, mồi, cơm cháo
- **Dairy**: sữa, sữa bò, sữa mẹ
- **Grains**: cơm, bánh, cao lương
- **Beverages**: nước, trà, rượu

### Animal Domain
- **General**: động vật, vật, sinh vật
- **Mammals**: thú, chó, mèo, bò
- **Birds**: chim, gà, vịt
- **Insects**: côn trùng, kiến, ong

## 🚀 Usage Examples

### With wn Library

```python
import wn

# Add a domain lexicon
wn.add('food/vietnet_food_high_confidence.xml')

# Search Vietnamese food words
words = wn.words("thức ăn", lexicon="vietnet-food-hc")
for word in words:
    print(f"Word: {word.lemma()}")
    
    # Get synset and relations
    synset = word.senses()[0].synset()
    print(f"Definition: {synset.definition()}")
    
    # Check hierarchical relations
    relations = synset.relations()
    if 'hyponym' in relations:
        print("More specific foods:")
        for hyponym in relations['hyponym']:
            print(f"  - {hyponym.id}: {hyponym.definition()[:50]}...")
```

### Direct XML Usage

```python
import xml.etree.ElementTree as ET

# Parse lexicon
tree = ET.parse('animal/vietnet_animal_all.xml')
root = tree.getroot()
lexicon = root.find('Lexicon')

# Find synsets with relations
for synset in lexicon.findall('Synset'):
    relations = synset.findall('SynsetRelation')
    if len(relations) > 5:  # Synsets with many relations
        print(f"Rich synset: {synset.get('id')}")
        definition = synset.find('Definition')
        if definition is not None:
            print(f"Definition: {definition.text}")
```

## 🔧 Technical Details

### Creation Algorithm

1. **Domain Identification**: 
   - Find all hyponyms of root concepts using BFS traversal
   - Food: 1,602 English synsets found
   - Animal: 4,008 English synsets found

2. **Vietnamese Data Filtering**:
   - Filter original CSV by `match_id` in domain synsets
   - Apply confidence filter if specified (`is_same = True`)

3. **Relation Extraction**:
   - Extract hypernym/hyponym relations from English WordNet
   - Map to Vietnamese synset IDs
   - Only keep relations where both source and target exist in Vietnamese data

4. **XML Generation**:
   - Follow WN-LMF 1.3 standard
   - Create unique Vietnamese synset IDs: `{lexicon-id}-{counter:08d}-{pos}`
   - Include definitions, examples, and relations

### Quality Metrics

- **Coverage**: Food domain covers 1.4% of total data, Animal domain covers 4.1%
- **Confidence**: High-confidence versions retain 62% (food) and 72% (animal) of entries
- **Relations**: Dense semantic networks with hierarchical structure
- **Validation**: All lexicons pass WN-LMF DTD validation

## 📝 File Formats

All lexicons follow the **WN-LMF 1.3** standard:
- XML encoding: UTF-8
- DTD validation: `http://globalwordnet.github.io/schemas/WN-LMF-1.3.dtd`
- Namespace: Dublin Core metadata
- Compatible with: wn library, Global WordNet tools

## 🎯 Use Cases

### Research Applications
- **Semantic Analysis**: Study Vietnamese food/animal terminology
- **Cross-linguistic Studies**: Compare Vietnamese-English conceptual mappings
- **Computational Linguistics**: Train domain-specific NLP models

### Practical Applications
- **Recipe Systems**: Vietnamese cooking applications
- **Veterinary Systems**: Animal health and classification
- **Educational Tools**: Vietnamese language learning
- **Search Engines**: Domain-specific semantic search

## 🔄 Regeneration

To recreate or modify the lexicons:

```bash
# Regenerate all 4 lexicons
python3 create_domain_lexicons.py

# The script will:
# 1. Find hyponyms of food/animal in English WordNet
# 2. Filter Vietnamese data by domain and confidence
# 3. Extract hypernym/hyponym relations
# 4. Generate WN-LMF XML files
```

## ✅ Validation Status

All 4 lexicons have been:
- ✅ **Structurally validated**: Pass XML and WN-LMF DTD validation
- ✅ **Semantically verified**: Relations form coherent hierarchies
- ✅ **Library tested**: Successfully integrate with wn library
- ✅ **Content checked**: Vietnamese definitions and examples preserved

---

**Created**: October 2, 2025  
**Format**: WN-LMF 1.3  
**Source**: VietNet Vietnamese WordNet Project  
**License**: CC-BY-4.0
