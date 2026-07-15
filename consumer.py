import time
import pika

# 1. RabbitMQ 서버에 연결
# 1. 인증 정보 설정 (사용자명, 비밀번호)
credentials = pika.PlainCredentials('user1', 'user1')

# 2. 연결 매개변수에 credentials 추가
# host: RabbitMQ 서버 주소 (로컬이면 'localhost')
# virtual_host: (선택사항) 특정 vhost를 사용한다면 지정
parameters = pika.ConnectionParameters(
    host='localhost',
    virtual_host='/',
    credentials=credentials
)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

# 2. 큐 선언 (Producer와 동일한 이름)
channel.queue_declare(queue='hello', durable=True)
channel.basic_qos(prefetch_count=1)

# 3. 메시지 처리 콜백 함수 정의
def callback(ch, method, properties, body):
    print(f" [x] Received {body.decode()}")
    
    # 여기서 메시지 처리 로직 수행 (예: DB 저장, 외부 API 호출 등)
    time.sleep(2) 
    print(" [x] Done")
    
    # 4. 수동 ACK 전송
    # delivery_tag를 사용하여 해당 메시지 처리가 끝났음을 서버에 알림
    ch.basic_ack(delivery_tag=method.delivery_tag)

# 4. 큐에서 메시지를 가져오도록 설정
channel.basic_consume(queue='hello',
                      on_message_callback=callback,
                      auto_ack=False)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()