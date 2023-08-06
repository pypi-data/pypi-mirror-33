from rest_framework.routers import SimpleRouter, Route


class KakaoAutoReplyRouter(SimpleRouter):
    routes = [
        Route(
            url='^{prefix}/keyboard$',
            mapping={'get': 'on_keyboard'},
            name='{basename}-on_keyboard',
            detail=False,
            initkwargs={},
        ),
        Route(
            url='^{prefix}/message$',
            mapping={'post': 'on_message'},
            name='{basename}-on_message',
            detail=False,
            initkwargs={},
        ),
        Route(
            url='^{prefix}/friend$',
            mapping={'post': 'on_friend_added'},
            name='{basename}-on_friend_added',
            detail=True,
            initkwargs={},
        ),
        Route(
            url='^{prefix}/friend/{lookup}$',
            mapping={'delete': 'on_friend_deleted'},
            name='{basename}-on_friend_deleted',
            detail=True,
            initkwargs={},
        ),
        Route(
            url='^{prefix}/chat_room/{lookup}$',
            mapping={'delete': 'on_chatroom_leaved'},
            name='{basename}-on_chatroom_leaved',
            detail=True,
            initkwargs={},
        )
    ]
