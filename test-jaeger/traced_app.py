# traced_app.py

import logging
import time

from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

logging.basicConfig(level=logging.INFO)

# Setup tracer
trace.set_tracer_provider(
    TracerProvider(resource=Resource.create({SERVICE_NAME: "traced-app"}))
)

jaeger_exporter = JaegerExporter(
    agent_host_name="jaeger",
    agent_port=6831,
)

trace.get_tracer_provider().add_span_processor(SimpleSpanProcessor(jaeger_exporter))

tracer = trace.get_tracer("example.traced_app")

print("🎯 tracer initialized:", tracer)

# Example traced function
with tracer.start_as_current_span("example-trace") as span:
    print("🔥 span started")
    span.set_attribute("demo", "value")
    time.sleep(2)  # simulate some work
    print("✅ Traced function completed")

# Force flush to ensure span is sent
trace.get_tracer_provider().force_flush()
