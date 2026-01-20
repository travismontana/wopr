workflow:
  
  1_discovery:
    name: "Discovery Phase"
    inputs:
      - /remote/wopr/labelstudio/source/*.jpg
      - /remote/wopr/labelstudio/target/{1..268} (JSON files)
    actions:
      - list_all_source_images
      - read_json_files_from_target
      - extract_image_reference_from_data_image_url
      - url_decode_filenames
      - parse_rectanglelabels_annotations
      - build_image_to_annotations_mapping
    outputs:
      - image_list
      - annotation_map: {filename: {task_id, boxes[]}}

  2_validation:
    name: "Validation Phase"
    checks:
      - verify_each_image_has_annotation
      - verify_each_annotation_references_existing_image
      - validate_label_format: "rectanglelabels present in all boxes"
      - check_coordinate_ranges: "x,y,width,height within 0-100"
    actions:
      - report_orphaned_images
      - report_orphaned_annotations
      - report_malformed_entries
    outputs:
      - validation_report
      - valid_pairs_list

  3_class_mapping:
    name: "Build class vocabulary"
    source: "rectanglelabels values from all JSON files"
    actions:
      - collect_unique_rectanglelabels
      - sort_alphabetically
      - assign_sequential_ids: "start at 0"
    outputs:
      - class_to_id_map
      - classes_yaml

  4_coordinate_conversion:
    name: "Convert to YOLO format"
    input_format: 
      labelstudio: "x%, y%, width%, height% (top-left corner)"
    output_format:
      yolo: "class_id x_center y_center width height (normalized 0-1)"
    conversion:
      x_center: "(x + width/2) / 100"
      y_center: "(y + height/2) / 100"
      width_normalized: "width / 100"
      height_normalized: "height / 100"
      class_id: "from class_to_id_map"
    actions:
      - convert_all_rectanglelabels_boxes
      - format_as_yolo_lines: "one line per box"
      - aggregate_by_image: "all boxes for same image in one .txt"
    outputs:
      - label_txt_files: {filename: yolo_formatted_content}

  5_split_calculation:
    name: "Calculate train/val/test splits"
    inputs:
      - valid_pairs_list
    ratios:
      train: 0.70
      val: 0.20
      test: 0.10
    method:
      - shuffle_list_randomly
      - calculate_train_count: "floor(N * 0.7)"
      - calculate_val_count: "floor(N * 0.2)"
      - calculate_test_count: "remainder"
      - slice_into_three_lists
    outputs:
      - train_files_list
      - val_files_list
      - test_files_list

  6_structure_creation:
    name: "Create YOLO directory structure"
    base: /remote/wopr/models/yolococo1
    directories:
      - images/train/
      - images/val/
      - images/test/
      - labels/train/
      - labels/val/
      - labels/test/
    actions:
      - mkdir_p_all_directories

  7_file_distribution:
    name: "Populate directory structure"
    method: "copy"  # or "symlink"
    actions:
      - for_each_split:
          - copy_images_from_source_to_images_split
          - write_label_txt_to_labels_split
          - ensure_matching_basenames: "image.jpg -> image.txt"
    filename_handling:
      - preserve_original_names
      - strip_extension_for_label: "file.jpg -> file.txt"

  8_metadata_generation:
    name: "Generate data.yaml"
    location: /remote/wopr/models/yolococo1/data.yaml
    content:
      path: /remote/wopr/models/yolococo1
      train: images/train
      val: images/val  
      test: images/test
      nc: <count from class_to_id_map>
      names: <list from class_to_id_map ordered by id>
    format: YAML

outputs:
  final_structure: |
    /remote/wopr/models/yolococo1/
    ├── images/
    │   ├── train/  (70% of images)
    │   ├── val/    (20% of images)
    │   └── test/   (10% of images)
    ├── labels/
    │   ├── train/  (matching .txt files)
    │   ├── val/    (matching .txt files)
    │   └── test/   (matching .txt files)
    └── data.yaml