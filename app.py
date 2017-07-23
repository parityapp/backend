import os

from aiohttp.web import Request, Response, Application, run_app
import aiohttp_cors

from app import auth_controller, stats_controller


async def index(_: Request) -> Response:
  return Response(
    text="Welcome to Parity Backend API",
    status=200
  )

app = Application()
app.router.add_get(path='/',
                   handler=index)
app.router.add_post(path='/auth',
                    handler=auth_controller.auth_route)
app.router.add_get(path='/stats/pulse',
                   handler=stats_controller.pulse_route)
app.router.add_get(path='/stats/pulse/{channel_id}',
                   handler=stats_controller.pulse_by_channel_route)
app.router.add_get(path='/stats/most_active/{channel_id}',
                   handler=stats_controller.most_active_by_channel_route)
app.router.add_get(path='/stats/hot_topics/{channel_id}',
                   handler=stats_controller.hot_topics_by_channel_route)
app.router.add_get(path='/stats/representative_messages/{channel_id}',
                   handler=stats_controller.representative_messages_by_channel_route)
app.router.add_get(path='/stats/summary/{channel_id}',
                   handler=stats_controller.summary_by_channel_route)

cors = aiohttp_cors.setup(app, defaults={
  "*": aiohttp_cors.ResourceOptions(
    allow_credentials=True,
    expose_headers="*",
    allow_headers="*",
  )
})
for route in list(app.router.routes()):
    cors.add(route)

run_app(
  app,
  port=int(os.getenv('BACKEND_PORT', '80'))
)
