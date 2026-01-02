#!/usr/bin/env python3
# tracing.py
"""
WOPR - Wargaming Oversight & Position Recognition
# Copyright (c) 2023-present Bob <bob@bomar.us>
# See git log for detailed authorship

Brief description of what this file does.
"""

from opentelemetry import trace
from opentelemetry.sdk.resources import (
    Resource, 
    SERVICE_NAME, 
    SERVICE_VERSION, 
    SERVICE_NAMESPACE,
    DEPLOYMENT_ENVIRONMENT
)
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
import os

def create_tracer(
    tracer_name: str, 
    tracer_version: str, 
    tracer_enabled: bool, 
    tracer_endpoint: str,
    service_namespace: str = "wopr",  # Add this parameter
    deployment_env: str = "production"  # Add this parameter
):
    if not tracer_enabled:
        return None
    
    # Initialize OpenTelemetry with full resource attributes
    resource = Resource(attributes={
        SERVICE_NAME: tracer_name,
        SERVICE_VERSION: tracer_version,
        SERVICE_NAMESPACE: service_namespace,  # This is what Grafana filters on
        DEPLOYMENT_ENVIRONMENT: deployment_env,
        "service.instance.id": f"{tracer_name}-{os.getpid()}",  # Useful for multi-instance tracking
    })
    
    trace.set_tracer_provider(TracerProvider(resource=resource))
    tracer = trace.get_tracer(tracer_name)
    
    otlp_exporter = OTLPSpanExporter(endpoint=tracer_endpoint)
    span_processor = BatchSpanProcessor(otlp_exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)

    return tracer