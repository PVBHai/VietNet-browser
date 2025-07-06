# from components.utils_wn import get_relationships

# def process_lemmas(lemmas, recursive_level=None):
#     names = '/'.join([l.name() for l in lemmas])
#     return f"Lv{recursive_level + 1}. {names}" if recursive_level is not None else names

# def build_tree_list(synsets, relationship_type, recursive_level=0, max_recursive=1):
#     if recursive_level >= max_recursive or not synsets:
#         return []
#     nodes = []
#     for syn in synsets:
#         children = get_relationships(syn, relationship_type)
#         node = {
#             "id": process_lemmas(syn.lemmas(), recursive_level) + f" ({syn.name()})",
#             "description": syn.definition(),
#             "children": build_tree_list(children, relationship_type, recursive_level + 1, max_recursive)
#         }
#         nodes.append(node)
#     return nodes

# def to_nested_dict(nodes):
#     result = {}
#     for node in nodes:
#         if node['children']:
#             result[node['id']] = to_nested_dict(node['children'])
#         else:
#             result[node['id']] = {}
#     return result
