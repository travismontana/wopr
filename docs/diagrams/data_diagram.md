erDiagram
  MODEL_FAMILIES ||--o{ MODEL_INFO : has
  MODEL_INFO ||--o{ MODEL_VERSION : has
  MODEL_VERSION ||--o{ MODEL_BACKUP : backed_up_as
  MODEL_VERSION ||--o{ TRAINING_RUN : trained_by
  DATASETS ||--o{ TRAINING_RUN : used_in
  RESULTS ||--o| TRAINING_RUN : produced_by

  MODEL_FAMILIES {
    int id PK
    uuid uuid "unique, not null"
    varchar name "unique, not null"
    varchar shortname "unique, not null"
    text description "null"
    text note "null"
    varchar url "null"
    timestamp created_at "not null"
    timestamp updated_at "not null"
    jsonb mf_status "null"
  }

  MODEL_INFO {
    int id PK
    uuid uuid "unique, not null"
    varchar name "unique, not null"
    varchar shortname "unique, not null"
    text description "null"
    text note "null"
    int family_id FK "not null"
    timestamp created_at "not null"
    timestamp updated_at "not null"
  }

  MODEL_VERSION {
    int id PK
    uuid uuid "unique, not null"
    int version "not null"
    varchar artifact_uri "not null"
    varchar checksum "null"
    text description "null"
    text note "null"
    timestamp trained_at "null"
    boolean is_current "not null, default=false"
    int model_id FK "not null"
    timestamp created_at "not null"
    timestamp updated_at "not null"
  }

  MODEL_BACKUP {
    int id PK
    uuid uuid "unique, not null"
    timestamp taken_at "not null"
    boolean was_successful "not null, default=false"
    varchar artifact_uri "unique, not null"
    int model_version_id FK "not null"
    timestamp created_at "not null"
    timestamp updated_at "not null"
    text note "null"
  }

  TRAINING_RUN {
    int id PK
    uuid uuid "unique, not null"
    text description "null"
    text note "null"
    jsonb training_parameters "null"
    int dataset_id FK "not null"
    int result_id FK "null"
    int model_version_id FK "not null"
    timestamp created_at "not null"
    timestamp updated_at "not null"
    timestamp run_timestamp "null"
  }

  DATASETS {
    int id PK
    uuid uuid "unique, not null"
    varchar artifact_uri "unique, not null"
    text description "null"
    text note "null"
    timestamp created_at "not null"
    timestamp updated_at "not null"
  }

  RESULTS {
    int id PK
    uuid uuid "unique, not null"
    float accuracy "null"
    float loss "null"
    text description "null"
    text note "null"
    varchar artifact_uri "unique, not null"
    timestamp created_at "not null"
    timestamp updated_at "not null"
  }
