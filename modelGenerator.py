import numpy as np
from stl import mesh

class modelGenerator:
    def __init__(self):
        self.model = [4]

    def safe_mesh(self):
        vertices = np.array([
            [0, 0, 0],  # 0
            [1, 0, 0],  # 1
            [1, 1, 0],  # 2
            [0, 1, 0],  # 3
            [0, 0, 1],  # 4
            [1, 0, 1],  # 5
            [1, 1, 1],  # 6
            [0, 1, 1],  # 7
        ])
        faces = np.array([
            [0, 3, 1], [1, 3, 2],  # bottom
            [0, 1, 4], [1, 5, 4],  # front
            [1, 2, 5], [2, 6, 5],  # right
            [2, 3, 6], [3, 7, 6],  # back
            [3, 0, 7], [0, 4, 7],  # left
            [4, 5, 6], [4, 6, 7],  # top
        ])
        self.model[0] = mesh.Mesh(np.zeros(len(faces), dtype=mesh.Mesh.dtype))
        for i, face in enumerate(faces):
            self.model[0].vectors[i] = vertices[face]
        self.model[0].save("model.stl")

if __name__ == "__main__":
    mg = modelGenerator()
    mg.safe_mesh()