from .constants import *
from .logging import Log

from pathlib import Path
from time import sleep

from selenium import webdriver


class Upload:
    def __init__(
        self,
        root_profile_directory: str,
        timeout: int = 3,
        headless: bool = True,
        debug: bool = True,
    ) -> None:
        profile = webdriver.FirefoxProfile(root_profile_directory.replace("\\", "/"))
        options = webdriver.FirefoxOptions()
        options.headless = headless

        self.driver = webdriver.Firefox(firefox_profile=profile, options=options)
        self.timeout = timeout
        self.log = Log(debug)

        self.log.debug("Firefox is now running")

    def upload(self, meta: dict) -> (bool, str):
        """Uploads a video to YouTube.

        meta: {
            "file": "path/to/video.mp4",
            "title": "my title",
            "description": "my description",
            "thumbnail": "path/to/thumbnail.jpg",
            "tags": ["these", "are", "my", "tags"]
        }

        Returns if the video was uploaded and the video id.
        """
        video = meta.get("file")
        title = meta.get("title")
        description = meta.get("description")
        thumbnail = meta.get("thumbnail")
        tags = meta.get("tags")

        if not video:
            raise FileNotFoundError('Could not find "file" in meta')

        self.driver.get(YOUTUBE_UPLOAD_URL)
        sleep(self.timeout)

        self.log.debug(f'Trying to upload "{video}" to YouTube...')
        path = str(Path.cwd() / video)
        self.driver.find_element_by_xpath(INPUT_FILE_VIDEO).send_keys(path)
        sleep(self.timeout)

        if title:
            if len(title) <= 100:
                self.log.debug(f'Trying to set "{title}" as title...')
                title_field = self.driver.find_element_by_id(TEXTBOX)
                title_field.click()
                sleep(self.timeout)

                title_field.clear()
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
                container = self.driver.find_element_by_xpath(DESCRIPTION_CONTAINER)
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
            path_thumbnail = str(Path.cwd() / thumbnail)
            self.log.debug(f'Trying to set "{path_thumbnail}" as thumbnail...')
            self.driver.find_element_by_xpath(INPUT_FILE_THUMBNAIL).send_keys(
                path_thumbnail
            )
            sleep(self.timeout)

        self.log.debug('Trying to set video to "Not made for kids"...')
        kids_section = self.driver.find_element_by_name(NOT_MADE_FOR_KIDS_LABEL)
        kids_section.find_element_by_id(RADIO_LABEL).click()
        sleep(self.timeout)

        if tags:
            self.driver.find_element_by_xpath(MORE_OPTIONS_CONTAINER).click()
            sleep(self.timeout)

            tags = ",".join(str(tag) for tag in tags)

            if len(tags) <= 500:
                self.log.debug(f'Trying to set "{tags}" as tags...')
                container = self.driver.find_element_by_xpath(TAGS_CONTAINER)
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

        self.driver.find_element_by_id(NEXT_BUTTON).click()
        sleep(self.timeout)

        self.driver.find_element_by_id(NEXT_BUTTON).click()
        sleep(self.timeout)

        self.driver.find_element_by_id(NEXT_BUTTON).click()
        sleep(self.timeout)

        self.log.debug("Trying to set video visibility to public...")
        public_main_button = self.driver.find_element_by_name(PUBLIC_BUTTON)
        public_main_button.find_element_by_id(RADIO_LABEL).click()
        video_id = self.get_video_id()

        status_container = self.driver.find_element_by_xpath(STATUS_CONTAINER)

        while True:
            in_process = status_container.text.find(UPLOADED) != -1
            if in_process:
                sleep(self.timeout)
            else:
                break

        done_button = self.driver.find_element_by_id(DONE_BUTTON)

        if done_button.get_attribute("aria-disabled") == "true":
            error_message = self.driver.find_element_by_xpath(ERROR_CONTAINER).text
            return False, None

        done_button.click()
        sleep(self.timeout)

        return True, video_id

    def get_video_id(self) -> str:
        video_id = None
        try:
            video_url_container = self.driver.find_element_by_xpath(VIDEO_URL_CONTAINER)
            video_url_element = video_url_container.find_element_by_xpath(
                VIDEO_URL_ELEMENT
            )

            video_id = video_url_element.get_attribute(HREF).split("/")[-1]
        except:
            pass
        return video_id

    def close(self):
        self.driver.quit()
        self.log.debug("Closed Firefox")
