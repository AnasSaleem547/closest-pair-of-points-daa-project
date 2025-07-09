import random
import math
import tkinter as tk
from tkinter import filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import json
import networkx as nx
#import sys
#sys.setrecursionlimit(10**6)//to expand our recursion limit

#variables for closest pair points
visualization_steps = []
final_closest_pair = []
closest_pair_left = None
closest_pair_right = None
closest_pair_overall = None
distances_doc = {"left": [], "right": [], "strip": []}
current_step = 0
text_widget = None
root = None

#distance calculate
def dist(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

#closest pair points
def single_split(px, py):
    x_min, x_max = px[0][0], px[-1][0]
    mid_x = (x_min + x_max) / 2
    lx = [p for p in px if p[0] <= mid_x]
    rx = [p for p in px if p[0] > mid_x]
    ly = [p for p in py if p[0] <= mid_x]
    ry = [p for p in py if p[0] > mid_x]
    
    visualization_steps.append((px, None, mid_x, None, None, 
                                "Step 1: Split using median of outermost x-axis values"))
    return lx, ly, rx, ry, mid_x


def bruteforce_region(points, region_name):
    global closest_pair_left, closest_pair_right
    min_dist = float("inf")
    closest_pair = None
    distances = []

    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            d = dist(points[i], points[j])
            distances.append((points[i], points[j], d))
            visualization_steps.append((points, (points[i], points[j]), None, None, d,
                                        f"{region_name}: Distance between {points[i]} and {points[j]} = {d:.2f}"))
            if d < min_dist:
                min_dist = d
                closest_pair = (points[i], points[j])

    visualization_steps.append((points, closest_pair, None, None, min_dist,
                                f"{region_name}: Closest pair found with distance {min_dist:.2f}"))

    if region_name == "Left Region":
        closest_pair_left = closest_pair
    elif region_name == "Right Region":
        closest_pair_right = closest_pair

    return min_dist, closest_pair, distances

def process_expanded_region(points, mid_x, min_distance):
    global closest_pair_overall
    
    if min_distance is None or min_distance == float('inf'):
        visualization_steps.append((points, None, mid_x, [], 0,
                                    "Expanded Region: Invalid or infinite minimum distance"))
        return []

    expanded_region = [p for p in points if abs(p[0] - mid_x) < min_distance]

    if not expanded_region:
        visualization_steps.append((points, None, mid_x, [], min_distance,
                                    "Expanded Region: No points in the expanded region"))
        return []

    expanded_region.sort(key=lambda p: p[1])

    min_dist = min_distance
    closest_pair = None
    distances = []

    #compare point to next 11 points only
    for i in range(len(expanded_region)):
        for j in range(i + 1, min(i + 11, len(expanded_region))):
            d = dist(expanded_region[i], expanded_region[j])
            distances.append((expanded_region[i], expanded_region[j], d))
            visualization_steps.append((expanded_region, (expanded_region[i], expanded_region[j]), None, expanded_region, d,
                                        f"Expanded Region: Distance between {expanded_region[i]} and {expanded_region[j]} = {d:.2f}"))
            if d < min_dist:
                min_dist = d
                closest_pair = (expanded_region[i], expanded_region[j])

    visualization_steps.append((expanded_region, closest_pair, None, expanded_region, min_dist,
                                f"Expanded Region: Closest pair found with distance {min_dist:.2f}"))

    if closest_pair and (closest_pair_overall is None or min_dist < dist(*closest_pair_overall)):
        closest_pair_overall = closest_pair

    return distances



def closest_pair(points):
    global closest_pair_overall
    visualization_steps.clear()
    closest_pair_overall = None 

    px = sorted(points, key=lambda p: p[0])
    py = sorted(points, key=lambda p: p[1])

    lx, ly, rx, ry, mid_x = single_split(px, py)

    d_left, pair_left, left_distances = bruteforce_region(lx, "Left Region")
    d_right, pair_right, right_distances = bruteforce_region(rx, "Right Region")

    if d_left is None or d_right is None:
        raise ValueError("Left or Right distance is None. Check input data.")

    if d_left < d_right:
        min_distance = d_left
        closest_pair = pair_left
    else:
        min_distance = d_right
        closest_pair = pair_right

    visualization_steps.append((points, closest_pair, mid_x, None, min_distance,
                                f"Comparison: Closest pair between left and right"))

    expanded_distances = process_expanded_region(py, mid_x, min_distance)

    if closest_pair_overall is None or min_distance < dist(*closest_pair_overall):
        closest_pair_overall = closest_pair

    final_distance = dist(*closest_pair_overall) if closest_pair_overall else None
    visualization_steps.append((points, closest_pair_overall, None, None, final_distance,
                                f"Final: Closest pair with distance {final_distance:.2f}" if final_distance else "No closest pair found"))

    distances_doc["left"] = left_distances
    distances_doc["right"] = right_distances
    distances_doc["strip"] = expanded_distances

    return closest_pair_overall


def plot_step():
    global current_step, text_widget
    ax.clear()
    points, closest_pair, mid_line, expanded_region, d, description = visualization_steps[current_step]
    ax.set_title(f"Step {current_step + 1}: {description}")

    ax.scatter([p[0] for p in points], [p[1] for p in points], color="blue", label="Points")

    if mid_line is not None:
        ax.axvline(mid_line, color="red", linestyle="--", label="Dividing Line")

    if expanded_region:
        ax.scatter([p[0] for p in expanded_region], [p[1] for p in expanded_region], color="orange", label="Expanded Region Points")

    if closest_pair:
        p1, p2 = closest_pair
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color="green", linewidth=2, label="Current Pair")
        mid_x = (p1[0] + p2[0]) / 2
        mid_y = (p1[1] + p2[1]) / 2
        if d is not None:
            ax.text(mid_x, mid_y, f"{d:.2f}", color="black", fontsize=8, ha="center", backgroundcolor="white")

    if current_step == len(visualization_steps) - 1 and closest_pair_overall:
        highlight_closest_pair(closest_pair_overall, "purple", "Final Closest Pair")

    #mid line
    if mid_line is not None and d is not None:
        ax.fill_betweenx([0, 10000], mid_line - d, mid_line + d, color='orange', alpha=0.2, label='Expanded Region')

    #text widget with distances
    if text_widget is not None:
        text_widget.delete(1.0, tk.END)
        for region, distances in distances_doc.items():
            text_widget.insert(tk.END, f"{region.upper()} Distances:\n")
            for p1, p2, dist_val in distances:
                text_widget.insert(tk.END, f"Points: {p1}, {p2} - Distance: {dist_val:.2f}\n")
            text_widget.insert(tk.END, "\n")

    ax.legend()
    plt.draw()

