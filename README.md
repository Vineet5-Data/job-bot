# Automated German Data Science Job Tracker & Telegram Alert Bot

This is a serverless Python job alert agent hosted on GitHub Actions. It polls real-time German student roles (Werkstudent, Praktikum, Masterarbeit) across the official Bundesagentur für Arbeit Public API and LinkedIn/Indeed (via JobSpy guest scrapers) every 25 minutes, deduplicates postings, and delivers instant push notifications to a personal Telegram chat with direct application links.

## Prerequisites

- Telegram Bot Token
- Telegram Chat ID
- GitHub Account

## Setup

1. Add your repository secrets in GitHub: `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`.
2. The GitHub Actions workflow will automatically run every 25 minutes to fetch and send jobs.
