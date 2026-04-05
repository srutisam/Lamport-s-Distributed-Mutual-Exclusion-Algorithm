import simpy
import random

class Process:
    def __init__(self, env, pid, processes):
        self.env = env
        self.pid = pid
        self.clock = 0
        self.queue = []
        self.replies = set()
        self.processes = processes
        self.in_cs = False

    def increment_clock(self):
        self.clock += 1

    def update_clock(self, received_time):
        self.clock = max(self.clock, received_time) + 1

    def send_request(self):
        self.increment_clock()
        timestamp = self.clock
        self.queue.append((timestamp, self.pid))
        self.queue.sort()

        print(f"{self.env.now}: P{self.pid} REQUEST at time {timestamp}")

        for p in self.processes:
            if p.pid != self.pid:
                self.env.process(p.receive_request(timestamp, self.pid))

    def receive_request(self, timestamp, sender_pid):
        yield self.env.timeout(random.uniform(0.1, 0.5))
        self.update_clock(timestamp)
        self.queue.append((timestamp, sender_pid))
        self.queue.sort()

        print(f"{self.env.now}: P{self.pid} received REQUEST from P{sender_pid}")

        # send reply
        self.increment_clock()
        sender = self.processes[sender_pid]
        self.env.process(sender.receive_reply(self.pid))

    def receive_reply(self, sender_pid):
        yield self.env.timeout(random.uniform(0.1, 0.3))
        self.replies.add(sender_pid)
        print(f"{self.env.now}: P{self.pid} received REPLY from P{sender_pid}")

    def send_release(self):
        print(f"{self.env.now}: P{self.pid} RELEASE")
        self.queue = [q for q in self.queue if q[1] != self.pid]

        for p in self.processes:
            if p.pid != self.pid:
                self.env.process(p.receive_release(self.pid))

    def receive_release(self, sender_pid):
        yield self.env.timeout(random.uniform(0.1, 0.3))
        self.queue = [q for q in self.queue if q[1] != sender_pid]

    def can_enter_cs(self):
        if len(self.replies) == len(self.processes) - 1:
            return self.queue[0][1] == self.pid
        return False

    def run(self):
        yield self.env.timeout(random.uniform(1, 3))

        self.send_request()

        while not self.can_enter_cs():
            yield self.env.timeout(0.1)

        # Enter CS
        self.in_cs = True
        print(f"{self.env.now}: P{self.pid} ENTER CS")

        yield self.env.timeout(random.uniform(1, 2))

        print(f"{self.env.now}: P{self.pid} EXIT CS")
        self.in_cs = False

        self.replies.clear()
        self.send_release()


def run_simulation(n=3):
    env = simpy.Environment()
    processes = []

    for i in range(n):
        processes.append(Process(env, i, None))

    for p in processes:
        p.processes = processes

    for p in processes:
        env.process(p.run())

    env.run(until=20)