fig, ax = plt.subplots(figsize=(10, 6))



def plot_visualization():
    global current_step, text_widget
    current_step = 0
    plot_step()

    canvas_frame = tk.Frame(root)
    canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    toolbar_frame = tk.Frame(canvas_frame)
    toolbar_frame.pack(side=tk.BOTTOM, fill=tk.X)
    toolbar = CustomToolbar(canvas, toolbar_frame)
    toolbar.update()

    if text_widget is None:
        text_widget = tk.Text(root, height=10, wrap=tk.WORD)
        text_widget.pack(side=tk.RIGHT, fill=tk.BOTH, padx=10, pady=10)

def highlight_closest_pair(pair, color, label):
    if pair:
        p1, p2 = pair
        # Plot the line connecting the pair
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=color, linewidth=2, label=label)
        # Highlight the points in the pair
        ax.scatter([p1[0], p2[0]], [p1[1], p2[1]], color=color, s=100, zorder=5)
        # Calculate and display the distance
        mid_x = (p1[0] + p2[0]) / 2
        mid_y = (p1[1] + p2[1]) / 2
        distance = dist(p1, p2)
        ax.text(mid_x, mid_y, f"{distance:.2f}", color=color, fontsize=10, ha="center", backgroundcolor="white")

#navigation bar
class CustomToolbar(NavigationToolbar2Tk):
    def __init__(self, canvas, window):
        super().__init__(canvas, window)
        self.add_custom_buttons()

    def add_custom_buttons(self):
        self.next_button = tk.Button(master=self, text="Next Step", command=self.next_step)
        self.next_button.pack(side=tk.LEFT, padx=2)

        self.prev_button = tk.Button(master=self, text="Previous Step", command=self.previous_step)
        self.prev_button.pack(side=tk.LEFT, padx=2)

        self.skip_left_button = tk.Button(master=self, text="Skip Left Region", command=self.skip_left_part)
        self.skip_left_button.pack(side=tk.LEFT, padx=2)

        self.skip_right_button = tk.Button(master=self, text="Skip Right Region", command=self.skip_right_part)
        self.skip_right_button.pack(side=tk.LEFT, padx=2)

        self.skip_end_button = tk.Button(master=self, text="Skip to End", command=self.skip_to_end)
        self.skip_end_button.pack(side=tk.LEFT, padx=2)

    def next_step(self):
        global current_step
        if current_step < len(visualization_steps) - 1:
            current_step += 1
            plot_step()
        
        # Highlight final closest pair when at the last step
        if current_step == len(visualization_steps) - 1 and closest_pair_overall:
            highlight_closest_pair(closest_pair_overall, "purple", "Final Closest Pair")
            ax.legend()
            plt.draw()


    def previous_step(self):
        global current_step
        if current_step > 0:
            current_step -= 1
            plot_step()

    def skip_left_part(self):
        global current_step
        for i, step in enumerate(visualization_steps):
            if "Left Region: Closest pair found" in step[5]:
                current_step = i
                break
        points, _, _, _, _, _ = visualization_steps[current_step]
        ax.clear()
        ax.scatter([p[0] for p in points], [p[1] for p in points], color="blue", label="Points")
        if closest_pair_left:
            highlight_closest_pair(closest_pair_left, "brown", "Left Closest Pair")
        ax.set_title("Skip Left: Closest Pair in Left Region")
        ax.legend()
        plt.draw()

    def skip_right_part(self):
        global current_step
        for i, step in enumerate(visualization_steps):
            if "Right Region: Closest pair found" in step[5]:
                current_step = i
                break
        points, _, _, _, _, _ = visualization_steps[current_step]
        ax.clear()
        ax.scatter([p[0] for p in points], [p[1] for p in points], color="blue", label="Points")
        if closest_pair_right:
            highlight_closest_pair(closest_pair_right, "orange", "Right Closest Pair")
        ax.set_title("Skip Right: Closest Pair in Right Region")
        ax.legend()
        plt.draw()

    def skip_to_end(self):
        global current_step
        current_step = len(visualization_steps) - 1

        if visualization_steps:
            points, _, _, _, _, _ = visualization_steps[current_step]
            ax.clear()            
            ax.scatter([p[0] for p in points], [p[1] for p in points], color="blue", label="Points")

            if closest_pair_overall:
                highlight_closest_pair(closest_pair_overall, "purple", "Final Closest Pair")
                ax.set_title("Skip to End: Final Closest Pair")
                ax.legend()
                plt.draw()
            else:
                ax.set_title("Skip to End: No Closest Pair Found")
                plt.draw()
        else:
            print("No visualization steps available to skip to.")


