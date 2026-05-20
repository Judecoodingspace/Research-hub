# -*- coding: utf-8 -*-
"""
定时任务配置脚本
自动创建 Windows Task Scheduler 任务，实现每日自动运行 arXiv 订阅工作流

使用方式（以管理员身份运行 PowerShell）：
    python setup_scheduler.py --install      # 安装每日定时任务
    python setup_scheduler.py --uninstall    # 卸载定时任务
    python setup_scheduler.py --status       # 查看任务状态
    python setup_scheduler.py --run-now      # 立即运行一次
"""

import sys
import os
import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
WORKFLOW_SCRIPT = Path(__file__).parent / "daily_workflow.py"
PYTHON_EXE = sys.executable
TASK_NAME = "ArxivSubscriberDaily"

# 定时任务 XML 模板
TASK_XML_TEMPLATE = '''<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Date>{date}</Date>
    <Author>ResearchHub</Author>
    <Description>arXiv 领域订阅：每日自动拉取最新论文并生成 papercard 简报</Description>
    <URI>\{task_name}</URI>
  </RegistrationInfo>
  <Triggers>
    <CalendarTrigger>
      <StartBoundary>{start_time}</StartBoundary>
      <Repetition>
        <Interval>PT24H</Interval>
        <StopAtDurationEnd>false</StopAtDurationEnd>
      </Repetition>
      <Enabled>true</Enabled>
      <ScheduleByDay>
        <DaysInterval>1</DaysInterval>
      </ScheduleByDay>
    </CalendarTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>{username}</UserId>
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>true</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>false</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <DisallowStartOnRemoteAppSession>false</DisallowStartOnRemoteAppSession>
    <UseUnifiedSchedulingEngine>true</UseUnifiedSchedulingEngine>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT1H</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>{python_path}</Command>
      <Arguments>"{workflow_path}" --min-relevance medium</Arguments>
      <WorkingDirectory>{working_dir}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>'''

def get_task_xml(start_hour: int = 8, start_minute: int = 0) -> str:
    """生成 Windows Task Scheduler XML"""
    import getpass
    from datetime import datetime, timedelta
    
    # 明天早上 8:00 (如果当前时间已过，则设置为明天)
    now = datetime.now()
    start_time = now.replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)
    if start_time <= now:
        start_time += timedelta(days=1)
    
    return TASK_XML_TEMPLATE.format(
        date=now.strftime("%Y-%m-%dT%H:%M:%S"),
        task_name=TASK_NAME,
        start_time=start_time.strftime("%Y-%m-%dT%H:%M:%S"),
        username=getpass.getuser(),
        python_path=PYTHON_EXE,
        workflow_path=str(WORKFLOW_SCRIPT),
        working_dir=str(WORKFLOW_SCRIPT.parent),
    )

def install_task(start_hour: int = 8):
    """安装定时任务"""
    import subprocess
    import tempfile
    
    print(f"📋 安装定时任务: {TASK_NAME}")
    print(f"   Python: {PYTHON_EXE}")
    print(f"   脚本: {WORKFLOW_SCRIPT}")
    print(f"   时间: 每日 {start_hour}:00")
    
    # 生成 XML 文件
    xml_content = get_task_xml(start_hour)
    xml_path = Path(tempfile.gettempdir()) / f"{TASK_NAME}.xml"
    with open(xml_path, "w", encoding="utf-8") as f:
        f.write(xml_content)
    
    # 创建计划任务
    cmd = f'schtasks /create /tn "{TASK_NAME}" /xml "{xml_path}" /f'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ 定时任务安装成功！")
        print(f"   任务名称: {TASK_NAME}")
        print(f"   执行频率: 每日 {start_hour}:00")
        print(f"   查看任务: schtasks /query /tn \"{TASK_NAME}\"")
    else:
        print(f"❌ 安装失败: {result.stderr}")
        print(f"   请以管理员身份运行 PowerShell 后重试")
    
    # 清理临时文件
    xml_path.unlink(missing_ok=True)

def uninstall_task():
    """卸载定时任务"""
    import subprocess
    
    print(f"🗑️ 卸载定时任务: {TASK_NAME}")
    cmd = f'schtasks /delete /tn "{TASK_NAME}" /f'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ 定时任务已卸载")
    else:
        print(f"⚠️ 卸载失败或任务不存在: {result.stderr}")

def check_status():
    """查看任务状态"""
    import subprocess
    
    cmd = f'schtasks /query /tn "{TASK_NAME}" /fo LIST /v'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"📊 定时任务状态:\n")
        # 提取关键信息
        for line in result.stdout.split("\n"):
            line = line.strip()
            if any(kw in line.lower() for kw in ["taskname", "status", "triggers", "next run", "last run"]):
                print(f"   {line}")
    else:
        print(f"⚠️ 任务不存在: {TASK_NAME}")
        print(f"   使用 --install 安装定时任务")

def run_now():
    """立即运行一次工作流"""
    import subprocess
    
    print(f"▶️ 立即运行工作流...")
    cmd = [PYTHON_EXE, str(WORKFLOW_SCRIPT), "--min-relevance", "medium"]
    result = subprocess.run(cmd, cwd=str(WORKFLOW_SCRIPT.parent))
    
    if result.returncode == 0:
        print(f"✅ 运行完成")
    else:
        print(f"⚠️ 运行异常，返回码: {result.returncode}")

def main():
    parser = argparse.ArgumentParser(description="arXiv 订阅定时任务管理")
    parser.add_argument("--install", action="store_true", help="安装每日定时任务")
    parser.add_argument("--uninstall", action="store_true", help="卸载定时任务")
    parser.add_argument("--status", action="store_true", help="查看任务状态")
    parser.add_argument("--run-now", action="store_true", help="立即运行一次")
    parser.add_argument("--hour", type=int, default=8, help="每日运行时间（小时，0-23，默认 8:00）")
    
    args = parser.parse_args()
    
    if args.install:
        install_task(start_hour=args.hour)
    elif args.uninstall:
        uninstall_task()
    elif args.status:
        check_status()
    elif args.run_now:
        run_now()
    else:
        parser.print_help()
        print("\n💡 推荐用法：")
        print("   python setup_scheduler.py --install    # 安装每日 8:00 自动运行")
        print("   python setup_scheduler.py --run-now    # 立即运行一次测试")

if __name__ == "__main__":
    main()
