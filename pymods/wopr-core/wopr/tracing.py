#!/usr/bin/env python3

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor


def create_tracer(tracer_name: str, tracer_enabled: bool, tracer_endpoint: str):
  if not tracer_enabled:
      return None
    # Initialize OpenTelemetry
  resource = Resource(attributes={
      "service.name": tracer_name,
      "service.version": tracer_version
  })
  trace.set_tracer_provider(TracerProvider(resource=resource))
  tracer = trace.get_tracer(tracer_name)

  span_processor = BatchSpanProcessor(otlp_exporter)
  trace.get_tracer_provider().add_span_processor(span_processor)

  return tracer

  tracing_enabled = woprconfig.get_bool(
    "tracing.enabled", False,
    service_name=woprvar.APP_NAME,
    description=woprvar.APP_DESCRIPTION,
    version=woprvar.APP_VERSION)