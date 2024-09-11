from openai import OpenAI
from tkinter import filedialog as fd
import datetime
import csv

# Jonah Lum
# 7/5/24

"""
Changes From V1
- Generalized format of file input
  - Can group responses by ip even if input file is not sorted
  - Utilizes csv library to accommodate for csv file formatting
    - Note: file should contain the fields in the following order: IP/ID, term, response
- Generalized name of output file
- Use of GPT-4o

Future work for V3
- Confirmation of fields
- Allow user-input prompts? or selection of prompts for term/term+response analysis
- Selection of GPT model?
- Preventing invalid runs from occurring
"""

client = OpenAI()

def get_sentiment(response):
    systemPrompt = "Each of the following 5 lines contains a word choice, sometimes followed by an explanation for the choice. For each line, provide a sentiment analysis score for the word between 0.00-1.00 (to two decimal places), and then an adjusted score for the word based on the explanation. Include your confidence in the accuracy of that score (low, medium, high). Additionally, provide a carefully crafted contextual explanation for the sentiment score that is related to the meaning of the text."
    completion = client.chat.completions.create(
        model = "gpt-4o",
        messages = [
            {
                "role": "system",
                "content": systemPrompt
                },
            {
                "role": "user",
                "content": response
                }
            ]
        )
    return completion.choices[0].message.content

def read_data():
    filePath = fd.askopenfilename()
    with open(filePath, 'r', encoding="UTF-8-sig") as file:
        reader = csv.DictReader(file)
        responseDict = {}
        fields = reader.fieldnames
        for line in reader:
            if(line[fields[0]] in responseDict.keys()):
                responseDict[line[fields[0]]] = responseDict[line[fields[0]]] + '"' + line[fields[1]].replace("\n", "") + '","' + line[fields[2]].replace("\n", "") + '"\n'
            else:
                responseDict[line[fields[0]]] = '"' + line[fields[1]].replace("\n", "") + '","' + line[fields[2]].replace("\n", "") + '"\n'
        return responseDict

def analyze_data(responseDict, usingAPI):
    sentiments = []
    for key in responseDict.keys():
        if(usingAPI):
            sentiments.append("\n" + key + "\n")
            sentiments.append(str(get_sentiment(responseDict[key])))
        else:
            sentiments.append(key + "\n")
            sentiments.append(responseDict[key])
    return sentiments
        
def main():
    sentiments = analyze_data(read_data(), True)
    outFile = open("PDT_Analysis_" + datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S").replace(" ", "_").replace("/", "-").replace(":", ";") + ".txt", "w", encoding="UTF-8-sig")
    outFile.writelines(sentiments)
    outFile.close()

if __name__ == "__main__":
    main()
    	
