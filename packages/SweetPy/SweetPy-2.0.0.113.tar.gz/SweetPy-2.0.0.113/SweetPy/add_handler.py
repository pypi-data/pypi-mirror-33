print('注册异常跟踪组件...')

from rest_framework import views
import SweetPy.extend.view_plus

views.exception_handler = SweetPy.extend.view_plus.exception_handler