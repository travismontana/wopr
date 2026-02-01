architecture_breakdown:

  1_discovery:
    business_logic:
      location: lib/training/discovery.py
      short_desc: Parse Label Studio exports and map annotations to source images
      desc: |
        Reads Label Studio JSON export files from target directory and extracts image 
        references from data.image URLs. Handles URL decoding of filenames. Lists all 
        source images and creates mapping between filenames and their annotations. 
        Validates JSON structure contains expected fields. Builds complete inventory 
        of available training data for downstream processing.
      functions:
        - list_source_images(source_dir) -> List[Path]
        - parse_labelstudio_json(json_path) -> Dict
        - extract_image_path(data_url) -> str
        - url_decode(filename) -> str
        - build_annotation_map(jsons, images) -> Dict
      returns: {image_list, annotation_map}
    
    specific_logic:
      webui: streamlit_app/pages/training/discover.py
      api: POST /api/v1/training/discover
      celery: tasks.training.discover_task

  2_validation:
    business_logic:
      location: lib/training/validation.py
      short_desc: Verify data integrity and completeness
      desc: |
        Validates each image has corresponding annotations and vice versa. Checks 
        coordinate ranges within valid bounds (0-100 for Label Studio format). 
        Verifies all bounding boxes have proper rectanglelabels. Identifies orphaned 
        files (images without annotations, annotations without images) and malformed 
        entries. Generates detailed validation report with warnings and errors to 
        prevent training on corrupt data. Reports statistics on valid pairs and issues 
        found.
      functions:
        - verify_image_annotation_pairs(image_list, annotation_map) -> ValidationReport
        - find_orphaned_images(images, annotations) -> List[str]
        - find_orphaned_annotations(annotations, images) -> List[int]
        - validate_coordinate_ranges(annotations) -> List[Issue]
        - check_label_format(annotations) -> List[Issue]
      returns: {validation_report, valid_pairs, orphans}
    
    specific_logic:
      webui: streamlit_app/pages/training/validate.py
      api: POST /api/v1/training/validate
      celery: tasks.training.validate_task

  3_class_mapping:
    business_logic:
      location: lib/training/classes.py
      short_desc: Build class vocabulary from label data
      desc: |
        Extracts all unique rectanglelabels values from annotation data to build 
        complete class vocabulary. Sorts labels alphabetically for consistency and 
        assigns sequential numeric IDs starting from 0 (YOLO requirement). Generates 
        classes.yaml metadata file with class names and IDs. Ensures consistent class 
        mapping across train/val/test splits for model training.
      functions:
        - collect_unique_labels(annotation_map) -> Set[str]
        - sort_and_index(labels) -> Dict[str, int]
        - generate_classes_yaml(class_map) -> str
      returns: {class_to_id_map, classes_yaml}
    
    specific_logic:
      webui: streamlit_app/pages/training/classes.py
      api: GET /api/v1/training/classes
      celery: tasks.training.build_classes_task

  4_coordinate_conversion:
    business_logic:
      location: lib/training/converter.py
      short_desc: Convert Label Studio format to YOLO format
      desc: |
        Transforms Label Studio bounding box coordinates (x%, y%, width%, height% from 
        top-left) to YOLO format (class_id, x_center, y_center, width, height normalized 
        0-1). Applies coordinate conversion formulas. Maps rectanglelabels to numeric 
        class IDs. Generates one .txt file per image containing all bounding boxes in 
        YOLO format, one box per line. Ensures compatibility with YOLO training pipeline.
      functions:
        - labelstudio_to_yolo(x, y, width, height) -> Tuple[float, float, float, float]
        - convert_box(box, class_map) -> str
        - convert_annotation(annotation, class_map) -> List[str]
        - generate_label_files(annotation_map, class_map) -> Dict[str, str]
      returns: {filename: yolo_txt_content}
    
    specific_logic:
      webui: streamlit_app/pages/training/convert.py
      api: POST /api/v1/training/convert
      celery: tasks.training.convert_task

  5_split_calculation:
    business_logic:
      location: lib/training/splitter.py
      short_desc: Split dataset into train/validation/test sets
      desc: |
        Randomly shuffles complete dataset and splits into train (70%), validation (20%), 
        and test (10%) sets. Uses configurable ratios and optional random seed for 
        reproducibility. Calculates split sizes using floor division with remainder going 
        to test set. Ensures no overlap between splits and maintains data distribution.
      functions:
        - shuffle_list(items, seed=None) -> List
        - calculate_split_sizes(total, train_ratio, val_ratio, test_ratio) -> Tuple[int, int, int]
        - split_dataset(items, train_size, val_size) -> Dict[str, List]
      returns: {train_files, val_files, test_files}
    
    specific_logic:
      webui: streamlit_app/pages/training/split.py
      api: POST /api/v1/training/split
      celery: tasks.training.split_task

  6_structure_creation:
    business_logic:
      location: lib/training/structure.py
      short_desc: Create YOLO-compatible directory structure
      desc: |
        Generates standard YOLO directory tree with separate folders for images and 
        labels, each split into train/val/test subdirectories. Verifies write permissions 
        on base path before creation. Creates all required directories recursively. 
        Returns list of created paths for verification.
      functions:
        - generate_directory_tree(base_path) -> List[Path]
        - create_directories(paths) -> None
        - verify_permissions(base_path) -> bool
      returns: {created_paths}
    
    specific_logic:
      webui: streamlit_app/pages/training/structure.py
      api: POST /api/v1/training/create-structure
      celery: tasks.training.create_structure_task

  7_file_distribution:
    business_logic:
      location: lib/training/distributor.py
      short_desc: Distribute images and labels to split directories
      desc: |
        Copies images from source to appropriate split directories (train/val/test) 
        based on split calculation. Writes converted YOLO label files to matching 
        label directories. Ensures image and label filenames match (image.jpg -> 
        image.txt). Supports copy or symlink methods. Validates successful distribution 
        and returns list of distributed file paths.
      functions:
        - copy_image(src, dest) -> Path
        - write_label_file(dest, content) -> Path
        - distribute_split(files, split_name, base_path, method='copy') -> List[Path]
        - ensure_matching_basenames(image_path, label_path) -> bool
      returns: {distributed_files}
    
    specific_logic:
      webui: streamlit_app/pages/training/distribute.py
      api: POST /api/v1/training/distribute
      celery: tasks.training.distribute_task

  8_metadata_generation:
    business_logic:
      location: lib/training/metadata.py
      short_desc: Generate YOLO data.yaml configuration file
      desc: |
        Creates YOLO data.yaml file containing dataset paths, class count, and class 
        names. Formats paths relative to base directory or as absolute paths. Validates 
        YAML structure before writing. Includes train/val/test paths, nc (number of 
        classes), and names (ordered list of class labels) required for YOLO training.
      functions:
        - generate_data_yaml(base_path, class_map) -> str
        - write_yaml(path, content) -> Path
        - validate_yaml_schema(content) -> bool
      returns: {yaml_path, yaml_content}
    
    specific_logic:
      webui: streamlit_app/pages/training/metadata.py
      api: POST /api/v1/training/generate-metadata
      celery: tasks.training.metadata_task

