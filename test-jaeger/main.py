import time

from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Setup tracer
trace.set_tracer_provider(
    TracerProvider(resource=Resource.create({SERVICE_NAME: "pure-python-service"}))
)
tracer = trace.get_tracer(__name__)

# Setup Jaeger exporter
jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",  # Must match Docker Compose service name
    agent_port=6831,
)

# Add span processor
span_processor = BatchSpanProcessor(jaeger_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Create some spans
with tracer.start_as_current_span("parent-span"):
    time.sleep(0.3)
    with tracer.start_as_current_span("child-span"):
        time.sleep(0.2)

print("✅ Traces sent to Jaeger!")
