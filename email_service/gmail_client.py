import os
import base64
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from datetime import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import markdown2

from utils.logger import setup_logger
from config import config

logger = setup_logger(__name__)

class GmailClient:
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']
    OAUTH_PORT = 8090  # Static port for OAuth redirect
    
    def __init__(self):
        self.credentials_path = config.GMAIL_CREDENTIALS_PATH
        self.token_path = config.GMAIL_TOKEN_PATH
        self.sender_email = config.SENDER_EMAIL
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Gmail API"""
        creds = None
        
        # Load existing token
        if os.path.exists(self.token_path):
            try:
                creds = Credentials.from_authorized_user_file(self.token_path, self.SCOPES)
            except Exception as e:
                logger.error(f"Error loading existing token: {str(e)}")
        
        # If there are no (valid) credentials available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    logger.error(f"Error refreshing token: {str(e)}")
                    creds = None
            
            if not creds:
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(
                        f"Gmail credentials file not found at {self.credentials_path}. "
                        "Please download it from Google Cloud Console."
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.SCOPES
                )
                creds = flow.run_local_server(port=self.OAUTH_PORT)
            
            # Save the credentials for the next run
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())
        
        try:
            self.service = build('gmail', 'v1', credentials=creds)
            logger.info("Gmail API authentication successful")
        except Exception as e:
            logger.error(f"Error building Gmail service: {str(e)}")
            raise
    
    def create_message(
        self, 
        to_emails: List[str], 
        subject: str, 
        body_html: str,
        body_text: Optional[str] = None
    ) -> dict:
        """Create a message for an email"""
        
        message = MIMEMultipart('alternative')
        message['to'] = ', '.join(to_emails)
        message['from'] = self.sender_email
        message['subject'] = subject
        
        # Add text version if provided
        if body_text:
            text_part = MIMEText(body_text, 'plain')
            message.attach(text_part)
        
        # Add HTML version
        html_part = MIMEText(body_html, 'html')
        message.attach(html_part)
        
        # Encode the message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        return {'raw': raw_message}
    
    def send_email(
        self, 
        to_emails: List[str], 
        subject: str, 
        body_html: str,
        body_text: Optional[str] = None
    ) -> bool:
        """Send an email using Gmail API"""
        
        if not self.service:
            logger.error("Gmail service not initialized")
            return False
        
        try:
            message = self.create_message(to_emails, subject, body_html, body_text)
            
            result = self.service.users().messages().send(
                userId="me", 
                body=message
            ).execute()
            
            logger.info(f"Email sent successfully. Message ID: {result['id']}")
            logger.info(f"Recipients: {', '.join(to_emails)}")
            return True
            
        except HttpError as error:
            logger.error(f"Gmail API error: {error}")
            return False
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return False
    
    def format_newsletter_html(self, newsletter_content: str, subject: str) -> str:
        """Format newsletter content as beautiful HTML email"""
        logger.info(f"Formatting newsletter content length: {len(newsletter_content)}")
        if newsletter_content:
            logger.info(f"Content preview: {newsletter_content[:200]}...")
        
        if not newsletter_content.strip():
            html_content = "<p>No content available</p>"
        else:
            html_content = markdown2.markdown(newsletter_content, extras=["tables", "fenced-code-blocks", "break-on-newline"])
        
        logger.info(f"HTML content length after markdown conversion: {len(html_content)}")
        if html_content:
            logger.info(f"HTML preview: {html_content[:200]}...")
        
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{subject}</title>
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; }}
                .container {{ max-width: 650px; margin: 0 auto; background: #ffffff; border-radius: 20px; overflow: hidden; box-shadow: 0 20px 40px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px 30px; text-align: center; }}
                .header h1 {{ font-size: 28px; font-weight: 700; margin-bottom: 10px; text-shadow: 0 2px 4px rgba(0,0,0,0.3); }}
                .header .date {{ font-size: 16px; opacity: 0.9; font-weight: 300; }}
                .content {{ padding: 40px 30px; }}
                .content h2 {{ color: #2c3e50; font-size: 24px; margin: 30px 0 15px 0; padding-bottom: 10px; border-bottom: 3px solid #667eea; display: inline-block; }}
                .content h3 {{ color: #34495e; font-size: 20px; margin: 25px 0 10px 0; }}
                .content p {{ color: #555; line-height: 1.8; margin-bottom: 15px; font-size: 16px; }}
                .content ul {{ margin: 15px 0; padding-left: 20px; }}
                .content li {{ color: #555; line-height: 1.7; margin-bottom: 8px; }}
                .highlight {{ background: linear-gradient(120deg, #a8edea 0%, #fed6e3 100%); padding: 20px; border-radius: 15px; margin: 20px 0; border-left: 5px solid #667eea; }}
                .article-card {{ background: #f8f9fa; padding: 20px; border-radius: 12px; margin: 15px 0; border-left: 4px solid #667eea; transition: transform 0.2s; }}
                .article-card:hover {{ transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
                .footer {{ background: #2c3e50; color: white; padding: 30px; text-align: center; }}
                .footer p {{ margin-bottom: 10px; opacity: 0.8; }}
                .social-links {{ margin-top: 20px; }}
                .social-links a {{ color: #667eea; text-decoration: none; margin: 0 10px; font-weight: 500; }}
                a {{ color: #667eea; text-decoration: none; font-weight: 500; }}
                a:hover {{ text-decoration: underline; }}
                .emoji {{ font-size: 1.2em; }}
                @media (max-width: 600px) {{
                    .container {{ margin: 10px; border-radius: 15px; }}
                    .header, .content {{ padding: 25px 20px; }}
                    .header h1 {{ font-size: 24px; }}
                    .content h2 {{ font-size: 20px; }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1><span class="emoji">🤖</span> {config.NEWSLETTER_TITLE} <span class="emoji">📧</span></h1>
                    <div class="date">📅 {datetime.now().strftime('%B %d, %Y')}</div>
                </div>
                
                <div class="content">
                    {html_content}
                </div>
                
                <div class="footer">
                    <p><span class="emoji">🚀</span> Powered by AI • Generated with ❤️</p>
                    <p>This newsletter was automatically generated by our AI agent</p>
                    <div class="social-links">
                        <a href="#">📧 Reply</a> • <a href="#">🔗 Share</a> • <a href="#">⚙️ Settings</a>
                    </div>
                    <p style="font-size: 12px; margin-top: 15px; opacity: 0.6;">
                        Generated on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_template
    
    def send_newsletter(self, newsletter_content: str, subject: str) -> bool:
        """Send the newsletter to all configured recipients"""
        
        if not config.RECIPIENT_EMAILS or not config.RECIPIENT_EMAILS[0]:
            logger.error("No recipient emails configured")
            return False
        
        # Format as HTML
        html_content = self.format_newsletter_html(newsletter_content, subject)
        
        # Create plain text version (simplified)
        text_content = newsletter_content.replace('**', '').replace('#', '')
        
        # Send email
        success = self.send_email(
            to_emails=config.RECIPIENT_EMAILS,
            subject=subject,
            body_html=html_content,
            body_text=text_content
        )
        
        if success:
            logger.info(f"Newsletter sent successfully to {len(config.RECIPIENT_EMAILS)} recipients")
        else:
            logger.error("Failed to send newsletter")
        
        return success