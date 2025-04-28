import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter
from datetime import datetime, timedelta
import altair as alt
import keepa
import requests
from bs4 import BeautifulSoup
import re
import time
from utils import extract_asin, get_amazon_product_info, search_walmart, girl_math_logic

# Page configuration
st.set_page_config(
    page_title="Girl Math Deal Finder",
    page_icon="💸",
    layout="wide",
)

# Custom CSS for pink theme and girly fonts
st.markdown("""
<style>
    /* Pink theme */
    .main {
        background-color: #fff0f5;
    }
    
    /* Headers */
    h1, h2, h3 {
        font-family: 'Pacifico', cursive;
        color: #FF69B4;
    }
    
    /* General text */
    p, div, label, span {
        font-family: 'Quicksand', sans-serif;
        color: #FF1493;
    }
    
    /* Streamlit widgets customization */
    .stButton button {
        background-color: #FF69B4;
        color: white;
        border-radius: 20px;
        border: none;
        font-family: 'Quicksand', sans-serif;
    }
    
    .stTextInput input {
        border-radius: 20px;
        border: 2px solid #FF69B4;
    }
    
    /* Card-like containers */
    .css-1r6slb0, .css-12oz5g7 {
        background-color: white;
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0px 4px 12px rgba(255, 105, 180, 0.2);
    }
    
    /* Success messages */
    .element-container .stAlert {
        background-color: #FFD1DC;
        border: 1px solid #FF69B4;
        border-radius: 20px;
    }

    /* Metrics */
    .stMetric {
        background-color: #FFD1DC;
        border-radius: 15px;
        padding: 10px;
        box-shadow: 0px 4px 8px rgba(255, 105, 180, 0.1);
    }

    /* Custom chart container */
    .chart-container {
        background-color: white;
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0px 4px 12px rgba(255, 105, 180, 0.2);
    }
    
    /* Footer */
    .footer {
        font-size: 12px;
        text-align: center;
        margin-top: 30px;
        color: #FF69B4;
    }
</style>

<!-- Import girly fonts -->
<link href="https://fonts.googleapis.com/css2?family=Pacifico&family=Quicksand:wght@400;700&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# App Header
st.title("✨ Girl Math Deal Finder 💅")
st.markdown("### Find the best deals and justify your shopping with Girl Math! 💸💖")
st.markdown("---")

# Sidebar with explanation
with st.sidebar:
    st.markdown("## 💁‍♀️ What is Girl Math?")
    st.markdown("""
    Girl Math is a fun way to justify purchases by using creative 
    calculations that make spending feel like saving!
    
    **Examples:**
    - If it's on sale, you're *saving* money
    - If you use it more than once, divide the cost by uses
    - If it's under $5, it's basically free
    - If you return something, that's free money to spend
    """)
    
    st.markdown("---")
    st.markdown("## 💎 How to use")
    st.markdown("""
    1. Paste an Amazon product URL
    2. Wait for the price analysis
    3. See the Girl Math savings!
    4. Compare with Walmart prices
    5. Make a justified purchase 💕
    """)
    
    # API Key input in sidebar
    st.markdown("---")
    st.markdown("## ⚙️ Settings")
    keepa_api_key = st.text_input("Keepa API Key", type="password", value=st.secrets.get("KEEPA_API_KEY", ""))
    if not keepa_api_key:
        st.warning("Please enter your Keepa API Key to access price history")

# Main content
col1, col2 = st.columns([3, 1])

with col1:
    amazon_url = st.text_input("Paste an Amazon Product Link:", placeholder="https://www.amazon.com/dp/...")

# Initialize session state for tracking past searches
if 'search_history' not in st.session_state:
    st.session_state.search_history = []

# Process the URL
if amazon_url:
    asin = extract_asin(amazon_url)
    
    if asin:
        with st.spinner("💖 Applying Girl Math magic to find you a deal..."):
            try:
                # Create Keepa API instance
                if not keepa_api_key:
                    st.error("Please enter your Keepa API Key in the sidebar to continue")
                    st.stop()
                
                api = keepa.Keepa(keepa_api_key)
                
                # Get product details
                product_info = get_amazon_product_info(api, asin)
                
                if not product_info:
                    st.error("Couldn't retrieve product information. Please check the URL or try again later.")
                    st.stop()
                
                product_title = product_info['title']
                
                # Display product info
                st.markdown(f"## {product_title}")
                
                # Extract relevant price data
                price_data = product_info['price_data']
                current_price = product_info['current_price']
                peak_price = product_info['peak_price']
                lowest_price = product_info['lowest_price']
                
                # Create price history chart
                st.markdown("### 📈 Price History")
                
                # Prepare data for chart
                chart_data = pd.DataFrame({
                    'date': [datetime.now() - timedelta(hours=len(price_data) - i) for i in range(len(price_data))],
                    'price': price_data
                })
                
                # Remove null values
                chart_data = chart_data[chart_data['price'] > 0]
                
                # Create Altair chart with pink theme
                chart = alt.Chart(chart_data).mark_line(
                    color='#FF69B4',
                    point=alt.OverlayMarkDef(color="#FF1493")
                ).encode(
                    x=alt.X('date:T', title='Date'),
                    y=alt.Y('price:Q', title='Price ($)', scale=alt.Scale(zero=False)),
                    tooltip=['date:T', 'price:Q']
                ).properties(
                    height=300
                ).interactive()
                
                st.altair_chart(chart, use_container_width=True)
                
                # Display price metrics
                st.markdown("### 💰 Price Analysis")
                
                col_current, col_peak, col_lowest = st.columns(3)
                with col_current:
                    st.metric("Current Price", f"${current_price:.2f}")
                with col_peak:
                    st.metric("Peak Price", f"${peak_price:.2f}", delta=f"-{peak_price - current_price:.2f}")
                with col_lowest:
                    delta = lowest_price - current_price
                    delta_text = f"{delta:.2f}" if delta < 0 else f"+{delta:.2f}"
                    st.metric("Lowest Price", f"${lowest_price:.2f}", delta=delta_text)
                
                # Girl Math calculation
                savings, percent = girl_math_logic(current_price, peak_price, lowest_price)
                
                # Display Girl Math results
                st.markdown("### ✨ Girl Math Results")
                
                # Create a styled box for the Girl Math results
                st.markdown(f"""
                <div style="background-color: #FFD1DC; padding: 20px; border-radius: 15px; margin: 10px 0; text-align: center; box-shadow: 0px 4px 12px rgba(255, 105, 180, 0.2);">
                    <h3 style="font-family: 'Pacifico', cursive; color: #FF1493; margin-bottom: 15px;">By Girl Math Logic...</h3>
                    <p style="font-family: 'Quicksand', sans-serif; font-size: 18px; color: #FF1493;">
                        You're <b>saving ${savings:.2f}</b> ({percent:.1f}% off peak price)!
                    </p>
                    <p style="font-family: 'Quicksand', sans-serif; font-size: 16px; color: #FF1493; margin-top: 10px;">
                        {girl_math_statement(current_price, peak_price, lowest_price)}
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # Check Walmart price
                st.markdown("### 🛒 Compare with Walmart")
                
                with st.spinner("Checking Walmart prices..."):
                    walmart_price_str = search_walmart(product_title)
                    
                    if walmart_price_str:
                        try:
                            # Extract numeric price from string
                            walmart_price_match = re.search(r'(\d+\.\d+)', walmart_price_str)
                            if walmart_price_match:
                                walmart_price = float(walmart_price_match.group(1))
                                
                                # Compare prices
                                price_diff = current_price - walmart_price
                                
                                if price_diff > 0:
                                    st.markdown(f"""
                                    <div style="background-color: #FFD1DC; padding: 15px; border-radius: 15px; margin: 10px 0;">
                                        <p style="font-family: 'Quicksand', sans-serif; color: #FF1493;">
                                            Walmart price: <b>${walmart_price:.2f}</b> (You'd save <b>${price_diff:.2f}</b> shopping at Walmart!)
                                        </p>
                                    </div>
                                    """, unsafe_allow_html=True)
                                elif price_diff < 0:
                                    st.markdown(f"""
                                    <div style="background-color: #FFD1DC; padding: 15px; border-radius: 15px; margin: 10px 0;">
                                        <p style="font-family: 'Quicksand', sans-serif; color: #FF1493;">
                                            Walmart price: <b>${walmart_price:.2f}</b> (Amazon is <b>${abs(price_diff):.2f}</b> cheaper!)
                                        </p>
                                    </div>
                                    """, unsafe_allow_html=True)
                                else:
                                    st.markdown(f"""
                                    <div style="background-color: #FFD1DC; padding: 15px; border-radius: 15px; margin: 10px 0;">
                                        <p style="font-family: 'Quicksand', sans-serif; color: #FF1493;">
                                            Walmart price: <b>${walmart_price:.2f}</b> (Same as Amazon!)
                                        </p>
                                    </div>
                                    """, unsafe_allow_html=True)
                            else:
                                st.markdown(f"""
                                <div style="background-color: #FFD1DC; padding: 15px; border-radius: 15px; margin: 10px 0;">
                                    <p style="font-family: 'Quicksand', sans-serif; color: #FF1493;">
                                        Walmart price: <b>{walmart_price_str}</b>
                                    </p>
                                </div>
                                """, unsafe_allow_html=True)
                        except:
                            st.markdown(f"""
                            <div style="background-color: #FFD1DC; padding: 15px; border-radius: 15px; margin: 10px 0;">
                                <p style="font-family: 'Quicksand', sans-serif; color: #FF1493;">
                                    Walmart price: <b>{walmart_price_str}</b>
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div style="background-color: #FFD1DC; padding: 15px; border-radius: 15px; margin: 10px 0;">
                            <p style="font-family: 'Quicksand', sans-serif; color: #FF1493;">
                                Couldn't find this product on Walmart 😔
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Show buy button
                st.markdown("### 💝 Ready to buy?")
                
                col_buy1, col_buy2, _ = st.columns([1, 1, 2])
                with col_buy1:
                    st.markdown(f"<a href='{amazon_url}' target='_blank'><button style='background-color: #FF69B4; color: white; padding: 10px 20px; border: none; border-radius: 20px; cursor: pointer; font-family: \"Quicksand\", sans-serif; width: 100%;'>Buy on Amazon</button></a>", unsafe_allow_html=True)
                
                with col_buy2:
                    if walmart_price_str:
                        walmart_search_url = f"https://www.walmart.com/search?q={product_title.replace(' ', '+')}"
                        st.markdown(f"<a href='{walmart_search_url}' target='_blank'><button style='background-color: #FFD1DC; color: #FF1493; padding: 10px 20px; border: 2px solid #FF69B4; border-radius: 20px; cursor: pointer; font-family: \"Quicksand\", sans-serif; width: 100%;'>Check on Walmart</button></a>", unsafe_allow_html=True)
                
                # Add to search history
                if asin not in [item['asin'] for item in st.session_state.search_history]:
                    st.session_state.search_history.append({
                        'asin': asin,
                        'title': product_title,
                        'current_price': current_price,
                        'url': amazon_url
                    })
            
            except Exception as e:
                st.error(f"Error fetching data: {str(e)}")
                st.markdown("Please check your API key and try again.")
    else:
        st.error("Couldn't find ASIN. Please check the link and make sure it's a valid Amazon product URL.")

# Display search history
if st.session_state.search_history:
    st.markdown("---")
    st.markdown("### 📚 Your Search History")
    
    history_df = pd.DataFrame(st.session_state.search_history)
    
    for idx, item in enumerate(st.session_state.search_history):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"""
            <div style="background-color: white; padding: 10px; border-radius: 10px; margin: 5px 0; border-left: 4px solid #FF69B4;">
                <p style="font-family: 'Quicksand', sans-serif; color: #FF1493; margin: 0; font-size: 15px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 400px;">
                    {item['title']}
                </p>
                <p style="font-family: 'Quicksand', sans-serif; color: #FF69B4; margin: 0; font-size: 14px;">
                    Current price: <b>${item['current_price']:.2f}</b>
                </p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"<a href='{item['url']}' target='_blank'><button style='background-color: #FFD1DC; color: #FF1493; padding: 5px 10px; border: 1px solid #FF69B4; border-radius: 10px; cursor: pointer; font-family: \"Quicksand\", sans-serif; font-size: 12px; width: 100%;'>View Item</button></a>", unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="footer">
    <p>✨ Made with Girl Math and glitter ✨</p>
</div>
""", unsafe_allow_html=True)

def girl_math_statement(current_price, peak_price, lowest_price):
    """Generate a fun girl math statement based on the price situation"""
    statements = [
        f"That's like getting paid ${peak_price - current_price:.2f} to shop!",
        "Remember, if it's on sale, it's basically saving money!",
        "If you use it 10 times, it's only $" + f"{current_price/10:.2f}" + " per use!",
        "That's only " + f"{current_price/30:.2f}" + " per day for a month!",
        "Buy now, your future self will thank you!",
        "It's an investment in your happiness!",
        "If you return something else, this is basically free!",
        "You've already saved money by not buying it at the peak price!"
    ]
    
    if current_price <= lowest_price * 1.1:
        return "This is literally the LOWEST price! It would be irresponsible NOT to buy it!"
    elif current_price <= peak_price * 0.8:
        return "That's a MAJOR discount! It's like they're paying you to take it!"
    else:
        import random
        return random.choice(statements)
