from rest_framework.viewsets import ViewSet
from rest_framework.response import Response


class KakaoAutoReplyViewSet(ViewSet):
    """
    KakaoAutoReplyViewSet

    카카오톡 플러스친구 자동응답 API 에서 구현해야 하는 함수를 미리 정리 해 둔 ViewSet 입니다.
    해당 ViewSet 을 상속받은 ViewSet 은 아래 명시된 5개의 메소드를 구현해야 합니다.
    구현하지 않은 메소드는 Response 204 응답을 반환하며, '~ function is not provided.' 메세지를 출력합니다.
    """

    """
    카카오톡 플러스친구 자동응답은 on_message 와 on_keyboard 에서 올바르지 않은 데이터나 HTTP 응답을 받는 경우
    문제가 발생한 것으로 간주합니다. on_friend_added, on_friend_deleted, on_chatroom_leaved 는 구현하지 않아도
    API 를 사용하는데 문제가 발생하지 않습니다. 관련 메세지 출력을 사용하지 않으려면,
    KakaoAutoReplyViewSet 을 상속받은 ViewSet 에 print_not_provided = False 를 추가하세요. 
    """
    print_not_provided = True

    def _not_provided_print(self, message):
        if not self.print_not_provided:
            return

        print(message)

    def on_keyboard(self, request, *args, **kwargs):
        self._not_provided_print("on_keyboard function is not provided.")
        return Response(None, 204)

    def on_message(self, request, *args, **kwargs):
        self._not_provided_print("on_message function is not provided.")
        return Response(None, 204)

    def on_friend_added(self, request, *args, **kwargs):
        self._not_provided_print("on_friend_added function is not provided.")
        return Response(None, 204)

    def on_friend_deleted(self, request, *args, **kwargs):
        self._not_provided_print("on_friend_deleted function is not provided.")
        return Response(None, 204)

    def on_chatroom_leaved(self, request, *args, **kwargs):
        self._not_provided_print("on_chatroom_leaved function is not provided.")
        return Response(None, 204)
