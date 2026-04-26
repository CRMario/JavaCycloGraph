import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os
 

# Color palette
C_EXEC    = '#22c55e'   # green  — executed node
C_ERROR   = '#ef4444'   # red    — error node
C_NEUTRAL = '#94a3b8'   # slate  — not executed
C_START   = '#3b82f6'   # blue   — START
C_END     = '#8b5cf6'   # purple — END
C_EDGE_EXEC    = '#16a34a'
C_EDGE_ERROR   = '#dc2626'
C_EDGE_NEUTRAL = '#475569'
 
def visualize_all(graphs, output_dir='cfg_output', errors=None):
    errors = errors or []
    os.makedirs(output_dir, exist_ok=True)
    for method_name, graph_data in graphs.items():
        out_path = visualize_cfg(graph_data, method_name,output_dir=output_dir, errors=errors)
        if out_path:
            print(f'  saved as: {out_path}')
 
 
def visualize_cfg(graph_data, method_name, output_dir='.', errors=None):
    errors = errors or []
    graph          = graph_data['graph']
    execution_path = set(graph_data.get('execution_path', []))
    error_node     = graph_data.get('error_node')
 
    if graph.number_of_nodes() == 0:
        return None
 
    #layout
    try:
        pos = nx.nx_agraph.graphviz_layout(graph, prog='dot')
    except Exception:
        try:
            pos = nx.drawing.nx_pydot.pydot_layout(graph, prog='dot')
        except Exception:
            pos = nx.spring_layout(graph, seed=42, k=2.5)
 
    # node appearance
    node_colors, node_sizes, node_labels = [], [], {}
    for node in graph.nodes():
        label = graph.nodes[node].get('label', str(node))
        node_labels[node] = _wrap(label, width=20)
 
        if label == 'START':
            node_colors.append(C_START)
            node_sizes.append(2200)
        elif label == 'END':
            node_colors.append(C_END)
            node_sizes.append(2200)
        elif node == error_node:
            node_colors.append(C_ERROR)
            node_sizes.append(2400)
        elif node in execution_path:
            node_colors.append(C_EXEC)
            node_sizes.append(2000)
        else:
            node_colors.append(C_NEUTRAL)
            node_sizes.append(1800)
 
    # edge
    edge_colors, edge_widths = [], []
    edge_labels = {}
    for u, v, data in graph.edges(data=True):
        lbl = data.get('label')
        if lbl:
            edge_labels[(u, v)] = lbl
 
        if u == error_node or v == error_node:
            edge_colors.append(C_EDGE_ERROR)
            edge_widths.append(2.0)
        elif u in execution_path and v in execution_path:
            edge_colors.append(C_EDGE_EXEC)
            edge_widths.append(2.5)
        else:
            edge_colors.append(C_EDGE_NEUTRAL)
            edge_widths.append(1.2)
 
    # figure
    n = graph.number_of_nodes()
    fig_w = max(10, n * 0.7)
    fig_h = max(7,  n * 0.9)
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    fig.patch.set_facecolor('#ffffff')
    ax.set_facecolor('#ffffff')
 
    nx.draw_networkx_nodes(
        graph, pos,
        node_color=node_colors,
        node_size=node_sizes,
        ax=ax,
        linewidths=1.5,
        edgecolors='#1e293b',
    )
    nx.draw_networkx_labels(
        graph, pos,
        labels=node_labels,
        font_size=5,
        font_color='black',
        font_weight='bold',
        ax=ax,
    )
    nx.draw_networkx_edges(
        graph, pos,
        edge_color=edge_colors,
        width=edge_widths,
        arrows=True,
        arrowsize=18,
        connectionstyle='arc3,rad=0.08',
        ax=ax,
        min_source_margin=18,
        min_target_margin=18,
    )
    nx.draw_networkx_edge_labels(
        graph, pos,
        edge_labels=edge_labels,
        font_size=7,
        font_color='#000000',
        bbox=dict(boxstyle='round,pad=0.2', fc='#ffffff', ec='none', alpha=0.8),
        ax=ax,
    )
 
    # title & Cyclomatic Complexity
    E  = graph.number_of_edges()
    N  = graph.number_of_nodes()
    cc = E - N + 2
 
    title_parts = [method_name, f'CC = {cc}']
    if errors:
        title_parts.append(f'!!! {errors[0]}')
    ax.set_title('   |   '.join(title_parts),
                 fontsize=10, color='black', pad=14,
                 fontfamily='monospace')
 
    # legend
    legend_items = [
        mpatches.Patch(color=C_START,   label='START'),
        mpatches.Patch(color=C_END,     label='END'),
        mpatches.Patch(color=C_EXEC,    label='Executed'),
        mpatches.Patch(color=C_NEUTRAL, label='Not executed'),
        mpatches.Patch(color=C_ERROR,   label='Error'),
    ]
    ax.legend(
        handles=legend_items,
        loc='upper right',
        fontsize=7,
        framealpha=0.3,
        facecolor='#1e293b',
        labelcolor='white',
        edgecolor='#334155',
    )
    ax.axis('off')
 
    # save
    os.makedirs(output_dir, exist_ok=True)
    safe = method_name.replace('.', '_').replace(' ', '_')
    out_path = os.path.join(output_dir, f'{safe}.png')
    fig.savefig(out_path, bbox_inches='tight', dpi=150,
                facecolor=fig.get_facecolor())
    plt.close(fig)
    return out_path

 
def _wrap(text, width=20):
    if len(text) <= width:
        return text
    words = text.split()
    lines, line = [], []
    for w in words:
        if sum(len(x) for x in line) + len(line) + len(w) > width:
            lines.append(' '.join(line))
            line = [w]
        else:
            line.append(w)
    if line:
        lines.append(' '.join(line))
    return '\n'.join(lines)