import os
import json
import logging
import asyncio
import traceback
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

from src.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, MASTER_PROFILE_PATH
from src.llm_engine import generate_tailored_content
from src.compiler import compile_pdfs

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if TELEGRAM_CHAT_ID and user_id != TELEGRAM_CHAT_ID:
        logger.warning(f"Unauthorized access attempt from user {user_id}")
        return
        
    job_description = update.message.text
    if not job_description or len(job_description) < 80:
        await update.message.reply_text("❌ Please paste a valid Job Description (at least 80 characters).")
        return
        
    status_msg = await update.message.reply_text("⏳ Analyzing Job Description with LLM...")
    
    try:
        # Load master profile
        with open(MASTER_PROFILE_PATH, "r", encoding="utf-8") as f:
            master_profile = json.load(f)
            
        # Generate content
        tailored_data = generate_tailored_content(job_description, master_profile)
        
        await status_msg.edit_text(f"⚙️ Compiling PDFs for {tailored_data.get('company_name', 'Company')}...")

        cv_path, cl_path = compile_pdfs(tailored_data)
        
        await status_msg.edit_text("✅ Compilation successful! Uploading documents...")
        
        # Upload
        with open(cv_path, "rb") as cv_f:
            await update.message.reply_document(
                document=cv_f,
                caption=f"📄 CV for {tailored_data.get('company_name', 'Company')}\nRole: {tailored_data.get('job_title', 'Role')}\nLanguage: {tailored_data.get('detected_language', 'unknown')}"
            )
            
        with open(cl_path, "rb") as cl_f:
            await update.message.reply_document(
                document=cl_f,
                caption=f"📝 Cover Letter for {tailored_data.get('company_name', 'Company')}"
            )
            
        await status_msg.delete()
        
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        logger.error(traceback.format_exc())
        await status_msg.edit_text(f"❌ An error occurred:\n{str(e)}")

def main():
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN is not set.")
        return
        
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("Bot is starting...")
    app.run_polling()

if __name__ == "__main__":
    main()
