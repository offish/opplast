from opplast import Upload


if __name__ == "__main__":
    videos = [
        {
            "file": r"C:/path/to/video.mp4",
            "title": "My First YouTube Title",
            "description": "My First YouTube Description",
            "thumbnail": r"C:/path/to/thumbnail.jpg",
            "tags": ["these", "are", "my", "tags"],
        },
        {
            "file": r"C:/path/to/video2.mp4",
            "title": "My Second YouTube Title",
            "description": "My Second YouTube Description",
            "thumbnail": r"C:/path/to/thumbnail2.jpg",
            "tags": ["these", "are", "my", "tags"],
        },
    ]

    upload = Upload(
        # use r"" for paths, this will not give formatting errors e.g. "\n"
        r"C:/Users/USERNAME/AppData/Roaming/Mozilla/Firefox/Profiles/r4Nd0m.selenium",
    )

    for video in videos:
        was_uploaded, video_id = upload.upload(**video)

        if was_uploaded:
            print(f"{video_id} has been uploaded to YouTube")

    upload.close()
