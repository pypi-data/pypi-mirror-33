# socketssh/__init__.py: 这个是socketssh的包.
#
# Copyright (C) 2018 Jiegl <jiegl1@lenovo.com>
#
# 这个文件是socketssh的一部分。
#
# 此软件是"按原样"提供的，没有任何明示或暗示
# 保修。在任何情况下，作者都不承担任何损害赔偿的责任
# 因使用本软件而产生。
#
# 介绍：这个模块主要用于监听客户端的socket连接，server端监听端口，client连接此端口。
# 通过rabbit消息队列往server端传送命令，这个是标准的生产者和消费者之间的关系。
# 当server端从rabbit里面获取命令之后，下发给所有client的socket然后执行命令。
#
__version__ = '1.0.0'

from socketssh import server
from socketssh import client
