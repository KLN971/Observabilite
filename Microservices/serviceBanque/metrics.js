'use strict';
require('./traces');
const { DiagConsoleLogger, DiagLogLevel, diag } = require('@opentelemetry/api');
const { OTLPMetricExporter } = require('@opentelemetry/exporter-metrics-otlp-http');
// const { OTLPMetricExporter } = require('@opentelemetry/exporter-metrics-otlp-grpc');
// const { OTLPMetricExporter } = require('@opentelemetry/exporter-metrics-otlp-proto');
// const { ConsoleMetricExporter } = require('@opentelemetry/sdk-metrics');
const {
    ExponentialHistogramAggregation,
    MeterProvider,
    PeriodicExportingMetricReader,
    View,
} = require('@opentelemetry/sdk-metrics');
const { Resource } = require('@opentelemetry/resources');
const {
    SEMRESATTRS_SERVICE_NAME, ATTR_SERVICE_NAME,
} = require('@opentelemetry/semantic-conventions');

// Optional and only needed to see the internal diagnostic logging (during development)
diag.setLogger(new DiagConsoleLogger(), DiagLogLevel.DEBUG);

const metricExporter = new OTLPMetricExporter({url: 'http://otel-collector:4318/v1/metrics'
    // headers: {
    //   foo: 'bar'
    // },
});

// Define view for the exponential histogram metric
const expHistogramView = new View({
    aggregation: new ExponentialHistogramAggregation(),
    // Note, the instrumentName is the same as the name that has been passed for
    // the Meter#createHistogram function for exponentialHistogram.
    instrumentName: 'test_exponential_histogram',
});

// Create an instance of the metric provider
const meterProvider = new MeterProvider({
    resource: new Resource({
        [ATTR_SERVICE_NAME]: 'service_banque_metric_service',
    }),
    views: [expHistogramView],
    readers: [new PeriodicExportingMetricReader({ exporter: metricExporter, exportIntervalMillis: 1000 })],
});

const meter = meterProvider.getMeter('service_banque');

const attributes = { pid: process.pid, environment: 'serviceBanque' };

const counter200Request = meter.createCounter('banque.http_request_valid', {
    description: 'Counter for HTTP 200 responses',
});

counter200Request.add(0, attributes);

const counter400Request = meter.createCounter('banque.http_request_bad',
    {
        description: 'Counter for HTTP 400 responses',
    });

counter400Request.add(0, attributes);

const counter500Request = meter.createCounter('banque.http_request_error', {
    description: 'Counter for HTTP 500 responses',
});

counter500Request.add(0, attributes);

const counter404Request = meter.createCounter('banque.http_request_notfound', {
    description: 'Counter for HTTP 404 responses',
});

counter404Request.add(0, attributes);

const requestDuration = meter.createHistogram('banque.request_duration', {
    description: 'Histogram for the duration of requests',
    unit: 'milliseconds',
    boundaries: [10, 50, 100, 250, 500, 1000, 2500, 5000]  // Custom bucket boundaries in milliseconds
});

requestDuration.record(0, attributes);

const activeConnections = meter.createUpDownCounter('banque.db_active_connections', {
    description: 'Tracks the number of active database connections'
});

activeConnections.add(0, attributes);

const responseSizeHistogram = meter.createHistogram('banque.http_response_size_bytes', {
    description: 'Records the size of outgoing responses in bytes'
});

responseSizeHistogram.record(0, attributes);

const debitAmountHistogram = meter.createHistogram('banque.debit_amount', {
    description: 'Tracks debit transaction amounts',
    boundaries: [10, 50, 100, 200, 500, 1000, 10000, 100000] // Boundaries can be adjusted as needed
});

debitAmountHistogram.record(0, attributes);

module.exports = {
    meter,
    counter200Request,
    counter400Request,
    counter500Request,
    counter404Request,
    requestDuration,
    attributes,
    activeConnections,
    responseSizeHistogram,
    debitAmountHistogram
};
