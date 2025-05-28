import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# === Page Configuration ===
st.set_page_config(layout="wide", page_title="AI Ad Agent", page_icon="🚀")

# === Groq Chat Function (from your code) ===
def groq_chat(prompt, api_key, model="deepseek-r1-distill-llama-70b"): # Changed model name
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful and creative marketing AI assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.6 # Slightly higher for more creative ad copy
    }
    try:
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data, timeout=30)
        response.raise_for_status() # Raise an exception for HTTP errors
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        st.error(f"API Request Error: {e}")
        return None
    except KeyError:
        st.error(f"Unexpected API response format: {response.text}")
        return None

# === Session State Initialization ===
if 'strategy_guide' not in st.session_state:
    st.session_state.strategy_guide = ""
if 'generated_ads' not in st.session_state:
    st.session_state.generated_ads = ""
if 'top_ads_df' not in st.session_state:
    st.session_state.top_ads_df = pd.DataFrame()

# === UI Layout ===
st.title("🚀 AI Agent for Competitive Ad Analysis & Creation")
st.markdown("Welcome! This tool helps analyze competitor ads and generate new ad creatives for Ventamin.")

# --- Sidebar for API Key and Data Upload ---
with st.sidebar:
    st.header("⚙️ Configuration")
    groq_api_key = st.text_input("Enter your Groq API Key:", type="password", help="Get your API key from console.groq.com")

    st.subheader("Competitor Data")
    uploaded_file = st.file_uploader("Upload Competitor Ad CSV", type="csv")
    st.caption(f"Default: `t1.csv` (IM8 data). Columns needed: `Ad_Copy`, `Start_Date` (YYYY-MM-DD).")

    if not groq_api_key:
        st.warning("Please enter your Groq API Key to proceed.")

# --- Main Content Tabs ---
tab1, tab2 = st.tabs(["📊 Competitor Ad Analysis", "✨ Ventamin Ad Generation"])

with tab1:
    st.header("📊 Step 1: Analyze Competitor Ads")

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.success(f"Successfully loaded `{uploaded_file.name}`")
        except Exception as e:
            st.error(f"Error loading CSV: {e}")
            df = None
    else:
        try:
            df = pd.read_csv("t1.csv") # Default
            st.info("Using default `t1.csv` for IM8.")
        except FileNotFoundError:
            st.warning("`t1.csv` not found. Please upload a competitor ad data file.")
            df = None
        except Exception as e:
            st.error(f"Error loading default CSV: {e}")
            df = None

    if df is not None:
        if 'Start_Date' not in df.columns or 'Ad_Copy' not in df.columns:
            st.error("CSV must contain 'Start_Date' and 'Ad_Copy' columns.")
        else:
            try:
                df['Start_Date'] = pd.to_datetime(df['Start_Date'])
                df['Active_Days'] = (pd.to_datetime(datetime.today().date()) - df['Start_Date']).dt.days
                top_ads = df.sort_values(by="Active_Days", ascending=False).head(5)
                st.session_state.top_ads_df = top_ads[['Ad_Copy', 'Start_Date', 'Active_Days']] # Store for display

                st.subheader("Top 5 Longest Running Competitor Ads:")
                st.dataframe(st.session_state.top_ads_df, use_container_width=True)

                if st.button("🔍 Analyze Top Ads with AI", disabled=not groq_api_key):
                    if not groq_api_key:
                        st.warning("Please enter your Groq API Key in the sidebar.")
                    else:
                        ad_texts = "\n\n".join([f"{i+1}. {row['Ad_Copy']}" for i, row in top_ads.iterrows()])
                        strategy_prompt = f"""
                        You are a senior marketing strategist. Analyze the following top-performing wellness ad copies from a competitor.

                        Top 5 Ad Copies:
                        {ad_texts}

                        Based on these, provide a concise strategy guide. Your analysis should identify:
                        1.  Common Hook Styles/Opening Techniques: (e.g., question, bold claim, pain point)
                        2.  Typical Ad Structure: (e.g., Hook → Problem → Solution/Benefit → Credibility → CTA)
                        3.  Predominant Tone of Voice: (e.g., urgent, empathetic, authoritative, friendly)
                        4.  Most Frequent Call-to-Actions (CTAs): (e.g., "Shop Now", "Learn More", "Try Today")
                        5.  Key Wellness Benefits Emphasized: (e.g., energy, gut health, mental clarity, sleep)
                        6.  Any unique selling propositions (USPs) or angles that seem effective.

                        Format your output clearly with headings for each point.
                        This guide will be used to help a new wellness brand, Ventamin, create competitive ads.
                        """
                        with st.spinner("🧠 AI is analyzing... this might take a moment."):
                            analysis_result = groq_chat(strategy_prompt, groq_api_key)
                        if analysis_result:
                            st.session_state.strategy_guide = analysis_result
                            st.subheader("📈 AI-Generated Strategy Guide:")
                            st.markdown(st.session_state.strategy_guide)
                            st.success("Analysis complete! Go to the 'Ventamin Ad Generation' tab.")
                        else:
                            st.error("Failed to get analysis from AI.")
            except Exception as e:
                st.error(f"Error processing data: {e}")
                st.error("Please ensure 'Start_Date' is in a recognizable date format (e.g., YYYY-MM-DD).")

    if st.session_state.strategy_guide: # Display if already generated
        with st.expander("Previously Generated Strategy Guide", expanded=False):
            st.markdown(st.session_state.strategy_guide)


