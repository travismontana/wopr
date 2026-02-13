# Do's and don'ts

Each system needs to have:
```
wopr-system/
|- wopr-system/ - the code if not a container
|- container/ - the base of the container, Dockerfile lives here
|- compose/ - the docker compose base

Image naming:

img_<stage>_<colorspace>_<dtype>[_range][_params]

stage = raw | decoded | gray | blur | edges | thresh | mask | contours | lines | circles | cells | overlay

colorspace = bgr | rgb | gray | hsv | lab

dtype = u8 | f32 | f64

range (optional) = 0_255 | 0_1

params = k5 | t50_150 | s1p2 | r20_200 (encode tunables)