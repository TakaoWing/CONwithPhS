
import math

Ax, Ay = 369, 337
Bx, By = 364, 393
Cx, Cy = 364, 213

print((math.atan2(Cy - By, Cx - Bx) - math.atan2(Ay - By, Ax - Bx)) / math.pi * 180)