def run_algorithm(file_path, algo):
    try:
        if "closest_pair" in file_path:
            with open(file_path, "r") as f:
                points = json.load(f)
            closest_pair(points)
            plot_visualization()
    except Exception as e:
        print(f"Error: {str(e)}")

#file selecton
def select_file(algo):
    file_path = filedialog.askopenfilename(initialdir="inputs", title="Select a File")
    if file_path:
        run_algorithm(file_path, algo)




#variables for integer multiplication
Integer_steps_tree = []  #holds recursion tree steps
Integer_current_step = 0
G = nx.DiGraph()  #directed graph to represent recursion tree
current_description = ""  #current step explanation

#integer multiplication
def Integer(x, y, depth=0, parent=None):
    """Perform Integer multiplication with enhanced explanations."""
    global current_description
    if x < 10 or y < 10:  #base case: single-digit numbers
        node_label = f"{x} * {y} = {x * y}"
        G.add_node(node_label, depth=depth)
        if parent:
            G.add_edge(parent, node_label)
        Integer_steps_tree.append((
            node_label,
            f"Base case:\n"
            f"Multiplying single-digit numbers {x} and {y}.\n"
            f"Result = {x * y}"
        ))
        return x * y

    n = max(len(str(x)), len(str(y)))
    half = n // 2

    a = x // 10**half
    b = x % 10**half
    c = y // 10**half
    d = y % 10**half

    node_label = f"{x} * {y}"
    G.add_node(node_label, depth=depth)
    if parent:
        G.add_edge(parent, node_label)

    Integer_steps_tree.append((
        node_label,
        f"Split:\n"
        f"x = {x} split into ({a}, {b})\n"
        f"y = {y} split into ({c}, {d})"
    ))
    ac = Integer(a, c, depth + 1, node_label)
    bd = Integer(b, d, depth + 1, node_label)
    abcd = Integer(a + b, c + d, depth + 1, node_label)

    # Combine results
    result = ac * 10**(2 * half) + (abcd - ac - bd) * 10**half + bd
    Integer_steps_tree.append((
        node_label,
        f"Combine:\n"
        f"ac = {ac}: Product of higher-order parts.\n"
        f"bd = {bd}: Product of lower-order parts.\n"
        f"abcd = {abcd}: Product of combined parts.\n\n"
        f"Formula:\n"
        f"Result = (ac * 10^{2 * half}) + ((abcd - ac - bd) * 10^{half}) + bd\n"
        f"Final result = {result}\n"
        f"Explanation:\n"
        f"This formula reconstructs the original multiplication problem by adjusting\n"
        f"for overlaps between the partial sums of ac, bd, and abcd."
    ))
    return result



