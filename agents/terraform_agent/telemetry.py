# telemetry.py

import os

from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

_service_name = os.getenv("OTEL_SERVICE_NAME", "multi-agent-framework")
_jaeger_host = os.getenv("JAEGER_HOST", "localhost")
_jaeger_port = int(os.getenv("JAEGER_PORT", 6831))

print(
    f"[Telemetry] Initialized tracer with Jaeger exporter targeting {_service_name} {_jaeger_host}:{_jaeger_port}"
)

trace.set_tracer_provider(
    TracerProvider(resource=Resource.create({SERVICE_NAME: _service_name}))
)

jaeger_exporter = JaegerExporter(
    agent_host_name=_jaeger_host,
    agent_port=_jaeger_port,
)

trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(jaeger_exporter))

tracer = trace.get_tracer("orchestrator")
