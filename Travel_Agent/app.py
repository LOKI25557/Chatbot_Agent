import sys
from pathlib import Path

# Ensure Travel_Agent directory is in sys.path for robust resolution regardless of launch CWD
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

import streamlit as st
from config import is_groq_configured, GROQ_MODEL
from agent import TravelAgent
from llm import verify_groq_connection
import memory

st.set_page_config(page_title="TripMate", page_icon="✈️", layout="wide")

@st.cache_data(ttl=60)
def check_api_status():
    """Cached check of Groq API connectivity without exposing credentials."""
    return verify_groq_connection()

def render_sidebar():
    with st.sidebar:
        st.title("✈️ TripMate Settings")
        
        if is_groq_configured():
            is_live, status_msg = check_api_status()
            if is_live:
                st.success("🟢 GROQ LLM MODE")
                st.caption(f"Model: {GROQ_MODEL} (Connected)")
            else:
                st.warning("🟡 GROQ CONFIGURED (DEMO FALLBACK)")
                st.caption(f"{status_msg}. Deterministic fallback active.")
        else:
            st.warning("🟡 DEMO MODE")
            st.caption("Groq API key not found. Using deterministic logic.")
            
        st.divider()
        st.subheader("🧠 Memory")
        if st.button("View Memory"):
            st.json(memory.load_memory())
        if st.button("Clear Memory"):
            memory.clear_memory()
            st.success("Memory cleared!")
            
        st.divider()
        st.subheader("About")
        st.info(
            "TripMate: Mini Autonomous Travel Agent\n\n"
            "Demonstrates LLM, Planning, Tools, Reasoning, Re-planning, and Human Approval."
        )

def render_main():
    st.title("✈️ TripMate")
    st.subheader("Mini Autonomous Travel Agent")
    st.markdown("**Plan → Use Tools → Observe → Reason → Re-plan → Ask Approval → Act**")
    
    default_req = "I want to travel from Bengaluru to Goa for 3 days under ₹15,000. I prefer beaches and vegetarian food."
    user_request = st.text_area("Travel Request", value=default_req, height=100)
    
    col1, col2 = st.columns(2)
    with col1:
        plan_btn = st.button("PLAN MY TRIP", type="primary", use_container_width=True)
    with col2:
        demo_fail_btn = st.button("RUN FAILURE / RE-PLANNING DEMO", use_container_width=True)
        
    if plan_btn or demo_fail_btn:
        st.session_state.agent = TravelAgent(force_failure=bool(demo_fail_btn))
        with st.spinner("Agent is working..."):
            st.session_state.agent.run(user_request)
        
    if "agent" in st.session_state and st.session_state.agent:
        agent = st.session_state.agent
        
        st.divider()
        st.subheader("Agent Execution Log")
        
        # Display execution log beautifully
        icons = {
            "GOAL": "🎯", "MEMORY": "🧠", "PLANNING": "📋",
            "TOOL": "🔧", "OBSERVATION": "👁", "REASONING": "🧠",
            "RE-PLANNING": "🔄", "NEW PLAN": "📋", "BUDGET": "💰",
            "HUMAN APPROVAL": "⚠️", "ACTION": "⚡", "MEMORY UPDATE": "💾",
            "HUMAN REJECTION": "🛑", "RE-PLANNING FAILED": "❌", "TERMINATION": "⛔"
        }
        for log in agent.state.execution_log:
            step = log["step"]
            msg = log["message"]
            icon = icons.get(step, "▪️")
            st.markdown(f"**{icon} {step}**")
            st.caption(f"{msg}")
            
        if agent.state.requires_human_approval and agent.state.action_status == "NONE":
            st.divider()
            st.warning("⚠️ HUMAN APPROVAL REQUIRED")
            
            plan = agent.state.plan
            st.markdown("### FINAL TRAVEL PLAN")
            st.markdown(f"**Transport:** {agent.state.goal.source} → {agent.state.goal.destination} | {plan.transport.get('type')} | ₹{plan.transport.get('price'):.0f}")
            st.markdown(f"**Hotel:** {plan.hotel.get('name')} | ₹{plan.hotel.get('price'):.0f}/night")
            st.markdown(f"**Duration:** {plan.duration_days} days")
            st.markdown(f"**Estimated total:** ₹{plan.estimated_total_cost:.0f}")
            st.caption("*(Prices are Estimated Demo Data — No Real Endpoints Charged)*")
            
            with st.expander("View Full Itinerary"):
                st.text(agent.planner.generate_itinerary())
            
            st.write("Do you want to proceed with the simulated booking?")
            
            c1, c2 = st.columns(2)
            with c1:
                if st.button("APPROVE BOOKING", type="primary"):
                    agent.execute_action()
                    st.rerun()
            with c2:
                if st.button("REJECT PLAN"):
                    agent.reject_action("User declined proposed itinerary.")
                    st.rerun()
                    
        elif agent.state.action_status == "COMPLETED":
            st.success("🎉 Simulated booking completed successfully! Persistent memory updated.")
            st.balloons()
        elif agent.state.action_status == "REJECTED":
            st.warning("🛑 Plan was rejected by human. No bookings were executed.")
        elif agent.state.action_status == "ABORTED_INFEASIBLE":
            st.error("⛔ Execution terminated: No feasible travel plan could be generated within constraints.")

def main():
    render_sidebar()
    render_main()

if __name__ == "__main__":
    main()

