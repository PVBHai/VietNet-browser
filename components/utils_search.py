from rapidfuzz import fuzz
import sqlite3
import pandas as pd
import numpy as np

# Hàm này là hàm tìm kiếm chính của browser
# => Trả về: 
# 1. [synset_id, ...]
# 2. message
# | None => Search thành công
# | string => Search không thành công, trả về message
def search_function(user_input, lexicon, db_path='data/vietnet_data/VIETNET.db'):
    # Nếu người dùng nhập synset_id
    if "oewn-" in user_input:
        ssid = user_input.strip()
        if lexicon.synset(ssid):
            return [ssid], None
        else:
            return [], f"Synset_ID {ssid} không tồn tại"
        
    result = []
    # 1. Tìm tiếng Việt
    temp = exact_search_vietnet_search(user_input, db_path)
    result += [lexicon.synset(ssid) for ssid in temp]
    # 2. Tìm tiếng Anh
    result += lexicon.synsets(user_input, pos='n')

    # Nếu không tìm thấy synset nào
    if not result:
        recommended_search = fuzzy_search_vietnet_search(user_input, db_path)
        suggestion = ' | '.join(recommended_search[:5])
        return [], f"Bạn hãy thử tìm các từ sau: {suggestion}"
    else:
        return list(set(result)), None



# Hàm này để chuẩn hóa chuỗi
# => Trả về chuỗi đã chuẩn hóa
def normalize(text):
    return text.lower().strip()


# Hàm này để tìm từ gợi ý
# => Trả về [word, ...]
def fuzzy_search_vietnet_search(user_input, db_path='data/vietnet_data/VIETNET.db', threshold=80):
    query = normalize(user_input)
    
    conn = sqlite3.connect(db_path)
    df_search = pd.read_sql_query("SELECT * FROM VIETNET_FUZZ_SEARCH", conn)
    conn.close()

    results = []
    for _, row in df_search.iterrows():
        tieng = normalize(row['tieng'])
        score = fuzz.ratio(query, tieng)
        if score >= threshold:
            results.append((row['word'], score))

    results = list(set(results))
    results.sort(key=lambda x: -x[1])
    return [word for word, _ in results]


# Hàm để tìm kiếm từ tiếng Việt 
# => Trả về [synset_id, ...]
def exact_search_vietnet_search(user_input, db_path='data/vietnet_data/VIETNET.db'):
    query = normalize(user_input)

    conn = sqlite3.connect(db_path)
    df_search = pd.read_sql_query("SELECT * FROM VIETNET_EXACT_SEARCH", conn)
    conn.close()
    
    results = []
    for _, row in df_search.iterrows():
        tieng = normalize(row['tieng'])
        if query == tieng:
            results.append(row['synset_id'])
    return results


# Hàm để tìm các thông tin tiếng Việt từ synset_id 
# (các cột có thể tìm 'viet_word', 'viet_definition', 'viet_example')
# => Trả về chuỗi tiếng Việt hoặc None nếu không tìm thấy
def get_viet_info_from_synset(synset_id, db_path='data/vietnet_data/VIETNET.db'):
    conn = sqlite3.connect(db_path)
    df_search = pd.read_sql_query(f"SELECT * FROM VIETNET_DATA WHERE synset_id = ?", conn, params=(synset_id,))
    conn.close()
    
    if not df_search.empty:
        # Lemmas
        lemmas_list = df_search['viet_word'].tolist()
        lemmas = ', '.join(lemmas_list) if lemmas_list else None
        # Định nghĩa
        definitions_list = df_search['viet_definition'].tolist()
        definitions = ''
        for i in range(len(definitions_list)):
            definitions += f"{i+1}. {definitions_list[i]} | "
        # Ví dụ
        examples_list = df_search['viet_example'].tolist()
        examples = ''
        ex_count = 0
        for i in range(len(examples_list)):
            if examples_list[i] is not None:
                examples += f"{ex_count+1}. {examples_list[i]} | "
                ex_count += 1            
        # Trả về
        return {
            'viet_word': lemmas,
            'viet_definition': definitions,
            'viet_example': examples
        }
    else:
        return {
            'viet_word': None,
            'viet_definition': None,
            'viet_example': None
        }



# --------------------------------------------------
# import wn
# from pathlib import Path
# if __name__ == "__main__":
#     wn.config.data_directory = Path('./data')
#     lexicon = wn.Wordnet('oewn:2024')
#     ssid = 'oewn-05481998-n'
#     # text = 'a'
#     # lst, text = search_function(text, lexicon)
#     # print(f"List found: {lst}")
#     # print(f"Message: {text}")
#     a = print(get_viet_info_from_synset(ssid))
#     print(a)
    