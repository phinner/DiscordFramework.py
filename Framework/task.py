from asyncio import sleep
from concurrent.futures import ThreadPoolExecutor
from discord.ext.tasks import Loop
from datetime import timedelta


class TaskManager(ThreadPoolExecutor):
    Tasks = dict()

    # --------------------------------------------------------------------------- #

    @classmethod
    def startScheduledTask(cls, name):
        if name in cls.Tasks:
            if not cls.Tasks[name].is_running():
                cls.Tasks[name].start()
        else:
            raise KeyError(f"{name} doesn't exist")

    @classmethod
    def startAllScheduledTasks(cls):
        for task in cls.Tasks.values():
            if not task.is_running():
                task.start()

    # --------------------------------------------------------------------------- #

    @classmethod
    def scheduledTask(cls, seconds=0, minutes=0, hours=0, count=None, reconnect=True, loop=None,
                        start=None, run=True):
        """
        This function is for scheduling functions to start at a certain hour or date,
        check https://docs.python.org/3/library/datetime.html to know how to format the "start" dictionary.
        """
        def wrapper(coro):
            task = Loop(coro, seconds, hours, minutes, count, reconnect, loop)
            cls.Tasks.update({coro.__name__: task})

            @task.before_loop
            async def before_task():
                sleep_time = 0

                if start is not None:
                    now = datetime.now()
                    keys = ["year", "month", "day", "hour", "minute", "second"]

                    future = dict(zip(keys, now.timetuple()))
                    future.update(start)
                    future = datetime(**future)

                    while now >= future:
                        future += timedelta(seconds=seconds, minutes=minutes, hours=hours)
                    sleep_time = (future - now).seconds

                await sleep(sleep_time)

            if run:
                task.start()

            return task
        return wrapper

if __name__ == "__main__":

    """
    Confusing demo lol
    """

    import asyncio
    from discord import Client


    manager = TaskManager(max_workers=4)
    n = 0


    def blocking_task():
        print("blocking task begin")

        with open("text.txt", "w") as file:
            for i in range(100000000):
                pass

        print("blocking task end")


    def bot_main():
        print("let us begin")

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        client = Client(loop=loop)

        @manager.scheduledTask(seconds=5, loop=loop)
        async def backgroung_bot_task():
            global n
            n += 1
            print(i * i)

        @client.event
        async def on_message(msg):
            if msg.author.id == client.user.id:
                return
            print(msg)

        loop.create_task(client.start(input("Bot token please: "), bot=True, reconnect=True))
        loop.run_forever()

        print("out")

    def Oh_no():
        print("zero")
        g = 1/0
        print("no zero ?")


    def trace(future):
        print(future)
        print(future.result())


    futures = list()

    with manager:
        futures.append(manager.submit(bot_main))
        futures.append(manager.submit(blocking_task))
        futures.append(manager.submit(Oh_no))
        futures.append(manager.submit(blocking_task))

        for fut in futures:
            fut.add_done_callback(trace)
