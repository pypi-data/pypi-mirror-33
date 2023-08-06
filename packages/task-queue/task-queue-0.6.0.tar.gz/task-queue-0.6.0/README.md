# python-task-queue
Python TaskQueue object that can rapidly populate and download from queues that conform to Google's Task Queue API

# Installation

`pip install taskqueue`

# Usage 

Define a class that inherits from taskqueue.RegisteredTask and implments the `execute` method.

Tasks can be loaded into queues locally or as based64 encoded data in the cloud and executed later.
Here's an example implementation of a `PrintTask`. Generally, you should specify a very lightweight
container and let the actual execution download and manipulate data.

```
class PrintTask(RegisteredTask):
  def __init__(self, txt=''):
    super(PrintTask, self).__init__()
    self.txt = txt
  def execute(self):
    if self.txt:
      print(str(self) + ": " + str(self.txt))
    else:
      print(self)
```

## Local Usage

For small jobs, you might want to use one or more processes to execute the tasks:
```
with LocalTaskQueue(parallel=5) as tq: # use 5 processes
  for _ in range(1000):
    tq.insert(
      PrintTask(i)
    )
```
This will load the queue with 1000 print tasks then execute them across five processes.

## Cloud Usage

Set up an SQS queue and acquire an aws-secret.json that is compatible with CloudVolume.

```
qurl = 'https://sqs.us-east-1.amazonaws.com/$DIGITS/$QUEUE_NAME'
with TaskQueue(queue_server='sqs', qurl=qurl) as tq:
  for _ in range(1000):
    tq.insert(PrintTask(i))
```

This inserts 1000 PrintTask descriptions into your SQS queue.

Somewhere else, you'll do the following (probably across multiple workers):

```
qurl = 'https://sqs.us-east-1.amazonaws.com/$DIGITS/$QUEUE_NAME'
with TaskQueue(queue_server='sqs', qurl=qurl) as tq:
  task = tq.lease(seconds=int($LEASE_SECONDS))
  task.execute()
  tq.delete(task)
```