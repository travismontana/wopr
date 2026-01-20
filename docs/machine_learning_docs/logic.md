architecture_breakdown:

  1_discovery:
    business_logic:
      location: lib/training/discovery.py
      functions:
        - list_source_images(source_dir) -> List[Path]
        - parse_labelstudio_json(json_path) -> Dict
        - extract_image_path(data_url) -> str
        - url_decode(filename) -> str
        - build_annotation_map(jsons, images) -> Dict
      returns: {image_list, annotation_map}
    
    specific_logic:
      CLI: scripts/01_discover.py
      API: POST /api/v1/training/discover
      Celery: tasks.training.discover_task

  2_validation:
    business_logic:
      location: lib/training/validation.py
      functions:
        - verify_image_annotation_pairs(image_list, annotation_map) -> ValidationReport
        - find_orphaned_images(images, annotations) -> List[str]
        - find_orphaned_annotations(annotations, images) -> List[int]
        - validate_coordinate_ranges(annotations) -> List[Issue]
        - check_label_format(annotations) -> List[Issue]
      returns: {validation_report, valid_pairs, orphans}
    
    specific_logic:
      CLI: scripts/02_validate.py
      API: POST /api/v1/training/validate
      Celery: tasks.training.validate_task

  3_class_mapping:
    business_logic:
      location: lib/training/classes.py
      functions:
        - collect_unique_labels(annotation_map) -> Set[str]
        - sort_and_index(labels) -> Dict[str, int]
        - generate_classes_yaml(class_map) -> str
      returns: {class_to_id_map, classes_yaml}
    
    specific_logic:
      CLI: scripts/03_build_classes.py
      API: GET /api/v1/training/classes
      Celery: tasks.training.build_classes_task

  4_coordinate_conversion:
    business_logic:
      location: lib/training/converter.py
      functions:
        - labelstudio_to_yolo(x, y, width, height) -> Tuple[float, float, float, float]
        - convert_box(box, class_map) -> str  # YOLO line format
        - convert_annotation(annotation, class_map) -> List[str]
        - generate_label_files(annotation_map, class_map) -> Dict[str, str]
      returns: {filename: yolo_txt_content}
    
    specific_logic:
      CLI: scripts/04_convert.py
      API: POST /api/v1/training/convert
      Celery: tasks.training.convert_task

  5_split_calculation:
    business_logic:
      location: lib/training/splitter.py
      functions:
        - shuffle_list(items, seed=None) -> List
        - calculate_split_sizes(total, train_ratio, val_ratio, test_ratio) -> Tuple[int, int, int]
        - split_dataset(items, train_size, val_size) -> Dict[str, List]
      returns: {train_files, val_files, test_files}
    
    specific_logic:
      CLI: scripts/05_split.py
      API: POST /api/v1/training/split
      Celery: tasks.training.split_task

  6_structure_creation:
    business_logic:
      location: lib/training/structure.py
      functions:
        - generate_directory_tree(base_path) -> List[Path]
        - create_directories(paths) -> None
        - verify_permissions(base_path) -> bool
      returns: {created_paths}
    
    specific_logic:
      CLI: scripts/06_create_structure.py
      API: POST /api/v1/training/create-structure
      Celery: tasks.training.create_structure_task

  7_file_distribution:
    business_logic:
      location: lib/training/distributor.py
      functions:
        - copy_image(src, dest) -> Path
        - write_label_file(dest, content) -> Path
        - distribute_split(files, split_name, base_path, method='copy') -> List[Path]
        - ensure_matching_basenames(image_path, label_path) -> bool
      returns: {distributed_files}
    
    specific_logic:
      CLI: scripts/07_distribute.py
      API: POST /api/v1/training/distribute
      Celery: tasks.training.distribute_task

  8_metadata_generation:
    business_logic:
      location: lib/training/metadata.py
      functions:
        - generate_data_yaml(base_path, class_map) -> str
        - write_yaml(path, content) -> Path
        - validate_yaml_schema(content) -> bool
      returns: {yaml_path, yaml_content}
    
    specific_logic:
      CLI: scripts/08_generate_metadata.py
      API: POST /api/v1/training/generate-metadata
      Celery: tasks.training.metadata_task

orchestration:
  
  business_logic:
    location: lib/training/pipeline.py
    function: run_full_pipeline(source_dir, target_dir, output_dir, config)
    calls_all_business_logic_in_sequence:
      - discovery → validation → class_mapping → conversion → split → structure → distribution → metadata
    returns: {final_structure, reports, metrics}
  
  specific_logic:
    CLI: scripts/run_pipeline.py --source X --target Y --output Z
    API: POST /api/v1/training/run-pipeline (async, returns task_id)
    Celery: tasks.training.pipeline_task (long-running)

shared_utilities:
  location: lib/training/utils.py
  functions:
    - read_json(path)
    - write_json(path, data)
    - parse_url_path(url)
    - ensure_dir(path)
```

**File structure:**
```
lib/training/
  ├── __init__.py
  ├── discovery.py       # Business logic
  ├── validation.py
  ├── classes.py
  ├── converter.py
  ├── splitter.py
  ├── structure.py
  ├── distributor.py
  ├── metadata.py
  ├── pipeline.py        # Orchestration
  └── utils.py

scripts/                 # CLI specific
  ├── 01_discover.py
  ├── 02_validate.py
  ├── ...
  └── run_pipeline.py

api/routes/training.py   # API specific
workers/tasks/training.py # Celery specific