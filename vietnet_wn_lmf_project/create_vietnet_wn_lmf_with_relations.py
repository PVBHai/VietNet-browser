#!/usr/bin/env python3
"""
Enhanced VietNet to WN-LMF Converter with Synset Relations
Converts Vietnamese lexical data to WordNet Lexical Markup Framework format
and adds synset relations based on English WordNet mappings.
"""

import pandas as pd
import xml.etree.ElementTree as ET
from xml.dom import minidom
import re
from datetime import datetime
import sys
import os
import wn
from collections import defaultdict

def extract_english_relations(match_ids, lexicon='oewn'):
    """
    Extract relations from English WordNet for the given match_ids
    
    Args:
        match_ids: List of English WordNet synset IDs
        lexicon: English WordNet lexicon to use
    
    Returns:
        Dictionary mapping synset_id -> list of relations
    """
    print(f"🔍 Extracting relations from {lexicon} for {len(match_ids)} synsets...")
    
    relations_map = defaultdict(list)
    processed = 0
    
    for match_id in match_ids:
        if match_id == 'none' or pd.isna(match_id):
            continue
            
        try:
            # Get the English synset
            synset = wn.synset(match_id, lexicon=lexicon)
            if synset:
                relations = synset.relations()
                
                # Relations is a dict: {relation_type: [target_synsets]}
                for rel_type, target_synsets in relations.items():
                    for target_synset in target_synsets:
                        target_id = target_synset.id
                        
                        # Only include relations where target is also in our Vietnamese data
                        if target_id in match_ids:
                            relations_map[match_id].append({
                                'type': rel_type,
                                'target': target_id
                            })
                
                processed += 1
                if processed % 1000 == 0:
                    print(f"  Processed {processed} synsets...")
                    
        except Exception as e:
            # Skip synsets that can't be found
            continue
    
    print(f"✅ Extracted relations for {len(relations_map)} synsets")
    return relations_map

