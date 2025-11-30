from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter,
)
import os


def initialize_langfuse_otel_exporter():
    """Configures OpenTelemetry to send traces directly to Langfuse."""

    LANGFUSE_HOST = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
    LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")

    if not LANGFUSE_SECRET_KEY:
        raise ValueError(
            "LANGFUSE_SECRET_KEY environment variable is required.")

    # 1. Define the service resource
    resource = Resource.create({"service.name": "my-adk-analyser-agent"})
    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)

    otlp_exporter = OTLPSpanExporter(
        endpoint=f"{LANGFUSE_HOST}/api/public/ingestion/otlp/v1/traces",
        headers={
            "Authorization": f"Bearer {LANGFUSE_SECRET_KEY}"
        }
    )

    span_processor = BatchSpanProcessor(otlp_exporter)
    provider.add_span_processor(span_processor)

    print("OpenTelemetry configured to export traces to Langfuse Cloud.")
    return trace.get_tracer(__name__)


tracer = initialize_langfuse_otel_exporter()
