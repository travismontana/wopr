1_discovery:
  webui:
    - Button: "Discover Dataset"
    - Input fields: source_path, target_path
    - Display: image count, annotation count
    - Show: annotation_map preview
  api:
    - POST /api/v1/training/discover
    - Validate paths exist
    - Enqueue celery task
    - Return task_id
    - GET /api/v1/training/status/{task_id}
  celery:
    - Call lib.training.discovery.run_discovery()
    - Update progress: "Reading JSONs... 50/268"
    - Store results in Redis
    - Return {image_list, annotation_map}

2_validation:
  webui:
    - Button: "Validate Dataset"
    - Display: validation report table
    - Show orphans list (red), valid pairs (green)
    - Download: validation_report.json
  api:
    - POST /api/v1/training/validate
    - Accept annotation_map from previous step or storage
    - Enqueue celery task
    - Return task_id
  celery:
    - Call lib.training.validation.verify_image_annotation_pairs()
    - Update progress: "Checking pairs... 120/242"
    - Return {validation_report, valid_pairs, orphans}

3_class_mapping:
  webui:
    - Display: class table (name, ID, count)
    - Preview: classes.yaml content
    - Download: classes.yaml
  api:
    - GET /api/v1/training/classes
    - Synchronous (fast operation)
    - Return class_map immediately
  celery:
    - Not used (too fast for async)
    - If part of pipeline: call lib.training.classes functions

4_coordinate_conversion:
  webui:
    - Button: "Convert to YOLO"
    - Progress bar: "Converting... 120/242"
    - Preview: sample .txt file content
  api:
    - POST /api/v1/training/convert
    - Enqueue celery task
    - Return task_id
  celery:
    - Call lib.training.converter.generate_label_files()
    - Update progress: "Converting boxes... 120/242"
    - Return {filename: yolo_txt_content} dict

5_split_calculation:
  webui:
    - Sliders: train%, val%, test%
    - Input: random seed (optional)
    - Display: split counts (train: 169, val: 48, test: 25)
    - Show file lists by split
  api:
    - POST /api/v1/training/split
    - Validate ratios sum to 1.0
    - Synchronous or async depending on size
    - Return split lists
  celery:
    - Call lib.training.splitter.split_dataset()
    - Return {train_files, val_files, test_files}

6_structure_creation:
  webui:
    - Input: base output path
    - Button: "Create Structure"
    - Display: directory tree preview
    - Show: created paths checklist
  api:
    - POST /api/v1/training/create-structure
    - Validate base path writable
    - Synchronous (fast)
    - Return created paths
  celery:
    - Not used (too fast)
    - If part of pipeline: call lib.training.structure.create_directories()

7_file_distribution:
  webui:
    - Radio: Copy vs Symlink
    - Button: "Distribute Files"
    - Progress: "Copying images... 120/242"
    - Display: distribution summary
  api:
    - POST /api/v1/training/distribute
    - Enqueue celery task
    - Return task_id
  celery:
    - Call lib.training.distributor.distribute_split()
    - Update progress: "Train: 120/169, Val: 30/48, Test: 15/25"
    - Copy images + write label files
    - Return {distributed_files}

8_metadata_generation:
  webui:
    - Preview: data.yaml content
    - Button: "Generate Metadata"
    - Download: data.yaml
  api:
    - POST /api/v1/training/generate-metadata
    - Synchronous (fast)
    - Return yaml content
  celery:
    - Not used (too fast)
    - If part of pipeline: call lib.training.metadata.generate_data_yaml()

orchestration (full_pipeline):
  webui:
    - Single button: "Run Full Pipeline"
    - Config panel: all parameters
    - Progress tracker: 8 phases with status
    - Real-time logs: current phase + substep
    - Final summary: files created, time elapsed
    - Download: complete dataset + reports
  api:
    - POST /api/v1/training/run-pipeline
    - Validate all parameters
    - Enqueue celery pipeline task
    - Return task_id
    - GET /api/v1/training/status/{task_id} returns:
      {
        status: "running",
        current_phase: "4_coordinate_conversion",
        phase_progress: "120/242",
        overall_progress: 0.52
      }
  celery:
    - Call lib.training.pipeline.run_full_pipeline()
    - Execute phases 1-8 in sequence
    - Update progress after each phase
    - Store intermediate results
    - Handle errors, rollback if needed
    - Return {final_structure, reports, metrics}

async_vs_sync_decisions:
  async_operations (celery):
    - 1_discovery (268 JSON files to parse)
    - 2_validation (242 pairs to check)
    - 4_coordinate_conversion (242 files to convert)
    - 7_file_distribution (242 files to copy)
    - orchestration (all phases)
  
  sync_operations (api direct):
    - 3_class_mapping (simple set operation)
    - 5_split_calculation (quick math)
    - 6_structure_creation (mkdir operations)
    - 8_metadata_generation (single YAML write)

data_flow:
  webui stores nothing permanently:
    - Displays results
    - Polls for updates
    - Downloads final files
  
  api stores:
    - Task status in Redis
    - Task results in Redis (TTL: 24h)
  
  celery stores:
    - Intermediate results in Redis
    - Final files on filesystem
    - Logs in database