def plot_Integer_tree_step():
    global Integer_current_step, current_description
    ax.clear()

    if Integer_steps_tree:
        node_label, description = Integer_steps_tree[Integer_current_step]
        current_description = description

        if "Split" in description:
            phase = "Splitting Phase"
        elif "Combine" in description:
            phase = "Combining Phase"
        else:
            phase = "Base Case"

        pos = nx.multipartite_layout(G, subset_key="depth")
        nx.draw(
            G, pos, ax=ax, with_labels=True,
            node_size=2000, node_color="lightblue", font_size=8
        )

        nx.draw_networkx_nodes(G, pos, nodelist=[node_label], node_color="orange", ax=ax)

        edges_to_highlight = [(u, v) for u, v in G.edges() if v == node_label]
        nx.draw_networkx_edges(
            G, pos, edgelist=edges_to_highlight, edge_color="orange", width=2, ax=ax
        )
        details_text.delete(1.0, tk.END)
        details_text.insert(tk.END, f"Current Node: {node_label}\n")
        details_text.insert(tk.END, f"Phase: {phase}\n\n{description}\n")
        if phase == "Splitting Phase":
            details_text.insert(tk.END, "\nExplanation:\n- This node splits the problem into smaller subproblems for recursion.\n")
        elif phase == "Base Case":
            details_text.insert(tk.END, "\nExplanation:\n- This is a base case. Multiplication is performed directly as both numbers are single digits.\n")
        elif phase == "Combining Phase":
            details_text.insert(tk.END, "\nWhy Are We Back Here?\n")
            details_text.insert(tk.END, "We are revisiting this node because all recursive calls are complete. The algorithm is now combining results.\n")
            details_text.insert(tk.END, "\nRecursive Call Status:\n")
            if "500 * 100" in node_label:
                details_text.insert(tk.END, "- ac = 500: Completed.\n")
                details_text.insert(tk.END, "- bd = 0: Completed.\n")
                details_text.insert(tk.END, "- abcd = 500: Completed.\n")
                details_text.insert(tk.END, "\nFormula:\n")
                details_text.insert(tk.END, "Result = (ac * 10^2) + ((abcd - ac - bd) * 10^1) + bd\n")
                details_text.insert(tk.END, "Substituting values: Result = (500 * 10^2) + ((500 - 500 - 0) * 10^1) + 0\n")
                details_text.insert(tk.END, "Final Result = 50000\n")

        legend_text = (
            "\nWhere:\n"
            "- Blue Nodes: Recursive calls completed.\n"
            "- Orange Node: Current step.\n"
            "- Yellow Edges: Dependencies in progress.\n"
        )
        details_text.insert(tk.END, legend_text)

        ax.set_title(f"Step {Integer_current_step + 1}/{len(Integer_steps_tree)}")

    else:
        ax.set_title("No steps available")

    plt.draw()


def run_Integer_visualization_tree(file_path):
    """Run the Integer multiplication and prepare tree steps for visualization."""
    global Integer_steps_tree, G, details_text
    Integer_steps_tree.clear()
    G.clear()

    try:
        with open(file_path, "r") as file:
            lines = file.readlines()
            if len(lines) < 2:
                raise ValueError("The file must contain at least two numbers on separate lines.")
            num1 = int(lines[0].strip())
            num2 = int(lines[1].strip())

        #perform multiplication
        Integer(num1, num2)

        if 'details_text' not in globals() or details_text is None:
            details_frame = tk.Frame(root, width=300)
            details_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
            details_label = tk.Label(details_frame, text="Step Details:", font=("Arial", 12))
            details_label.pack(pady=5)
            details_text = tk.Text(details_frame, wrap=tk.WORD, font=("Arial", 10), height=10)
            details_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        plot_Integer_tree_visualization()

    except Exception as e:
        messagebox.showerror("Error", f"Error during Integer multiplication: {e}")

