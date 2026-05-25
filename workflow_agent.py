from datetime import datetime, timedelta
from enum import Enum
from typing import List, Dict, Optional

# 任务状态枚举
class TaskStatus(Enum):
    PENDING = "待处理"
    IN_PROGRESS = "进行中"
    COMPLETED = "已完成"
    OVERDUE = "已逾期"

# 任务数据结构
class Task:
    def __init__(self, task_id: str, title: str, description: str, 
                 assignee: str, deadline: datetime, status=TaskStatus.PENDING):
        self.task_id = task_id
        self.title = title
        self.description = description
        self.assignee = assignee
        self.deadline = deadline
        self.status = status

    def __repr__(self):
        return f"【{self.status.value}】{self.title} | 负责人：{self.assignee} | 截止：{self.deadline.strftime('%m-%d %H:%M')}"

# ====================== 1. 任务分配Agent ======================
class TaskAssignerAgent:
    def __init__(self):
        self.name = "任务分配Agent"

    def assign_task(self, task: Task) -> str:
        """自动分配任务并确认负责人"""
        return f"✅ {self.name}：任务【{task.title}】已分配给【{task.assignee}】"

# ====================== 2. 进度跟踪Agent ======================
class ProgressTrackerAgent:
    def __init__(self):
        self.name = "进度跟踪Agent"

    def check_progress(self, tasks: List[Task]) -> List[Task]:
        """自动检查任务状态，标记逾期任务"""
        now = datetime.now()
        for task in tasks:
            if task.status == TaskStatus.PENDING and task.deadline < now:
                task.status = TaskStatus.OVERDUE
        return tasks

    def get_summary(self, tasks: List[Task]) -> str:
        """统计任务完成率"""
        total = len(tasks)
        completed = len([t for t in tasks if t.status == TaskStatus.COMPLETED])
        rate = (completed / total * 100) if total > 0 else 0
        return f"📊 {self.name}：总任务{total}项，已完成{completed}项，完成率{rate:.1f}%"

# ====================== 3. 提醒Agent ======================
class ReminderAgent:
    def __init__(self):
        self.name = "智能提醒Agent"

    def generate_reminders(self, tasks: List[Task]) -> List[str]:
        """生成待办/逾期提醒"""
        reminders = []
        now = datetime.now()
        soon = now + timedelta(hours=6)

        for task in tasks:
            if task.status == TaskStatus.PENDING and task.deadline < soon:
                reminders.append(f"🔔 即将截止：{task.title}（{task.assignee}）")
            elif task.status == TaskStatus.OVERDUE:
                reminders.append(f"⚠️ 已逾期：{task.title}（{task.assignee}）")
        return reminders

# ====================== 4. 总结汇报Agent ======================
class ReportAgent:
    def __init__(self):
        self.name = "总结汇报Agent"

    def generate_daily_report(self, tasks: List[Task]) -> str:
        """自动生成工作日报"""
        completed = [t for t in tasks if t.status == TaskStatus.COMPLETED]
        pending = [t for t in tasks if t.status == TaskStatus.PENDING]
        overdue = [t for t in tasks if t.status == TaskStatus.OVERDUE]

        report = "\n".join([
            "=" * 50,
            "📅 每日工作汇报",
            f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "=" * 50,
            f"✅ 已完成：{len(completed)}项",
            "\n".join([f"- {t.title}" for t in completed]) if completed else "无",
            f"\n⏳ 待处理：{len(pending)}项",
            "\n".join([f"- {t.title}" for t in pending]) if pending else "无",
            f"\n❌ 已逾期：{len(overdue)}项",
            "\n".join([f"- {t.title}" for t in overdue]) if overdue else "无",
            "=" * 50
        ])
        return report

# ====================== 5. 协调中枢Agent ======================
class CoordinatorAgent:
    def __init__(self):
        self.name = "中央协调Agent"
        self.assigner = TaskAssignerAgent()
        self.tracker = ProgressTrackerAgent()
        self.reminder = ReminderAgent()
        self.reporter = ReportAgent()
        self.tasks: List[Task] = []

    def add_task(self, task: Task):
        """添加任务并自动分配"""
        self.tasks.append(task)
        print(self.assigner.assign_task(task))

    def run_workflow(self):
        """执行完整工作流：跟踪→提醒→总结"""
        print(f"\n===== {self.name} 启动工作流程 =====")
        
        # 1. 跟踪进度
        self.tasks = self.tracker.check_progress(self.tasks)
        print(self.tracker.get_summary(self.tasks))
        
        # 2. 生成提醒
        reminders = self.reminder.generate_reminders(self.tasks)
        if reminders:
            print("\n📩 任务提醒：")
            for r in reminders:
                print(r)
        else:
            print("\n📩 暂无任务提醒")
        
        # 3. 生成日报
        report = self.reporter.generate_daily_report(self.tasks)
        print("\n📄 自动生成工作汇报：")
        print(report)

# ====================== 测试运行 ======================
if __name__ == "__main__":
    # 创建中央协调器
    coordinator = CoordinatorAgent()

    # 当前时间
    now = datetime.now()

    # 创建测试任务
    task1 = Task(
        task_id="T001",
        title="完成项目需求文档",
        description="整理功能需求并输出文档",
        assignee="张三",
        deadline=now - timedelta(hours=1)  # 已逾期
    )

    task2 = Task(
        task_id="T002",
        title="代码审查",
        description="检查组员代码规范",
        assignee="李四",
        deadline=now + timedelta(hours=3)  # 即将截止
    )

    task3 = Task(
        task_id="T003",
        title="周报撰写",
        description="编写本周工作总结",
        assignee="王五",
        deadline=now + timedelta(days=1),
        status=TaskStatus.COMPLETED
    )

    # 添加任务
    coordinator.add_task(task1)
    coordinator.add_task(task2)
    coordinator.add_task(task3)

    # 运行多Agent协同工作流
    coordinator.run_workflow()
