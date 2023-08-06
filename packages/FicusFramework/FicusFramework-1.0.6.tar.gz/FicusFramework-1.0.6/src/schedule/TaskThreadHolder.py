from api.handler import ITaskHandler
from schedule.TaskThread import TaskThread

__actor_port = 8011
__task_thread_cache = dict()


def registry_task_thread(task_id: int, handler: ITaskHandler, remove_old_reason: str):
    """
       注册一个任务线程
    :param task_id:
    :param handler:
    :param remove_old_reason:
    :return:
    """
    # 实例化一个线程
    new_task_thread = TaskThread(handler, __actor_port)
    new_task_thread.start()  # 开启线程

    old_task_thread: TaskThread = __task_thread_cache.get(task_id)
    __task_thread_cache[task_id] = new_task_thread

    if old_task_thread is not None:
        old_task_thread.stop(remove_old_reason)

    return new_task_thread


def remove_task_thread(task_id: int, remove_old_reason: str):
    """
    删除一个任务线程
    :param task_id:
    :param remove_old_reason:
    :return:
    """
    old_task_thread: TaskThread = __task_thread_cache.pop(task_id)

    if old_task_thread is not None:
        old_task_thread.stop(remove_old_reason)


def load_task_thread(task_id: int):
    """
    返回一个任务线程
    :param task_id:
    :return:
    """
    return __task_thread_cache.get(task_id)
