import os
import datetime
import streamlit as st
from graph import compiled_graph

# Configure Streamlit page options
st.set_page_config(
    page_title="AI Multi-Agent Travel Planner",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium styling
st.markdown("""
<style>
    /* Gradient Header */
    .header-container {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 2.5rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    .header-title {
        font-family: 'Outfit', 'Inter', sans-serif;
        font-size: 2.8rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        letter-spacing: -0.5px;
    }
    .header-subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 1.1rem;
        opacity: 0.9;
        font-weight: 300;
    }
    
    /* Metrics and Dashboard Cards */
    .card-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
        gap: 1.25rem;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #ffffff;
        border: 1px solid #eef2f6;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.05);
        border-color: #dbeafe;
    }
    .metric-title {
        font-size: 0.85rem;
        color: #64748b;
        text-transform: uppercase;
        font-weight: 600;
        letter-spacing: 0.5px;
        margin-bottom: 0.5rem;
    }
    .metric-value {
        font-size: 1.4rem;
        color: #1e293b;
        font-weight: 700;
    }
    
    /* Segment Cards */
    .detail-card {
        background-color: #ffffff;
        border-left: 5px solid #2563eb;
        border-radius: 8px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .hotel-card {
        border-left-color: #10b981;
    }
    .flight-card {
        border-left-color: #f59e0b;
    }
    .weather-card {
        border-left-color: #06b6d4;
    }
    
    /* Badges */
    .custom-badge {
        display: inline-block;
        padding: 0.25rem 0.6rem;
        font-size: 0.75rem;
        font-weight: 600;
        border-radius: 9999px;
        margin-right: 0.5rem;
    }
    .badge-blue { background-color: #dbeafe; color: #1e40af; }
    .badge-green { background-color: #d1fae5; color: #065f46; }
    .badge-amber { background-color: #fef3c7; color: #92400e; }
    .badge-purple { background-color: #f3e8ff; color: #6b21a8; }
</style>
""", unsafe_allow_html=True)

# Application Header
st.markdown("""
<div class="header-container">
    <div class="header-title">🌍 AI Travel Planner</div>
    <div class="header-subtitle">Multi-Agent orchestration powered by LangGraph, LangChain, and Streamlit</div>
</div>
""", unsafe_allow_html=True)

# Initialize Session State for Travel Plan
if "travel_state" not in st.session_state:
    st.session_state.travel_state = None
if "is_running" not in st.session_state:
    st.session_state.is_running = False

# Sidebar inputs
st.sidebar.header("🛠️ Planner Configuration")

# API Key Settings
openai_key = st.sidebar.text_input(
    "OpenAI API Key (Optional)", 
    type="password", 
    placeholder="sk-...",
    help="Provide your OpenAI API key to run agents using GPT-4o-mini. If left blank, the planner runs in SIMULATION mode with high-quality pre-seeded and procedurally generated mock data."
)

st.sidebar.divider()
st.sidebar.subheader("✈️ Travel Details")

source = st.sidebar.text_input("Source City", value="New York", placeholder="e.g. Chicago, New York")
destination = st.sidebar.text_input("Destination City", value="Paris, France", placeholder="e.g. London, UK or Tokyo")

# Dates selection
today = datetime.date.today()
tomorrow = today + datetime.timedelta(days=15)
default_return = tomorrow + datetime.timedelta(days=5)

col_d1, col_d2 = st.sidebar.columns(2)
with col_d1:
    start_date = st.date_input("Departure", value=tomorrow, min_value=today)
with col_d2:
    end_date = st.date_input("Return", value=default_return, min_value=start_date + datetime.timedelta(days=1))

# Budget & Preferences
budget = st.sidebar.number_input("Total Budget (USD)", min_value=100.0, value=2500.0, step=100.0)
preferences = st.sidebar.text_area(
    "Travel Style & Preferences", 
    value="museums, local bakery food, art, relaxed pace, boutique shops",
    placeholder="e.g. historic sights, hiking, vegan food, shopping, luxury spa"
)

# Execution trigger
generate_btn = st.sidebar.button("🧭 Generate Travel Plan", use_container_width=True, type="primary")

# Execute Graph
if generate_btn:
    st.session_state.is_running = True
    
    # Configure API key environment variable
    if openai_key.strip():
        os.environ["OPENAI_API_KEY"] = openai_key.strip()
    else:
        if "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]

    # Initial state setup
    initial_inputs = {
        "source": source,
        "destination": destination,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "budget": float(budget),
        "preferences": preferences,
        
        # Initialize output structures
        "extracted_destination": {},
        "flights": [],
        "hotels": [],
        "weather": {},
        "itinerary": [],
        "final_plan": "",
        "logs": ["Planner: Starting travel graph execution."],
        "errors": []
    }

    # Stream graph nodes execution
    st.session_state.travel_state = initial_inputs
    
    with st.status("💡 Coordinatings agents to design your plan...", expanded=True) as status_box:
        try:
            current_state = dict(initial_inputs)
            
            # Use LangGraph compiled_graph.stream to get block updates
            for event in compiled_graph.stream(initial_inputs):
                for node_name, updates in event.items():
                    # Format node name nicely
                    node_label = node_name.replace("_", " ").title()
                    status_box.write(f"✔️ **{node_label}** finalized updates.")
                    
                    # Merge updates into current_state
                    for key, val in updates.items():
                        if key in ["logs", "errors"]:
                            current_state[key] = current_state.get(key, []) + val
                        else:
                            current_state[key] = val
                            
            status_box.update(label="✈️ Travel Plan Drafted successfully!", state="complete", expanded=False)
            st.session_state.travel_state = current_state
            
        except Exception as e:
            st.error(f"Execution Error inside LangGraph Workflow: {str(e)}")
            st.session_state.travel_state["errors"].append(f"Graph execution failed: {str(e)}")
            
    st.session_state.is_running = False

# Draw results
state = st.session_state.travel_state

if state:
    # Diagnostic error notice if any occurred
    if state.get("errors"):
        for err in state["errors"]:
            st.error(f"⚠️ {err}")

    # Gather extracted parameters
    ext_dest = state.get("extracted_destination", {})
    city_name = ext_dest.get("city", destination)
    country_name = ext_dest.get("country", "")
    num_days = ext_dest.get("num_days", 5)
    budget_tier = ext_dest.get("budget_tier", "Mid-range")
    
    # Check if running in simulation
    is_simulation = "OpenAI" not in ext_dest.get("method", "")
    
    # Render Dashboard metrics
    st.markdown("### 📋 Trip Dashboard Summary")
    st.markdown(f"""
    <div class="card-grid">
        <div class="metric-card">
            <div class="metric-title">📍 Destination</div>
            <div class="metric-value">{city_name}{f', {country_name}' if country_name else ''}</div>
        </div>
        <div class="metric-card">
            <div class="metric-title">⏱️ Duration</div>
            <div class="metric-value">{num_days} Days</div>
        </div>
        <div class="metric-card">
            <div class="metric-title">💰 Budget Tier</div>
            <div class="metric-value">{budget_tier}</div>
        </div>
        <div class="metric-card">
            <div class="metric-title">⚙️ Agent Mode</div>
            <div class="metric-value">{'🌐 Simulation Mode' if is_simulation else '🤖 OpenAI GPT-4o-mini'}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Multi-tab view of outputs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Travel Summary", 
        "✈️ Flight Details", 
        "🏨 Hotels Recommended", 
        "☀️ Weather & Packing", 
        "🗺️ Day-wise Itinerary", 
        "📖 Final Travel Plan Document"
    ])
    
    # TAB 1: SUMMARY DASHBOARD
    with tab1:
        st.markdown(f"### 🌟 Quick Look at your Trip to {city_name}")
        
        col_s1, col_s2 = st.columns([2, 1])
        with col_s1:
            st.markdown(f"**Trip from**: {source} ➔ **{city_name}, {country_name}**")
            st.markdown(f"**Dates**: {start_date} to {end_date}")
            st.markdown(f"**Preferences**: *{preferences}*")
            
            # Quick summary text
            weather_out = state.get("weather", {})
            st.info(f"⛅ **Weather Outlook**: {weather_out.get('summary', 'Typical local seasonal temperatures.')}")
            
        with col_s2:
            st.markdown("##### 💵 Cost Projections")
            best_flight = state.get("flights", [{}])[0]
            best_hotel = state.get("hotels", [{}])[0]
            
            flight_cost = best_flight.get("base_price", 0)
            hotel_cost_per_night = best_hotel.get("price_per_night", 0)
            total_hotel_cost = hotel_cost_per_night * num_days
            estimated_total = flight_cost + total_hotel_cost
            
            st.metric("Est. Flight Cost", f"${flight_cost} USD")
            st.metric(f"Est. Hotel Cost ({num_days} nights)", f"${total_hotel_cost} USD", help=f"${hotel_cost_per_night}/night at {best_hotel.get('name', 'Hotel')}")
            
            rem_budget = budget - estimated_total
            if rem_budget >= 0:
                st.metric("Remaining Pocket Money", f"${rem_budget:.2f} USD", delta=f"+${rem_budget:.2f} left")
            else:
                st.metric("Pocket Money Deficit", f"${abs(rem_budget):.2f} USD", delta=f"-${abs(rem_budget):.2f} over budget", delta_color="inverse")

    # TAB 2: FLIGHT DETAILS
    with tab2:
        st.markdown("### ✈️ Flight Recommendations")
        if is_simulation:
            st.caption("ℹ️ *Displaying simulated airline availability matching your routes and parameters.*")
            
        for f in state.get("flights", []):
            st.markdown(f"""
            <div class="detail-card flight-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size:1.2rem; font-weight:700; color:#1e293b;">✈️ {f['airline']} <span style="font-size:0.9rem; font-weight:400; color:#64748b;">({f['flight_no']})</span></span>
                    <span style="font-size:1.3rem; font-weight:700; color:#b45309;">{f['price_display']}</span>
                </div>
                <div style="margin-top:0.5rem; display:flex; gap:1.5rem; font-size:0.95rem; color:#475569;">
                    <span><b>Schedule:</b> {f['departure']} ➔ {f['arrival']}</span>
                    <span><b>Duration:</b> {f['duration']}</span>
                    <span><b>Stops:</b> {f['stops']}</span>
                    <span><b>Class:</b> {f['class']}</span>
                </div>
                <div style="margin-top:0.75rem; font-style:italic; font-size:0.9rem; color:#475569; padding-top:0.5rem; border-top:1px dashed #e2e8f0;">
                    💡 <b>Recommendation Note:</b> {f.get('recommendation_reason')}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # TAB 3: HOTELS RECOMMENDED
    with tab3:
        st.markdown("### 🏨 Hotel Recommendations")
        if is_simulation:
            st.caption("ℹ️ *Displaying simulated hospitality options aligned with budget tier.*")
            
        for idx, h in enumerate(state.get("hotels", [])):
            rec_tag = '<span class="custom-badge badge-green">🏆 Recommended Selection</span>' if idx == 0 else ""
            amenities_html = "".join([f'<span class="custom-badge badge-blue" style="margin-top:0.25rem;">{am}</span>' for am in h['amenities']])
            
            st.markdown(f"""
            <div class="detail-card hotel-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size:1.2rem; font-weight:700; color:#1e293b;">🏨 {h['name']} <span style="font-size:1rem; color:#f59e0b;">★ {h['rating']}</span> {rec_tag}</span>
                    <span style="font-size:1.3rem; font-weight:700; color:#065f46;">{h['price_display']}</span>
                </div>
                <div style="font-size:0.9rem; color:#64748b; margin-top:0.25rem;">🌐 Area: <b>{h['area']}</b> | {h['tier_label']}</div>
                <p style="margin-top:0.5rem; font-size:0.95rem; color:#334155;">{h['description']}</p>
                <div style="margin:0.75rem 0;">
                    {amenities_html}
                </div>
                <div style="margin-top:0.75rem; font-style:italic; font-size:0.9rem; color:#475569; padding-top:0.5rem; border-top:1px dashed #e2e8f0;">
                    💡 <b>Matching Verdict:</b> {h.get('match_reason')}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # TAB 4: WEATHER & PACKING
    with tab4:
        weather_out = state.get("weather", {})
        st.markdown(f"### ☀️ Weather Outlook for {city_name} ({weather_out.get('month_name')})")
        if is_simulation:
            st.caption("ℹ️ *Climate forecast generated by simulated historical climate metrics.*")
            
        col_w1, col_w2 = st.columns([1, 1])
        
        with col_w1:
            st.markdown(f"""
            <div class="detail-card weather-card" style="height:100%;">
                <h4 style="margin:0 0 0.5rem 0; color:#0e7490;">⛅ Condition: {weather_out.get('condition')}</h4>
                <p style="font-size:1.15rem; font-weight:600; margin:0 0 0.75rem 0; color:#1e293b;">{weather_out.get('temp_display')}</p>
                <div style="font-size:0.95rem; color:#475569;">
                    <div style="margin-bottom:0.25rem;">💧 <b>Humidity:</b> {weather_out.get('humidity')}</div>
                    <div style="margin-bottom:0.25rem;">🌬️ <b>Wind Speed:</b> {weather_out.get('wind')}</div>
                    <div style="margin-bottom:0.25rem;">🌧️ <b>Precipitation Chance:</b> {weather_out.get('rain_chance')}</div>
                </div>
                <p style="margin-top:1rem; font-size:0.95rem; line-height:1.4; color:#334155; padding-top:0.5rem; border-top:1px solid #e2e8f0;">
                    <b>Summary Outlook:</b> {weather_out.get('summary')}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
        with col_w2:
            st.markdown("##### 🎒 Recommended Packing Checklist")
            st.write("Use this checklist as you package details:")
            for item in weather_out.get("packing_tips", []):
                st.checkbox(item, value=True, key=f"pack_check_{item}")

    # TAB 5: DAY-WISE ITINERARY
    with tab5:
        st.markdown(f"### 🗺️ Day-by-Day Travel Itinerary")
        
        for d in state.get("itinerary", []):
            with st.container():
                st.markdown(f"""
                <div style="background-color:#f8fafc; border-radius:10px; padding:1.25rem; margin-bottom:1rem; border:1px solid #e2e8f0;">
                    <h4 style="margin:0 0 0.75rem 0; color:#1e3c72; border-bottom:2px solid #3b82f6; padding-bottom:0.25rem;">🗓️ {d['title']}</h4>
                    <div style="display:flex; flex-direction:column; gap:0.75rem;">
                        <div>
                            <span class="custom-badge badge-blue">🌅 Morning</span>
                            <span style="font-size:0.95rem; color:#1e293b;">{d['morning']}</span>
                        </div>
                        <div>
                            <span class="custom-badge badge-amber">☀️ Afternoon</span>
                            <span style="font-size:0.95rem; color:#1e293b;">{d['afternoon']}</span>
                        </div>
                        <div>
                            <span class="custom-badge badge-purple">🌙 Evening</span>
                            <span style="font-size:0.95rem; color:#1e293b;">{d['evening']}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # TAB 6: FINAL TRAVEL PLAN DOCUMENT
    with tab6:
        st.markdown("### 📖 Consolidated Travel Document")
        
        final_doc = state.get("final_plan", "")
        
        # Download option
        st.download_button(
            label="💾 Download Travel Plan (Markdown)",
            data=final_doc,
            file_name=f"Travel_Plan_{city_name.replace(' ', '_')}.md",
            mime="text/markdown",
            use_container_width=True
        )
        
        # Render markdown directly
        st.markdown(final_doc)

    st.divider()
    
    # Expandable log log
    with st.expander("⚙️ LangGraph Agent Execution Trace Logs"):
        st.markdown("Below are the step-by-step logs output by the specialized agents during graph execution:")
        for log in state.get("logs", []):
            st.code(log)

else:
    # App guide instructions
    st.markdown("""
    <div style="background-color:#f8fafc; border-radius:12px; padding:2rem; border:1px solid #e2e8f0; margin-top:1rem;">
        <h3 style="color:#1e3c72; margin-top:0;">🗺️ Welcome to the AI Multi-Agent Travel Planner!</h3>
        <p>This system uses a structured <b>LangGraph workflow</b> to coordinate six specialized agents to plan your dream vacation. Rather than a single prompt, the planning is split among independent experts working together.</p>
        
        <h4 style="color:#1e293b;">🤖 How the Agent Team Collaborates:</h4>
        <ol>
            <li><b>Destination Agent:</b> Parses your travel dates, calculates duration, cleans location strings, and deduces your budget tier.</li>
            <li><b>Parallel Execution (Flights, Hotels, Weather):</b>
                <ul>
                    <li><b>Flight Agent:</b> Interfaces with the simulated airline inventories to locate flights fitting your budget and path.</li>
                    <li><b>Hotel Agent:</b> Selects top rated lodging and scores them against your personal preferences.</li>
                    <li><b>Weather Agent:</b> Compiles climate forecasts and builds custom packing recommendations.</li>
                </ul>
            </li>
            <li><b>Itinerary Agent:</b> Fan-ins details from flights, hotels, and weather, synthesizing a tailored day-by-day plan.</li>
            <li><b>Final Planner Agent:</b> Coalesces all data elements, writing a rich markdown brochure plan.</li>
        </li>
        </ol>
        
        <div style="background-color:#eff6ff; border-left:4px solid #3b82f6; padding:1rem; border-radius:4px; margin-top:1rem;">
            <b>💡 Pro-Tip:</b> You can run the app immediately in <b>Simulation Mode</b>. To use real generative AI capabilities, paste your OpenAI API Key into the sidebar.
        </div>
    </div>
    """, unsafe_allow_html=True)
