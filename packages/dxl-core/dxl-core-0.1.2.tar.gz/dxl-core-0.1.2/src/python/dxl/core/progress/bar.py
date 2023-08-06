import time
import datetime

PROGRESS_FORMATS = {
    'std': "[{current:>8}/{total:>8}({complete_percentage:5.2f}%, {iteration_speed}) | {time_elapsed} < {time_estimate}]"
}

MIN_ELAPSED_TIME = 1e-5


class ProgressReporter:
    def __init__(self, total=100, message=None, min_elapsed_time=1.0, print_func=None):
        self.total = total
        self.min_elapsed_time = min_elapsed_time
        self.message = message or PROGRESS_FORMATS['std']
        self.step = 0
        self.time_start = None
        self.time_previous = None
        self.print_func = print_func if print_func is not None else print
        self.reset()

    def reset(self):
        self.time_start = time.time()
        self.time_next_report = self.time_start

    def set_time_next_report(self, previous):
        self.time_next_report = previous + self.min_elapsed_time

    def complete_percentage(self):
        return float(self.step) / float(self.total) * 100

    def time_estimate(self):
        if self.complete_percentage() <= 0.0:
            return None
        return (1 / self.complete_percentage() * 100 - 1) * self.time_elapsed()

    def time_elapsed(self):
        return time.time() - self.time_start

    def iterations_per_second(self):
        return self.step / max(self.time_elapsed(), MIN_ELAPSED_TIME)

    def iteration_speed(self) -> str:
        if self.iterations_per_second() > 1.0 or self.iterations_per_second() < MIN_ELAPSED_TIME:
            return "{:4.2f}it/s".format(self.iterations_per_second())
        else:
            return "{:4.2f}s/it".format(1.0 / self.iterations_per_second())

    def passed_enough_time(self):
        return time.time() > self.time_next_report

    def update(self, step=None, *args, **kwargs):
        if step is None:
            step = self.step + 1
        self.step = step

        if not self.passed_enough_time():
            return

        self.print_func(self.message.format(*args,
                                            current=self.step,
                                            total=self.total,
                                            complete_percentage=self.complete_percentage(),
                                            iteration_speed=self.iteration_speed(),
                                            time_elapsed=str(datetime.timedelta(
                                                seconds=self.time_elapsed())),
                                            time_estimate=str(datetime.timedelta(
                                                seconds=self.time_estimate())),
                                            **kwargs))
        self.set_time_next_report(time.time())
