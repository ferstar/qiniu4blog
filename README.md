转用腾讯COS了, 配合[PicGo](https://molunerfinn.com/PicGo/)使用, 爽歪歪

## Python 3.x Only

此版本是对文件上传到七牛的key进行了修改，修改后的key格式为：

`文件类型/年/月/原文件的md5值.文件类型`，如

`png/2015/11/cd3c25b07c417cfe2921c16a122a4363.png`

个人觉得这样修改似乎更和谐点, 文件名即`md5`hash值, 可以随时验证自己上传附件的完整性, 毕竟自己偶尔也会任性一把, 在七牛传点略大的东西, 不仅仅是图片~

~另外在之后生成的`image_markdown.txt`文本中，将资源链接以如下`md`的格式写入`![文件名](七牛对应链接)`，如:~

上传成功后自动生成符合MarkDown图片链接格式的内容到剪贴板, 如:
```
![DeepinScrot-5621.png](http://7xivdp.com1.z0.glb.clouddn.com/png/2015/11/cd3c25b07c417cfe2921c16a122a4363.png)
```

可能会遇到`“Pyperclip could not find a copy/paste mechanism for your system. Please see https://pyperclip.readthedocs.org for how to fix this.”`的错误，可以参考下面的链接解决：

<http://pyperclip.readthedocs.org/en/latest/introduction.html>

## 使用方法

```shell
pip install qiniu pyperclip watchdog
# 随便放哪, 有执行权限就行, qiniu.cfg与qiniu4blog.py务必要放在一起
python qiniu4blog.py [dir_to_watch]
```
## 演示
> gif录制软件: [LICEcap](https://www.cockos.com/licecap/)
![演示](test.gif)

## 注意
1. `qiniu.cfg`最后一行自定义`url`别忘了形如`addr = http://7qnct6.com1.z0.glb.clouddn.com/`后面的斜杠`/`
2. 支持七牛云新出的图片样式(原图保护), 假如你的图片样式名称为`/xyz`, 可以在`qiniu.cfg`中添加
3. Windows10 / Ubuntu 16.04测试可用, macOS未测试
---
原版readme链接:<https://github.com/wzyuliyang/qiniu4blog/blob/master/README.md>
