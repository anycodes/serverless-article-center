# -*- coding:utf-8 -*-
import os
import datetime
import oss2
import hashlib
from django.views import generic
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .configs import MDConfig

bucketName = os.environ.get('oss_BUCKET', '')
endpoint = os.environ.get('oss_ENDPOINT', '')
auth = oss2.Auth(os.environ.get('aliyun_KeyId', ''), os.environ.get('aliyun_KeySecret', ''))
bucket = oss2.Bucket(auth, endpoint, bucketName)
getMd5 = lambda content: hashlib.md5(content.encode("utf-8")).hexdigest()
# TODO 此处获取default配置，当用户设置了其他配置时，此处无效，需要进一步完善
MDEDITOR_CONFIGS = MDConfig('default')


class UploadView(generic.View):
    """ upload image file """

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(UploadView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        upload_image = request.FILES.get("editormd-image-file", None)
        # media_root = settings.MEDIA_ROOT

        # image none check
        if not upload_image:
            return JsonResponse({
                'success': 0,
                'message': "未获取到要上传的图片",
                'url': ""
            })

        # image format check
        file_name_list = upload_image.name.split('.')
        file_extension = file_name_list.pop(-1)
        file_name = '.'.join(file_name_list)
        if file_extension not in MDEDITOR_CONFIGS['upload_image_formats']:
            return JsonResponse({
                'success': 0,
                'message': "上传图片格式错误，允许上传图片格式为：%s" % ','.join(
                    MDEDITOR_CONFIGS['upload_image_formats']),
                'url': ""
            })

        # image floder check
        # file_path = os.path.join(media_root, MDEDITOR_CONFIGS['image_folder'])
        # if not os.path.exists(file_path):
        #     try:
        #         os.makedirs(file_path)
        #     except Exception as err:
        #         return JsonResponse({
        #             'success': 0,
        #             'message': "上传失败：%s" % str(err),
        #             'url': ""
        #         })

        # save image
        file_full_name = '%s_%s.%s' % (file_name,
                                       '{0:%Y%m%d%H%M%S%f}'.format(datetime.datetime.now()),
                                       file_extension)
        # with open(os.path.join(file_path, file_full_name), 'wb+') as file:
        #     for chunk in upload_image.chunks():
        #         file.write(chunk)
        bucket.put_object(file_full_name, upload_image.chunks())
        return JsonResponse({'success': 1,
                             'message': "上传成功！",
                             'url': 'https://%s.%s/%s'%(bucketName, endpoint, file_full_name)})
