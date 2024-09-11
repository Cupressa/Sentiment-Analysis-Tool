To use the OpenAI API, you may follow the instructions found at the following link: https://platform.openai.com/docs/quickstart

Alternatively, you may follow the steps below:
First, generate an OpenAI API key, then set it using the following command on your terminal in the sentiment analysis tool file location:
MacOS/Linux: export OPENAI_API_KEY="your_api_key_here"
Windows: setx OPENAI_API_KEY "your_api_key_here"

Next, activate the virtual environment included in the repository with the following command in the terminal:
MacOS/Linux: source .\openai-env\Scripts\Activate
Windows: openai-env\Scripts\Activate

Lastly, run the script in your terminal and follow the prompts:
MacOS/Linux: python3 sentimentAnalysisTool.py
Windows: python sentimentAnalysisTool.py