# AI Ad Analysis & Creation Tool

A Streamlit application that analyzes competitor ads and generates new ad creatives using AI.

## Documentation

- View the project presentation slides [here](https://www.canva.com/design/DAGopXlTBA8/YvarWN20f0-43QcH7S1fsQ/view?utm_content=DAGopXlTBA8&utm_campaign=designshare&utm_medium=link2&utm_source=uniquelinks&utlId=h174af92f66)

## Setup

1. Install Python 3.8 or higher
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the App

1. Get your API key from [Groq Console](https://console.groq.com)
2. Run the app:
```bash
streamlit run main.py
```

## Features

- 📊 Analyze competitor ads from CSV files
- 🎯 Generate AI-powered ad strategies
- ✨ Create new ad creatives for your brand
- 📱 Support for static and video ad formats

## Data Format

Your CSV file should include:
- `Ad_Copy`: The text content of the ad
- `Start_Date`: Date in YYYY-MM-DD format

## Note

Make sure to keep your Groq API key secure and never share it publicly. 
