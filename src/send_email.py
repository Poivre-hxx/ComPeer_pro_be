import json
import os
from datetime import datetime
import schedule
import time
from llmail import Email
from extract_module import event_detector  # 导入EventDetector类

class SafetyMonitor:
    def __init__(self, email_sender, email_password, email_receiver, role_prompt,log_file):
        # 邮件配置
        self.email_sender = email_sender
        self.email_password = email_password
        self.email_receiver = email_receiver
        self.log_file = log_file
        
        # 创建EventDetector实例
        self.event_detector = event_detector(role_prompt)

    def send_email(self, subject, message):
        """发送紧急邮件通知"""
        # 初始化 Email 类
        email = Email(
            sender=self.email_sender,
            password=self.email_password,
            receiver=self.email_receiver,
            subject=subject,
            message=message,
        )
        
        # 发送邮件
        email.send()
        print(f"⚠️ 紧急邮件已发送至 {self.email_receiver}")

    def record_event(self, user_id, danger_type, res, extracted_event):
        """将事件记录到本地文件"""
        time_to = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"时间: {time_to}\n" \
                    f"用户 {user_id} 表现出以下需求：\n" \
                    f"需求类型: {danger_type}\n" \
                    f"内容: {res}\n\n" \
                    f"事件详情: {extracted_event}\n\n" \
                    "----------------------------------------\n"

        # 将事件记录到本地文件
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)
        
        print(f"事件已记录到本地文件：{self.log_file}")

    def handle_emergency(self, user_id, danger_type, res,extracted_event):
        time_to = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        subject = f"紧急通知：用户 {user_id} 存在 {danger_type} 危险情况"
        
        if danger_type in ["身体不适", "计划困难"]:
            # 紧急邮件内容
            message = f"时间: {time_to}\n\n" \
                      f"用户 {user_id} 表现出以下危险行为：\n" \
                      f"危机类型: {danger_type}\n" \
                      f"内容: {res}\n\n" \
                      f"我们将会采取以下措施：{extracted_event}"\
                      f"请您立即采取必要的处理措施。"
        else:
            subject = f"帮助通知：用户 {user_id} 需要帮助"
            message = f"时间: {time_to}\n\n" \
                      f"用户 {user_id} 表现出以下需求：\n" \
                      f"需求类型: {danger_type}\n" \
                      f"内容: {res}\n\n" \
                      f"我们将会采取以下措施：{extracted_event}"\
                      f"请您尽快联系并给予支持。"

        # 发送邮件
        self.send_email(subject, message)

    def extract_and_process_event(self, user_id, dialogue_content): 
        '''提取事件并处理'''  
        event_is_json, extracted_event = self.event_detector.extract_event(user_id, dialogue_content)
        
        # 判断是否有危险警告，如果有，根据严重程度启动处理办法
        dialog_type, user_id = self.dialog_pre_check(extracted_event['Content'], user_id)
        if dialog_type != "暂无":
            # 根据危险类型启动不同的处理办法
            if dialog_type == "身体不适" or dialog_type == "计划困难":
                # 发送紧急通知邮件
                self.handle_emergency(user_id, dialog_type, extracted_event)
            elif dialog_type == "需要帮助" or dialog_type == "心情不适":
                print("启动帮助方案！")
                self.handle_emergency(user_id, dialog_type, extracted_event)
            else:
                self.record_event(dialog_type,extracted_event)
                print("启动一般处理方案！")
        
        return event_is_json, extracted_event
    

    def schedule_daily_report(self):
        def send_daily_report():
            # 读取日志文件
            if os.path.exists(self.log_file):
                with open(self.log_file, "r", encoding="utf-8") as f:
                    report_content = f.read()
                
                if report_content:
                    subject = "每日事件报告"
                    message = f"以下是今天记录的所有事件：\n\n{report_content}"
                    self.send_email(subject, message)
                else:
                    print("没有新的记录。")
            else:
                print(f"{self.log_file} 文件不存在。")
        schedule.every().day.at("20:00").do(send_daily_report)

        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次


# # 配置邮件发送的发件人、密码和收件人
# email_sender = "your_email@example.com"
# email_password = "your_email_password"
# email_receiver = "receiver_email@example.com"
# role_prompt = "你是一个健康管理助手，帮助用户识别和管理他们的健康问题。"

# # 初始化SafetyMonitor
# safety_monitor = SafetyMonitor(email_sender, email_password, email_receiver, )