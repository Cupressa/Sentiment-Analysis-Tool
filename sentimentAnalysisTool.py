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

Changes From V2
- Allows for different methods of analysis
  - Term scoring grouped by user (aggregate score)
  - Sentiment scoring grouped by user (aggregate score)
  - Term + sentiment scoring grouped by user (aggregate score)
  - Individual term scoring
  - Individual sentiment scoring
  - Individual term + sentiment scoring
  | Top N improvement and strength analysis of entire dataset (if it fits in the context window)
  | Top N improvement and strength cross-sectional analysis
- CSV formatting
- Selection of GPT Model

Future work for V3/V4
- Confirmation of fields
- Preventing invalid runs from occurring
- More accurate output file names
"""

client = OpenAI()

systemPrompts = [
    [
        "Each of the following lines contains a word. Based on this data, please provide a singular sentiment analysis score for all of the words between 0.00-1.00 (to two decimal places). Include your confidence in the accuracy of that score (low, medium, high). Additionally, provide a carefully crafted contextual explanation for the sentiment score that is related to the meaning of the words. Please provide your response in a text-based csv format, with columns for the score, confidence, and explanation. In the event that words are not provided, please respond with 0.00,none,none. Please do not provide any other response aside from the csv formatted data. Please do not evaluate each line individually, evaluate all of the lines as a whole:",
        "Each of the following lines contains a statement. Based on this data, please provide a singular sentiment analysis score for all of the statements between 0.00-1.00 (to two decimal places). Include your confidence in the accuracy of that score (low, medium, high). Additionally, provide a carefully crafted contextual explanation for the sentiment score that is related to the meaning of the texts. Please provide your response in a text-based csv format, with columns for the score, confidence, and explanation. In the event that statements are not provided, please respond with 0.00,none,none. Please do not provide any other response aside from the csv formatted data. Please do not evaluate each line individually, evaluate all of the lines as a whole:",
        "Each of the following lines contains a word choice, sometimes followed by an explanation for the choice. Based on this data, please provide a singular sentiment analysis score for all of the words between 0.00-1.00 (to two decimal places), and then a singular adjusted score for all of the words based on all of the explanations. In the event that explanations are not provided with the word choices, please make the adjusted score the same as the original. Include your confidence in the accuracy of that score (low, medium, high). Additionally, provide a carefully crafted contextual explanation for the sentiment score that is related to the meaning of the texts. Please provide your response in a text-based csv format, with columns for the original score, adjusted score, confidence, and explanation. Please do not provide any other response aside from the csv formatted data. Please do not evaluate each line individually, evaluate all of the lines as a whole:",
        ],
    [
        "The following lines contain words. For each word, provide a sentiment analysis score between 0.00-1.00 (to two decimal places). Include your confidence in the accuracy of that score (low, medium, high). Additionally, provide a carefully crafted contextual explanation for the sentiment score that is related to the meaning of the word. Please provide your response in a text-based csv format, with columns for the word, score, confidence, and explanation. If no word is provided, please give the response 0.00,none,none. Please do not provide any other response aside from the csv formatted data:",
        "The following lines contain statements. For each statement, provide a sentiment analysis score between 0.00-1.00 (to two decimal places). Include your confidence in the accuracy of that score (low, medium, high). Additionally, provide a carefully crafted contextual explanation for the sentiment score that is related to the meaning of the text. Please provide your response in a text-based csv format, with columns for the score, confidence, and explanation. If no statement is provided, please give the response 0.00,none,none. Please do not provide any other response aside from the csv formatted data:",
        "The following lines contain word choices, which are sometimes followed by explanations for the choice. For these lines, provide a sentiment analysis score for each word between 0.00-1.00 (to two decimal places), and then an adjusted score for the word based on the explanation. Include your confidence in the accuracy of that score (low, medium, high). Additionally, provide a carefully crafted contextual explanation for the sentiment score that is related to the meaning of the text. Please provide your response in a text-based csv format, with columns for the word, original score, adjusted score, confidence, and explanation. Please do not provide any other response aside from the csv formatted data. Please provide only one response per line, which analyzes the provided term-explanation pair:",
        ],
    [
        "Based on the following user-based responses towards a assistive farming application, determine 5 areas of improvement for the application. Please give your response in a csv format, with columns for the topic of improvement and your explanation. Please ensure that your explanation does not contain commas: ",
        "",
        ],
    ]

GPTmodels = ["gpt-4o", "gpt-4", "gpt-3.5-turbo"]

def get_sentiment(modelType, response, promptIndex, dataTypeInt):
    completion = client.chat.completions.create(
        model = modelType,
        messages = [
            {
                "role": "system",
                "content": systemPrompts[promptIndex][dataTypeInt]
                },
            {
                "role": "user",
                "content": response
                }
            ]
        )
    return completion.choices[0].message.content

def read_and_group_data(dataType):
    filePath = fd.askopenfilename()
    with open(filePath, 'r', encoding="UTF-8-sig") as file:
        reader = csv.DictReader(file)
        responseDict = {}
        fields = reader.fieldnames
        for line in reader:
            match(dataType):
                case("1"):
                    if(line[fields[0]] in responseDict.keys()):
                        responseDict[line[fields[0]]] = responseDict[line[fields[0]]] + line[fields[1]].replace("\n", "") + '\n'
                    else:
                        responseDict[line[fields[0]]] = line[fields[1]].replace("\n", "") + '\n'
                case("2"):
                    if(line[fields[0]] in responseDict.keys()):
                        responseDict[line[fields[0]]] = responseDict[line[fields[0]]] + line[fields[2]].replace("\n", "") + '\n'
                    else:
                        responseDict[line[fields[0]]] = line[fields[2]].replace("\n", "") + '\n'
                case("3"):
                    if(line[fields[0]] in responseDict.keys()):
                        responseDict[line[fields[0]]] = responseDict[line[fields[0]]] + '"' + line[fields[1]].replace("\n", "") + '","' + line[fields[2]].replace("\n", "") + '"\n'
                    else:
                        responseDict[line[fields[0]]] = '"' + line[fields[1]].replace("\n", "") + '","' + line[fields[2]].replace("\n", "") + '"\n'
                case _:
                    return {}, 0
        return responseDict, int(dataType) - 1

def read_data(dataType):
    filePath = fd.askopenfilename()
    with open(filePath, 'r', encoding="UTF-8-sig") as file:
        reader = csv.DictReader(file)
        responses = []
        currentPrompt = ""
        fields = reader.fieldnames
        for line in reader:
            if(len(currentPrompt) >= 2000):
                responses.append(currentPrompt)
                # print("=== START OF PROMPT ===")
                # print(currentPrompt)
                # print("=== END OF PROMPT ===")
                currentPrompt = ""
            match(dataType):
                case("1"):
                    currentPrompt += line[fields[1]].replace("\n", "") + "\n"
                case("2"):
                    currentPrompt += line[fields[2]].replace("\n", "") + "\n"
                case("3"):
                    currentPrompt += ('"' + line[fields[1]].replace("\n", "") + '","' + line[fields[2]].replace("\n", "") + '"\n')
                case _:
                    return [], 0
        responses.append(currentPrompt)
    return responses, int(dataType) - 1

def analyze_data(usingAPI):
    sentiments = []
    if(usingAPI):
        print("Please select a GPT model")
        for i in range(len(GPTmodels)):
            print("[{0}] - {1}".format(i+1, GPTmodels[i]))
        modelIndex = input()
        try:
            modelIndex = int(modelIndex) - 1
            if((modelIndex < 0) or (modelIndex >= len(GPTmodels))):
                raise Exception("Input out of range")
        except:
            print("Invalid input")
            return []
    analysisIndex = input("""Please select an analysis method:
