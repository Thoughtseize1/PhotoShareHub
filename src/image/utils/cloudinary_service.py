import re
import uuid
from datetime import datetime

import cloudinary.uploader

from src.config import settings
from src.database.sql.models import User
from src.image.schemas import EditFormData


class UploadImage:
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True,
    )

    @staticmethod
    def generate_name_folder(user: User, edited: bool = False):
        current_date = datetime.now()
        formatted_date = current_date.strftime("%d-%m-%Y")
        if not edited:
            return f"Memento/{user.username}/{formatted_date}/{str(uuid.uuid4())}"
        return (
            f"Memento/{user.username}/transformed/{formatted_date}/{str(uuid.uuid4())}"
        )

    @staticmethod
    def upload(file, public_id: str):
        r = cloudinary.uploader.upload(file, public_id=public_id, overwrite=True)
        return r

    @staticmethod
    def get_pic_url(public_id, r):
        src_url = cloudinary.CloudinaryImage(public_id).build_url(
            # version=r.get("version")
        )
        return src_url


class ImageEditor(UploadImage):
    async def edit_image(
        self,
        original_img_url: str,
        edit_data: EditFormData,
    ):
        match = re.search(r"Memento/(.*)/(\d{2}-\d{2}-\d{4})/(.*)", original_img_url)
        if not match:
            raise ValueError("Invalid URL format")

        public_id = match.group()
        print(public_id)

        if edit_data:
            image_edit_html = await self._edit_image_cloudinary(public_id, edit_data)
            pattern2 = re.search(r'src="([^"]+)"', image_edit_html)
            image_edit = pattern2.group(1)
            print(pattern2.group(1))
            return image_edit

        raise ValueError("No transformation specified")

    async def _edit_image_cloudinary(self, public_id, edit_data: EditFormData):
        transformation = []
        if (
            edit_data.ai_replace
            and edit_data.ai_replace.Object_to_detect
            and edit_data.ai_replace.Replace_with
        ):
            transformation.append(
                {
                    "effect": f"gen_replace:from_{edit_data.ai_replace.Object_to_detect};to_{edit_data.ai_replace.Replace_with}"
                }
            )
        if edit_data.scale and edit_data.scale.Width != 0:
            transformation.append(
                {
                    "width": edit_data.scale.Width,
                    "height": edit_data.scale.Height,
                    "crop": "scale",
                }
            )
        if edit_data.black_and_white and edit_data.black_and_white.black_and_white:
            transformation.append({"effect": "simulate_colorblind:cone_monochromacy"})
        if edit_data.rotation:
            transformation.append({"angle": edit_data.rotation.angle})
        return cloudinary.CloudinaryImage(public_id).image(
            transformation=transformation
        )
