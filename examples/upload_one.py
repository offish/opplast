from opplast import Upload


upload = Upload(
    # like Users/truelove/Library/Application Support/Firefox/Profiles/4oqb2upm.xxd
    root_profile_directory="you root profile directory file",
    headless= False,
    # if you download in this folder like ./geckodriver
    executable_path='./geckodriver'
)

was_uploaded, video_id = upload.upload(
    {
        "file": "path/to/video.mp4",
        "title": "My YouTube Title",
        "description": "My YouTube Description",
        "thumbnail": "path/to/thumbnail.jpg",
        "tags": ["these", "are", "my", "tags"],
    }
)

if was_uploaded:
    print(f"{video_id} has been uploaded to YouTube")

upload.close()
