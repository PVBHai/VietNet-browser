# VietNet WN-LMF Project

This project converts Vietnamese lexical data to WordNet Lexical Markup Framework (WN-LMF) format and integrates it with the `wn` library.

## 🎯 Project Overview

- **Goal**: Create a Vietnamese lexicon in WN-LMF format compatible with the `wn` library
- **Input**: Vietnamese lexical data with English WordNet mappings
- **Output**: WN-LMF 1.3 compliant XML lexicon
- **Status**: ✅ **COMPLETED SUCCESSFULLY**

## 📁 Project Files

- **`vietnet_lexicon.xml`** - The main Vietnamese lexicon in WN-LMF 1.3 format (8.2MB)
- **`create_vietnet_wn_lmf.py`** - Python converter script for regenerating the lexicon
- **`vietnet_wn_lmf.csv`** - Source Vietnamese lexical data (4.1MB)
- **`build_vietnet_wn_lmf.ipynb`** - Jupyter notebook with development process and testing
- **`README.md`** - This documentation file

## 📊 Lexicon Statistics

- **Total Vietnamese Words**: 21,517 entries
- **Total Synsets**: 10,446 synsets
- **Language**: Vietnamese (vi)
- **Format**: WN-LMF 1.3 (compatible with wn library)
- **English WordNet Mapping**: Via ILI (Inter-Lingual Index)

## 🚀 Usage

### 1. Using with wn Library

```python
import wn

# The lexicon should already be added to your wn database
# If not, add it with:
# wn.add('vietnet_lexicon.xml')

# Search Vietnamese words
words = wn.words("từ_tiếng_việt", lexicon="vietnet")

# Get synsets
synsets = wn.synsets(lexicon="vietnet")

# Access lexicon info
lexicons = wn.lexicons()  # vietnet will be in the list
```

### 2. Regenerating the Lexicon

```bash
# Run the converter script
python create_vietnet_wn_lmf.py

# This will create a new vietnet_lexicon.xml file
```

### 3. Testing

```python
# Test Vietnamese word searches
import wn

test_words = ['a', 'ả', 'sự vật']
for word in test_words:
    words = wn.words(word, lexicon='vietnet')
    if words:
        w = words[0]
        print(f"Word: {w.lemma()}")
        senses = w.senses()
        if senses:
            definition = senses[0].synset().definition()
            print(f"Definition: {definition[:100]}...")
```

## 🔧 Technical Details

### Key Issue Resolved
- **Problem**: `wn` library rejected WN-LMF 1.4 format
- **Solution**: Used WN-LMF 1.3 DTD instead (supported versions: 1.0-1.3)
- **DTD**: `http://globalwordnet.github.io/schemas/WN-LMF-1.3.dtd`

### Data Structure
- **Input CSV columns**: `word`, `pos`, `meaning`, `example`, `match_id`, `is_same`
- **POS Mapping**: Vietnamese → WordNet standard (d→n, t→a, đt→v, tt→r, etc.)
- **Confidence Scores**: Based on `is_same` field (True→1.0, False→0.8)

### XML Structure
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE LexicalResource SYSTEM "http://globalwordnet.github.io/schemas/WN-LMF-1.3.dtd">
<LexicalResource xmlns:dc="https://globalwordnet.github.io/schemas/dc/">
  <Lexicon id="vietnet" label="VietNet Vietnamese Lexicon" language="vi" ...>
    <Synset id="vietnet-00000001-n" ili="oewn-04165311-n">
      <Definition>Vietnamese definition</Definition>
      <Example>Vietnamese example</Example>
    </Synset>
    <LexicalEntry id="vietnet-00000001">
      <Lemma writtenForm="Vietnamese_word" partOfSpeech="n"/>
      <Sense id="vietnet-00000001-1" synset="vietnet-00000001-n" confidenceScore="1.0"/>
    </LexicalEntry>
  </Lexicon>
</LexicalResource>
```

## 🌐 Standards Compliance

- ✅ **Global WordNet Schema**: https://globalwordnet.github.io/schemas/
- ✅ **WN-LMF 1.3 DTD**: Compatible with `wn` library
- ✅ **BCP-47 Language Code**: `vi` for Vietnamese
- ✅ **Dublin Core Metadata**: Proper namespace and publisher info
- ✅ **ILI Mapping**: Links to English WordNet synsets

## 🎉 Success Metrics

- ✅ XML validates against WN-LMF 1.3 DTD
- ✅ Successfully loads with `wn.lmf.load()`
- ✅ Integrates with `wn.add()` without errors
- ✅ Vietnamese words are searchable via `wn.words()`
- ✅ Definitions and examples properly displayed
- ✅ English WordNet mappings preserved

## 📝 Development Notes

1. **Initial Challenge**: WN-LMF 1.4 format was not supported by `wn` library
2. **Solution Discovery**: Found that `wn` library supports versions 1.0-1.3 only
3. **Format Adjustment**: Changed DTD from 1.4 to 1.3
4. **Validation Success**: XML now passes all validation checks
5. **Integration Complete**: Vietnamese lexicon fully functional in `wn` library

## 🔗 References

- [Global WordNet Schemas](https://globalwordnet.github.io/schemas/)
- [Global WordNet Converter](https://server1.nlp.insight-centre.org/gwn-converter/)
- [wn Python Library](https://github.com/goodmami/wn)
- [WordNet-LMF Specification](https://globalwordnet.github.io/schemas/)

---

**Project Status**: ✅ **COMPLETED**  
**Last Updated**: October 1, 2025  
**Vietnamese Lexicon**: Ready for production use
