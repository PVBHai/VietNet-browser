#!/usr/bin/env python3
"""
VietNet to WN-LMF Converter
Converts Vietnamese lexical data to WordNet Lexical Markup Framework format
Following Global WordNet schema: https://globalwordnet.github.io/schemas/
"""

import pandas as pd
import xml.etree.ElementTree as ET
from xml.dom import minidom
import re
from datetime import datetime
import sys
import os

def create_wn_lmf_from_vietnet_data(csv_file_path, output_xml_path, lexicon_id="vietnet", lexicon_label="VietNet Vietnamese Lexicon"):
    """
    Convert VietNet CSV data to WN-LMF XML format following Global WordNet schema
    Based on: https://globalwordnet.github.io/schemas/
    
    Args:
        csv_file_path: Path to the CSV file containing Vietnamese data
        output_xml_path: Path where the WN-LMF XML file will be saved
        lexicon_id: Identifier for the lexicon
        lexicon_label: Human-readable label for the lexicon
    """
    
    # Read the CSV data
    df = pd.read_csv(csv_file_path)
    print(f"Loaded {len(df)} entries from {csv_file_path}")
    
    # Create XML with proper DOCTYPE declaration compatible with wn library (supports 1.0-1.3)
    xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>\n'
    doctype = '<!DOCTYPE LexicalResource SYSTEM "http://globalwordnet.github.io/schemas/WN-LMF-1.3.dtd">\n'
    
    # Create root element with proper namespace
    root = ET.Element("LexicalResource")
    root.set("xmlns:dc", "https://globalwordnet.github.io/schemas/dc/")
    
    # Create Lexicon element with all required attributes per Global WordNet schema
    lexicon = ET.SubElement(root, "Lexicon")
    lexicon.set("id", lexicon_id)
    lexicon.set("label", lexicon_label)
    lexicon.set("language", "vi")  # Vietnamese BCP-47 code
    lexicon.set("email", "vietnet@example.com")
    lexicon.set("license", "https://creativecommons.org/licenses/by/4.0/")
    lexicon.set("version", "1.0")
    lexicon.set("url", "https://github.com/vietnet/lexicon")
    lexicon.set("citation", "VietNet: Vietnamese WordNet Lexicon")
    lexicon.set("dc:publisher", "VietNet Project")
    
    # Vietnamese part-of-speech mapping to WordNet standard
    # Based on Global WordNet schema part-of-speech values
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
    
    # Process each synset group
    for synset_id, group in synset_groups:
        # Determine part of speech from first entry
        original_pos = str(group.iloc[0]['pos']).lower().strip()
        pos = pos_mapping.get(original_pos, 'n')  # default to noun
        
        # Create internal synset ID following Global WordNet conventions
        internal_synset_id = f"{lexicon_id}-{synset_counter:08d}-{pos}"
        
        # Create Synset element
        synset = ET.SubElement(lexicon, "Synset")
        synset.set("id", internal_synset_id)
        synset.set("ili", synset_id)  # Inter-Lingual Index mapping to English WordNet
        
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
        
        synset_counter += 1
    
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
    
    print(f"✅ Created WN-LMF file: {output_xml_path}")
    print(f"📊 Total synsets: {synset_counter - 1}")
    print(f"📝 Total lexical entries: {lexical_entry_counter - 1}")
    print(f"🔗 Format follows Global WordNet schema: https://globalwordnet.github.io/schemas/")
    print(f"🔍 Validate at: https://server1.nlp.insight-centre.org/gwn-converter/")
    
    return output_xml_path

def validate_and_preview_xml(xml_file_path):
    """
    Validate XML structure and show preview
    """
    try:
        # Parse the XML to check if it's well-formed
        tree = ET.parse(xml_file_path)
        root = tree.getroot()
        
        print("✅ XML is well-formed")
        print(f"Root element: {root.tag}")
        
        # Find lexicon
        lexicon = root.find('Lexicon')
        if lexicon is not None:
            print(f"Lexicon ID: {lexicon.get('id')}")
            print(f"Language: {lexicon.get('language')}")
            print(f"Version: {lexicon.get('version')}")
            
            # Count elements
            synsets = lexicon.findall('Synset')
            entries = lexicon.findall('LexicalEntry')
            
            print(f"Total Synsets: {len(synsets)}")
            print(f"Total Lexical Entries: {len(entries)}")
            
            # Show first few entries as examples
            print("\n📋 Sample Synset:")
            if synsets:
                first_synset = synsets[0]
                print(f"  ID: {first_synset.get('id')}")
                print(f"  ILI: {first_synset.get('ili')}")
                definition = first_synset.find('Definition')
                if definition is not None:
                    print(f"  Definition: {definition.text[:100]}...")
            
            print("\n📝 Sample Lexical Entry:")
            if entries:
                first_entry = entries[0]
                print(f"  ID: {first_entry.get('id')}")
                lemma = first_entry.find('Lemma')
                if lemma is not None:
                    print(f"  Word: {lemma.get('writtenForm')}")
                    print(f"  POS: {lemma.get('partOfSpeech')}")
                sense = first_entry.find('Sense')
                if sense is not None:
                    print(f"  Synset: {sense.get('synset')}")
                    confidence = sense.get('confidenceScore')
                    if confidence:
                        print(f"  Confidence: {confidence}")
        
        # Show first 15 lines of the file
        print("\n📄 XML File Preview (first 15 lines):")
        with open(xml_file_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f, 1):
                if i <= 15:
                    print(f"{i:2d}: {line.rstrip()}")
                else:
                    break
        
        print("\n🔗 Next Steps:")
        print("1. Upload the XML file to: https://server1.nlp.insight-centre.org/gwn-converter/")
        print("2. Validate the format and convert if needed")
        print("3. Use with wn library or other WordNet tools")
        
        return True
        
    except ET.ParseError as e:
        print(f"❌ XML Parse Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """
    Main function to convert VietNet data to WN-LMF format
    """
    print("🚀 VietNet to WN-LMF Converter")
    print("=" * 50)
    
    # Input and output file paths
    csv_input = "vietnet_wn_lmf.csv"
    xml_output = "vietnet_lexicon.xml"
    
    # Check if input file exists
    if not os.path.exists(csv_input):
        print(f"❌ Input file not found: {csv_input}")
        print("Please ensure the CSV file is in the current directory")
        return
    
    try:
        # Create the WN-LMF file
        print(f"📖 Converting {csv_input} to WN-LMF format...")
        create_wn_lmf_from_vietnet_data(csv_input, xml_output)
        
        print("\n" + "=" * 50)
        print("🔍 Validating and previewing the XML...")
        validate_and_preview_xml(xml_output)
        
        print("\n" + "=" * 50)
        print("✅ Conversion completed successfully!")
        print(f"📁 Output file: {xml_output}")
        print("\n🎯 Ready for validation at:")
        print("   https://server1.nlp.insight-centre.org/gwn-converter/")
        
    except Exception as e:
        print(f"❌ Error during conversion: {e}")
        return

if __name__ == "__main__":
    main()
