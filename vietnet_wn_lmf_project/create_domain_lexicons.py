#!/usr/bin/env python3
"""
Domain-Specific Vietnamese Lexicon Creator
Creates specialized lexicons for food and animal domains with hyponym/hypernym relations
"""

import pandas as pd
import xml.etree.ElementTree as ET
from xml.dom import minidom
import re
from datetime import datetime
import wn
from collections import defaultdict, deque

def get_all_hyponyms(root_synset_id, lexicon='oewn'):
    """
    Get all hyponyms (including indirect) of a root synset using BFS
    
    Args:
        root_synset_id: The root synset ID (e.g., 'oewn-00021445-n' for food)
        lexicon: WordNet lexicon to use
    
    Returns:
        Set of all hyponym synset IDs
    """
    print(f"🔍 Finding all hyponyms of {root_synset_id}...")
    
    try:
        root_synset = wn.synset(root_synset_id, lexicon=lexicon)
    except:
        print(f"❌ Could not find root synset: {root_synset_id}")
        return set()
    
    all_hyponyms = set()
    queue = deque([root_synset])
    visited = set([root_synset_id])
    
    while queue:
        current_synset = queue.popleft()
        current_id = current_synset.id
        
        # Get direct hyponyms
        relations = current_synset.relations()
        if 'hyponym' in relations:
            for hyponym in relations['hyponym']:
                hyponym_id = hyponym.id
                if hyponym_id not in visited:
                    all_hyponyms.add(hyponym_id)
                    visited.add(hyponym_id)
                    queue.append(hyponym)
    
    print(f"✅ Found {len(all_hyponyms)} hyponyms for {root_synset_id}")
    return all_hyponyms

def filter_vietnamese_data_by_domain(csv_file_path, domain_synsets, is_same_filter=None):
    """
    Filter Vietnamese data to only include synsets in the domain
    
    Args:
        csv_file_path: Path to Vietnamese CSV data
        domain_synsets: Set of English synset IDs in the domain
        is_same_filter: If True, only keep is_same=True; if False, only keep is_same=False; if None, keep all
    
    Returns:
        Filtered DataFrame
    """
    df = pd.read_csv(csv_file_path)
    print(f"📖 Original data: {len(df)} entries")
    
    # Add root synset to domain (include the root itself)
    domain_synsets_with_root = domain_synsets.copy()
    
    # Filter by domain (match_id in domain synsets)
    domain_df = df[df['match_id'].isin(domain_synsets_with_root)]
    print(f"🎯 Domain filtered: {len(domain_df)} entries")
    
    # Filter by is_same if specified
    if is_same_filter is not None:
        domain_df = domain_df[domain_df['is_same'] == is_same_filter]
        filter_text = "TRUE" if is_same_filter else "FALSE"
        print(f"✅ is_same={filter_text} filtered: {len(domain_df)} entries")
    
    return domain_df

def extract_domain_relations(domain_synsets, lexicon='oewn'):
    """
    Extract only hypernym/hyponym relations within the domain
    """
    print(f"🔗 Extracting hypernym/hyponym relations for {len(domain_synsets)} synsets...")
    
    relations_map = defaultdict(list)
    
    for synset_id in domain_synsets:
        try:
            synset = wn.synset(synset_id, lexicon=lexicon)
            relations = synset.relations()
            
            # Only keep hypernym and hyponym relations
            for rel_type in ['hypernym', 'hyponym']:
                if rel_type in relations:
                    for target_synset in relations[rel_type]:
                        target_id = target_synset.id
                        # Only include if target is also in domain
                        if target_id in domain_synsets:
                            relations_map[synset_id].append({
                                'type': rel_type,
                                'target': target_id
                            })
        except:
            continue
    
    total_relations = sum(len(rels) for rels in relations_map.values())
    print(f"✅ Extracted {total_relations} hypernym/hyponym relations")
    return relations_map

