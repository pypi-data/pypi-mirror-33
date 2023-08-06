import threading
import logging
import time
import client
from queue import Queue, Empty

from api.exceptions import IllegalArgumentException
from api.handler import ITaskHandler
from api.model.ResultVO import *

logger = logging.getLogger('eureka_client')


class TaskThread(threading.Thread):
    """
    真正开始执行任务的线程
    """

    def __init__(self, handler: ITaskHandler, actor_port):
        """
        执行器线程的构造函数
        :param handler:
        :param actor_port:
        """
        threading.Thread.__init__(self, name="任务线程")

        if handler is None:
            raise IllegalArgumentException("创建TaskThread失败,传入的ITaskHandler为空,无法执行")

        self.handler = handler
        self.actor_port = actor_port
        self.to_stop = False
        self.stop_reason = None
        self.running = False
        self.trigger_queue: Queue = Queue()  # 使用了Python中的队列
        self.trigger_log_id_set = set()  # TODO ConcurrentHashSet

    def get_handler(self):
        """
        获取handler
        :return:
        """
        return self.handler

    def push_trigger_queue(self, trigger_param):
        """
        把任务放入 任务队列中去
        :param trigger_param:
        :return:
        """
        if trigger_param.logId in self.trigger_log_id_set:
            return ResultVO(code=ResultVO.FAIL_CODE, msg=f"任务已重复,LogId:{trigger_param.log_id}")

        # 放入队列中
        self.trigger_log_id_set.add(trigger_param.logId)
        self.trigger_queue.put_nowait(trigger_param)
        return SUCCESS

    def stop(self, stop_reason):
        """
        强制杀掉任务
        :param stop_reason:
        :return:
        """
        logger.info(f"任务TaskThread终止,原因:{stop_reason}")
        self.to_stop = True
        self.stop_reason = stop_reason

    def is_running_or_has_queue(self):
        """
        判断任务线程的情况
        :return:
        """
        # TODO trigger_queue.size()还有问题
        return self.running or not self.trigger_queue.empty()

    def run(self):
        """
        周期执行的东西
        :return:
        """

        log_id = None
        while not self.to_stop:
            self.running = False
            try:
                # 3秒等待一个任务
                task_param = None
                try:
                    task_param = self.trigger_queue.get(timeout=3)
                except Empty:
                    pass

                if task_param is None:
                    # 没有任务
                    continue

                log_id = task_param.logId

                logger.info(f"开始处理logId:{log_id}的任务")

                # 有任务, 修改状态
                self.running = True
                self.trigger_log_id_set.remove(log_id)

                # 更新任务状态到正在执行
                import eureka
                self.__update_task_status_to_execute(log_id, eureka.client.get_host_ip(), 1)

                try:
                    execute_result = self.handler.execute(task_param.actorParams)
                    if execute_result is None:
                        execute_result = FAIL
                except Exception as e:
                    logger.error(f"处理logId:{log_id}出现错误:{str(e)}")
                    if self.to_stop:
                        logger.error(f"任务线程强制停止:{str(e)}")
                        try:
                            self.handler.kill()
                        except:
                            pass
                    execute_result = ResultVO(FAIL_CODE, str(e))

                if not self.to_stop:
                    # 执行完成,回调写入 执行结果
                    self.__update_task_status_to_finished(log_id, execute_result, 1)
                    # 这里判断执行次数,如果判断到已经到达执行次数的上限,就要把这个cron调度给停止了
                    if task_param.limitTimes is not None and task_param.limitTimes > 0:
                        # 说明这个任务是只执行有限次数的任务. 那么就需要查询这个Job已经执行成功了的任务的次数
                        success_times = client.ScheduleJobTaskLogClient.count_success_task_log_by_job(task_param.jobId,
                                                                                                      task_param.updateTime)
                        if success_times >= task_param.limitTimes:
                            # 说明已经到达了执行次数的限制.那么就需要停止这个调度
                            if client.JobScheduleClient.stop(task_param.jobId):
                                self.stop("达到任务执行次数上限,完成job")
                else:
                    # 执行强制停止,回调写入 失败信息
                    self.__update_task_status_to_finished(log_id,
                                                          ResultVO(FAIL_CODE, f"{self.stop_reason} 业务运行中,被强制终止"), 1)
            except Exception as e:
                logger.error(f"处理logId:{log_id}出现严重错误", e)
                if log_id is not None:
                    self.__update_task_status_to_finished(log_id,
                                                          ResultVO(FAIL_CODE,
                                                                   f"{self.stop_reason}  处理logId:{log_id} 出现严重错误:"),
                                                          1)

        while self.trigger_queue is not None and not self.trigger_queue.empty():
            try:
                task_param = self.trigger_queue.get_nowait()
            except Empty:
                return
            if task_param is not None:
                self.__update_task_status_to_finished(task_param.logId,
                                                      ResultVO(FAIL_CODE,
                                                               f"{self.stop_reason}  处理logId:{log_id} 任务尚未执行,在调度队列中被终止:"),
                                                      1)

    # region 私有方法
    def __update_task_status_to_execute(self, log_id, instance_address, deep):
        """
        更新任务的状态到正在执行中
        :param log_id:
        :param instance_address:
        :param deep:
        :return:
        """
        if deep > 3:
            # 重试3次还不行, 直接退出
            logger.error(f"更新logId:{log_id} 的状态,重试3次仍然无法连接到ficus,无法更新任务状态到正在执行.")
            return False

        try:
            # 把任务状态设置为执行中
            client.ScheduleJobTaskLogClient.update_task_status_to_execute(log_id, instance_address)
        except Exception:
            logger.error(f"更新logId:{log_id} 的状态,连接到ficus,无法更新任务状态到正在执行.次数:{deep}")
            time.sleep(5)
            return self.__update_task_status_to_execute(log_id, instance_address, ++deep)

    def __update_task_status_to_finished(self, log_id, execute_result, deep):
        """
        更新任务的状态到结束
        :param log_id:
        :param execute_result:
        :param deep:
        :return:
        """
        if deep > 3:
            # 重试3次还不行, 直接退出
            logger.error(f"更新logId:{log_id} 的状态,重试3次仍然无法连接到ficus,无法更新任务状态到完成.")
            return False

        try:
            # 把任务状态设置为执行中
            client.ScheduleJobTaskLogClient.update_task_status_to_finished(log_id, execute_result.to_dict())
        except Exception:
            logger.error(f"更新logId:{log_id} 的状态,连接到ficus,无法更新任务状态到到完成.次数:{deep}")
            time.sleep(5)
            return self.__update_task_status_to_execute(log_id, execute_result, ++deep)
    # endregion
