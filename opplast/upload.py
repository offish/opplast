from .constants import *
from .logging import Log
from .exceptions import *

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

    def click(self, element):
        element.click()
        sleep(self.timeout)
        return element

    def send(self, element, text: str) -> None:
        element.clear()
        sleep(self.timeout)
        element.send_keys(text)
        sleep(self.timeout)

    def click_next(self, modal) -> None:
        modal.find_element_by_id(NEXT_BUTTON).click()
        sleep(self.timeout)

    def not_uploaded(self, modal) -> bool:
        return modal.find_element_by_xpath(STATUS_CONTAINER).text.find(UPLOADED) != -1

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

        self.log.debug(f'Trying to set "{title}" as title...')

        # TITLE
        title_field = self.click(modal.find_element_by_id(TEXTBOX))

        # get file name (default) title
        title = title if title else title_field.text

        if len(title) > TITLE_COUNTER:
            raise ExceedsCharactersAllowed(
                f"Title was not set due to exceeding the maximum allowed characters ({len(title)}/{TITLE_COUNTER})"
            )

        # clearing out title which defaults to filename
        for i in range(len(title_field.text) + 10):
            # more backspaces than needed just to be sure
            title_field.send_keys(Keys.BACKSPACE)
            sleep(0.1)

        self.send(title_field, title)

        if description:
            if len(description) > DESCRIPTION_COUNTER:
                raise ExceedsCharactersAllowed(
                    f"Description was not set due to exceeding the maximum allowed characters ({len(description)}/{DESCRIPTION_COUNTER})"
                )

            self.log.debug(f'Trying to set "{description}" as description...')
            container = modal.find_element_by_xpath(DESCRIPTION_CONTAINER)
            description_field = self.click(container.find_element_by_id(TEXTBOX))

            self.send(description_field, description)

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
            self.click(modal.find_element_by_xpath(MORE_OPTIONS_CONTAINER))

            tags = ",".join(str(tag) for tag in tags)

            if len(tags) > TAGS_COUNTER:
                raise ExceedsCharactersAllowed(
                    f"Tags were not set due to exceeding the maximum allowed characters ({len(tags)}/{TAGS_COUNTER})"
                )

            self.log.debug(f'Trying to set "{tags}" as tags...')
            container = modal.find_element_by_xpath(TAGS_CONTAINER)
            tags_field = self.click(container.find_element_by_id(TEXT_INPUT))
            self.send(tags_field, tags)

        # sometimes you have 4 tabs instead of 3
        # this handles both cases
        for _ in range(3):
            try:
                self.click_next(modal)
            except:
                pass

        self.log.debug("Trying to set video visibility to public...")
        public_main_button = modal.find_element_by_name(PUBLIC_BUTTON)
        public_main_button.find_element_by_id(RADIO_LABEL).click()
        video_id = self.get_video_id(modal)

        while self.not_uploaded(modal):
            self.log.debug("Still uploading...")
            sleep(1)

        done_button = modal.find_element_by_id(DONE_BUTTON)

        if done_button.get_attribute("aria-disabled") == "true":
            error_message = self.driver.find_element_by_xpath(ERROR_CONTAINER).text
            return False, None

        self.click(done_button)

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
            raise VideoIDError("Could not get video ID")

        return video_id

    def close(self):
        self.driver.quit()
        self.log.debug("Closed Firefox")
