import logging

from api.model.ResultVO import *
from schedule import TaskThreadHolder, TaskThread, TaskHandlerContext

log = logging.getLogger('TriggerActor')


def stop_job(job_id):
    task_thread = TaskThreadHolder.load_task_thread(job_id)
    if task_thread is not None:
        TaskThreadHolder.remove_task_thread(job_id, "人工手动终止")
        return SUCCESS
    return ResultVO(SUCCESS_CODE, "job thread aleady killed.")


def handle_trigger(task_param):
    log.info(f"接收到任务请求,jobId:{task_param.jobId} logId:{task_param.logId}")

    # TODO 这里如果打了断点, 有可能导致生成两个TaskThread
    task_thread: TaskThread = TaskThreadHolder.load_task_thread(task_param.jobId)
    remove_old_reason = None

    if task_thread is not None:
        task_handler = task_thread.get_handler()
    else:
        task_handler = None

    if "BEAN" == task_param.jobType:
        if task_thread is not None and task_handler is not None and task_thread.get_handler() != task_handler:
            remove_old_reason = "更新JobHandler或更换任务模式,终止旧任务线程"
            # 这里不需要显示的终止,在调用 registryTaskThread的时候会自己终止
            task_thread = None
            task_handler = None

        if task_handler is None:
            task_handler = TaskHandlerContext.load_task_handler(task_param.actorHandler)

    elif "JAVA" == task_param.jobType:
        pass
    elif "SHELL" == task_param.jobType or "PYTHON" == task_param.jobType:
        pass
    else:
        return ResultVO(FAIL_CODE, f"jobType [{task_param.jobType} 不合法")

    if task_thread is not None:
        # TODO 阻塞策略
        pass

    if task_thread is None:
        task_thread = TaskThreadHolder.registry_task_thread(task_param.jobId, task_handler, remove_old_reason)

    return task_thread.push_trigger_queue(task_param)


def ping():
    return "pong"
