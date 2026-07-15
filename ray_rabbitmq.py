import time
import pika
import ray

# Define Ray Log Actor to handle concurrent logging safely
@ray.remote
class LogActor:
    def __init__(self, log_filepath="ray_rabbitmq.log"):
        self.log_filepath = log_filepath
        self.file = open(self.log_filepath, "a", encoding="utf-8")

    def log(self, message: str):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        formatted = f"[{timestamp}] {message}"
        # Print to console (will show up in driver's output)
        print(formatted)
        # Write to log file
        self.file.write(formatted + "\n")
        self.file.flush()

    def close(self):
        self.file.close()

# Define Ray Consumer Actor
@ray.remote
class RayConsumer:
    def __init__(self, consumer_id: int, logger):
        self.consumer_id = consumer_id
        self.logger = logger

    def start(self):
        credentials = pika.PlainCredentials('user1', 'user1')
        parameters = pika.ConnectionParameters(
            host='localhost',
            virtual_host='/',
            credentials=credentials
        )
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        channel.queue_declare(queue='hello', durable=True)
        channel.basic_qos(prefetch_count=1)

        def callback(ch, method, properties, body):
            self.logger.log.remote(f"[Consumer {self.consumer_id}] Received: {body.decode()}")
            # Simulate processing time
            time.sleep(2)
            self.logger.log.remote(f"[Consumer {self.consumer_id}] Done processing.")
            ch.basic_ack(delivery_tag=method.delivery_tag)

        channel.basic_consume(
            queue='hello',
            on_message_callback=callback,
            auto_ack=False
        )
        self.logger.log.remote(f"[Consumer {self.consumer_id}] Started consuming...")
        try:
            channel.start_consuming()
        except KeyboardInterrupt:
            channel.stop_consuming()
        finally:
            connection.close()

# Define Ray Producer Actor
@ray.remote
class RayProducer:
    def __init__(self, logger):
        self.logger = logger

    def produce(self, messages_count: int):
        credentials = pika.PlainCredentials('user1', 'user1')
        parameters = pika.ConnectionParameters(
            host='localhost',
            virtual_host='/',
            credentials=credentials
        )
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        channel.queue_declare(queue='hello', durable=True)

        self.logger.log.remote(f"[Producer] Starting to publish {messages_count} messages...")
        for i in range(messages_count):
            message = f"Message #{i} from Ray Producer"
            channel.basic_publish(
                exchange='',
                routing_key='hello',
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                )
            )
            self.logger.log.remote(f"[Producer] Sent: {message}")
            time.sleep(0.5)

        connection.close()
        self.logger.log.remote("[Producer] Finished publishing all messages.")

if __name__ == "__main__":
    # Initialize Ray locally
    ray.init()

    # Create the central Logger Actor
    logger = LogActor.remote("ray_rabbitmq.log")
    ray.get(logger.log.remote("System initialized. Starting Actors..."))

    # 1. Start 2 Ray Consumer Actors
    consumers = [RayConsumer.remote(i, logger) for i in range(2)]
    # Call the start method asynchronously on each consumer
    consumer_refs = [c.start.remote() for c in consumers]

    time.sleep(2)  # Give consumers a moment to start

    # 2. Start Ray Producer Actor
    producer = RayProducer.remote(logger)
    producer_ref = producer.produce.remote(10)

    # 3. Wait for Producer to finish sending messages
    ray.get(producer_ref)

    # 4. Wait a bit for Consumers to finish processing remaining messages
    ray.get(logger.log.remote("Waiting for consumers to finish processing..."))
    time.sleep(15)

    ray.get(logger.log.remote("Shutting down Ray..."))
    # Close log file
    ray.get(logger.close.remote())
    ray.shutdown()
