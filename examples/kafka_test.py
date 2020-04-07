from locust_plugins.debug import run_single_user
from locust_plugins.kafka import KafkaLocust
from locust import task, TaskSet
from locust.wait_time import constant
import time
import random
import os


class MyTaskSet(TaskSet):
    @task
    def t(self):
        self.client.send("lafp_test", message=f"{time.time() * 1000}:" + ("kafka" * 24)[: random.randint(32, 128)])
        self.client.producer.flush(timeout=5)
        time.sleep(1)


class MyLocust(KafkaLocust):
    bootstrap_servers = os.environ["LOCUST_KAFKA_SERVERS"].split(",")
    tasks = {MyTaskSet: 1}
    task_set = MyTaskSet
    wait_time = constant(0)


# how to set up a (global) consumer and read the last message. Look at this as inspiration, it might not work for you.
#
# @events.init.add_listener
# def on_locust_init(environment, **_kwargs):
#     consumer = KafkaConsumer(bootstrap_servers=MyLocust.bootstrap_servers)
#     tp = TopicPartition("my_topic", 0)
#     consumer.assign([tp])
#     last_offset = consumer.position(tp)
#     consumer.seek(tp, last_offset - 1)
#     last_message = next(consumer)
#     last = someProtobufObject()
#     last.ParseFromString(last_message.value)
#     environment.events.request_success.fire(
#         request_type="CONSUME", name="retrans1", response_time=0, response_length=0,
#     )
#     control_consumer(environment)
#     gevent.spawn(wait_for_retrans, environment, consumer)
#
# def wait_for_retrans(environment: Environment, consumer):
#     for message in consumer:
#         with sema:
#             control_message = someProtobufObject().FromString(message.value)
#             environment.events.request_success.fire(
#                 request_type="CONSUME",
#                 name="retrans2",
#                 response_time=0,
#                 response_length=0,
#             )

if __name__ == "__main__":
    # env = Environment()
    # on_locust_init(env)
    # run_single_user(MyLocust, env)
    run_single_user(MyLocust)
