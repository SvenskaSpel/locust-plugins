from locust_plugins.users import KafkaUser
from locust import task, run_single_user
import os


class MyUser(KafkaUser):
    bootstrap_servers = os.environ["LOCUST_KAFKA_SERVERS"]

    @task
    def t(self):
        self.client.send("lafp_test", b"payload")
        # if you dont poll immediately after sending message your timings will be incorrect
        # (but if throughput is most important then you may want to delay it)
        self.client.producer.poll(1)


# How to set up a (global) consumer and read the last message. Consider this as inspiration, it might not work for you.
# And it is probably out of date. Probably best to ignore this.
#
# @events.init.add_listener
# def on_locust_init(environment, **kwargs):
#     consumer = KafkaConsumer(MyUser.bootstrap_servers)
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
    run_single_user(MyUser)
