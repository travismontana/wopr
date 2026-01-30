erDiagram
    model_families ||--o{ model_info : "has"
    model_info ||--o{ model_version : "has"
    model_version ||--o{ model_status : "has"
    model_version ||--o{ model_backup : "has"

    model_families {
        integer id PK
        uuid uuid UK
        varchar name UK
        varchar shortname UK
        text description
        text note
        varchar url
        timestamp created_at
        timestamp updated_at
    }

    model_info {
        integer id PK
        uuid uuid UK
        varchar name UK
        varchar shortname UK
        text description
        text note
        integer family_id FK
        timestamp created_at
        timestamp updated_at
    }

    model_version {
        integer id PK
        uuid uuid UK
        integer version
        varchar artifact_uri UK
        varchar checksum
        text description
        text note
        timestamp trained_at
        boolean is_current
        integer model_id FK
        timestamp created_at
        timestamp updated_at
    }

    model_status {
        integer id PK
        uuid uuid UK
        timestamp observed_at
        boolean has_distfile
        boolean has_backup
        integer model_version_id FK
        timestamp created_at
        timestamp updated_at
    }

    model_backup {
        integer id PK
        uuid uuid UK
        timestamp taken_at
        boolean was_successful
        varchar artifact_uri UK
        integer model_version_id FK
        timestamp created_at
        timestamp updated_at
    }