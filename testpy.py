import ray
import time

ray.init()

try:
    # 모니터링 로직
    while True:
        # Actor 상태 확인 및 로깅 등
        print("모니터링 중...")
        time.sleep(10)
except KeyboardInterrupt:
    print("프로그램 종료 중...")
finally:
    # 프로그램이 종료될 때 자원을 정리
    ray.shutdown()