def create_wn_lmf_with_relations(csv_file_path, output_xml_path, lexicon_id="vietnet", lexicon_label="VietNet Vietnamese Lexicon"):
    """
    Convert VietNet CSV data to WN-LMF XML format with synset relations
    """
    
    # Read the CSV data
    df = pd.read_csv(csv_file_path)
    print(f"📖 Loaded {len(df)} entries from {csv_file_path}")
    
    # Get unique match_ids for relation extraction
    unique_match_ids = set(df['match_id'].dropna().unique())
    unique_match_ids.discard('none')
    print(f"🔗 Found {len(unique_match_ids)} unique English synset mappings")
    
    # Extract relations from English WordNet
    relations_map = extract_english_relations(unique_match_ids)
    
    # Create XML with proper DOCTYPE declaration
    xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>\n'
    doctype = '<!DOCTYPE LexicalResource SYSTEM "http://globalwordnet.github.io/schemas/WN-LMF-1.3.dtd">\n'
    
    # Create root element with proper namespace
    root = ET.Element("LexicalResource")
    root.set("xmlns:dc", "https://globalwordnet.github.io/schemas/dc/")
    
    # Create Lexicon element with all required attributes
    lexicon = ET.SubElement(root, "Lexicon")
    lexicon.set("id", lexicon_id)
    lexicon.set("label", lexicon_label)
    lexicon.set("language", "vi")  # Vietnamese BCP-47 code
    lexicon.set("email", "vietnet@example.com")
    lexicon.set("license", "https://creativecommons.org/licenses/by/4.0/")
    lexicon.set("version", "1.1")  # Increment version for relations
    lexicon.set("url", "https://github.com/vietnet/lexicon")
    lexicon.set("citation", "VietNet: Vietnamese WordNet Lexicon with Relations")
    lexicon.set("dc:publisher", "VietNet Project")
    
    # Vietnamese part-of-speech mapping to WordNet standard
    pos_mapping = {
        'd': 'n',   # danh từ -> noun
        'đ': 'n',   # danh từ -> noun  
        't': 'a',   # tính từ -> adjective
        'đt': 'v',  # động từ -> verb
        'tt': 'r',  # trạng từ -> adverb
        'g': 'p',   # giới từ -> adposition
        'l': 'c',   # liên từ -> conjunction
        'th': 'x',  # thán từ -> other
        'đm': 'x'   # đại từ -> other
    }
    
    # Group entries by synset_id to create synsets
    synset_groups = df.groupby('match_id')
    
    synset_counter = 1
    lexical_entry_counter = 1
    
    # Create mapping from English synset ID to Vietnamese synset ID
    eng_to_viet_synset_map = {}
    
    print(f"🔄 Processing {len(synset_groups)} synset groups...")
    
    # First pass: Create synsets and build mapping
    for synset_id, group in synset_groups:
        # Determine part of speech from first entry
        original_pos = str(group.iloc[0]['pos']).lower().strip()
        pos = pos_mapping.get(original_pos, 'n')  # default to noun
        
        # Create internal synset ID
        internal_synset_id = f"{lexicon_id}-{synset_counter:08d}-{pos}"
        eng_to_viet_synset_map[synset_id] = internal_synset_id
        
        # Create Synset element
        synset = ET.SubElement(lexicon, "Synset")
        synset.set("id", internal_synset_id)
        synset.set("ili", synset_id)  # Inter-Lingual Index mapping
        
        # Add definition from the first entry
        definition_text = str(group.iloc[0]['meaning']).strip()
        if definition_text and definition_text != 'nan':
            definition = ET.SubElement(synset, "Definition")
            definition.text = definition_text
        
        # Add examples if available (avoid duplicates)
        examples_added = set()
        for _, row in group.iterrows():
            if pd.notna(row['example']) and str(row['example']).strip():
                example_text = str(row['example']).strip()
                # Clean up example text (remove # markers)
                example_text = re.sub(r'^#\s*', '', example_text)
                example_text = re.sub(r'#', '', example_text)
                example_text = example_text.strip()
                
                if example_text and example_text not in examples_added:
                    example = ET.SubElement(synset, "Example")
                    example.text = example_text
                    examples_added.add(example_text)
        
        synset_counter += 1
    
    # Second pass: Add relations
    print(f"🔗 Adding synset relations...")
    relations_added = 0
    
    for synset_elem in lexicon.findall('Synset'):
        synset_id = synset_elem.get('id')
        ili = synset_elem.get('ili')
        
        if ili in relations_map:
            for relation in relations_map[ili]:
                rel_type = relation['type']
                target_eng_id = relation['target']
                
                # Map English target to Vietnamese synset
                if target_eng_id in eng_to_viet_synset_map:
                    target_viet_id = eng_to_viet_synset_map[target_eng_id]
                    
                    # Create SynsetRelation element
                    synset_relation = ET.SubElement(synset_elem, "SynsetRelation")
                    synset_relation.set("relType", rel_type)
                    synset_relation.set("target", target_viet_id)
                    
                    relations_added += 1
    
    print(f"✅ Added {relations_added} synset relations")
    
    # Third pass: Create lexical entries
    print(f"📝 Creating lexical entries...")
    
    for synset_id, group in synset_groups:
        internal_synset_id = eng_to_viet_synset_map[synset_id]
        original_pos = str(group.iloc[0]['pos']).lower().strip()
        pos = pos_mapping.get(original_pos, 'n')
        
        # Create LexicalEntry for each unique word in this synset
        words_added = set()
        for _, row in group.iterrows():
            word = str(row['word']).strip()
            if word and word != 'nan' and word not in words_added:
                # Create LexicalEntry
                lexical_entry = ET.SubElement(lexicon, "LexicalEntry")
                entry_id = f"{lexicon_id}-{lexical_entry_counter:08d}"
                lexical_entry.set("id", entry_id)
                
                # Create Lemma with required attributes
                lemma = ET.SubElement(lexical_entry, "Lemma")
                lemma.set("writtenForm", word)
                lemma.set("partOfSpeech", pos)
                
                # Create Sense linking to the synset
                sense = ET.SubElement(lexical_entry, "Sense")
                sense_id = f"{entry_id}-1"
                sense.set("id", sense_id)
                sense.set("synset", internal_synset_id)
                
                # Add confidence based on is_same field
                if 'is_same' in row and pd.notna(row['is_same']):
                    if str(row['is_same']).lower() in ['true', '1', 'yes']:
                        sense.set("confidenceScore", "1.0")
                    else:
                        sense.set("confidenceScore", "0.8")
                
                words_added.add(word)
                lexical_entry_counter += 1
    
    # Convert to string with proper formatting
    rough_string = ET.tostring(root, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    
    # Get pretty XML without the default XML declaration
    pretty_lines = reparsed.toprettyxml(indent="  ", encoding=None).split('\n')
    # Remove the first line (XML declaration) and empty lines
    pretty_lines = [line for line in pretty_lines[1:] if line.strip()]
    pretty_xml = '\n'.join(pretty_lines)
    
    # Combine with proper XML declaration and DOCTYPE
    final_xml = xml_declaration + doctype + pretty_xml
    
    # Write to file
    with open(output_xml_path, 'w', encoding='utf-8') as f:
        f.write(final_xml)
    
    print(f"✅ Created enhanced WN-LMF file: {output_xml_path}")
    print(f"📊 Total synsets: {synset_counter - 1}")
    print(f"📝 Total lexical entries: {lexical_entry_counter - 1}")
    print(f"🔗 Total synset relations: {relations_added}")
    print(f"🎯 Format: WN-LMF 1.3 with synset relations")
    
    return output_xml_path

def main():
    """
    Main function to convert VietNet data to WN-LMF format with relations
    """
    print("🚀 Enhanced VietNet to WN-LMF Converter (with Relations)")
    print("=" * 60)
    
    # Input and output file paths
    csv_input = "vietnet_wn_lmf.csv"
    xml_output = "vietnet_lexicon_with_relations.xml"
    
    # Check if input file exists
    if not os.path.exists(csv_input):
        print(f"❌ Input file not found: {csv_input}")
        print("Please ensure the CSV file is in the current directory")
        return
    
    try:
        # Create the enhanced WN-LMF file with relations
        print(f"📖 Converting {csv_input} to WN-LMF format with relations...")
        create_wn_lmf_with_relations(csv_input, xml_output)
        
        print("\n" + "=" * 60)
        print("✅ Enhanced conversion completed successfully!")
        print(f"📁 Output file: {xml_output}")
        print("\n🎯 New features:")
        print("  ✅ Synset relations based on English WordNet")
        print("  ✅ Hypernym, hyponym, and other semantic relations")
        print("  ✅ Cross-references between Vietnamese synsets")
        print("  ✅ Enhanced semantic network structure")
        
    except Exception as e:
        print(f"❌ Error during conversion: {e}")
        import traceback
        traceback.print_exc()
        return

if __name__ == "__main__":
    main()
