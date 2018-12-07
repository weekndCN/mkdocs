# 人民币数字转大写汉字
## Before Your Start
---

!!! Warning ""
        财务对账时，经常需要把 **数字类型** 的人民币 转换为 **汉字类型** 的人民币，这里通过不同的组合方式实现大部分的需求，如果为满足，则可以对应的修改代码。


## transnum.py
---

```python

import warnings
from decimal import Decimal


def cncurrency(value, capital=True, prefix=False, classical=None):
    if not isinstance(value, (Decimal, str, int)):
        msg = '''
        由于浮点数精度问题，请考虑使用字符串，或者 decimal.Decimal 类。
        '''
        warnings.warn(msg, UserWarning)
    # 默认圆
    if classical is None:
        classical = True if capital else False

    # 汉字金额前缀
    if prefix is True:
        prefix = '人民币'
    else:
        prefix = ''

    # 汉字金额字符定义
    dunit = ('角', '分')
    if capital:
        num = ('零', '壹', '贰', '叁', '肆', '伍', '陆', '柒', '捌', '玖')
        iunit = [None, '拾', '佰', '仟', '万', '拾', '佰', '仟', '亿', '拾', '佰', '仟', '万', '拾', '佰', '仟']
    else:
        num = ('〇', '一', '二', '三', '四', '五', '六', '七', '八', '九')
        iunit = [None, '十', '百', '千', '万', '十', '百', '千', '亿', '十', '百', '千', '万', '十', '百', '千']
    if classical:
        iunit[0] = '元' if classical else '圆'

    if not isinstance(value, Decimal):
        value = Decimal(value).quantize(Decimal('0.01'))

    if value < 0:
        prefix += '负'
        value = - value
    s = str(value)
    if len(s) > 19:
        raise ValueError('Beyond definition range')
    # 小数部分和整数部分分别处理
    istr, dstr = s.split('.')
    # 翻转整数部分字符串
    istr = istr[::-1]
    # 定于存放结果的数组
    so = []

    # 零
    if value == 0:
        return prefix + num[0] + iunit[0]
    haszero = False  # 用于标记零的使用
    if dstr == '00':
        haszero = True  # 如果无小数部分，则标记加过零，避免出现“圆零整”

    # 处理小数部分
    # 分
    if dstr[1] != '0':
        so.append(dunit[1])
        so.append(num[int(dstr[1])])
    else:
        so.append('整')  # 无分，则加“整”
    # 角
    if dstr[0] != '0':
        so.append(dunit[0])
        so.append(num[int(dstr[0])])
    elif dstr[1] != '0':
        so.append(num[0])  # 无角有分，添加“零”
        haszero = True  # 标记加过零了

    # 无整数部分
    if istr == '0':
        if haszero:  # 既然无整数部分，那么去掉角位置上的零
            so.pop()
        so.append(prefix)  # 加前缀
        so.reverse()  # 翻转
        return ''.join(so)

    # 处理整数部分
    for i, n in enumerate(istr):
        n = int(n)
        if i % 4 == 0:  # 在圆、万、亿等位上，即使是零，也必须有单位
            if i == 8 and so[-1] == iunit[4]:  # 亿和万之间全部为零的情况
                so.pop()  # 去掉万
            so.append(iunit[i])
            if n == 0:  # 处理这些位上为零的情况
                if not haszero:  # 如果以前没有加过零
                    so.insert(-1, num[0])  # 则在单位后面加零
                    haszero = True  # 标记加过零了
            else:  # 处理不为零的情况
                so.append(num[n])
                haszero = False  # 重新开始标记加零的情况
        else:  # 在其他位置上
            if n != 0:  # 不为零的情况
                so.append(iunit[i])
                so.append(num[n])
                haszero = False  # 重新开始标记加零的情况
            else:  # 处理为零的情况
                if not haszero:  # 如果以前没有加过零
                    so.append(num[0])
                    haszero = True

    # 最终结果
    so.append(prefix)
    so.reverse()
    return ''.join(so)


i = input('请输入金额：')
print(cncurrency(i))
```

!!! Info ""
        **参数** :
        **capital** :
        - True   繁体汉字金额
        - False  简体汉字金额
        **classical** :
        - True   元
        - False  圆
        **prefix** :
        - True   以'人民币'开头
        - False  无开头


## Test Result
---

#### 1. default

```
print(cncurrency('1234.56'))
壹仟贰佰叁拾肆元伍角陆分
```

#### 2. addon Prefix(人民币)

```
print(cncurrency('1234.56',capital=True, prefix=True, classical=None))
人民币壹仟贰佰叁拾肆元伍角陆分
```

#### 3. addon classical(元)

```
print(cncurrency('1234.56',capital=True, prefix=False, classical=True))
壹仟贰佰叁拾肆元伍角陆分
```

#### 4. addon capital(简体汉字金额)

```
print(cncurrency('1234.56',capital=False, prefix=False, classical=True))
一千二百三十四元五角六分
```
