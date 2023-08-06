from functools import wraps


def on_message_parse(func):
    """
    POST /message 를 호출 시 전송하는 user_key, type, content 를
    request.data 에서 파싱하여 함수에 전달합니다.
    """
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        req = args[0]
        user_key, content_type, content = [req.data[key] for key in ('user_key', 'type', 'content')]
        return func(request, user_key=user_key, content_type=content_type, content=content, *args, **kwargs)

    return wrapper


def on_friend_added_parse(func):
    """
    POST /friend 를 호출 시 전송하는 user_key 를
    request.data 에서 파싱하여 함수에 전달합니다.
    """
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        req = args[0]
        user_key = req.data['user_key']
        return func(request, user_key=user_key, *args, **kwargs)

    return wrapper


def on_friend_deleted_parse(func):
    """
    DELETE /friend/:user_key 를 호출 시 전송하는 user_key 를
    kwargs 로 넘어오는 pk(user_key) 를 함수에 전달합니다.
    """
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        user_key = kwargs['pk']
        return func(request, user_key=user_key, *args, **kwargs)

    return wrapper


def on_chatroom_leaved_parse(func):
    """
    DELETE /chat_room/:user_key 를 호출 시 전송하는 user_key 를
    kwargs 로 넘어오는 pk(user_key) 를 함수에 전달합니다.
    """
    return on_friend_deleted_parse(func)