def create_domain_lexicon(csv_file_path, domain_synsets, relations_map, output_xml_path, 
                         lexicon_id, lexicon_label, is_same_filter=None):
    """
    Create a domain-specific Vietnamese lexicon
    """
    # Filter Vietnamese data for this domain
    df = filter_vietnamese_data_by_domain(csv_file_path, domain_synsets, is_same_filter)
    
    if len(df) == 0:
        print(f"❌ No data found for domain. Skipping {output_xml_path}")
        return None
    
    # Create XML structure
    xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>\n'
    doctype = '<!DOCTYPE LexicalResource SYSTEM "http://globalwordnet.github.io/schemas/WN-LMF-1.3.dtd">\n'
    
    root = ET.Element("LexicalResource")
    root.set("xmlns:dc", "https://globalwordnet.github.io/schemas/dc/")
    
    lexicon = ET.SubElement(root, "Lexicon")
    lexicon.set("id", lexicon_id)
    lexicon.set("label", lexicon_label)
    lexicon.set("language", "vi")
    lexicon.set("email", "vietnet@example.com")
    lexicon.set("license", "https://creativecommons.org/licenses/by/4.0/")
    lexicon.set("version", "1.0")
    lexicon.set("url", "https://github.com/vietnet/lexicon")
    lexicon.set("citation", f"VietNet: {lexicon_label}")
    lexicon.set("dc:publisher", "VietNet Project")
    
    # Vietnamese POS mapping
    pos_mapping = {
        'd': 'n', 'đ': 'n', 't': 'a', 'đt': 'v', 'tt': 'r', 
        'g': 'p', 'l': 'c', 'th': 'x', 'đm': 'x'
    }
    
    # Group by synset and create Vietnamese synsets
    synset_groups = df.groupby('match_id')
    synset_counter = 1
    lexical_entry_counter = 1
    eng_to_viet_map = {}
    
    print(f"🔄 Creating {len(synset_groups)} synsets...")
    
    # First pass: Create synsets
    for english_synset_id, group in synset_groups:
        original_pos = str(group.iloc[0]['pos']).lower().strip()
        pos = pos_mapping.get(original_pos, 'n')
        
        vietnamese_synset_id = f"{lexicon_id}-{synset_counter:08d}-{pos}"
        eng_to_viet_map[english_synset_id] = vietnamese_synset_id
        
        # Create Synset element
        synset = ET.SubElement(lexicon, "Synset")
        synset.set("id", vietnamese_synset_id)
        synset.set("ili", english_synset_id)
        
        # Add definition
        definition_text = str(group.iloc[0]['meaning']).strip()
        if definition_text and definition_text != 'nan':
            definition = ET.SubElement(synset, "Definition")
            definition.text = definition_text
        
        # Add examples (avoid duplicates)
        examples_added = set()
        for _, row in group.iterrows():
            if pd.notna(row['example']) and str(row['example']).strip():
                example_text = str(row['example']).strip()
                example_text = re.sub(r'^#\s*', '', example_text)
                example_text = re.sub(r'#', '', example_text)
                example_text = example_text.strip()
                
                if example_text and example_text not in examples_added:
                    example = ET.SubElement(synset, "Example")
                    example.text = example_text
                    examples_added.add(example_text)
        
        synset_counter += 1
    
    # Second pass: Add relations
    print(f"🔗 Adding relations...")
    relations_added = 0
    
    for synset_elem in lexicon.findall('Synset'):
        ili = synset_elem.get('ili')
        
        if ili in relations_map:
            for relation in relations_map[ili]:
                rel_type = relation['type']
                target_eng_id = relation['target']
                
                if target_eng_id in eng_to_viet_map:
                    target_viet_id = eng_to_viet_map[target_eng_id]
                    
                    synset_relation = ET.SubElement(synset_elem, "SynsetRelation")
                    synset_relation.set("relType", rel_type)
                    synset_relation.set("target", target_viet_id)
                    
                    relations_added += 1
    
    # Third pass: Create lexical entries
    print(f"📝 Creating lexical entries...")
    
    for english_synset_id, group in synset_groups:
        vietnamese_synset_id = eng_to_viet_map[english_synset_id]
        original_pos = str(group.iloc[0]['pos']).lower().strip()
        pos = pos_mapping.get(original_pos, 'n')
        
        words_added = set()
        for _, row in group.iterrows():
            word = str(row['word']).strip()
            if word and word != 'nan' and word not in words_added:
                lexical_entry = ET.SubElement(lexicon, "LexicalEntry")
                entry_id = f"{lexicon_id}-{lexical_entry_counter:08d}"
                lexical_entry.set("id", entry_id)
                
                lemma = ET.SubElement(lexical_entry, "Lemma")
                lemma.set("writtenForm", word)
                lemma.set("partOfSpeech", pos)
                
                sense = ET.SubElement(lexical_entry, "Sense")
                sense_id = f"{entry_id}-1"
                sense.set("id", sense_id)
                sense.set("synset", vietnamese_synset_id)
                
                if 'is_same' in row and pd.notna(row['is_same']):
                    if str(row['is_same']).lower() in ['true', '1', 'yes']:
                        sense.set("confidenceScore", "1.0")
                    else:
                        sense.set("confidenceScore", "0.8")
                
                words_added.add(word)
                lexical_entry_counter += 1
    
    # Generate XML
    rough_string = ET.tostring(root, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    pretty_lines = reparsed.toprettyxml(indent="  ", encoding=None).split('\n')
    pretty_lines = [line for line in pretty_lines[1:] if line.strip()]
    pretty_xml = '\n'.join(pretty_lines)
    final_xml = xml_declaration + doctype + pretty_xml
    
    # Write to file
    with open(output_xml_path, 'w', encoding='utf-8') as f:
        f.write(final_xml)
    
    print(f"✅ Created {output_xml_path}")
    print(f"📊 Synsets: {synset_counter - 1}")
    print(f"📝 Lexical entries: {lexical_entry_counter - 1}")
    print(f"🔗 Relations: {relations_added}")
    
    return output_xml_path

def main():
    print("🚀 CREATING DOMAIN-SPECIFIC VIETNAMESE LEXICONS")
    print("=" * 60)
    
    # Define root synsets
    FOOD_ROOT = "oewn-00021445-n"  # food
    ANIMAL_ROOT = "oewn-00015568-n"  # animal
    
    csv_file = "vietnet_wn_lmf.csv"
    
    # Get all hyponyms for each domain
    print("\\n🍎 FOOD DOMAIN:")
    food_hyponyms = get_all_hyponyms(FOOD_ROOT)
    food_hyponyms.add(FOOD_ROOT)  # Include root
    
    print("\\n🐾 ANIMAL DOMAIN:")
    animal_hyponyms = get_all_hyponyms(ANIMAL_ROOT)
    animal_hyponyms.add(ANIMAL_ROOT)  # Include root
    
    # Extract relations for each domain
    print("\\n🔗 EXTRACTING RELATIONS:")
    food_relations = extract_domain_relations(food_hyponyms)
    animal_relations = extract_domain_relations(animal_hyponyms)
    
    # Create 4 lexicons
    lexicons = [
        {
            'domain_synsets': food_hyponyms,
            'relations': food_relations,
            'output_path': 'food/vietnet_food_all.xml',
            'lexicon_id': 'vietnet-food',
            'lexicon_label': 'VietNet Vietnamese Food Lexicon (All)',
            'is_same_filter': None
        },
        {
            'domain_synsets': food_hyponyms,
            'relations': food_relations,
            'output_path': 'food/vietnet_food_high_confidence.xml',
            'lexicon_id': 'vietnet-food-hc',
            'lexicon_label': 'VietNet Vietnamese Food Lexicon (High Confidence)',
            'is_same_filter': True
        },
        {
            'domain_synsets': animal_hyponyms,
            'relations': animal_relations,
            'output_path': 'animal/vietnet_animal_all.xml',
            'lexicon_id': 'vietnet-animal',
            'lexicon_label': 'VietNet Vietnamese Animal Lexicon (All)',
            'is_same_filter': None
        },
        {
            'domain_synsets': animal_hyponyms,
            'relations': animal_relations,
            'output_path': 'animal/vietnet_animal_high_confidence.xml',
            'lexicon_id': 'vietnet-animal-hc',
            'lexicon_label': 'VietNet Vietnamese Animal Lexicon (High Confidence)',
            'is_same_filter': True
        }
    ]
    
    print("\\n🏗️ CREATING LEXICONS:")
    for i, config in enumerate(lexicons, 1):
        print(f"\\n{i}. {config['lexicon_label']}")
        create_domain_lexicon(
            csv_file,
            config['domain_synsets'],
            config['relations'],
            config['output_path'],
            config['lexicon_id'],
            config['lexicon_label'],
            config['is_same_filter']
        )
    
    print("\\n" + "=" * 60)
    print("✅ ALL DOMAIN LEXICONS CREATED SUCCESSFULLY!")
    print("\\n📁 Files created:")
    for config in lexicons:
        print(f"  - {config['output_path']}")

if __name__ == "__main__":
    main()
