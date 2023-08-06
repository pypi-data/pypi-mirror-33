def MessageResponse(message=None, keyboard=None):
    assert message is not None, 'message 는 필수로 입력해야 합니다.'

    result = {
        'message': message
    }

    if keyboard:
        result['keyboard'] = keyboard

    return result


def Keyboard(type, buttons=None):
    assert type in ['text', 'buttons'], 'type 에는 text 또는 buttons 를 입력해야 합니다.'

    result = {
        'type': type,
    }

    if buttons:
        result['buttons'] = buttons

    return result


def Message(text=None, photo=None, message_button=None):
    assert text is not None or photo is not None and message_button is not None, \
        'type, photo, message_buttons 중 한 개 이상은 필수로 입력해야 합니다.'

    result = dict()

    if text:
        result['text'] = text

    if photo:
        result['photo'] = photo

    if message_button:
        result['message_button'] = message_button

    return result


def Photo(url, width, height):
    assert url is not None and width is not None and height is not None, 'url, width, height 전부 입력해야 합니다.'

    return {
        'url': url,
        'width': width,
        'height': height,
    }


def MessageButton(label, url):
    assert label is not None and url is not None, 'label, url 전부 입력해야 합니다.'

    return {
        'label': label,
        'url': url
    }
