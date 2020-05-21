# 电梯模拟器

## 项目介绍

某一层楼20层，有五部互联的电梯。基于线程思想，编写一个电梯调度程序。功能描述如下：

- [x] 每个电梯里面设置必要功能键：数字键、关门键、开门键、上行键、下行键、报警键、当前电梯的楼层数、上升及下降状态等；
- [x] 每层楼的每部电梯门口，有上行和下行按钮和当前电梯状态的数码显示器；
- [x] 五部电梯门口的按钮是互联结的，即当一个电梯按钮按下去时，其他电梯的相应按钮也就同时点亮，表示也按下去了；
- [x] 每个电梯如果在它的上层或者下层没有相应请求情况下，则应该在原地保持不动；
- [x] 调度算法自行设计。

## 问题分析

整个电梯模拟系统其实可以看作是一个复杂的**有限状态机**，其状态更新有两个来源，其一是由电梯运行引起的系统状态周期性地更新，其二是用户输入导致的系统状态的瞬间变化。这两部分是独立并发的，即用户可以在电梯运行的任意时间发出乘梯请求。

- 第一部分，系统状态周期性更新通过周期性调用更新函数即可实现；

- 第二部分，用户输入导致的状态变化。为此需要解决两个问题，一是用户请求如何分派给各部电梯，二是用户请求如何改变电梯运行状态。因为电梯不能突然改变方向，为了尽量提高电梯运送效率，电梯应该保持一个方向运行，直至此方向没有请求，才能考虑调转方向。这就要求电梯具有”记忆”，能够记住用户的请求，和自己需要停靠的楼层。

用户可以发出的操作可以分为以下四种：

1. 外部请求

对外部请求的定义如下：除了最顶层和最底层外，在每一楼层可以发出两种外部请求：向上/向下。五部电梯的按钮为互联结，按下其中一个按钮，五部电梯中的对应按钮均会亮起。每一次发出外部请求，将根据调度算法找到最合适的电梯，将该请求加入该电梯的运行路径中按下的按钮直到被响应前一直保持按下状态，再次按下将不会再次发送请求。当电梯停靠在请求层后，按钮恢复初始状态。

2. 内部请求

对内部请求的定义如下：每一部电梯的内部请求互相独立用户在电梯内部任意时刻都可以发出请求电梯内部可以显示当前楼层，按下的按钮直到被响应前一直保持按下状态，得到响应后恢复初始状态。

3. 开关门操作

当电梯停靠在某一层后，电梯门会持续打开5秒钟。在这5秒时间内，如果按下开门键，持续时间将会延长至8秒；如果按下关门键，持续时间将会缩短至3秒。在电梯处于空闲状态时，如果按下开门键，电梯将会转变为停靠状态，电梯门会持续打开8秒钟供乘客进出。

4. 电梯维修

考虑到电梯运行过程中可能出现故障，需要停机维修。因此每部电梯内设有维修键，按下后可以暂停当前电梯的使用。

## 设计方案

我们基于`MVC`模式进行整个程序的设计。建立模型层`EModel`类，视图层`EView`类，控制器层`EController`类。

- 模型层是求解问题的核心，负责模拟五部电梯运行，处理接收到的请求（内/外请求，开/关门，故障），更新电梯运行路径，同时给出电梯系统当前的状态；

- 视图层负责展示程序GUI界面。将电梯状态实时绘制在GUI界面上，同时读取用户输入；

- 控制器层负责和模型层、视图层交互，控制整个程序的正常运行。

我们按照面向对象的思想来进行算法设计：

- 对于每部电梯建立电梯类`EElevator`，模拟单部电梯的运行；

- 用户请求的分派由`EModel`类负责，由被分配的电梯处理用户请求并更新自己的运行路径。

### 1. 系统状态定义

#### 电梯状态表示

由问题分析部分，我们将电梯的状态分为运行、空闲、停靠、停止使用四种。每部电梯的状态由`ECB`数据结构表示，`ECB`数据结构的定义如下：

- `eid`，整数，表示当前电梯的编号

- `route`，由一系列用户请求构成的列表，由一系列离散的用户请求作为路径关键点来表示。 列表的第一项指示电梯当前位置。

- `timeout`，整数，表示电梯距离关门剩余时间（秒）

- `disable`，布尔值，表示电梯是否停止使用

#### 电梯按钮表示

在程序GUI界面上的每一个按钮，在电梯模型类中，都有一个`bool`型变量与之对应，表示按钮是否被按下。

### 2. 请求分派算法

我们定义了统一请求格式`Request(Req_Pos, Req_Dir)`来表示内部和外部请求，其中第一项`Req_Pos`表示请求目的地；第二项`Req_Dir`表示请求方向，取值范围为`REQ_UP`, `REQ_DOWN`或`REQ_NOSPEC`，分别表示向上，向下和不指定方向。当用户在任意时刻发出一个外部或内部请求时，请求分派算法负责将用户请求转换成统一格式，并分派给对应的电梯。

#### 外部请求分派

对于外部请求`Request(Req_Pos, Req_Dir)`，我们参考实际生活中电梯调度策略将优先级设定如下：

1. 遍历所有电梯，计算每部电梯响应该请求需要的时间

2. 计算需时最短的电梯

3. 将请求发送给该电梯

#### 内部请求分派

由于内部请求是一定是在某一部电梯内部发出的，无需单独分派，因此对于内部请求”电梯e请求去往楼层i”，请求分派算法将会构造请求`Request(i, REQ_NOSPEC)`发送给电梯对象e。

### 3. 请求响应算法

当用户请求（设为r）被调度算法分配给某一部电梯（设为e）后，电梯e将会处理该请求，同时权衡当前位置、运行方向和运行路径，将请求按如下算法插入运行路径`route`中：

1. 如果`r.Req_Pos`与电梯运行路径中某一个路径点重合，则将r插入到区间两个端点中间之后返回
2. 如果`r.Req_Pos`位于电梯运行路径中某一个区间的中间，而且`r.Req_Dir`与电梯实际运行路径不冲突，则将r插入到区间两个端点中间之后返回
3. 如果`r.Req_Pos`位于电梯运行路径中第一个拐弯处的延长线上，则需判断拐点处的方向，如果拐点处方向与拐点前一致，则将r插入到拐点之后；否则插入到拐点之前，之后返回
4. 否则将r插入到电梯运行路径的末尾。