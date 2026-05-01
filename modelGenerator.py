import numpy as np
from stl import mesh
from PIL import Image

class modelGenerator:
    def __init__(self):
        self.baseVertices = None
        self.baseFaces = None
        self.finalVertices = [4]

    def _generateBase(self, xSize, ySize):
        # Create Vertices
        xs = np.tile(np.arange(xSize), ySize * 2)
        ys = np.repeat(np.arange(ySize), xSize)
        ys = np.tile(ys, 2)
        zs = np.repeat([0, 1], xSize * ySize)
        self.baseVertices = np.stack([xs, ys, zs], axis=1)

        # Create Faces
        L = xSize * ySize  # layer size

        # --- Top / Bottom ---
        x = np.tile(np.arange(xSize - 1), ySize - 1)
        y = np.repeat(np.arange(ySize - 1), xSize - 1)

        tl = y * xSize + x;        tr = y * xSize + x + 1
        bl = (y+1) * xSize + x;    br = (y+1) * xSize + x + 1

        top    = np.stack([L + tl, L + tr, L + br,
                        L + tl, L + br, L + bl], axis=1).reshape(-1, 3)
        bottom = np.stack([tl, br, tr,
                        tl, bl, br], axis=1).reshape(-1, 3)

        # --- Front / Back ---
        x = np.arange(xSize - 1)

        fl = x;              fr = x + 1
        front = np.stack([fl, fr, L + fr,
                        fl, L + fr, L + fl], axis=1).reshape(-1, 3)

        bl_ = (ySize-1) * xSize + x;  br_ = (ySize-1) * xSize + x + 1
        back  = np.stack([bl_, L + bl_, L + br_,
                        bl_, L + br_, br_], axis=1).reshape(-1, 3)

        # --- Left / Right ---
        y = np.arange(ySize - 1)

        lt = y * xSize;            lb = (y+1) * xSize
        left  = np.stack([lt, L + lt, L + lb,
                        lt, L + lb, lb], axis=1).reshape(-1, 3)

        rt = y * xSize + (xSize-1);   rb = (y+1) * xSize + (xSize-1)
        right = np.stack([rt, rb, L + rb,
                        rt, L + rb, L + rt], axis=1).reshape(-1, 3)
        
        self.baseFaces = np.concatenate([top, bottom, front, back, left, right])

    def loadHeightMap(self, heightMap):
        xSize = len(heightMap)
        ySize = len(heightMap[0])

        self._generateBase(xSize, ySize)
        self.baseVertices[xSize*ySize:, 2] = heightMap[:, :, 0].T.ravel()

    def get_mesh(self, filament):
        # Create Mesh
        model = mesh.Mesh(np.zeros(len(self.baseFaces), dtype=mesh.Mesh.dtype))
        for i, face in enumerate(self.baseFaces):
            model.vectors[i] = self.finalVertices[filament][face]
        
        return model

if __name__ == "__main__":
    mg = modelGenerator()
    # mg._generateBase(32, 32)
    img  = Image.open("Height.png").convert("RGB")
    data = np.array(img, dtype=np.uint8)
    mg.loadHeightMap(data)
    mg.finalVertices[0] = mg.baseVertices
    mg.get_mesh(0).save("model.stl")