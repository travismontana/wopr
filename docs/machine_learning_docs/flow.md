Discovery Phase:
    - List all images in source

    - Map target directories to their annotation files

    - Match annotations to images (probably by task ID in filename or directory number)


Validation Phase:

    - Verify each image has corresponding label file (what is a label file)
    - Check label format (YOLO expects: class_id x_center y_center width height per line)
    - Report orphans (images without labels, labels without images)


Split Calculation

Total valid pairs: N
Train: floor(N * 0.7)
Val: floor(N * 0.2)
Test: remainder
Shuffle list, then slice


Structure Creation

mkdir -p images/{train,val,test}
mkdir -p labels/{train,val,test}


File Distribution

For each split, copy/symlink image and matching .txt to appropriate dirs
Keep matching basenames (image.jpg → image.txt)


Metadata Generation

Create data.yaml with paths, class names, class count
(Need to extract class info from labels or Label Studio config)








Parse JSON → Extract mapping

Read each target/{N} JSON file
Extract filename from data.image URL path (after ?d=labelstudio/source/)
URL-decode filename (handle %20 → space, etc)
Store: task_id → filename → bounding_boxes


Convert annotations

For each bounding box in JSON:

Convert Label Studio format (x%, y%, width%, height%)
To YOLO format (class_id, x_center, y_center, width, height) normalized 0-1
Map rectanglelabels value to class_id integer


Generate one .txt per image with all its boxes


Build class mapping

Collect all unique rectanglelabels values from all JSONs
Assign numeric IDs (0, 1, 2...)
Store for data.yaml


Validation

Verify each JSON has corresponding image in source/
Verify each image has annotation JSON
Report orphans


Split dataset

Shuffle complete image list
Split: 70% train, 20% val, 10% test


Organize files

Create yolococo1/{images,labels}/{train,val,test}/
Copy/symlink images to appropriate split
Write converted .txt labels to appropriate split
Match basenames (image.jpg → image.txt)


Generate data.yaml

Paths to train/val/test dirs
Class count + names from step 3



workflow:
  
  1_discovery:
    name: "Parse and map annotations"
    inputs:
      - /remote/wopr/labelstudio/target/{1..268}
      - /remote/wopr/labelstudio/source/*.jpg
    actions:
      - parse_json_files
      - extract_image_path_from_data_image_url
      - url_decode_filename
      - build_mapping: task_id -> filename -> annotations
    outputs:
      - task_to_image_map
      - annotation_data

  2_class_mapping:
    name: "Build class vocabulary"
    actions:
      - collect_all_rectanglelabels_values
      - sort_unique_labels
      - assign_numeric_ids_starting_zero
    outputs:
      - classes.yaml  # {class_name: class_id}

  3_coordinate_conversion:
    name: "Convert Label Studio to YOLO format"
    input_format: "x%, y%, width%, height%"
    output_format: "class_id x_center y_center width height (normalized 0-1)"
    formula:
      x_center: "(x + width/2) / 100"
      y_center: "(y + height/2) / 100"
      width_norm: "width / 100"
      height_norm: "height / 100"
    actions:
      - convert_all_boxes_to_yolo_format
      - generate_txt_files_per_image

  4_validation:
    name: "Verify completeness"
    checks:
      - all_jsons_have_matching_images
      - all_images_have_annotations
      - all_labels_in_class_map
    outputs:
      - validation_report
      - orphan_list

  5_dataset_split:
    name: "Split into train/val/test"
    method: random_shuffle
    ratios:
      train: 0.70
      val: 0.20
      test: 0.10
    outputs:
      - train_list
      - val_list
      - test_list

  6_file_organization:
    name: "Create YOLO directory structure"
    base_path: /remote/wopr/models/yolococo1
    structure:
      - images/train/
      - images/val/
      - images/test/
      - labels/train/
      - labels/val/
      - labels/test/
    actions:
      - create_directories
      - copy_or_symlink_images_by_split
      - write_label_txt_files_by_split
      - match_basenames: "image.jpg -> image.txt"

  7_metadata:
    name: "Generate data.yaml"
    location: /remote/wopr/models/yolococo1/data.yaml
    contents:
      path: /remote/wopr/models/yolococo1
      train: images/train
      val: images/val
      test: images/test
      nc: <from_class_mapping>
      names: <from_class_mapping>

decisions:
  file_handling: "copy"  # or "symlink"