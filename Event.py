

class Event:
    """
    Stores any function, its arguments and when it should be executed.
    :param tick: When should the function be executed
    :type tick: int
    :param function: The function
    :param `*args`: Arguments for the function
    """
    def __init__(self, tick, function, *args):
        self.trigger = function
        self.args = args
        self.tick = tick


class EventManager:
    """Class that manages events"""
    events = []
    total_ticks = 0
    @staticmethod
    def process_events(total_ticks):
        """Execute the event's function and remove the event"""

        EventManager.total_ticks = total_ticks
        for event in EventManager.events:
            if event.tick <= EventManager.total_ticks:
                event.trigger(*event.args)
                # Make sure the event exists. There was game reset related bug.
                if event in EventManager.events:
                    EventManager.events.remove(event)

    @staticmethod
    def fire_event_after_delay(ticks, function, *args):
        """
        Create an event from a function and add it to the event queue

        :param ticks: After how many ticks should the function be executed
        :param function: The function to be executed
        :param `*args`: The function's arguments

        """
        # print(args)
        e = Event(ticks + EventManager.total_ticks, function, *args)
        EventManager.events.append(e)
