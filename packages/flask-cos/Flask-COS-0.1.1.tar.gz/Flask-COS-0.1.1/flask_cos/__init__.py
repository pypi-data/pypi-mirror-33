import uuid
from mimetypes import guess_extension
from urllib.parse import urljoin

from qcos.client import COSClient


class COS(object):
    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app):
        secret_id = app.config['COS_SECRET_ID']
        secret_key = app.config['COS_SECRET_KEY']
        region = app.config['COS_REGION']
        appid = app.config['COS_APPID']
        bucket = app.config['COS_BUCKET']
        self.host = app.config['COS_HOST']

        self.client = COSClient(secret_id, secret_key, region, appid, bucket)

    def upload_content(self, content, cos_path, insertOnly=None):
        """
        :params insertOnly: 0:覆盖 1:不覆盖 默认不覆盖
        """
        return self.client.upload_content(content, cos_path,
                                          insertOnly=insertOnly)

    def get_url(self, key):
        return urljoin(self.host, key)


def gen_filename(mimetype=''):
    """使用uuid生成随机文件名
    :params mimetype: 用于生成文件扩展名
    """
    ext = guess_extension(mimetype)
    if ext == '.jpe':
        ext = '.jpg'
    elif ext is None:
        ext = ''

    return uuid.uuid4().hex + ext
