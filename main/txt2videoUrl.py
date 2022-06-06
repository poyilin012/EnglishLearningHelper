
def init_video_urls():
    video_url = {}
    for i in range(1, 7):
        file = open('Audio_Urls/Audio_Urls_' + str(i) + '.txt')
        lines = file.readlines()
        file.close()
        for line in lines:
            line = line.split('@')
            video_url[line[0]] = line[1]
    return video_url


video_url = init_video_urls()
print(video_url['abandon'])
# audio_message = AudioSendMessage(
#     original_content_url=video_url['abandon'],
#     duration=0
# )
