import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import tkinter as tk
from tkinter import messagebox, filedialog

# Função para criar o grafo e o diagrama CPM
def generate_cpm_diagram():
    global activities, critical_path, pos
    activities = {}
    try:
        for i in range(len(activity_entries)):
            activity_name = activity_entries[i].get().strip()
            duration = int(duration_entries[i].get().strip())
            dependencies = [dep.strip() for dep in dependency_entries[i].get().split(",") if dep.strip()]
            activities[activity_name] = {'duration': duration, 'dependencies': dependencies}
    except ValueError:
        messagebox.showerror("Erro", "Por favor, insira durações válidas.")
        return

    # Criar grafo
    G = nx.DiGraph()
    for activity, info in activities.items():
        G.add_node(activity, duration=info['duration'])
        for dependency in info['dependencies']:
            G.add_edge(dependency, activity)

    # Calcular o caminho crítico
    try:
        lengths = nx.single_source_dijkstra_path_length(G, list(activities.keys())[0], weight='duration')
        critical_path = nx.dag_longest_path(G, weight='duration')
    except nx.NetworkXNoPath:
        messagebox.showerror("Erro", "Não foi possível calcular um caminho crítico. Verifique as dependências.")
        return

    # Layout do gráfico
    plt.figure(figsize=(16, 10))
    pos = {
        'A': (0, 4), 'B': (2, 5), 'C': (2, 3), 'D': (2, 7), 'E': (4, 5), 
        'F': (4, 3), 'G': (4, 1), 'H': (6, 7), 'I': (6, 3), 
        'J': (8, 4), 'K': (8, 6), 'L': (10, 5), 'FIM': (12, 5)
    }

    # Configurações de cor para o caminho crítico e outras atividades
    node_colors = ['#FF5733' if node in critical_path else '#AED6F1' for node in G.nodes()]
    edge_colors = ['#FF5733' if edge[0] in critical_path and edge[1] in critical_path else 'gray' for edge in G.edges()]

    # Desenhar o grafo sem rótulos principais
    nx.draw(G, pos, with_labels=False, node_size=3000, node_color='none', edge_color=edge_colors, width=2, font_size=10)

    # Adicionando caixas de atividades com o estilo PMBOK
    for node, (x, y) in pos.items():
        if node in activities:
            duration = activities[node]['duration']
            early_start = lengths.get(node, 0) - duration if node in lengths else 0
            early_finish = lengths.get(node, duration)
            
            # Caixa de atividade com estilo PMBOK
            box = FancyBboxPatch((x - 0.5, y - 0.4), 1, 0.8, boxstyle="round,pad=0.2", edgecolor="black", facecolor='#FFEBEE' if node in critical_path else '#E3F2FD')
            plt.gca().add_patch(box)
            
            # Rótulos de dados dentro da caixa
            plt.text(x, y + 0.2, f"{node}", ha='center', va='center', color='black', fontsize=10, fontweight='bold')
            plt.text(x, y, f"Início: {early_start}", ha='center', va='center', color='blue', fontsize=9)
            plt.text(x, y - 0.2, f"Fim: {early_finish}", ha='center', va='center', color='darkred', fontsize=9)
            plt.text(x, y - 0.35, f"Duração: {duration}", ha='center', va='center', color='darkgreen', fontsize=8)

    # Rótulos das arestas com duração
    edge_labels = {(u, v): f"{activities[v]['duration']} dias" for u, v in G.edges() if v in activities}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8, font_color='black')

    # Título e resumo do caminho crítico
    plt.title("Diagrama de Caminho Crítico (CPM) - Layout Estilo PMBOK", fontsize=14, fontweight='bold')
    plt.text(-1, -1, f"Resumo do Caminho Crítico:\n{' -> '.join(critical_path)}\nDuração Total: {sum(activities[node]['duration'] for node in critical_path)} dias", fontsize=12, color='black', ha='left', bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.5'))
    plt.axis('off')  # Ocultar eixos
    plt.show()

# Funções para salvar o diagrama em PNG e PDF
def save_as_png():
    generate_cpm_diagram()
    file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Files", "*.png")])
    if file_path:
        plt.savefig(file_path, format="png")
        messagebox.showinfo("Sucesso", f"Diagrama salvo como {file_path}")

def save_as_pdf():
    generate_cpm_diagram()
    file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
    if file_path:
        plt.savefig(file_path, format="pdf")
        messagebox.showinfo("Sucesso", f"Diagrama salvo como {file_path}")

# Função para adicionar uma nova linha de entrada
def add_activity():
    row = len(activity_entries)
    activity_label = tk.Label(root, text=f"Atividade {row+1}")
    activity_label.grid(row=row+2, column=0)
    activity_entry = tk.Entry(root)
    activity_entry.grid(row=row+2, column=1)
    activity_entries.append(activity_entry)

    duration_label = tk.Label(root, text="Duração (dias)")
    duration_label.grid(row=row+2, column=2)
    duration_entry = tk.Entry(root)
    duration_entry.grid(row=row+2, column=3)
    duration_entries.append(duration_entry)

    dependency_label = tk.Label(root, text="Dependências (separadas por vírgula)")
    dependency_label.grid(row=row+2, column=4)
    dependency_entry = tk.Entry(root)
    dependency_entry.grid(row=row+2, column=5)
    dependency_entries.append(dependency_entry)

# Configurar a interface gráfica
root = tk.Tk()
root.title("Gerador de Diagrama CPM Estilo PMBOK")

# Listas para armazenar entradas
activity_entries = []
duration_entries = []
dependency_entries = []

# Labels principais
title_label = tk.Label(root, text="Insira as Atividades, Duração e Dependências")
title_label.grid(row=0, column=0, columnspan=6, pady=10)

# Adicionar primeira linha de entrada
add_activity()

# Botão para adicionar mais atividades
add_activity_button = tk.Button(root, text="Adicionar Atividade", command=add_activity)
add_activity_button.grid(row=1, column=0, columnspan=2, pady=10)

# Botões para gerar, salvar em PNG e salvar em PDF
generate_button = tk.Button(root, text="Gerar Diagrama CPM", command=generate_cpm_diagram)
generate_button.grid(row=1, column=2, pady=10)

generate_png_button = tk.Button(root, text="Salvar como PNG", command=save_as_png)
generate_png_button.grid(row=1, column=3, pady=10)

generate_pdf_button = tk.Button(root, text="Salvar como PDF", command=save_as_pdf)
generate_pdf_button.grid(row=1, column=4, pady=10)

# Executar o aplicativo
root.mainloop()