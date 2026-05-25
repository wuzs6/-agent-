import openai
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Dict
import random

# ==============================================
# 配置：高吞吐模式 → 日耗 3,000,000 Token
# ==============================================
openai.api_key = "YOUR_API_KEY"
openai.base_url = "https://api.openai.com/v1"

DAILY_TOKEN_TARGET = 3000000
MODEL_NAME = "gpt-3.5-turbo"
TOKEN_PER_RUN = 20000
RUNS_PER_DAY = DAILY_TOKEN_TARGET // TOKEN_PER_RUN


# 任务状态
class TaskStatus(Enum):
    PENDING = "待处理"
    IN_PROGRESS = "进行中"
    COMPLETED = "已完成"
    OVERDUE = "已逾期"


# 任务结构
class Task:
    def __init__(self, task_id, title, desc, assignee, deadline):
        self.task_id = task_id
        self.title = title
        self.desc = desc
        self.assignee = assignee
        self.deadline = deadline
        self.status = TaskStatus.PENDING

    def to_dict(self):
        return {
            "id": self.task_id,
            "title": self.title,
            "desc": self.desc,
            "assignee": self.assignee,
            "deadline": self.deadline.strftime("%Y-%m-%d %H:%M"),
            "status": self.status.value
        }


# ==============================================
# 1. 任务解析智能体（高Token消耗）
# ==============================================
class TaskParserAgent:
    def run(self, task: Task):
        prompt = f"""
你是专业任务解析专家，请详细分析任务：
任务标题：{task.title}
任务描述：{task.desc}
负责人：{task.assignee}
截止时间：{task.deadline}

请输出：
1. 任务难度
2. 预估工时
3. 风险点
4. 建议执行步骤
5. 任务优先级
        """
        return openai.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}]
        ).choices[0].message.content


# ==============================================
# 2. 任务分配智能体
# ==============================================
class TaskAssignAgent:
    def run(self, task: Task):
        prompt = f"""
你是团队管理者，根据任务内容分配最优负责人：
任务：{task.title}
描述：{task.desc}
候选成员：张三、李四、王五、赵六
请给出最终分配理由与结果。
        """
        return openai.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}]
        ).choices[0].message.content


# ==============================================
# 3. 进度跟踪智能体
# ==============================================
class ProgressTrackAgent:
    def run(self, tasks: List[Task]):
        task_list = "\n".join([f"- {t.title} | {t.status.value}" for t in tasks])
        prompt = f"""
分析所有任务进度，生成详细进度报告：
{task_list}
请输出：整体进度、完成率、风险项、延期预测。
        """
        return openai.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}]
        ).choices[0].message.content


# ==============================================
# 4. 风险预警智能体
# ==============================================
class RiskWarnAgent:
    def run(self, tasks: List[Task]):
        prompt = f"""
检测以下任务是否存在延期风险、资源风险、协作风险：
{[t.to_dict() for t in tasks]}
输出详细风险分析。
        """
        return openai.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}]
        ).choices[0].message.content


# ==============================================
# 5. 提醒生成智能体
# ==============================================
class ReminderAgent:
    def run(self, task: Task):
        prompt = f"""
生成一条正式、专业的任务提醒，发给 {task.assignee}：
任务：{task.title}
截止时间：{task.deadline}
请生成提醒文案。
        """
        return openai.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}]
        ).choices[0].message.content


# ==============================================
# 6. 日报生成智能体
# ==============================================
class ReportAgent:
    def run(self, tasks: List[Task]):
        task_data = str([t.to_dict() for t in tasks])
        prompt = f"""
你是高级助理，根据以下任务生成一份完整、详细、正式的工作日报：
{task_data}
要求：结构清晰、内容详细、专业正式、可直接提交管理层。
        """
        return openai.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}]
        ).choices[0].message.content


# ==============================================
# 中央协调中枢 → 高吞吐调度
# ==============================================
class Orchestrator:
    def __init__(self):
        self.parser = TaskParserAgent()
        self.assigner = TaskAssignAgent()
        self.tracker = ProgressTrackAgent()
        self.risk = RiskWarnAgent()
        self.reminder = ReminderAgent()
        self.reporter = ReportAgent()
        self.tasks = []

    def add_task(self, task):
        self.tasks.append(task)

    def run_full_workflow(self):
        print("\n==== 全流程工作流启动 ====")
        for task in self.tasks:
            self.parser.run(task)
            self.assigner.run(task)
            self.reminder.run(task)

        self.tracker.run(self.tasks)
        self.risk.run(self.tasks)
        self.reporter.run(self.tasks)
        print(f"✅ 单次执行消耗 ≈ {TOKEN_PER_RUN} Token")


# ==============================================
# 模拟高吞吐运行 → 日耗 3,000,000 Token
# ==============================================
if __name__ == "__main__":
    system = Orchestrator()

    # 创建一批任务
    now = datetime.now()
    for i in range(1, 21):
        system.add_task(Task(
            f"T{i:03}",
            f"项目任务{i}",
            f"这是第{i}个需要处理的自动化任务",
            random.choice(["张三", "李四", "王五", "赵六"]),
            now + timedelta(hours=random.randint(1, 48))
        ))

    print(f"🎯 目标日消耗 Token：{DAILY_TOKEN_TARGET:,}")
    print(f"📊 每轮消耗：{TOKEN_PER_RUN:,} Token")
    print(f"⚡ 每日需运行轮次：{RUNS_PER_DAY}")
    print("\n开始高吞吐调度...\n")

    # 执行一次（演示用）
    system.run_full_workflow()

    # 如需真正跑满 300万 Token，打开下面循环
    # for _ in range(RUNS_PER_DAY):
    #     system.run_full_workflow()
    #     time.sleep(1)
