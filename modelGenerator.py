import numpy as np
from stl import mesh
from PIL import Image

class ModelGenerator:
    def __init__(self):
        self.baseVertices = None
        self.baseFaces = None
        self.finalVertices = [[]] * 4
        self.imgWidth = None
        self.imgLength = None
        self.imgSize = None
        self.meshWidth = None
        self.meshLenght = None

    def _generateBase(self, xSize, ySize):
        # Create Vertices
        xs = np.tile(np.arange(xSize), ySize * 2)
        ys = np.repeat(np.arange(ySize), xSize)
        ys = np.tile(ys, 2)
        zs = np.repeat([0, 1], xSize * ySize)
        self.baseVertices = np.stack([xs, ys, zs], axis=1, dtype=np.float64)

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
        self.imgWidth = len(heightMap)
        self.imgLength = len(heightMap[0])

        self.imgSize = self.imgWidth * self.imgLength

        self._generateBase(self.imgWidth, self.imgLength)
        self.baseVertices[self.imgSize:, 2] = heightMap.T.ravel() / 65536   # 2^16 because png16

    def generateMeshes(self, matrices, layerHeight, width, length, heightOffset, heightScale):
        self.meshWidth = width
        self.meshLenght = length

        # Set up master layer
        self.finalVertices[0] = self.baseVertices
        self.finalVertices[0][self.imgSize:, :2] = self.baseVertices[self.imgSize:, :2]
        self.finalVertices[0][self.imgSize:, 2] = self.baseVertices[self.imgSize:, 2] * heightScale + heightOffset

        # Set up other layers
        for filament in range(1, 4):
            # Set x and y axis
            self.finalVertices[filament] = self.finalVertices[0]
            # Set z axis
            for pixel in range(self.imgSize):
                if matrices[filament][pixel % self.imgWidth, pixel // self.imgWidth] < 6:
                    self.finalVertices[filament][self.imgSize + pixel, 2] = self.finalVertices[0][self.imgSize + pixel, 2] - (layerHeight * matrices[filament][pixel % self.imgWidth, pixel // self.imgWidth])
                else:
                    # Filament not used
                    self.finalVertices[filament][self.imgSize + pixel, 2] = 0
        print("Mesh generation complete")

    def get_mesh(self, filament):
        # Create Mesh
        model = mesh.Mesh(np.zeros(len(self.baseFaces), dtype=mesh.Mesh.dtype))
        for i, face in enumerate(self.baseFaces):
            model.vectors[i] = self.finalVertices[filament][face]

        model.x *= (self.meshWidth / self.imgWidth)
        model.y *= (self.meshLenght / self.imgLength)
        
        return model

if __name__ == "__main__":
    mg = ModelGenerator()
    img  = Image.open("Height16.png")
    data = np.array(img, dtype=np.uint16)
    # data = np.array([[[0, 0, 0], [1, 1, 1], [100, 100, 100]], [[223, 223, 223], [224, 224, 224], [225, 225, 225]]], dtype=np.uint8)
    # data = np.array([[0, 1, 100], [223, 224, 225]], dtype=np.uint16)
    mg.loadHeightMap(data)
    mg.generateMeshes(0.2, 1, 1, 1, 0.5)
    mg.get_mesh(0).save("model.stl")