import os
import csv
import requests
from django.core.management.base import BaseCommand

from core.models import ModelFamily, ModelInfo

MODEL_URL = os.getenv("MODEL_URL")


def handle_mf_bulk(uploaded_file):
    mf_to_create = []

    # Decode uploaded file - it's bytes, not a file path
    decoded = uploaded_file.read().decode("utf-8").splitlines()
    reader = csv.DictReader(decoded)

    for row in reader:
        mf_to_create.append(
            ModelFamily(
                name=row.get("name", ""),
                shortname=row.get("name", ""),
                url=row.get("url", ""),
                description=row.get("description", ""),
                note=row.get("note", ""),
            )
        )

    ModelFamily.objects.bulk_create(mf_to_create, batch_size=100)
    return len(mf_to_create)
