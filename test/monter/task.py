import time
# 这个Celery就类似于flask中的Flask, 然后实例化得到一个app
from celery import Celery

# 指定一个name、以及broker的地址、backend的地址
app = Celery("satori",
             # 这里使用我阿里云上的Redis, broker用1号库, backend用2号库
             broker="redis://:myredis@192.168.60.120:6379/2",
             backend="redis://:myredis@192.168.60.120:6379/1")

# 这里通过@app.task对函数进行装饰，那么之后我们便可通过调用task.delay创建一个任务
@app.task
def task(name, age):
    print("准备执行任务啦")
    time.sleep(3)
    return f"name is {name}, age is {age}"
#celery worker -A task -l info -P eventlet