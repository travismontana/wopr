# The Dejarik board and how to figure out the cells.

- The marker (AprilTag 36h11) is on a radial.  That radial will be 360/0
- The dimensions are:
    -  Radius  | Diameter | what
    - 185 mm   |          | Marker
    - 157.5 mm | 315 mm   | outer edge
    - 137.5 mm | 275 mm   | outer ring of the board (use this or the outer edge)
    -  86 mm   | 174 mm   | middle ring
    -  40 mm   | 80 mm    | inner ring
    -   0 mm   |  0 mm    | center
- 30 deg (12 cells)
- 2 cell corridors (*HERE*), outer ring < [*HERE1*] > middle ring < [*HERE2*] > inner ring <-> center
- HERE1 = ((outer ring - middle ring)/2)+middle ring (111.75 mm)
- HERE2 = ((middle_ring - inner_ring)/2)+inner ring (63 mm)
Cell 0 center: (111.75 mm, 15*)
Cell 1 center: (111.75 mm, 45*)
...
cell 6 center: (111.75 mm, 195*)
Cell 11 center: (111.75 mm, 345*)
Cell 12 center: (63 mm, 15*)
...
cell 18 center: (63 mm, 195*)
Cell 23 center: (63 mm, 345*)
Marker: (185 mm, 0*)