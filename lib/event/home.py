import lib.event as e
from lib.function import global_value as g


@g.app.action("actionId-back")
def handle_some_action(ack, body, client):
    ack()
    g.logging.trace(body)

    result = client.views_publish(
        user_id = body["user"]["id"],
        view = e.DispMainMenu(),
    )

    g.logging.trace(result)
