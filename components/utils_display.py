import json
import streamlit as st

# Hàm dựng HTML <details> tree
def render_details_tree(data, level=0):
    html = ""
    indent_px = level * 15

    for node in data:
        has_children = isinstance(node.children, list) and bool(node.children)

        html += f'''
<div class="tree-node" style="margin-left:{indent_px}px;">
    <div class="tree-line"></div>
    <details>
        <summary>
            <strong>Lv{node._level + 1}</strong>. 🇻🇳 {node._viet_lemmas} || 🇬🇧 {node._lemmas} <strong>({node._synset.id})</strong>
        </summary>
        <div class="node-extra">🇻🇳 Định nghĩa: {node._viet_definition}</div>
        <div class="node-extra">📖 Definitions: {node._definition}</div>
        <div class="node-extra">🇻🇳 Ví dụ: {node._viet_example}</div>
        <div class="node-extra">💬 Examples: {node._example}</div>
'''.strip()

        if has_children:
            html += render_details_tree(node.children, level + 1)

        html += '</details></div>'

    return html

# Hàm hiển thị Tree HTML trong Streamlit
def get_tree_view_css():
    return """
    <style>
    .tree-node {
        position: relative;
        padding-left: 20px;
        margin: 4px 0;
    }

    .tree-node .tree-line {
        position: absolute;
        top: 0;
        bottom: 0;
        left: 10px;
        width: 1px;
        background-color: #ccc;
    }

    .tree-node summary {
        list-style: none;
        cursor: pointer;
        font-weight: bold;
        padding-left: 5px;
    }

    .tree-node summary::-webkit-details-marker {
        display: none;
    }

    .tree-node details > summary::before {
        content: "▶";
        display: inline-block;
        transform: rotate(0deg);
        margin-right: 5px;
        transition: transform 0.2s ease;
    }

    .tree-node details[open] > summary::before {
        transform: rotate(90deg);
        content: "▼";
    }

    .node-extra {
        color: #666;
        font-size: 13px;
        padding-left: 20px;
        padding-top: 4px;
    }

    </style>
    """

# Hàm tạo dữ liệu Cytoscape từ dict lồng dict
def nodefamily_to_cytoscape_elements(nodes, parent_id=None, elements=None, seen=None, added_edges=None):
    if elements is None:
        elements = []
    if seen is None:
        seen = {}
    if added_edges is None:
        added_edges = set()

    for node in nodes:
        # synset_id = node._synset.name()
        synset_id = node._synset.id

        # Gán ID duy nhất cho node theo synset name
        if synset_id in seen:
            node_id = seen[synset_id]
        else:
            node_id = f"n{len(seen)}"
            seen[synset_id] = node_id
            # Nếu lemmas tiếng Việt có, dùng nó, nếu không thì dùng lemmas tiếng Anh
            if node._viet_lemmas:
                lemmas_label = node._viet_lemmas
            elif node._lemmas:
                lemmas_label = node._lemmas
            label = f"{synset_id}\n{lemmas_label}"
            elements.append({
                "data": {"id": node_id, "label": label},
                "classes": "wordnode"
            })

        # Thêm edge nếu chưa có trong added_edges
        if parent_id and (parent_id, node_id) not in added_edges:
            elements.append({
                "data": {"source": parent_id, "target": node_id}
            })
            added_edges.add((parent_id, node_id))

        # Duyệt đệ quy các con
        if node.children:
            nodefamily_to_cytoscape_elements(
                node.children,
                parent_id=node_id,
                elements=elements,
                seen=seen,
                added_edges=added_edges
            )

    return elements



# Hàm hiển thị Cytoscape trong Streamlit
def render_cytoscape(elements):
    html_code = f"""
    <html>
    <head>
        <script src="https://unpkg.com/cytoscape@3.23.0/dist/cytoscape.min.js"></script>
    </head>
    <body>
        <div id="cy" style="width: 100%; height: 500px;"></div>
        <script>
            var cy = cytoscape({{
                container: document.getElementById('cy'),
                elements: {json.dumps(elements)},
                layout: {{
                    name: 'breadthfirst',
                    directed: true,
                    padding: 40,
                    spacingFactor: 1
                }},
                style: [
                    {{
                        selector: 'node',
                        style: {{
                            'shape': 'rectangle',
                            'label': 'data(label)',
                            'text-valign': 'center',
                            'text-halign': 'center',
                            'background-color': '#A8D0E6',
                            'color': '#000',
                            'padding': '8px',
                            'font-size': '14px',
                            'border-width': 1,
                            'border-color': '#333',
                            'width': 'label',
                            'height': 'label',
                            'text-wrap': 'wrap',
                            'text-max-width': 80,
                            'grabbable': false
                        }}
                    }},
                    {{
                        selector: 'edge',
                        style: {{
                            'width': 5,
                            'line-color': '#ccc',
                            'target-arrow-shape': 'triangle',
                            'target-arrow-color': '#ccc',
                            'curve-style': 'bezier',
                            'arrow-scale': 2,
                            'target-distance-from-node': 2
                        }}
                    }}
                ],
                userPanningEnabled: true,
                userZoomingEnabled: true,
                boxSelectionEnabled: true,
                autoungrabify: true
            }});
        </script>
    </body>
    </html>
    """
    st.components.v1.html(html_code, height=500, scrolling=False)


