import streamlit as st
import ollama
from PIL import Image
import io
import base64

# --- Configuration and Setup ---
st.set_page_config(
    page_title="Gemma-3 OCR & Chat",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Function to load and encode image (avoids re-reading file)
def load_image_base64(path):
    try:
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except FileNotFoundError:
        st.warning(f"Asset image not found at {path}. Using placeholder text.")
        return "" # Return empty string or a default placeholder base64 if needed

# Load logo image once
gemma_logo_base64 = load_image_base64("./assets/gemma3.png")

# Initialize session state variables if they don't exist
if 'ocr_result' not in st.session_state:
    st.session_state['ocr_result'] = None
if "chat_messages" not in st.session_state:
    st.session_state["chat_messages"] = []

# --- Header and Clear Button ---
col_title, col_clear = st.columns([6, 1])
with col_title:
    if gemma_logo_base64:
        st.markdown(f"""
            # <img src="data:image/png;base64,{gemma_logo_base64}" width="50" style="vertical-align: -12px;"> Gemma-3 OCR & Chat
        """, unsafe_allow_html=True)
    else:
         st.markdown("# Gemma-3 OCR & Chat") # Fallback title
    st.markdown('<p style="margin-top: -20px;">Extract text from images and chat about the content!</p>', unsafe_allow_html=True)

with col_clear:
    if st.button("Clear All 🗑️"):
        st.session_state['ocr_result'] = None
        st.session_state["chat_messages"] = []
        # Clear uploaded file state if needed (Streamlit usually handles this on rerun)
        # If you store the uploaded file object in session state, clear it here too.
        st.rerun()

st.markdown("---")

# --- Sidebar for Image Upload and OCR ---
with st.sidebar:
    st.header("1. Upload Image")
    uploaded_file = st.file_uploader("Choose an image...", type=['png', 'jpg', 'jpeg'], key="file_uploader")

    if uploaded_file is not None:
        # Display the uploaded image
        try:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image")

            st.header("2. Extract Text")
            if st.button("Extract Text 🔍", type="primary", key="extract_button"):
                # Clear previous results and chat before new extraction
                st.session_state['ocr_result'] = None
                st.session_state["chat_messages"] = []
                with st.spinner("Processing image for OCR..."):
                    try:
                        # Get image bytes
                        img_bytes = uploaded_file.getvalue()

                        # Prepare the prompt for OCR
                        ocr_prompt = """Analyze the text in the provided image and extract all readable content *exactly as it appears*. 
                        Return the text in a structured Markdown format, preserving the original language (e.g., French), layout, and intent. 
                        Use headings, lists, tables, or code blocks as needed to reflect the source’s organization. 
                                        """

                        response = ollama.chat(
                            model='gemma3:4b', # Make sure this model supports vision
                            messages=[{
                                'role': 'user',
                                'content': ocr_prompt,
                                'images': [img_bytes] # Pass image bytes directly
                            }]
                        )
                        st.session_state['ocr_result'] = response.message.content
                        st.success("Text extracted successfully!")
                        # No explicit rerun needed here, Streamlit will rerun after button press completes
                    except Exception as e:
                        st.error(f"Error during OCR processing: {str(e)}")
        except Exception as e:
            st.error(f"Error opening or displaying image: {str(e)}")
    else:
         # Clear results if no file is uploaded (e.g., user removed the file)
         # Check if the button isn't currently triggering a rerun to avoid loops
         # This logic might need refinement depending on exact desired behavior
         if st.session_state.get('ocr_result') is not None and not st.session_state.get('extract_button'):
              st.session_state['ocr_result'] = None
              st.session_state["chat_messages"] = []
              # Consider adding st.rerun() here if you want the main area to update immediately when file is removed

# --- Main Content Area for OCR Results and Chat ---
st.header("Extracted Text")
if st.session_state['ocr_result']:
    st.markdown(st.session_state['ocr_result'])
    st.markdown("---") # Separator

    # --- Chat Section ---
    st.header("Chat about the Extracted Text")

    # Display existing chat messages
    for message in st.session_state["chat_messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input field - appears only if OCR result exists
    if prompt := st.chat_input("Ask a question about the text above..."):
        # Add user message to chat history
        st.session_state["chat_messages"].append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Prepare context for the chat model
        context = st.session_state['ocr_result']
        chat_prompt = f"""Based *only* on the following text extracted from an image, please answer the user's question.
                        Do not use any external knowledge. If the answer cannot be found in the text, say so.

                        Extracted Text Context:
                        ---
                        {context}
                        ---

                        User Question: {prompt}
                        """

        # Display thinking indicator and call Ollama for chat response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("Thinking...")
            try:
                response = ollama.chat(
                    model='gemma3:4b', # Or another suitable text model like 'llama3' or 'gemma'
                    messages=[
                        {'role': 'system', 'content': 'You are a helpful assistant answering questions based *only* on the provided text context.'},
                        {'role': 'user', 'content': chat_prompt}
                         # No images needed for the chat part
                    ]
                )
                full_response = response.message.content
                message_placeholder.markdown(full_response)
                # Add assistant response to chat history
                st.session_state["chat_messages"].append({"role": "assistant", "content": full_response})

            except Exception as e:
                 error_message = f"Error getting chat response: {str(e)}"
                 message_placeholder.error(error_message)
                 st.session_state["chat_messages"].append({"role": "assistant", "content": f"Error: Could not process the request. {str(e)}"})


else:
    st.info("Upload an image and click 'Extract Text' in the sidebar to see the results and enable chat.")


# --- Footer ---
st.markdown("---")
st.markdown("Made using Gemma3 Vision Model | [Report an Issue](https://github.com/patchy631/ai-engineering-hub/issues)")