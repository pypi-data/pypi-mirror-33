# pig
This is a simple package named 'pig'. You can see
[猪猪的主页](https://gitee.com/pigbrother_1/pig)
to write your content.

# 安装
```
pip3 install piger
```

# 使用

## 函数从运行开始到结束用了多长时间
```
from piger.timecost import tc
@tc
def func():
    print('func开始')
    a=1
    print('func结束')

func()
```
结果
```
func开始
func结束
函数 func 耗时 0.000126 秒
```


