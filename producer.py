import pika


# 1. RabbitMQ 서버에 연결 (로컬 서버 기준)
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

# 2. 메시지를 보낼 큐 선언 (큐가 없으면 생성됨)
channel.queue_declare(queue='hello', durable=True)



# 3. 메시지 전송
for i in range(4, 15):
    print(i, end=" ")
    message = f"hello rabbitmq!!!---{i}"
    channel.basic_publish(exchange='',
                      routing_key='hello',
                      body=message)

print(" [x] Sent 'Hello RabbitMQ!'")

# 4. 연결 종료
connection.close()