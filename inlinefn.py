def make_multiplier(x):
    def multiplier(y):
        return x * y  # 외부 함수 변수 x를 기억함
    return multiplier

double = make_multiplier(4)
print(double(1))  # 결과: 10