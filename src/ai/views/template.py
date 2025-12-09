import glob
import logging
import os

import aiofiles
from adrf.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.http import StreamingHttpResponse, Http404


logger = logging.getLogger("ai")


async def get_template_file(filename):
    template_dir = os.path.join(settings.MEDIA_ROOT, 'templates')
    logger.info("Template workbook directory {}".format(template_dir))
    
    template_glob = glob.glob(f"{template_dir}/**", recursive=True)
    for file_path in template_glob:
        yield file_path
    

class TemplateWorkbookView(APIView):
    # permission_classes = (IsAuthenticated,)
    
    async def get(self, request, filename):
        logger.info("Filename to search {}".format(filename))
        file_path = None
        async for file in get_template_file(filename):
            logger.info("Searching in: {}".format(file))
            logger.info("Search result: {result} {value}".format(result=filename in file.split("/")[-1], value=file.split("/")[-1]))
            if filename in file.split("/")[-1]:
                file_path = file
        
        if not file_path or not os.path.exists(file_path):
            raise Http404("File not found")

        async def file_iterator(file_path, chunk_size=8192):
            async with aiofiles.open(file_path, 'rb') as f:
                while chunk := await f.read(chunk_size):
                    yield chunk

        response = StreamingHttpResponse(file_iterator(file_path))
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response