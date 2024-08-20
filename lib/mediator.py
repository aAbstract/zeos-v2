subscribers = {}


def subscribe(event_type: str, func_id: str, func):
    if not event_type in subscribers:
        subscribers[event_type] = {}
    subscribers[event_type][func_id] = func


def unsubscribe(event_type: str, func_id: str):
    del subscribers[event_type][func_id]
    if len(subscribers[event_type].keys()) == 0:
        del subscribers[event_type]


def post_event(event_type: str, args):
    if not event_type in subscribers:
        return
    for key in subscribers[event_type]:
        subscribers[event_type][key](args)
