const { Resource } = require("@opentelemetry/resources");
const { SimpleSpanProcessor } = require("@opentelemetry/sdk-trace-base");
const { NodeTracerProvider } = require("@opentelemetry/sdk-trace-node");
const { trace } = require("@opentelemetry/api");
const { JaegerExporter} = require("@opentelemetry/exporter-jaeger");
const { HttpInstrumentation } = require("@opentelemetry/instrumentation-http");
const { registerInstrumentations } = require("@opentelemetry/instrumentation");
const { ExpressInstrumentation } = require("opentelemetry-instrumentation-express");


module.exports = () => {
    const exporter = new JaegerExporter({
        endpoint: "http://jaeger:14268/api/traces"
    })

    const provider = new NodeTracerProvider({
        resource: new Resource({
            'service.name': 'serviceclient',
        }),
    });

    provider.addSpanProcessor(new SimpleSpanProcessor(exporter));
    provider.register();

    registerInstrumentations({
        instrumentations: [
            new HttpInstrumentation(),
            new ExpressInstrumentation(),
        ],
    });

    return trace.getTracer('serviceclient');
};
