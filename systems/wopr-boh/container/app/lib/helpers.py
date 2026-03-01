import logging
import sys

wopr_json = {
  "api": {
    "host": "0.0.0.0",
    "port": 8000,
    "ollama_timeout_seconds": 60,
    "ollama_url": "http://groth.abode.tailandtraillabs.org:11434",
    "internalUrl": "http://wopr-api.wopr.svc:8000",
    "externalUrl": "https://api.wopr.tailandtraillabs.org",
    "models_url": "http://groth.abode.tailandtraillabs.org:9000",
    "yolo_models": "http://groth.abode.tailandtraillabs.org:8001",
    "images_url": "https://images.wopr.tailandtraillabs.org",
    "thumbs_url": "https://imgproxy.wopr.tailandtraillabs.org",
    "labels_url": "https://labelstudio.wopr.tailandtraillabs.org",
    "version": "v2"
  },
  "baseDomain": "wopr.tailandtraillabs.org",
  "camera": {
    "buffer_count": 2,
    "capture_delay_seconds": 2,
    "default_format": "RGB888",
    "default_resolution": "4k",
    "camDict": {
      "0": {
        "id": 0,
        "name": "imx 477",
        "description": "IMX 477 with M12 lens",
        "host": "wopr-cam",
        "port": "5102",
        "type": "imx477",
        "width": 4056,
        "height": 3040,
        "mode": "RGB888",
        "flipImg": True
      },
      "1": {
        "id": 1,
        "name": "c960",
        "description": "Eemeet c960 almost 4k webcam",
        "host": "172.16.2.20",
        "port": "5100",
        "type": "usb",
        "width": 3840,
        "height": 2160,
        "mode": "RGB888"
      },
      "2": {
        "id": 2,
        "name": "c950",
        "description": "Eemeet c950 1080p webcam",
        "host": "172.16.2.20",
        "port": "5101",
        "type": "usb"
      }
    }
  },
  "database": {
    "connection_pool_size": 5,
    "connection_timeout_seconds": 30,
    "max_overflow": 10
  },
  "filenames": {
    "mlcapture": {
      "fullImageFilename": "{{pieces_id}}-{{game_catalog_id}}-{{capture_id}}.jpg",
      "thumbnailFilename": "{{pieces_id}}-{{game_catalog_id}}-{{capture_id}}-thumb.jpg"
    }
  },
  "logging": {
    "date_format": "%Y-%m-%d %H:%M:%S",
    "default_level": "INFO",
    "enabled": True,
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
  },
  "lightSettings": {
    "temp": {
      "warm": 3000,
      "neutral": 4000,
      "cool": 5000
    },
    "intensity": [ 10, 20, 30, 40, 50, 60, 70, 80, 90, 100 ]
  },
  "homeAssistant": {
    "enabled": True,
    "host": "http://moya.hangar.bpfx.org:8123"
  },
  "nelson": "haha",
  "object": {
    "rotations": [ 0, 45, 90, 135, 180, 225, 270, 315 ],
    "positions": {
      "Center": "center",
      "Near Center": "nearCenter",
      "Random": "random",
      "Top Edge": "topEdge",
      "Bottom Edge": "bottomEdge",
      "Left Edge": "leftEdge",
      "Right Edge": "rightEdge",
      "Top Right": "topRight",
      "Top Left": "topLeft",
      "Bottom Right": "bottomRight",
      "Bottom Left": "bottomLeft"
    }
  },

  "storage": {
    "base_path": "/remote/wopr",
    "images_subdir": "images",
    "incoming_subdir": "incoming",
    "archive_subdir": "archive",
    "backups_subdir": "backup",
    "label_subdir": "labelstudio",
    "label_source_subdir": "source",
    "label_target_subdir": "target",
    "models_subdir": "models/ua",
    "weights_subdir": "weights",
    "runs_subdir": "runs",
    "distfiles_subdir": "distfiles",
    "default_extension": "jpg",
    "ensure_directories": True,
    "sessions_subdir": "sessions",
    "image_extensions": [
      "jpg",
      "png"
    ],
    "thumbnail_size": [
      480,
      480
    ]
  },
  "analysis_statuses": [
    "pending",
    "processing",
    "completed",
    "failed"
  ],
  "tracing": {
    "enabled": True,
    "hostInternal": "http://wopr-monitoring-tempo",
    "portInternal": 4318,
    "hostExternal": "https://tempo.monitoring.abode.tailandtraillabs.org",
    "portExternal": 443,
    "service_name": "wopr-unknown",
    "sampling_rate": 1.0
  },
  "notifications": {
    "email": {
      "enabled": False,
      "smtp_server": "smtp.example.com",
      "smtp_port": 587,
      "use_tls": True,
      "username": "",
      "password": ""
    },
    "discord": {
      "enabled": True,
      "webhook_url": "https://discord.com/api/webhooks/1457873231133544459/3yUwg89RsfjgRu-AmZB_hr0LU586d3OMZ2HniDdoW8YpgNhOO4rcBwCSKaSLJPYq01yE"
    }
  },
  "vision": {
    "default_model": "qwen2-vl:7b",
    "gaussian_blur_kernel": [
      21,
      21
    ],
    "label_studio_url": "https://labelstudio.wopr.tailandtraillabs.org",

    "min_change_area_pixels": 1000,
    "morphology_iterations": {
      "dilate": 2,
      "erode": 1
    },
    "morphology_kernel": [
      5,
      5
    ],
    "opencv_change_threshold": 30
  },
  "project": {
    "project_status": {
      "idea": "Not started yet",
      "staged": "Ready for development",
      "pretraining": "Learning the game",
      "training": "In progress",
      "trained": "Completed"
    },
    "project_state": {
      "open": "Currently active",
      "archived": "No longer active"
    }
  }
}


def setup_logger(logger_name="wopr") -> logging.Logger:
    """
    Configure logging for helper functions.

    Returns:
        Configured logger instance

    Note:
        Only configures once - subsequent calls return existing logger
    """
    file_path = "/tmp/wopr.log"
    logger = logging.getLogger(logger_name)
    if logger.handlers:
        return logger  # Already configured

    logger.setLevel(logging.DEBUG)
    logging.FileHandler(file_path)
    handler = logging.StreamHandler(sys.stdout)
    fmt = logging.Formatter(
        fmt="%(asctime)s %(levelname)s %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(fmt)
    logger.addHandler(handler)

    return logger
