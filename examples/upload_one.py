from opplast import Upload


upload = Upload(
    "C:/Users/USERNAME/AppData/Roaming/Mozilla/Firefox/Profiles/random.selenium",
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
