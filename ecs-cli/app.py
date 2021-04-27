# From: https://docs.docker.com/compose/gettingstarted/#step-1-setup
# Instrumented for tracing with Datadog: http://pypi.datadoghq.com/trace/docs/
# So far this incorporates the instructions for Flask and Redis.

import time
import redis
import random
from flask import Flask
import blinker as _
from ddtrace import tracer, Pin, patch
from ddtrace.contrib.flask import TraceMiddleware

# Required for instrumenting tracing in Redis
patch(redis=True)

app = Flask(__name__)

# The docs for tracing Redis in ddtrace include using redis.StrictRedis.
# If this breaks, consider using redis.Redis instead.
cache = redis.StrictRedis(host='localhost', port=6379)

traced_app = TraceMiddleware(app, tracer, service="ecs-demo-app", distributed_tracing=False)

# Pin, or "Patch Info," assigns metadata to a connection for tracing.
Pin.override(cache, service='ecs-demo-redis')

def get_hit_count():
    retries = 5
    while True:
        try:
            return cache.incr('hits')
        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)

def random_wait_interval_ms():
    base_intervals_ms = [10, 30, 60, 90]
    base_interval_ms = random.choice(base_intervals_ms)
    ms_to_subtract = random.randrange(1, base_interval_ms/2)
    return base_interval_ms - ms_to_subtract

def arbitrary_service_span():
    return random.choice(
        [
            request_validator,
            request_validator,
            request_publisher
        ]
    )()

def request_validator():
    return tracer.trace(
        "checker.validate", 
        service="ecs-demo-checker", 
        span_type="web", 
        resource="ecs-demo-checker"
    ) 

def request_publisher():
    return tracer.trace(
        "publisher.publish", 
        service="ecs-demo-publisher", 
        span_type="web", 
        resource="ecs-demo-publisher"
    )

@app.route('/')
def hello():
    span = arbitrary_service_span()
    time.sleep(random_wait_interval_ms() * .001)
    span.finish()
    
    count = get_hit_count()
    return 'Hello World! I have been seen {} times.\n'.format(count)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port="4999", debug=False)
