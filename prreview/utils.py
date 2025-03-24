def graph_to_png(graph, filename):
    with open(filename, "wb") as f:
        f.write(graph.get_graph().draw_mermaid_png())
