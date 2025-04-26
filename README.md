# Gemma-3 OCR App

This project leverages Gemma-3 vision capabilities and Streamlit to create a 100% locally running computer vision app that can perform both OCR and extract structured text from the image.

In fact all the version of Gemma3 models except 1b are vision, due to local constraints, i will use only the 4 billion model.

![Alt Text](https://storage.googleapis.com/gweb-developer-goog-blog-assets/images/comparison-chart-gemma-models.original.jpg)

You can choose from a variaty of models using ollama : 

[Link Text](https://ollama.com/search?c=vision)

## Installation and setup

first, you should have installed ollama

**Setup Ollama**:
   ```bash
   ollama serve
   # pull gemma-3 vision model
   ollama run gemma3:1b
   ```

**Install Dependencies**:
   Ensure you have Python 3.11 or later installed.
   ```bash
   pip install -r requirements.txt 
   or
   pip install streamlit ollama pillow
   ```

---


