from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By

from pathlib import Path
from typing import Tuple, Optional, Union
from time import sleep

from .constants import *
from .logging import Log
from .exceptions import *

def get_path(file_path: str) -> str:
    # no clue why, but this character gets added for me when running
    return str(Path(file_path)).replace("\u202a", "")

class Upload:
    def __init__(
        self,
        profile: Union[str, webdriver.FirefoxProfile],
        executable_path: str = "geckodriver",
        timeout: int = 3,
        headless: bool = True,
        debug: bool = True,
        options: FirefoxOptions = FirefoxOptions(),
    ) -> None:
        if isinstance(profile, str):
            profile = webdriver.FirefoxProfile(profile)

        options.headless = headless

        service = FirefoxService(executable_path=executable_path)
        self.driver = webdriver.Firefox(
            service=service, firefox_profile=profile, options=options
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
        modal.find_element(By.ID, NEXT_BUTTON).click()
        sleep(self.timeout)

    def not_uploaded(self, modal) -> bool:
        return modal.find_element(By.XPATH, STATUS_CONTAINER).text.find(UPLOADED) != -1

    def upload(
        self,
        file: str,
        title: str = "",
        description: str = "",
        thumbnail: str = "",
        tags: list = [],
        only_upload: bool = False,
    ) -> Tuple[bool, Optional[str]]:
        """Uploads a video to YouTube.
        Returns if the video was uploaded and the video id.
        """
        if not file:
            raise FileNotFoundError(f'Could not find file with path: "{file}"')

        self.driver.get(YOUTUBE_UPLOAD_URL)
        sleep(self.timeout)

        self.log.debug(f'Trying to upload "{file}" to YouTube...')

        self.driver.find_element(By.XPATH, INPUT_FILE_VIDEO).send_keys(get_path(file))
        sleep(self.timeout)

        modal = self.driver.find_element(By.CSS_SELECTOR, UPLOAD_DIALOG_MODAL)
        self.log.debug("Found YouTube upload Dialog Modal")

        if only_upload:
            video_id = self.get_video_id(modal)

            while self.not_uploaded(modal):
                self.log.debug("Still uploading...")
                sleep(self.timeout)

            return True, video_id

        self.log.debug(f'Trying to set "{title}" as title...')

        # TITLE
        title_field = self.click(modal.find_element(By.ID, TEXTBOX))

        # get file name (default) title
        title = title if title else title_field.text

        if len(title) > TITLE_COUNTER:
            raise ExceedsCharactersAllowed(
                f"Title was not set due to exceeding the maximum allowed characters ({len(title)}/{TITLE_COUNTER})"
            )

        # clearing out title which defaults to filename
        for _ in range(len(title_field.text) + 10):
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
            container = modal.find_element(By.XPATH, DESCRIPTION_CONTAINER)
            description_field = self.click(container.find_element(By.ID, TEXTBOX))

            self.send(description_field, description)

        if thumbnail:
            self.log.debug(f'Trying to set "{thumbnail}" as thumbnail...')
            modal.find_element(By.XPATH, INPUT_FILE_THUMBNAIL).send_keys(
                get_path(thumbnail)
            )
            sleep(self.timeout)

        self.log.debug('Trying to set video to "Not made for kids"...')
        kids_section = modal.find_element(By.NAME, NOT_MADE_FOR_KIDS_LABEL)
        kids_section.find_element(By.ID, RADIO_LABEL).click()
        sleep(self.timeout)

        if tags:
            self.click(modal.find_element(By.XPATH, MORE_OPTIONS_CONTAINER))

            tags = ",".join(str(tag) for tag in tags)

            if len(tags) > TAGS_COUNTER:
                raise ExceedsCharactersAllowed(
                    f"Tags were not set due to exceeding the maximum allowed characters ({len(tags)}/{TAGS_COUNTER})"
                )

            self.log.debug(f'Trying to set "{tags}" as tags...')
            container = modal.find_element(By.XPATH, TAGS_CONTAINER)
            tags_field = self.click(container.find_element(By.ID, TEXT_INPUT))
            self.send(tags_field, tags)

        # sometimes you have 4 tabs instead of 3
        # this handles both cases
        for _ in range(3):
            try:
                self.click_next(modal)
            except:
                pass

        self.log.debug("Trying to set video visibility to public...")
        public_main_button = modal.find_element(By.NAME, PUBLIC_BUTTON)
        public_main_button.find_element(By.ID, RADIO_LABEL).click()
        video_id = self.get_video_id(modal)

        while self.not_uploaded(modal):
            self.log.debug("Still uploading...")
            sleep(1)

        done_button = modal.find_element(By.ID, DONE_BUTTON)

        if done_button.get_attribute("aria-disabled") == "true":
            self.log.debug(self.driver.find_element(By.XPATH, ERROR_CONTAINER).text)
            return False, None

        self.click(done_button)

        return True, video_id

    def get_video_id(self, modal) -> Optional[str]:
        video_id = None
        try:
            video_url_container = modal.find_element(By.XPATH, VIDEO_URL_CONTAINER)
            video_url_element = video_url_container.find_element(By.XPATH, VIDEO_URL_ELEMENT)

            video_id = video_url_element.get_attribute(HREF).split("/")[-1]
        except:
            raise VideoIDError("Could not get video ID")

        return video_id

    def close(self):
        self.driver.quit()
        self.log.debug("Closed Firefox")
