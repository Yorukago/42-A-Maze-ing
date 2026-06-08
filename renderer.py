from mlx import Mlx

class MlxUtils():
    def __init__(self, width: int, height: int):
        self.mlx: Mlx = Mlx()
        self.pmlx: any = self.mlx.mlx_init()
        self.pwin: any = self.mlx.mlx_new_window(self.pmlx, width, height, "A-Maze-ing")

c


omlx = MlxUtils(1000, 1000)
omlx.mlx.mlx_loop(omlx.pmlx)

bgimg = omlx.mlx.mlx_new_image()
