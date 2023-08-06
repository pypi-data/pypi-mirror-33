import requests


resp = requests.post("http://msc5.dev.yiducloud.cn/s3/upload_unsafe", files=[("file1", open("../classes.png", "rb"))])
print(11111111111, resp.headers)
print(resp.text)