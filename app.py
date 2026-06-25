import io
import streamlit as st
import pandas as pd
from datetime import datetime

from boc_agent.schemas.transaction import TransactionRecord
from boc_agent.agents.orchestrator import Orchestrator
from boc_agent.hitl.review_decision import HumanReviewDecision, apply_human_decision
from boc_agent.hitl.review_queue import build_review_queue
from boc_agent.hitl.review_exporter import export_human_review_log
from boc_agent.ui_helpers import calculate_summary_metrics
from boc_agent.rules.allocation_rules import ALLOCATION_COLUMNS
from boc_agent.io.workbook_exporter import rename_and_reorder_df
from boc_agent.chat.assistant import ReviewConversationAssistant

# 1. Page Configuration
st.set_page_config(
    page_title="BOC Allocation Review Agent Dashboard",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Styling and Sidebar Header
st.sidebar.title("💼 Control Panel")
st.sidebar.markdown(
    """
    **Canadian Film & TV Production Accounting Review MVP**
    
    *Supporting deterministic allocation review.*
    """
)

# 3. Header and Disclaimer
st.title("💼 BOC Allocation Review Agent")
st.warning(
    "⚠️ **Disclaimer**: This MVP supports production accounting review. "
    "It does NOT provide official tax-credit determinations or compile official filings (like CAVCO Form 6)."
)

# 4. Initialize Session State
if "reviewed_df" not in st.session_state:
    st.session_state.reviewed_df = None
if "human_decisions_list" not in st.session_state:
    st.session_state.human_decisions_list = []
if "original_columns" not in st.session_state:
    st.session_state.original_columns = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Helper: Convert DataFrame to Excel bytes for download
def to_excel_bytes(df: pd.DataFrame) -> bytes:
    df_renamed = rename_and_reorder_df(df, st.session_state.get("original_columns", []))
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df_renamed.to_excel(writer, index=False)
    return buffer.getvalue()

# Helper: Convert DataFrame to CSV bytes for download
def to_csv_bytes(df: pd.DataFrame) -> bytes:
    df_renamed = rename_and_reorder_df(df, st.session_state.get("original_columns", []))
    return df_renamed.to_csv(index=False).encode('utf-8')

# 5. File Upload Section
st.subheader("1. Ingest General Ledger Workbook")
uploaded_file = st.file_uploader(
    "Upload a synthetic General Ledger workbook (.xlsx or .csv)",
    type=["xlsx", "csv"]
)

if uploaded_file is not None:
    try:
        # Load raw file for preview
        if uploaded_file.name.endswith('.csv'):
            raw_df = pd.read_csv(uploaded_file)
        else:
            raw_df = pd.read_excel(uploaded_file)
            
        st.session_state.original_columns = list(raw_df.columns)
        st.success(f"Successfully loaded '{uploaded_file.name}' with {len(raw_df)} rows.")
        
        # Preview raw workbook
        with st.expander("Preview Raw Ledger Ingestion"):
            st.dataframe(raw_df.head(10))
            
        # Run review button
        if st.button("🚀 Run Review Agent"):
            # Run schema validation first
            from boc_agent.io.workbook_loader import validate_dataframe_schema
            try:
                validate_dataframe_schema(raw_df)
            except Exception as schema_err:
                st.error(f"Schema Validation Failed: {schema_err}")
                st.stop()
                
            st.info("Processing General Ledger transactions through Agent Orchestration...")
            
            orchestrator = Orchestrator()
            reviewed_data = []
            
            # Loop through transactions and execute agent pipeline
            progress_bar = st.progress(0)
            for idx, row in raw_df.iterrows():
                tx = TransactionRecord.from_row_dict(row.to_dict())
                result = orchestrator.process_transaction(tx)
                reviewed_data.append({**tx.model_dump(), **result.model_dump()})
                progress_bar.progress((idx + 1) / len(raw_df))
                
            reviewed_df = pd.DataFrame(reviewed_data)
            
            # Initialize human review columns
            human_cols = [
                "human_review_decision", "human_review_comment", 
                "human_reviewer", "human_reviewed_at", 
                "human_override_allocation", "human_override_reason"
            ]
            for col in human_cols:
                if col not in reviewed_df.columns:
                    reviewed_df[col] = None
                    
            st.session_state.reviewed_df = reviewed_df
            st.session_state.human_decisions_list = []
            st.success("Review processing completed successfully!")
            
    except Exception as e:
        st.error(f"Error reading file: {e}")

# 6. Main Dashboard Actions
if st.session_state.reviewed_df is not None:
    df = st.session_state.reviewed_df
    metrics = calculate_summary_metrics(df)
    
    st.subheader("2. Audit Summary Metrics")
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    m_col1.metric("Total Transactions", metrics["total_rows"])
    m_col2.metric("Approved (Auto)", metrics["approved"])
    m_col3.metric("Needs Human Review", metrics["needs_human_review"], delta=metrics["needs_human_review"], delta_color="inverse")
    m_col4.metric("Ineligible Costs", metrics["ineligible"])
    
    m_col5, m_col6, m_col7, m_col8 = st.columns(4)
    m_col5.metric("Eligible", metrics["eligible"])
    m_col6.metric("Needs Review (Eligibility)", metrics["needs_review"])
    m_col7.metric("Out of Canada", metrics["out_of_canada"])
    m_col8.metric("Quebec Needs Review", metrics["quebec_needs_review"])
    
    # 7. Navigation Tabs
    tab_ledger, tab_queue, tab_actions, tab_chat = st.tabs([
        "📋 Full Reviewed Ledger", 
        "🔍 Human Review Queue", 
        "✍️ HITL Review Actions",
        "💬 Conversational Assistant"
    ])
    
    # --- Tab 1: Full Reviewed Ledger ---
    with tab_ledger:
        st.markdown("### Full Reviewed Ledger Preview")
        st.dataframe(df)
        
        # Download reviewed data
        dl_xlsx = to_excel_bytes(df)
        dl_csv = to_csv_bytes(df)
        
        c1, c2 = st.columns(2)
        c1.download_button(
            "Download Full Reviewed Excel Workbook",
            data=dl_xlsx,
            file_name="reviewed_boc_gl_dataset.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        c2.download_button(
            "Download Full Reviewed CSV",
            data=dl_csv,
            file_name="reviewed_boc_gl_dataset.csv",
            mime="text/csv"
        )
        
    # --- Tab 2: Human Review Queue ---
    with tab_queue:
        st.markdown("### Items Flagged for Human Attention")
        queue_df = build_review_queue(df)
        
        if queue_df.empty:
            st.success("No items require human review!")
        else:
            # Filter controls
            f_col1, f_col2, f_col3 = st.columns(3)
            with f_col1:
                provinces = ["All"] + list(queue_df["application_province"].dropna().unique())
                sel_prov = st.selectbox("Filter by Application Province", provinces)
            with f_col2:
                statuses = ["All"] + list(queue_df["eligibility_status"].dropna().unique())
                sel_status = st.selectbox("Filter by Eligibility Status", statuses)
            with f_col3:
                allocs = ["All"] + list(queue_df["suggested_allocation_column"].dropna().unique())
                sel_alloc = st.selectbox("Filter by Suggested Allocation", allocs)
                
            # Apply filters
            filtered_queue = queue_df.copy()
            if sel_prov != "All":
                filtered_queue = filtered_queue[filtered_queue["application_province"] == sel_prov]
            if sel_status != "All":
                filtered_queue = filtered_queue[filtered_queue["eligibility_status"] == sel_status]
            if sel_alloc != "All":
                filtered_queue = filtered_queue[filtered_queue["suggested_allocation_column"] == sel_alloc]
                
            st.dataframe(filtered_queue)
            
            # Download queue
            dl_queue_xlsx = to_excel_bytes(filtered_queue)
            st.download_button(
                "Download Filtered Queue Excel",
                data=dl_queue_xlsx,
                file_name="human_review_queue.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
    # --- Tab 3: HITL Review Actions ---
    with tab_actions:
        st.markdown("### Resolve Flagged Transactions")
        queue_df = build_review_queue(df)
        
        if queue_df.empty:
            st.info("No transactions require human review.")
        else:
            # Get list of references for selection
            ref_list = queue_df["trans_ref"].dropna().unique().tolist()
            selected_ref = st.selectbox(
                "Select Transaction Reference ID (Trans Ref) to Review",
                ref_list
            )
            
            # Extract details of the selected transaction
            selected_row = queue_df[queue_df["trans_ref"] == selected_ref].iloc[0]
            
            col_info1, col_info2 = st.columns(2)
            with col_info1:
                st.markdown(f"**Vendor**: {selected_row.get('vendor_name') or 'N/A'}")
                st.markdown(f"**Employee**: {selected_row.get('employee') or 'N/A'}")
                st.markdown(f"**Amount**: {selected_row.get('amount')} {selected_row.get('currency') or 'CAD'}")
                st.markdown(f"**Description**: {selected_row.get('description')}")
            with col_info2:
                st.markdown(f"**Agent Suggested Allocation**: `{selected_row.get('suggested_allocation_column')}`")
                st.markdown(f"**Agent Rationale**: {selected_row.get('rationale')}")
                st.markdown(f"**Ep Code / Location**: {selected_row.get('ep')} / {selected_row.get('location')}")
                
            st.markdown("---")
            
            # Form for human decision
            with st.form("human_decision_form"):
                reviewer = st.text_input("Reviewer Name", value="Senior Auditor")
                
                decision_status = st.selectbox(
                    "Reviewer Decision",
                    [
                        "Accept Agent Suggestion", 
                        "Override Allocation", 
                        "Mark Ineligible", 
                        "Request More Documentation", 
                        "Defer"
                    ]
                )
                
                comment = st.text_area("Justification Comment", placeholder="Explain why this decision is made...")
                
                # Dynamic override selection
                override_col = None
                override_reason = None
                if decision_status == "Override Allocation":
                    override_col = st.selectbox("Override Target Allocation Column", ALLOCATION_COLUMNS)
                    override_reason = st.text_input("Override Reason")
                    
                submitted = st.form_submit_submit_button = st.form_submit_button("Submit Audit Decision")
                
                if submitted:
                    # Construct Pydantic model
                    decision_model = HumanReviewDecision(
                        transaction_ref=str(selected_ref),
                        reviewer_decision=decision_status,
                        reviewer_comment=comment,
                        reviewer_name=reviewer,
                        reviewed_at=datetime.utcnow().isoformat() + "Z",
                        override_allocation=override_col,
                        override_reason=override_reason
                    )
                    
                    # Update row in main reviewed DataFrame
                    idx_in_main = df[df["trans_ref"] == selected_ref].index[0]
                    main_row = df.loc[idx_in_main].to_dict()
                    updated_row = apply_human_decision(main_row, decision_model)
                    
                    # Commit to session state DataFrame
                    for k, v in updated_row.items():
                        st.session_state.reviewed_df.at[idx_in_main, k] = v
                        
                    # Save to log list
                    st.session_state.human_decisions_list.append(decision_model.model_dump())
                    st.success(f"Decision submitted for transaction reference: {selected_ref}")
                    st.rerun()
                    
            # Display accumulated decisions
            if st.session_state.human_decisions_list:
                st.markdown("### Accumulated Human Decisions Log")
                decisions_df = pd.DataFrame(st.session_state.human_decisions_list)
                st.dataframe(decisions_df)
                
                dl_log_xlsx = to_excel_bytes(decisions_df)
                st.download_button(
                    "Download Human Decisions Log Excel",
                    data=dl_log_xlsx,
                    file_name="human_decisions_log.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

    # --- Tab 4: Conversational Assistant ---
    with tab_chat:
        st.markdown("### 💬 Conversational Review Assistant")
        st.markdown(
            "Ask natural language questions about the reviewed ledger, human review queue, ineligible costs, or specific transactions. "
            "This assistant operates deterministically using the reviewed workbook data and is completely read-only."
        )
        
        # Reset chat history button
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_history = []
            st.rerun()
            
        st.markdown("---")
        
        # Display existing messages
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                
        # Chat input
        prompt = st.chat_input("Ask a question about the reviewed ledger...")
        if prompt:
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            
            # Answer query
            assistant = ReviewConversationAssistant()
            response = assistant.answer(prompt, df)
            
            # Display assistant message
            with st.chat_message("assistant"):
                st.markdown(response)
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.rerun()
