from openai import OpenAI
from tkinter import filedialog as fd
client = OpenAI()

def get_sentiment(response):
    systemPrompt = "Each of the following 5 lines contains a word choice followed by an explanation for the choice. For each line, provide a sentiment analysis score for the word between 0.00-1.00 (to two decimal places), and then an adjusted score for the word based on the explanation."
    completion = client.chat.completions.create(
        model = "gpt-3.5-turbo",
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

def sortedDataReader():
    filePath = fd.askopenfilename()
    inFile = open(filePath, 'r')
    data = inFile.readlines()
    inFile.close()
    return data[1:]

def analyze_data(data):
    prevIP = ""
    responseString = ""
    sentiments = []
    for line in data:
        line = line.replace(",", "").split("|")
        IP = line[2]
        if(prevIP == IP):
            responseString += '"' + line[0].replace("\n", "") + '","' + line[1].replace("\n", "") + '"\n'
        else:
            #sentiments.append(responseString)
            sentiments.append("\n" + IP)
            sentiments.append(str(get_sentiment(responseString)))
            prevIP = IP
            responseString = '"' + line[0].replace("\n", "") + '","' + line[1].replace("\n", "") + '"\n'
    #sentiments.append(responseString)
    sentiments.append("\n" + IP)
    sentiments.append(str(get_sentiment(responseString)))
    return sentiments

def main():
    outFile = open("CARMA_Analysis.txt", "w")
    sentiments = analyze_data(sortedDataReader())
    outFile.writelines(sentiments)
    outFile.close()

if __name__ == "__main__":
    main()
    	
