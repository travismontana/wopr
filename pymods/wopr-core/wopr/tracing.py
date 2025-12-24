#!/usr/bin/env python3

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor


def create_tracer(tracer_name: str, tracer_enabled: bool, tracer_endpoint: str):
  if not tracer_enabled:
      return None
    # Initialize OpenTelemetry
  trace.set_tracer_provider(TracerProvider())
  tracer = trace.get_tracer(tracer_name)

  # Set up OTLP exporter
  otlp_exporter = OTLPSpanExporter(endpoint=tracer_endpoint)
  span_processor = BatchSpanProcessor(otlp_exporter)
  trace.get_tracer_provider().add_span_processor(span_processor)

  return tracer