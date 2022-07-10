# 基于flower 0.9版本的二次开发

- 在flower 0.9版本基础上新增supervisor 的进程实时日志展示，以及进程的管理
- 以实现在celery 中的分布式管理节点，并能实时查看每个节点的ansible运行情况
- 基于tornado实现流模式，实时的给前端推送日志信息
- 前端页面采用amis 低代码引擎

## 安装

```
python setup.py install
```


## 卸载

```
pip uninstall flower
```

## 测试

```
cd test/
```

```
celery flower --broker=redis://:myredis@192.168.95.120:6379/2  --address='0.0.0.0'  --port=5555  --basic_auth=admin:Pas1234 --persistent=True --db=logs/flowerdb
```

![image-84c50304e399245981047af3c6922a0](img/84c50304e399245981047af3c6922a0.png)

![image-c999c5c270b0cd8416e3431e2195018](img/c999c5c270b0cd8416e3431e2195018.png)

## 参考资料

- [文档](https://www.rddoc.com/doc/Supervisor/3.3.1/zh/)

- [amis 低代码引擎](https://aisuda.bce.baidu.com/amis/zh-CN/docs/index)
- [Miniconda3-py37_4.8.2-Windows-x86_64.exe](http://mirrors4.hit.edu.cn/anaconda/miniconda/)