with tab2:
    st.header("✨ Step 2: Generate Ad Creatives for Ventamin")

    if not st.session_state.strategy_guide:
        st.info("⬅️ Please analyze competitor ads in the first tab to generate a strategy guide.")
    else:
        st.subheader("Current Strategy Guide (from Analysis):")
        st.markdown(st.session_state.strategy_guide)
        st.markdown("---")

        brand_name = st.text_input("Your Brand Name:", value="Ventamin")

        if st.button(f"💡 Generate Ads for {brand_name}", disabled=not groq_api_key or not st.session_state.strategy_guide):
            if not groq_api_key:
                st.warning("Please enter your Groq API Key in the sidebar.")
            else:
                ad_prompt = f"""
                    You are a creative advertising copywriter and visual director for {brand_name}, a modern wellness supplement brand.
                    Your task is to generate three distinct ad types based on the following competitor-derived strategy.
                    Make the ads compelling, authentic, and aligned with the {brand_name} brand.

                    Strategy to Emulate/Adapt:
                    --- STRATEGY START ---
                    {st.session_state.strategy_guide}
                    --- STRATEGY END ---

                    Product Core Message:
                    Discover the secret to glowing skin with Ventamin — your ultimate oral skincare solution. Our expert-curated products harness potent ingredients backed by science for real results. Clinically proven and rigorously tested, Ventamin offers clean, natural solutions for your health goals — especially tackling acne from within.

                    Now, create the following for {brand_name}:

                    1.  **Static Image Ad:**
                        *   **Headline:** (Compelling and short)
                        *   **Body Text/Subheadline:** (Elaborate slightly on the benefit or USP)
                        *   **Call to Action (CTA):** (Clear and direct)
                        *   **Visual Description:** (Describe the ideal image. Think about mood, subject, colors. Consider if it should feature product, lifestyle, or benefit representation.)

                    2.  **Faceless User-Generated Content (UGC) Style Video Ad:**
                        *   **Video Concept/Hook:** (e.g., "My morning routine changed when I found this...")
                        *   **Voice-Over Script (15-30 seconds):** (Casual, relatable, benefit-focused. Could be a 'day in the life' snippet, product unboxing/use, or quick tip format.)
                        *   **Key Visuals to Show (B-Roll Ideas):** (e.g., hands preparing the supplement, close-up of product, person feeling energetic doing a simple activity – without showing face clearly.)
                        *   **On-screen Text (Optional):** (e.g., key benefit, discount code)
                        *   **CTA (Spoken or Text Overlay):**

                    3.  **Face-Featuring User-Generated Content (UGC) Style Video Ad:**
                        *   **Video Concept/Hook:** (e.g., "Okay, I have to tell you about this...")
                        *   **Selfie-Style Testimonial Script (up to 45 seconds):** (Authentic, personal story. Focus on a specific problem {brand_name} solved or a benefit experienced. Show genuine emotion. Introduce yourself briefly if natural.)
                        *   **Setting/Background:** (e.g., natural home environment, outdoors, gym)
                        *   **Key Visuals:** (Primarily the person talking to the camera, maybe a quick shot of the product if they show it.)
                        *   **CTA (Spoken):** (Encourage viewers to try or learn more.)

                    Provide each ad type clearly separated.
                    """
                with st.spinner(f"🎨 AI is crafting ads for {brand_name}... this can take a minute."):
                    ads_result = groq_chat(ad_prompt, groq_api_key)
                if ads_result:
                    st.session_state.generated_ads = ads_result
                    st.subheader(f"🎉 Generated Ad Creatives for {brand_name}:")
                    st.markdown(st.session_state.generated_ads)
                else:
                    st.error("Failed to generate ads from AI.")

    

# --- Footer ---
st.markdown("---")
st.caption("AI Intern Assignment Demo | Built with Streamlit & Groq")