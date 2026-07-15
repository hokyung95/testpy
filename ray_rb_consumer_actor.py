import ray
import pika
import time

# 1. 실제 작업을 수행할 Ray Task 정의
@ray.remote
def process_message_task(body):
    print(f" [x] Task started for: {body.decode()}")
    # 여기에 실제 무거운 작업 로직 작성
    time.sleep(2)
    print(f" [x] Task finished: {body.decode()}")
    return True

# 2. RabbitMQ를 감시할 Ray Actor 정의
@ray.remote
class RabbitMQConsumer:
    def __init__(self, queue_name):
        self.queue_name = queue_name
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue_name, durable=True)

    def run(self):
        print(f" [*] Waiting for messages in {self.queue_name}. To exit press CTRL+C")

        def callback(ch, method, properties, body):
            # 메시지 수신 시 Ray Task를 비동기 호출 (non-blocking)
            process_message_task.remote(body)
            # 메시지 처리가 큐에서 수락되었음을 알림
            ch.basic_ack(delivery_tag=method.delivery_tag)

        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue=self.queue_name, on_message_callback=callback)
        self.channel.start_consuming()

# 3. 실행부
if __name__ == "__main__":
    #ray.init()
    ray.init(address='auto')

    # Consumer Actor 시작
    consumer = RabbitMQConsumer.remote("task_queue")
    consumer.run.remote()

    # Consumer Actor 시작
    consumer2 = RabbitMQConsumer.remote("task_queue")
    consumer2.run.remote()


    # 메인 프로세스가 종료되지 않도록 유지
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        ray.shutdown()