from .constants import *
from .logging import Log

from pathlib import Path
from typing import Tuple, Optional
from time import sleep

from selenium.webdriver.common.keys import Keys
from selenium import webdriver


def get_path(file_path: str) -> str:
    # no clue why, but this character gets added for me when running
    return str(Path(file_path)).replace("\u202a", "")


class Upload:
    def __init__(
        self,
        root_profile_directory: str,
        executable_path: str = "geckodriver",
        timeout: int = 3,
        headless: bool = True,
        debug: bool = True,
    ) -> None:
        profile = webdriver.FirefoxProfile(root_profile_directory)
        options = webdriver.FirefoxOptions()
        options.headless = headless

        self.driver = webdriver.Firefox(
            firefox_profile=profile, options=options, executable_path=executable_path
        )
        self.timeout = timeout
        self.log = Log(debug)

        self.log.debug("Firefox is now running")

    def upload(
        self,
        file: str,
        title: str = "",
        description: str = "",
        thumbnail: str = "",
        tags: list = [],
    ) -> Tuple[bool, Optional[str]]:
        """Uploads a video to YouTube.
        Returns if the video was uploaded and the video id.
        """
        if not file:
            raise FileNotFoundError(f'Could not find file with path: "{file}"')

        self.driver.get(YOUTUBE_UPLOAD_URL)
        sleep(self.timeout)

        self.log.debug(f'Trying to upload "{file}" to YouTube...')

        self.driver.find_element_by_xpath(INPUT_FILE_VIDEO).send_keys(get_path(file))
        sleep(self.timeout)

        modal = self.driver.find_element_by_css_selector(UPLOAD_DIALOG_MODAL)
        self.log.debug("Found YouTube upload Dialog Modal")

        if title:
            if len(title) <= 100:
                self.log.debug(f'Trying to set "{title}" as title...')
                title_field = modal.find_element_by_id(TEXTBOX)
                title_field.click()
                sleep(self.timeout)

                # clearing out title which defaults to filename
                for i in range(len(title_field.text) + 10):
                    title_field.send_keys(Keys.BACKSPACE)
                    sleep(0.1)

                sleep(self.timeout)
                title_field.send_keys(title)
                sleep(self.timeout)
            else:
                self.log.debug(
                    "Did not set title. Title cannot be longer than 100 characters"
                )

        if description:
            if len(description) <= 5000:
                self.log.debug(f'Trying to set "{description}" as description...')
                container = modal.find_element_by_xpath(DESCRIPTION_CONTAINER)
                description_field = container.find_element_by_id(TEXTBOX)
                description_field.click()
                sleep(self.timeout)

                description_field.clear()
                sleep(self.timeout)

                description_field.send_keys(description)
                sleep(self.timeout)
            else:
                self.log.debug(
                    "Did not set description. Description cannot be longer than 5000 characters"
                )

        if thumbnail:
            self.log.debug(f'Trying to set "{thumbnail}" as thumbnail...')
            modal.find_element_by_xpath(INPUT_FILE_THUMBNAIL).send_keys(
                get_path(thumbnail)
            )
            sleep(self.timeout)

        self.log.debug('Trying to set video to "Not made for kids"...')
        kids_section = modal.find_element_by_name(NOT_MADE_FOR_KIDS_LABEL)
        kids_section.find_element_by_id(RADIO_LABEL).click()
        sleep(self.timeout)

        if tags:
            modal.find_element_by_xpath(MORE_OPTIONS_CONTAINER).click()
            sleep(self.timeout)

            tags = ",".join(str(tag) for tag in tags)

            if len(tags) <= 500:
                self.log.debug(f'Trying to set "{tags}" as tags...')
                container = modal.find_element_by_xpath(TAGS_CONTAINER)
                tags_field = container.find_element_by_id(TEXT_INPUT)
                tags_field.click()
                sleep(self.timeout)

                tags_field.clear()
                sleep(self.timeout)

                tags_field.send_keys(tags)
                sleep(self.timeout)
            else:
                self.log.debug(
                    "Did not set tags. Tags cannot be longer than 500 characters"
                )

        modal.find_element_by_id(NEXT_BUTTON).click()
        sleep(self.timeout)

        modal.find_element_by_id(NEXT_BUTTON).click()
        sleep(self.timeout)

        # sometimes you have 4 tabs instead of 3
        # this handles both cases
        try:
            modal.find_element_by_id(NEXT_BUTTON).click()
            sleep(self.timeout)
        except:
            pass

        self.log.debug("Trying to set video visibility to public...")
        public_main_button = modal.find_element_by_name(PUBLIC_BUTTON)
        public_main_button.find_element_by_id(RADIO_LABEL).click()
        video_id = self.get_video_id(modal)

        status_container = modal.find_element_by_xpath(STATUS_CONTAINER)

        while True:
            in_process = status_container.text.find(UPLOADED) != -1
            if in_process:
                sleep(self.timeout)
            else:
                break

        done_button = modal.find_element_by_id(DONE_BUTTON)

        if done_button.get_attribute("aria-disabled") == "true":
            error_message = self.driver.find_element_by_xpath(ERROR_CONTAINER).text
            return False, None

        done_button.click()
        sleep(self.timeout)

        return True, video_id

    def get_video_id(self, modal) -> Optional[str]:
        video_id = None
        try:
            video_url_container = modal.find_element_by_xpath(VIDEO_URL_CONTAINER)
            video_url_element = video_url_container.find_element_by_xpath(
                VIDEO_URL_ELEMENT
            )

            video_id = video_url_element.get_attribute(HREF).split("/")[-1]
        except:
            self.log.debug("Exception getting video ID")
            pass

        return video_id

    def close(self):
        self.driver.quit()
        self.log.debug("Closed Firefox")
