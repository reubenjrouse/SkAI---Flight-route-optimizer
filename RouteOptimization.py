import csv
import networkx as nx
import matplotlib.pyplot as plt

def load_data(filename):
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        headers = next(reader) 
        nodes = headers[1:]   

        graph_data = {}
        for row in reader:
            origin_city = row[0]
            for i in range(1, len(row)):
                destination_city = headers[i]
                distance = int(row[i])  
                graph_data[(origin_city, destination_city)] = distance
    return nodes, graph_data

def create_graph(nodes, graph_data):
    G = nx.Graph()
    G.add_nodes_from(nodes)

    G.add_weighted_edges_from((key[0], key[1], value) for key, value in graph_data.items())

    return G

def find_optimized_path(G, start, end, unavailable_nodes=[]):
    temp_G = G.copy()  

    try:
        primary_path = nx.dijkstra_path(temp_G, start, end, weight='weight')
        primary_time = nx.dijkstra_path_length(temp_G, start, end, weight='weight')
    except nx.NetworkXNoPath:
        print("No path exists between the specified nodes.")
        return None, None

  
    if unavailable_nodes:
        for unavailable_node in unavailable_nodes:
            if unavailable_node in primary_path:
                temp_G.remove_node(unavailable_node)
                try:
                    alternate_path = nx.dijkstra_path(temp_G, start, end, weight='weight')
                    alternate_time = nx.dijkstra_path_length(temp_G, start, end, weight='weight')
                    return primary_path, primary_time, alternate_path, alternate_time
                except nx.NetworkXNoPath:
                    pass
                temp_G.add_node(unavailable_node)  

    return primary_path, primary_time, None, None


def plot(G, primary_path, alternate_path, dep_city, arr_city):

    if alternate_path:
        path=alternate_path
    else:
        path=primary_path

    pos = nx.spring_layout(G)

    plt.figure(figsize=(10, 10))
    
    nx.draw_networkx_nodes(G, pos, node_size=700, node_color='skyblue', edgecolors='black', linewidths=1)
    nx.draw_networkx_nodes(G, pos, nodelist=path, node_color='orange', node_size=700, linewidths=2)
    nx.draw_networkx_edges(G, pos, width=2, edge_color='gray')
    nx.draw_networkx_labels(G, pos, font_size=8, font_weight='bold')

    plt.title(f'Flight path from {dep_city} to {arr_city}', fontsize=16)
    plt.axis('off')
    plt.show()




filename = 'Cities_FlightDuration_Mins.csv'
nodes, graph_data = load_data(filename)
G = create_graph(nodes, graph_data)

