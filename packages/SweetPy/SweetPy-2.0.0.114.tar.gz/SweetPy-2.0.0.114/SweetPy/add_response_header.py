print('注册标准响应头组件...')

from rest_framework import response
import SweetPy.extend.response_plus

response.Response = SweetPy.extend.response_plus.Response