[1] - User-grouped analysis
[2] - Individual statement analysis
[3] - Improvement and strength analysis
""")
    match(analysisIndex):
        case("1"):
            dataType = input("""Please select the data to analyze:
[1] - Term scoring
[2] - Explanation scoring
[3] - Term + explanation scoring
""")
            responseDict, dataTypeInt = read_and_group_data(dataType)
            if(len(responseDict) == 0):
                return []
            promptIndex = int(analysisIndex) - 1
            print(systemPrompts[promptIndex][dataTypeInt])
            for key in responseDict.keys():
                if(usingAPI):
                    print("=== START OF CURRENT DATA ===")
                    print(responseDict[key])
                    print("=== END OF CURRENT DATA ===")
                    sentiments.append("\n" + key + ",")
                    sentiments.append(str(get_sentiment(GPTmodels[modelIndex], responseDict[key], promptIndex, dataTypeInt)).replace('"', "'"))
                else:
                    sentiments.append(key + "\n")
                    sentiments.append(responseDict[key])              
        case("2"):
            dataType = input("""Please select the data to analyze:
[1] - Term scoring
[2] - Explanation scoring
[3] - Term + explanation scoring
""")
            responses, dataTypeInt = read_data(dataType)
            if(len(responses) == 0):
                return []
            promptIndex = int(analysisIndex)-1
            print(systemPrompts[promptIndex][dataTypeInt])
            print("Number of runs:", len(responses))
            for response in responses:
                if(usingAPI):
                    print("=== START OF CURRENT DATA ===")
                    print(response)
                    print("=== END OF CURRENT DATA ===")
                    sentiments.append(str(get_sentiment(GPTmodels[modelIndex], response, promptIndex, dataTypeInt)).replace('"', "'") + "\n")
                else:
                    return responses
        case _:
            print("Invalid selection")
            return []
    return sentiments
        
def main():
    usingAPI = input("Use openAI API? (y/n): ").lower()[0] == 'y'
    sentiments = analyze_data(usingAPI)
    if(len(sentiments) != 0):
        outFileName = "PDT_Analysis_" + datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S").replace(" ", "_").replace("/", "-").replace(":", ";") + ".txt"
        outFile = open(outFileName, "w", encoding="UTF-8-sig")
        outFile.writelines(sentiments)
        outFile.close()

if __name__ == "__main__":
    main()
    	
