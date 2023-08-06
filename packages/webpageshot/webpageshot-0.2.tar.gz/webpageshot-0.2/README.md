# webpageshot [![Version][version-badge]][version-link] ![MIT License][license-badge]


Take screenshot of webpage


`webpageshot` 是一个抓取整个网页截屏的工具


### 示例

抓取[Google](https://www.google.com/)主页

```
$ webpageshot --url https://www.google.com/
```

结果如下

![](https://raw.githubusercontent.com/pythonml/webpageshot/master/webpageshot/google.png)


### 使用方式

```
usage: webpageshot [-h] [--url URL] [--outfile OUTFILE]

optional arguments:
  -h, --help         show this help message and exit
  --url URL          page url
  --outfile OUTFILE  output image location
```


### 安装

```
$ pip install webpageshot
```


### License

[MIT](https://github.com/pythonml/webpageshot/blob/master/LICENSE)


[version-badge]:   https://img.shields.io/badge/version-0.1-brightgreen.svg
[version-link]:    https://pypi.python.org/pypi/webpageshot/
[license-badge]:   https://img.shields.io/github/license/pythonml/webpageshot.svg
