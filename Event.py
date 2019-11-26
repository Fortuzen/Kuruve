

class Event:
    def __init__(self, tick, function, *args):
        self.trigger = function
        self.args = args
        self.tick = tick


class EventManager:
    events = []
    total_ticks = 0
    @staticmethod
    def process_events(total_ticks):
        EventManager.total_ticks = total_ticks
        for event in EventManager.events:
            if event.tick <= EventManager.total_ticks:
                event.trigger(*event.args)
                EventManager.events.remove(event)

    @staticmethod
    def fire_event_after_delay(ticks, function, *args):
        # print(args)
        e = Event(ticks + EventManager.total_ticks, function, *args)
        EventManager.events.append(e)
