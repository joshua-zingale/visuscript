"""An Example where Updater is used to implement some physics.

The resultant animation has little didactic value, but this animation
nonetheless demonstrates the use of Updater to create a physical system.

Updater here is used to move nodes away from each other in a way that
ideally would create a graph with neatly spaced nodes.
(This method does not work very well, but it tries.)
"""

from visuscript import *
from visuscript.connector import Edges
from visuscript.math_utility import unit_diff, magnitude, invert
from typing import Generator
import random
RADIUS = 10
WEIGHT = 1
SEPARATION = 3*RADIUS
N = 15
AVG_NUM_CONNECTIONS = 3
DAMPING = 10
CENTER_CONSTANT = 5
ATTRACTION_CONSTANT = 3
REPULSION_CONSTANT = 300000
LINE_REPULSION_CONSTANT = 10000
def main():
    
    random.seed(316)
    scene = Scene()

    # Build graph
    random_adjacency_matrix = [
        [0 for _ in range(N)] for _ in range(N)
    ]
    for row in random_adjacency_matrix:
        num_edges = max(round(random.normalvariate(AVG_NUM_CONNECTIONS,0.5)),0)
        indices = random.choices(range(N), k=num_edges)
        for index in indices:
            row[index] = 1
    for i in range(N):
        random_adjacency_matrix[i][i] = 0
    nodes, edges = get_nodes_and_edges(random_adjacency_matrix)


    scene << nodes
    scene << edges

    scene.player << UpdaterAnimation(UpdaterBundle(
        FunctionUpdater(get_graph_updater(nodes, edges)),
        FunctionUpdater(get_velocity_mover(nodes))
        ).set_update_rate(60), duration=8)
    
    sequence = AnimationSequence()
    red = Color('red').rgb
    white = Color('white').rgb
    colors = {i: red.interpolate(white, i/8) for i in range(8)}

    for distance, source, destination in bfs(nodes, edges):
        sequence << AnimationBundle(
            RgbAnimation(destination.stroke, colors[distance]),
            RgbAnimation(edges.get_edge(source, destination).stroke, 'red') if source else None,
            )
    scene.player << sequence


def get_nodes_and_edges(adjacency_matrix):
    edges = Edges()

    num_nodes = len(adjacency_matrix)
    nodes = [GraphNode(chr(ord("A") + i)).translate(random.randrange(-30,30), random.randrange(-20,20)) for i in range(num_nodes)]

    for i, row in enumerate(adjacency_matrix):
        for j, connected in enumerate(row):
            if connected and not edges.connected(nodes[i], nodes[j]):
                edges.connect(nodes[i], nodes[j]).finish()

    return nodes, edges

class GraphNode(Circle):

    def __init__(self, letter: str):
        super().__init__(RADIUS)
        self.add_child(Text(letter, font_size=RADIUS))

        self.letter = letter

        self.weight = WEIGHT
        self.velocity = Vec2(0,0)
        self.moveable = True

    def __str__(self):
        return f"GraphNode({self.letter})"
    
    def __repr__(self):
        return str(self)

    

    
def get_graph_updater(nodes: set[GraphNode], edges: Edges):

    
    def graph_physics(t: float, dt: float, edges=edges):
        
        positions = {node: pos for node, pos in zip(nodes, map(lambda x: x.transformed_shape.center, nodes))}

        lines = [*edges.lines_iter(),]
        for node1 in nodes:
            node1_pos = positions[node1]
            force = spring_force(node1_pos, Vec2(0,0), 0, CENTER_CONSTANT)
            for node2 in nodes:
                node2_pos = positions[node2]
                if edges.connected(node1, node2):    
                    force += repulse_force(node1_pos, node2_pos, REPULSION_CONSTANT/16)
                    force += spring_force(node1_pos, node2_pos, 0, ATTRACTION_CONSTANT)
                    force -= DAMPING * node1.velocity
                else:
                    force += repulse_force(node1_pos, node2_pos, REPULSION_CONSTANT)

            for start, end in lines:
                force += line_repulsion_force(node1_pos, start, end, LINE_REPULSION_CONSTANT)
                
            node1.velocity += dt*force/node1.weight

    return graph_physics

def line_repulsion_force(loc: Vec2, line_start: Vec2, line_end: Vec2, constant: float) -> Vec2:

    unit = unit_diff(line_end, line_start)
    ortho = Vec2(-unit.y, unit.x)

    basis_vectors = [unit, ortho]
    change_of_basis_matrix = invert(basis_vectors)

    dist = magnitude(line_start - line_end)

    pos = (loc - line_start) @ change_of_basis_matrix

    displacement_from_line = pos.y
    distance_from_line = abs(displacement_from_line)

    if dist < pos.x or pos.x < 0:
        return Vec2(0,0)
    
    return constant * (Vec2(0, pos.y) @ basis_vectors)/max(distance_from_line, 1e-8)**2


def repulse_force(loc1: Vec2, loc2: Vec2, constant: float):
    diff = loc2 - loc1
    dist = magnitude(diff)
    unit = 0 if dist == 0 else diff/dist 
    return -unit/max(dist,1)**2 * constant



def spring_force(loc1: Vec2, loc2: Vec2, length: float, constant: float):
    diff = loc2 - loc1
    dist = magnitude(diff)
    unit = 0 if dist == 0 else diff/dist
    displacement = dist - length
    return unit * displacement * constant


def get_velocity_mover(nodes: set[GraphNode]):
    def velocity_mover(t: float, dt: float):
        for node in nodes:
            # print(node.velocity * dt)
            if node.moveable:
                node.transform.translation = node.transform.translation.xy + node.velocity * dt
        return
    return velocity_mover


def bfs(nodes: list[GraphNode], edges: Edges) -> Generator[GraphNode]:
    queue = [(0, None, nodes[0])]
    queued = set(nodes[0])
    while queue:
        distance, source, destination = queue.pop(0)

        yield (distance, source, destination)

        next_nodes = list(filter(lambda x: edges.connected(destination, x) and x not in queued, nodes))
        queue.extend(map(lambda x: (distance+1, destination, x), next_nodes))
        queued.update(next_nodes)



if __name__ == "__main__":
    main()