from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views import View


class TelegramWebhookView(View):
    """Временная вьюшка для вебхуков телеграма"""

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        # Временная заглушка
        return JsonResponse({"status": "ok"})
