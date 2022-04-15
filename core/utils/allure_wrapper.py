from functools import wraps
from os import getenv
from os.path import join
from uuid import uuid4

from allure_commons._allure import StepContext, attach
from allure_commons.types import AttachmentType
from allure_commons.utils import func_parameters, represent

from core.utils.helpers import get_current_folder


def step(title):
    if callable(title):
        return CustomStepContext(title.__name__, {})(title)
    else:
        return CustomStepContext(title, {})


class CustomStepContext(StepContext):
    def __enter__(self):
        super().__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        super().__exit__(exc_type, exc_val, exc_tb)

    def __call__(self, func):
        @wraps(func)
        def impl(*args, **kwargs):
            f_args = list(map(lambda x: represent(x), args))
            f_params = func_parameters(func, *args, **kwargs)
            with StepContext(self.title.format(*f_args, **f_params), f_params):
                try:
                    return func(*args, **kwargs)
                finally:
                    try:
                        attach.file(source=args[0].browser.save_screenshot(), attachment_type=AttachmentType.PNG)
                    except BaseException:
                        image_path = join(get_current_folder(getenv('ALLURE_DIR')), f'{uuid4()}.png')
                        args[0].driver.get_screenshot_as_file(filename=image_path)
                        attach.file(
                            source=image_path,
                            attachment_type=AttachmentType.PNG
                        )

        return impl