orchestration:
  
  business_logic:
    location: lib/training/pipeline.py
    short_desc: Execute complete dataset preparation pipeline
    desc: |
      Orchestrates all eight phases in sequence: discovery, validation, class mapping, 
      coordinate conversion, dataset splitting, structure creation, file distribution, 
      and metadata generation. Handles errors at each step with detailed reporting. 
      Allows individual phase execution or full pipeline run. Collects metrics and 
      generates summary report. Returns complete dataset structure ready for YOLO 
      training.
    function: run_full_pipeline(source_dir, target_dir, output_dir, config)
    calls_sequence:
      - discovery → validation → class_mapping → conversion → split → structure → distribution → metadata
    returns: {final_structure, reports, metrics}
  
  specific_logic:
    webui: streamlit_app/pages/training/pipeline.py
    api: POST /api/v1/training/run-pipeline (async, returns task_id)
    celery: tasks.training.pipeline_task (long-running)

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
  ├── discovery.py
  ├── validation.py
  ├── classes.py
  ├── converter.py
  ├── splitter.py
  ├── structure.py
  ├── distributor.py
  ├── metadata.py
  ├── pipeline.py
  └── utils.py

streamlit_app/pages/training/
  ├── discover.py
  ├── validate.py
  ├── classes.py
  ├── convert.py
  ├── split.py
  ├── structure.py
  ├── distribute.py
  ├── metadata.py
  └── pipeline.py

api/routes/training.py
workers/tasks/training.py