#tere visualization
def plot_Integer_tree_visualization():
    global Integer_current_step
    Integer_current_step = 0
    plot_Integer_tree_step()

    canvas_frame = tk.Frame(root)
    canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    toolbar_frame = tk.Frame(canvas_frame)
    toolbar_frame.pack(side=tk.BOTTOM, fill=tk.X)
    toolbar = CustomToolbarForTree(canvas, toolbar_frame)
    toolbar.update()

#navbar for int multiplcation
class CustomToolbarForTree(NavigationToolbar2Tk):
    def __init__(self, canvas, window):
        super().__init__(canvas, window)
        self.add_custom_buttons()

    def add_custom_buttons(self):
        self.next_button = tk.Button(master=self, text="Next Step", command=self.next_step)
        self.next_button.pack(side=tk.LEFT, padx=2)

        self.prev_button = tk.Button(master=self, text="Previous Step", command=self.previous_step)
        self.prev_button.pack(side=tk.LEFT, padx=2)

        self.restart_button = tk.Button(master=self, text="Restart", command=self.restart)
        self.restart_button.pack(side=tk.LEFT, padx=2)

    def next_step(self):
        global Integer_current_step
        if Integer_current_step < len(Integer_steps_tree) - 1:
            Integer_current_step += 1
            plot_Integer_tree_step()

    def previous_step(self):
        global Integer_current_step
        if Integer_current_step > 0:
            Integer_current_step -= 1
            plot_Integer_tree_step()

    def restart(self):
        global Integer_current_step
        Integer_current_step = 0
        plot_Integer_tree_step()


def select_Integer_file_tree():
    file_path = filedialog.askopenfilename(initialdir="inputs", title="Select a File", filetypes=[("Text Files", "*.txt")])
    if file_path:
        run_Integer_visualization_tree(file_path)


def main():
    global root, details_text, fig, ax
    root = tk.Tk()
    root.title("Algorithm Visualization")
    menu_frame = tk.Frame(root, padx=20, pady=20)
    menu_frame.pack(fill=tk.BOTH, expand=True)

    title_label = tk.Label(menu_frame, text="Choose an Algorithm to Visualize", font=("Arial", 16))
    title_label.pack(pady=10)

    closest_pair_button = tk.Button(
        menu_frame,
        text="Closest Pair of Points",
        font=("Arial", 14),
        width=25,
        command=lambda: [select_file("closest_pair"), menu_frame.destroy()]
    )
    closest_pair_button.pack(pady=10)

    integer_multiplication_button = tk.Button(
        menu_frame,
        text="Integer Multiplication",
        font=("Arial", 14),
        width=25,
        command=lambda: [select_Integer_file_tree(), menu_frame.destroy()]
    )
    integer_multiplication_button.pack(pady=10)

    group_members_button = tk.Button(
        menu_frame,
        text="Group Members",
        font=("Arial", 14),
        width=25,
        command=show_group_members
    )
    group_members_button.pack(pady=10)

    exit_button = tk.Button(
        menu_frame,
        text="Exit",
        font=("Arial", 14),
        width=25,
        command=root.destroy
    )
    exit_button.pack(pady=10)

    root.mainloop()


def show_group_members():
    """Display the group members' details in a new window."""
    members_window = tk.Toplevel(root)
    members_window.title("Group Members")

    members_frame = tk.Frame(members_window, padx=20, pady=20)
    members_frame.pack(fill=tk.BOTH, expand=True)

    title_label = tk.Label(members_frame, text="Group Members", font=("Arial", 16))
    title_label.pack(pady=10)

    members = [
        "22K-0500 Anas Saleem",
        "22K-4241 Ashar Zamir",
        "22K-4525 Bilal Ahmed Khan"
    ]

    for member in members:
        member_label = tk.Label(members_frame, text=member, font=("Arial", 14))
        member_label.pack(pady=5)

    close_button = tk.Button(
        members_frame,
        text="Close",
        font=("Arial", 12),
        command=members_window.destroy
    )
    close_button.pack(pady=10)

if __name__ == "__main__":
    main()
