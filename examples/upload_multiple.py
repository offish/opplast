from opplast import Upload


videos = [
    {
        "file": "path/to/video.mp4",
        "title": "My First YouTube Title",
        "description": "My First YouTube Description",
        "thumbnail": "path/to/thumbnail.jpg",
        "tags": ["these", "are", "my", "tags"],
    },
    {
        "file": "path/to/video2.mp4",
        "title": "My Second YouTube Title",
        "description": "My Second YouTube Description",
        "thumbnail": "path/to/thumbnail2.jpg",
        "tags": ["these", "are", "my", "tags"],
    },
]

upload = Upload(
    "C:/Users/USERNAME/AppData/Roaming/Mozilla/Firefox/Profiles/random.selenium",
)

for video in videos:
    was_uploaded, video_id = upload.upload(video)

    if was_uploaded:
        print(f"{video_id} has been uploaded to YouTube")

upload.close()
