"""
Email Templates
===============
Professional HTML email templates for candidate notifications.
"""


def shortlisted_template(candidate_name: str, job_title: str, company: str = "") -> tuple[str, str]:
    """Generate shortlisted notification email."""
    subject = f"Congratulations! You've Been Shortlisted for {job_title}"
    body = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"></head>
    <body style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background: #f8fafc;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 12px 12px 0 0; text-align: center;">
            <h1 style="color: white; margin: 0; font-size: 24px;">🎉 Congratulations!</h1>
        </div>
        <div style="background: white; padding: 30px; border-radius: 0 0 12px 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            <p style="font-size: 16px; color: #334155;">Dear <strong>{candidate_name}</strong>,</p>
            <p style="font-size: 15px; color: #475569; line-height: 1.6;">
                We are pleased to inform you that after careful review of your application,
                you have been <strong style="color: #059669;">shortlisted</strong> for the position of
                <strong>{job_title}</strong>{f' at {company}' if company else ''}.
            </p>
            <div style="background: #f0fdf4; border-left: 4px solid #059669; padding: 15px; margin: 20px 0; border-radius: 0 8px 8px 0;">
                <p style="margin: 0; color: #166534; font-weight: 600;">Next Steps</p>
                <p style="margin: 5px 0 0; color: #15803d;">Our team will reach out to you shortly with further details about the interview process.</p>
            </div>
            <p style="font-size: 14px; color: #64748b;">Best regards,<br><strong>Recruitment Team</strong></p>
        </div>
    </body>
    </html>
    """
    return subject, body


def rejected_template(candidate_name: str, job_title: str, company: str = "") -> tuple[str, str]:
    """Generate rejection notification email."""
    subject = f"Application Update for {job_title}"
    body = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"></head>
    <body style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background: #f8fafc;">
        <div style="background: linear-gradient(135deg, #475569 0%, #334155 100%); padding: 30px; border-radius: 12px 12px 0 0; text-align: center;">
            <h1 style="color: white; margin: 0; font-size: 24px;">Application Update</h1>
        </div>
        <div style="background: white; padding: 30px; border-radius: 0 0 12px 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            <p style="font-size: 16px; color: #334155;">Dear <strong>{candidate_name}</strong>,</p>
            <p style="font-size: 15px; color: #475569; line-height: 1.6;">
                Thank you for your interest in the <strong>{job_title}</strong> position
                {f'at {company}' if company else ''} and for taking the time to apply.
            </p>
            <p style="font-size: 15px; color: #475569; line-height: 1.6;">
                After careful consideration, we have decided to move forward with other candidates
                whose qualifications more closely match our current needs.
            </p>
            <p style="font-size: 15px; color: #475569; line-height: 1.6;">
                We encourage you to apply for future openings that match your skills and experience.
            </p>
            <p style="font-size: 14px; color: #64748b;">Best regards,<br><strong>Recruitment Team</strong></p>
        </div>
    </body>
    </html>
    """
    return subject, body


def interview_scheduled_template(
    candidate_name: str,
    job_title: str,
    interview_date: str,
    interview_time: str,
    mode: str,
    meeting_link: str = "",
    company: str = "",
) -> tuple[str, str]:
    """Generate interview scheduled notification email."""
    subject = f"Interview Scheduled: {job_title}"
    meeting_info = ""
    if meeting_link:
        meeting_info = f"""
        <div style="background: #eff6ff; border-left: 4px solid #3b82f6; padding: 15px; margin: 10px 0; border-radius: 0 8px 8px 0;">
            <p style="margin: 0; color: #1e40af; font-weight: 600;">Meeting Link</p>
            <a href="{meeting_link}" style="color: #2563eb; text-decoration: none;">{meeting_link}</a>
        </div>
        """

    body = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"></head>
    <body style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background: #f8fafc;">
        <div style="background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); padding: 30px; border-radius: 12px 12px 0 0; text-align: center;">
            <h1 style="color: white; margin: 0; font-size: 24px;">📅 Interview Scheduled</h1>
        </div>
        <div style="background: white; padding: 30px; border-radius: 0 0 12px 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            <p style="font-size: 16px; color: #334155;">Dear <strong>{candidate_name}</strong>,</p>
            <p style="font-size: 15px; color: #475569; line-height: 1.6;">
                We are pleased to invite you for an interview for the
                <strong>{job_title}</strong> position{f' at {company}' if company else ''}.
            </p>
            <div style="background: #f1f5f9; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <table style="width: 100%; font-size: 15px; color: #334155;">
                    <tr><td style="padding: 8px 0;"><strong>📆 Date:</strong></td><td>{interview_date}</td></tr>
                    <tr><td style="padding: 8px 0;"><strong>⏰ Time:</strong></td><td>{interview_time}</td></tr>
                    <tr><td style="padding: 8px 0;"><strong>💻 Mode:</strong></td><td>{mode.title()}</td></tr>
                </table>
            </div>
            {meeting_info}
            <p style="font-size: 14px; color: #64748b;">Please confirm your availability by replying to this email.</p>
            <p style="font-size: 14px; color: #64748b;">Best regards,<br><strong>Recruitment Team</strong></p>
        </div>
    </body>
    </html>
    """
    return subject, body
