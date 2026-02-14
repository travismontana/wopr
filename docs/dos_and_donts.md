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


Here's the pipeline broken down stage by stage. Each stage has alternatives to swap in and compare. The idea is to treat it like a signal chain — each stage feeds the next, and the "best" combo depends on what's being detected.

Stage 0: Input (already done)
cv2.imdecode() → img_bgr_u8
cv2.cvtColor()  → img_gray_u8, img_rgb_u8
This is the starting point. Everything below works on img_gray_u8 unless noted.

Stage 1: Blurring (noise reduction)
Purpose: smooth out noise so edge/contour detection doesn't hallucinate edges from texture or camera grain.
FunctionWhat it doesGood forcv2.GaussianBlur(img, (k,k), 0)Weighted average, smooth all-aroundGeneral purpose, good defaultcv2.medianBlur(img, k)Takes median of neighborhoodSalt-and-pepper noise, preserves edges bettercv2.bilateralFilter(img, d, sigmaColor, sigmaSpace)Smooths while preserving edgesBest edge preservation, but slowestcv2.blur(img, (k,k))Simple box averageFast, dumb, rarely the best choice
k must be odd (3, 5, 7...). Start with 5.
For board detection: medianBlur or bilateralFilter — the board has hard edges that matter, and texture inside cells that doesn't.
pythonblur_gauss = cv2.GaussianBlur(img_gray_u8, (5,5), 0)
blur_median = cv2.medianBlur(img_gray_u8, 5)
blur_bilateral = cv2.bilateralFilter(img_gray_u8, 9, 75, 75)

Stage 2: Thresholding (optional, depends on path)
Two paths diverge here — edge-based (go to Stage 3) or threshold-based (stay here then go to Stage 4).
FunctionWhat it doesGood forcv2.threshold(img, thresh, max, type)Global binary cutoffUniform lighting onlycv2.adaptiveThreshold(img, max, method, type, blockSize, C)Local adaptive cutoffUneven lighting (camera shots of boards)cv2.inRange(img_hsv, lower, upper)Color range maskFinding colored regions in HSV space
For boards under variable lighting: adaptiveThreshold with ADAPTIVE_THRESH_GAUSSIAN_C is almost always better than global.
python# Global
_, thresh_global = cv2.threshold(blur_gauss, 127, 255, cv2.THRESH_BINARY)

# Otsu (auto-picks threshold)
_, thresh_otsu = cv2.threshold(blur_gauss, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

# Adaptive
thresh_adapt = cv2.adaptiveThreshold(blur_gauss, 255,
    cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

Stage 3: Edge Detection
FunctionWhat it doesGood forcv2.Canny(img, low, high)Gradient-based, dual thresholdClean edges, most commoncv2.Laplacian(img, cv2.CV_64F)Second derivativeDetects edges but noisiercv2.Sobel(img, cv2.CV_64F, dx, dy)First derivative, directionalWhen direction matters (horizontal vs vertical lines)
Canny is the workhorse here. The two thresholds control sensitivity — low catches more edges, high is strict.
pythonedges_canny = cv2.Canny(blur_gauss, 50, 150)
edges_canny_tight = cv2.Canny(blur_gauss, 100, 200)
edges_canny_loose = cv2.Canny(blur_median, 30, 100)

edges_laplacian = np.uint8(np.absolute(cv2.Laplacian(blur_gauss, cv2.CV_64F)))
edges_sobel_x = np.uint8(np.absolute(cv2.Sobel(blur_gauss, cv2.CV_64F, 1, 0)))
edges_sobel_y = np.uint8(np.absolute(cv2.Sobel(blur_gauss, cv2.CV_64F, 0, 1)))

Stage 4: Finding Things
This is where the goals split by target:
4a: Contours — for board outline, cells, circumference
pythoncontours, hierarchy = cv2.findContours(edges_or_thresh,
    cv2.RETR_TREE,        # or RETR_EXTERNAL for outermost only
    cv2.CHAIN_APPROX_SIMPLE)
Retrieval modes matter:
ModeReturnsRETR_EXTERNALOnly outermost contoursRETR_LISTAll contours, flat listRETR_TREEFull hierarchy (parent/child) — best for nested board cells
Then for each contour:
python# Approximate polygon (reduce points)
epsilon = 0.02 * cv2.arcLength(contour, True)
approx = cv2.approxPolyDP(contour, epsilon, True)

# If len(approx) == 4 → likely a cell or board rectangle
# If len(approx) > 8  → likely circular (board edge?)

# Bounding shapes
area = cv2.contourArea(contour)
x, y, w, h = cv2.boundingRect(contour)
(cx, cy), radius = cv2.minEnclosingCircle(contour)  # ← circumference + center
rect = cv2.minAreaRect(contour)                       # ← rotated rectangle
4b: Hough Lines — for grid/cell edges
python# Standard (returns rho, theta)
lines = cv2.HoughLines(edges_canny, 1, np.pi/180, threshold=150)

# Probabilistic (returns line segments — usually more useful)
lines_p = cv2.HoughLinesP(edges_canny, 1, np.pi/180,
    threshold=80, minLineLength=50, maxLineGap=10)
Probabilistic Hough is generally better for finding grid lines. The intersections of detected lines = cell corners.
4c: Hough Circles — for circular board outline
pythoncircles = cv2.HoughCircles(blur_median, cv2.HOUGH_GRADIENT,
    dp=1, minDist=100,
    param1=200, param2=50,
    minRadius=100, maxRadius=500)
If the board is circular (Dune Imperium board regions?), this directly gives center + radius.
4d: ArUco Markers — dedicated detector
pythonaruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
parameters = cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)

corners, ids, rejected = detector.detectMarkers(img_gray_u8)
ArUco detection runs its own internal adaptive thresholding and contour finding. It works best on the unblurred grayscale image — the blur can actually hurt marker detection. The parameters object has ~30 tunable knobs if detection is flaky (adaptiveThreshWinSizeMin, adaptiveThreshWinSizeStep, cornerRefinementMethod, etc.).

Recommended comparison matrix
For each of the 4 goals, the pipeline that makes the most sense to try first:
GoalBlurNext StepFinderBoard centermedianBlur(5)Canny(50,150)findContours(RETR_EXTERNAL) → minEnclosingCircleOuter circumferencemedianBlur(5)Canny(50,150)HoughCircles or largest contourCell cornersbilateralFilteradaptiveThresholdfindContours(RETR_TREE) → approxPolyDP or HoughLinesP → intersectionsArUco markernone (raw gray)—ArucoDetector.detectMarkers()
Want me to put together a comparison notebook that runs all the combos side by side with matplotlib subplots so each step is visible? That'd be a Medium — but it'd make the A/B testing a lot faster than doing it piecemeal.