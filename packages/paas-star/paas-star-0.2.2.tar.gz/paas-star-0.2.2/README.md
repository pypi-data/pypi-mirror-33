### Paas-star是基于star-builder的APIStar 异步web服务建工具，使用Paas-star可以轻松构建适合公司内部使用的项目。
除了apistar本身的特性以外，还增加如下几点高级用法：

- CSMR架构，将业务层，视图层，model层完全分离，耦合性降至最低。
- 模板式定制各类模型，轻松扩展模型定义的模板类。
- 自带event hook，轻松实现认证及异常处理。
- 集成日志模块，直接引用，无需关心日志的管理。
- 集成配置模块，集中管理所有配置信息。
- 离线任务管理，同一web服务下的离线任务，轻松复用web模块定义的model, backend, repository等等可注入对象。模板一键创建。
- 集成IPython交互式命令行工具，自动注入model, backend, repository等对象。提供异步代码执行能力，轻松调试各模块(类似rails console)。

## 目录
- [Quick Start](http://wiki.intra.yiducloud.cn/display/~shichao.ma/Quick+Start)
- [paas-star项目组成](http://wiki.intra.yiducloud.cn/pages/viewpage.action?pageId=7316419)
- [model的使用方法](http://wiki.intra.yiducloud.cn/pages/viewpage.action?pageId=7316425)
- [model component 使用方法](http://wiki.intra.yiducloud.cn/pages/viewpage.action?pageId=7316902)
- [service使用方法](http://wiki.intra.yiducloud.cn/pages/viewpage.action?pageId=7316908)
- [repository使用方法](http://wiki.intra.yiducloud.cn/pages/viewpage.action?pageId=7316993)
- [backend使用方法](http://wiki.intra.yiducloud.cn/pages/viewpage.action?pageId=7317115)
- [使用EventHook实现auth认证](http://wiki.intra.yiducloud.cn/pages/viewpage.action?pageId=7317000)
- [错误码处理](http://wiki.intra.yiducloud.cn/pages/viewpage.action?pageId=7317028)
- [配置信息管理](http://wiki.intra.yiducloud.cn/pages/viewpage.action?pageId=7317032)
- [日志管理](http://wiki.intra.yiducloud.cn/pages/viewpage.action?pageId=7317043)
- [自定义模板任务](http://wiki.intra.yiducloud.cn/pages/viewpage.action?pageId=7317074)
- [solo任务](http://wiki.intra.yiducloud.cn/pages/viewpage.action?pageId=7320156)
- [使用集成的IPython进行异步代码的调试](http://wiki.intra.yiducloud.cn/pages/viewpage.action?pageId=7320340)