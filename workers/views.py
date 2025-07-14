import asyncio
from datetime import datetime

from datastar_py.django import DatastarResponse
from datastar_py.django import ServerSentEventGenerator as SSE
from django.shortcuts import render


def test(request):
    return render(request, "workers/test.html")


async def time_stream(request):
    async def event_stream():
        while True:
            now = datetime.now().strftime("%H:%M:%S")
            yield SSE.patch_signals({"currentTime": now})
            await asyncio.sleep(1)

    return DatastarResponse((event_stream()))
