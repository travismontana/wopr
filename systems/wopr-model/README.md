# this runs on the machine with the gpu.

```
# Recommended: mount workspace and specify project path
sudo docker run --rm -it -v "$(pwd)":/w -w /w ultralytics/ultralytics:latest \
  yolo train model=yolo26n.pt data=coco8.yaml project=/w/runs
```

```
-v host volume

-w working directory
```

```
BASE_DIR=/remote/wopr/models

export PROJECTID= <where to save>
export YOLO_COMMAND= <what command to give to yolo>
export PATH_TO_MODEL= <which model to use>

docker run \
--ipc=host \
--runtime=nvidia \
--gpus all \
--rm -it \
-v /remote/wopr/ultralytics/${PROJECTID}:/external \
-w /ultralytics \
ultralytics/ultralytics:latest \
yolo ${YOLO_COMMAND} model=${PATH_TO_MODEL} project=/external/runs

```

```
export BASE_DIR=/remote/wopr/models
models = get_all("models")
