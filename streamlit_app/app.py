import hmac
import json
import logging
import os
import re
import uuid

import streamlit as st
from services import aws_helper, bedrock_agent_runtime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def log(message):
    logger.info(message)



# Get config from environment variables
agent_id = os.getenv("BEDROCK_AGENT_ID")
agent_alias_id = os.getenv("BEDROCK_AGENT_ALIAS_ID")
ui_title = "SV Darmstadt 98 KI Helfer"

def init_state():
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.messages = []
    st.session_state.citations = []
    st.session_state.trace = {}

# General page configuration and initialization
if len(st.session_state.items()) == 0:
    init_state()

# def check_password():
#     def password_entered():
#         actual_password = aws_helper.get_ssm_parameter("/ai-agent/streamlit/auth_secret")
#         if hmac.compare_digest(st.session_state["password"], actual_password):
#             st.session_state["password_correct"] = True
#             del st.session_state["password"]  # Don't store the password.
#         else:
#             st.session_state["password_correct"] = False

#     # Return True if the password is validated.
#     if st.session_state.get("password_correct", False):
#         return True

#     # Show input for password.
#     st.text_input(
#         "Password", type="password", on_change=password_entered, key="password"
#     )
#     if "password_correct" in st.session_state:
#         st.error("😕 Password incorrect")
#     return False


# if not check_password():
#     st.stop()  

st.set_page_config(page_title=ui_title, layout="wide")
st.title(ui_title)

# Sidebar button to reset session state
with st.sidebar:
    if st.button("Reset Session"):
        init_state()

# Messages in the conversation
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)

# Chat input that invokes the agent
if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown("...")
        response = bedrock_agent_runtime.invoke_agent(
            agent_id,
            agent_alias_id,
            st.session_state.session_id,
            prompt
        )
        output_text = response["output_text"]
        print(output_text)

        # Add citations
        if len(response["citations"]) > 0:
            citation_num = 1
            num_citation_chars = 0
            citation_locs = ""
            for citation in response["citations"]:
                end_span = citation["generatedResponsePart"]["textResponsePart"]["span"]["end"] + 1
                for retrieved_ref in citation["retrievedReferences"]:
                    citation_marker = f"[{citation_num}]"
                    output_text = output_text[:end_span + num_citation_chars] + citation_marker + output_text[end_span + num_citation_chars:]
                    citation_locs = citation_locs + "\n<br>" + citation_marker + " " + retrieved_ref["location"]["s3Location"]["uri"]
                    citation_num = citation_num + 1
                    num_citation_chars = num_citation_chars + len(citation_marker)
                output_text = output_text[:end_span + num_citation_chars] + "\n" + output_text[end_span + num_citation_chars:]
                num_citation_chars = num_citation_chars + 1
            output_text = output_text + "\n" + citation_locs

        placeholder.markdown(output_text, unsafe_allow_html=True)
        st.session_state.messages.append({"role": "assistant", "content": output_text})
        st.session_state.citations = response["citations"]
        st.session_state.trace = response["trace"]

trace_type_headers = {
    "preProcessingTrace": "Pre-Processing",
    "orchestrationTrace": "Orchestration",
    "postProcessingTrace": "Post-Processing"
}
trace_info_types = ["invocationInput", "modelInvocationInput", "modelInvocationOutput", "observation", "rationale"]

# Sidebar section for trace
with st.sidebar:
    st.title("Trace")

    # Show each trace types in separate sections
    step_num = 1
    for trace_type in trace_type_headers:
        st.subheader(trace_type_headers[trace_type])

        # Organize traces by step similar to how it is shown in the Bedrock console
        if trace_type in st.session_state.trace:
            trace_steps = {}
            for trace in st.session_state.trace[trace_type]:
                # Each trace type and step may have different information for the end-to-end flow
                for trace_info_type in trace_info_types:
                    if trace_info_type in trace:
                        trace_id = trace[trace_info_type]["traceId"]
                        if trace_id not in trace_steps:
                            trace_steps[trace_id] = [trace]
                        else:
                            trace_steps[trace_id].append(trace)
                        break

            # Show trace steps in JSON similar to the Bedrock console
            for trace_id in trace_steps.keys():
                with st.expander("Trace Step " + str(step_num), expanded=False):
                    for trace in trace_steps[trace_id]:
                        trace_str = json.dumps(trace, indent=2)
                        st.code(trace_str, language="json", line_numbers=trace_str.count("\n"))
                step_num = step_num + 1
        else:
            st.text("None")

    st.subheader("Citations")
    if len(st.session_state.citations) > 0:
        citation_num = 1
        for citation in st.session_state.citations:
            for retrieved_ref_num, retrieved_ref in enumerate(citation["retrievedReferences"]):
                with st.expander("Citation [" + str(citation_num) + "]", expanded=False):
                    citation_str = json.dumps({
                        "generatedResponsePart": citation["generatedResponsePart"],
                        "retrievedReference": citation["retrievedReferences"][retrieved_ref_num]
                    }, indent=2)
                    st.code(citation_str, language="json", line_numbers=trace_str.count("\n"))
                citation_num = citation_num + 1
    else:
        st.text("None")

    st.subheader("Final query")

    def extract_stdout_content(text):
        pattern = re.compile(r'<stdout>(.*?)</stdout>', re.DOTALL)
        matches = pattern.findall(text)
        if matches:
            return matches[-1].strip()
        return None

    def extract_source_content(text):
        pattern = re.compile(r'Source:\s*(.*?)\\\s*Returned', re.DOTALL)
        match = pattern.search(text)
        if match:
            return match.group(1).strip().replace("\\", "")
        return None

    def get_nested_text(trace):
        orchestration_trace = trace.get('orchestrationTrace', [])
        if not isinstance(orchestration_trace, list) or len(orchestration_trace) < 2:
            return None
        
        model_invocation_input = orchestration_trace[-2].get("modelInvocationInput", {})
        text = model_invocation_input.get("text")
        if not text:
            return None

        stdout_content = extract_stdout_content(text)
        if not stdout_content:
            return None

        source_content = extract_source_content(stdout_content)
        if not source_content:
            return None

        return source_content
    
    # prinprint(st.session_state.trace)
    st.code(get_nested_text(st.session_state.trace))

