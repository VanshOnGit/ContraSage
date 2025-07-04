<p align="center">
  <img src="logo/ContraSageLogo.png" alt="ContraSage Logo" width="300"/>
</p>

**ContraSage** is a simple but smart tool that finds contradictions in documents.


Just upload your PDFs, text files, or markdown notes and it will highlight if any parts say different or opposite things by asking your own question while it scans.

---

## What It Does

- Finds logical or factual contradictions in writing  
- Works with `.pdf`, `.txt`, and `.md` files  
- Uses a local AI model (Mistral via Ollama) — fast and private  
- Gives clear results with file names and reasons  
- Lets you download a CSV of all contradictions found  

**Note:** Since Ollama runs locally on your machine, ContraSage cannot be deployed to public platforms like Streamlit Cloud.

---

## How to Run

1. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

2. Make sure [Ollama](https://ollama.com) is installed and running with the `mistral` model:
   ```bash
   ollama run mistral
   ```

3. Launch the app:
   ```bash
   streamlit run app.py
   ```

4. Upload your documents  
5. Ask a contradiction-related question. 
6. See results and download them as CSV  

---

## 🛠️ Built With

- **Streamlit** – interactive frontend  
- **LangChain** – document loading and chunking  
- **Guardrails** – structured output validation  
- **Ollama + Mistral** – local LLM for contradiction analysis  
- **FAISS + Hugging Face** – for optional context retrieval  

---

## 👤 Made By

**Vansh Kumar**  
B.Tech AI & Data Science, IIT Gandhinagar  
AI & Data Science Intern @ Tata Communications

📬 [kumar.vansh@iitgn.ac.in](mailto:kumar.vansh@iitgn.ac.in)  
🔗 [LinkedIn](https://www.linkedin.com/in/vansh-ai/)  
🔗 [GitHub](https://github.com/VanshOnGit)
```
