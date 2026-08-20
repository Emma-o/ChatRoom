from livekit import api
    

class LiveKitService:
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret

    def create_token(self, username, room_name):
        token = (
            api.AccessToken(
                self.api_key,
                self.api_secret
            )
            .with_identity(username)
            .with_name(username)
            .with_grants(
                api.VideoGrants(
                    room_join=True,
                    room=room_name
                )
            )
        )

        return token.to_jwt()