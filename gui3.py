import PySimpleGUI as psg
import re
import string
# l=psg.Text("Enter Name")

#input pattern
inputP=psg.Text("Pattern Input")
fileuploadPT=psg.Text('Select a file to open:')
fileuploadP = [psg.Input(key='-FILEBROWSEP-', enable_events=True), psg.FileBrowse(target='-FILEBROWSEP-')]

#input text
inputT=psg.Text("Text Input")
fileuploadTT=psg.Text('Select a file to open:')
fileuploadT = [psg.Input(key='-FILEBROWSET-', enable_events=True), psg.FileBrowse(target='-FILEBROWSET-')]

#submit and exit buttons
runB = psg.Button('Run', key='-OK-')
exitB = psg.Button('Exit', key='-Exit-')

#pattern section
file = open("pattern.txt")
text = file.read()
patternT=psg.Text("Conjunctions/Adverb/Adjectives")
patternOutput=psg.Multiline(text, enable_events=True, key='-PATTERNO-', justification='left', size={15,20})

#status section
statusT=psg.Text("Status: ")
statusV=psg.Text(key='-OUTPUT-')

#occurences patterns
detailT=psg.Text("Details: ")
occurT=psg.Text("Occurrences of Patterns")
occurOutput=psg.Multiline('',key='-OCCUR-', size={15,20})

#text section
textT=psg.Text("Text")
textOutput=psg.Multiline('', enable_events=True, key='-TEXTO-', expand_x=True, expand_y=True, justification='left', size={100,30})

#layout
inputLcol = [[patternT],[patternOutput]]
inputRcol = [[statusT, statusV],[occurOutput]]
inputCol = [[inputP],[fileuploadPT],fileuploadP,[inputT],[fileuploadTT], fileuploadT,[runB, exitB],[psg.Column(inputLcol,  vertical_alignment='t'),psg.Column(inputRcol,  vertical_alignment='t')]]

leftCol=[[psg.Column(inputCol)]]
rightCol=[[textT],[textOutput]]

layout=[[psg.Column(leftCol), psg.Column(rightCol)]]
window = psg.Window('English Conjunctions/Adverb/Adjectives Finder', layout, finalize=True)

# highlight text purpose
multiline = window['-TEXTO-']
widget = multiline.Widget
widget.tag_config('HIGHLIGHT', foreground='white', background='blue')

#algorithm
totalCharCount = -1 #store total char count for to trach which character to highlight
hightlight_list = []


# get result using DFA
def dfa_result(input_str, nested_dict):
    # gotWordFound = 'Reject'
    current_dict = nested_dict
    for char in input_str:
        if char in current_dict: #found path to next state
            current_dict = current_dict[char] # go to next state
        else:   #other character goes inside trap state
            if len(current_dict) == 1 and '-2' in current_dict: #trap loop terminate program
                return 'reject'
            else:
                if '-2' in current_dict:
                    current_dict = current_dict['-2'] #go inside trap loop
                else:
                    return 'reject' #handle char other than alphabet
    if '-1' in current_dict: # current state is accepting state
        return 'accept'
    else:
        return 'reject' # current state is not accepting state

# get pattern location and get total char count
def getPatternLoc(input_str, nested_dict, totalCharCount, count, total_list,i):
    
    current_dict = nested_dict
    if (count == 1 ):
        totalCharCount += len(input_str) # store total char count
    elif (count == 3):

        totalCharCount += len(total_list[i])

    for char in input_str:
        if char not in current_dict: # no path to accepting state, will go to terminate state
            return totalCharCount
        current_dict = current_dict[char] # go to next state
    if '-1' in current_dict: # current state is accepting state
        # should highlight this text
        if(count == 1):
            temp = totalCharCount + 1
            temp -= len(input_str)
            hightlight_list.append((temp, totalCharCount + 1))
            return totalCharCount
        elif(count ==3):
            temp = totalCharCount + 1
            temp -= len(total_list[i])
            hightlight_list.append((temp, totalCharCount + 1 + len(input_str) - len(total_list[i])))
            return totalCharCount
        
    else:
        return totalCharCount # current state is not accepting state    

nested_dict = {}

# generate DFA
def generate_dfa(wordlist, nested_dict):
    for layer in wordlist:
        current_dict = nested_dict
        for i, char in enumerate(layer):
            if char not in current_dict:  # check for whether the dfa got output for current state when input = char 

                if (i<len(layer)-1): 
                    current_dict[char] = {'-2':{'-2':'-2'}} # havent reach the accepting state

                else:
                    current_dict[char] = {'-1':'-1'} # reach the accepting state
            
            # go to next state
            current_dict = current_dict[char]

while True:
    event, values = window.read()
    if event == '-OK-':
        for index1, index2 in hightlight_list:
            widget.tag_remove('HIGHLIGHT', f"1.0+{index1}c", f"1.0+{index2}c") #clear previous highlight
        
        nested_dict.clear() #reset all variables
        hightlight_list=[]
        totalCharCount = -1

        pattern = window['-PATTERNO-'].get().lower().strip().split('\n') #read pattern
        generate_dfa(pattern, nested_dict) #generate dfa using pattern
        # print(nested_dict)

        textList = re.split(r'(\s+|['+re.escape(string.punctuation)+'])', values['-TEXTO-'].lower()) #tokenize text
        testList_new = [token for token in textList if token != ''] #remove delimiter

        textList_combine= []

        for i in range(len(testList_new)-2): #handle two words pattern
            textList_combine.append((testList_new[i]+testList_new[i+1]+testList_new[i+2]))
        status = 'reject' #display purpose
        dictOccur = {}
        
        for text in testList_new:
            result = dfa_result(text, nested_dict) #evaluate text using dfa
            if result == 'accept':
                if text not in dictOccur:
                    dictOccur[text] = 1 #store new occurrences of patterns
                else:
                    dictOccur[text] += 1 #increment occurrences of current patterns
                status = 'accept'
            totalCharCount = getPatternLoc(text,nested_dict,totalCharCount,1,testList_new,0) #count total char count

        totalCharCount = -1 #reset

        for i, text in enumerate(textList_combine): #handle two words pattern
            result = dfa_result(text, nested_dict) #evaluate text using dfa
            if result == 'accept':
                if text not in dictOccur:
                    dictOccur[text] = 1 #store new occurrences of patterns
                else:
                    dictOccur[text] += 1 #increment occurrences of current patterns
                status = 'accept'
            totalCharCount = getPatternLoc(text,nested_dict,totalCharCount,3,testList_new,i) #count total char count

        occurDisplay = [f"{key}: {value}" for key, value in dictOccur.items()] #format occurrences of patterns
        result = '\n'.join(occurDisplay) #format occurrences of patterns
        window['-OUTPUT-'].update(status) #update status
        window['-OCCUR-'].update(result) #update occurrences of patterns

        for index1, index2 in hightlight_list: #highlight pattern
            widget.tag_add('HIGHLIGHT', f"1.0+{index1}c", f"1.0+{index2}c")
    
    if event == '-FILEBROWSEP-': #pattern file upload
        filename = values['-FILEBROWSEP-']
        try:
            with open(filename, 'r') as f:
                contents = f.read()
                window['-PATTERNO-'].update(contents)
        except Exception as e:
            psg.popup(f'Error opening file: {e}')

    if event == '-FILEBROWSET-': #text file upload
        filename = values['-FILEBROWSET-']
        try:
            with open(filename, 'r') as f:
                contents = f.read()
                window['-TEXTO-'].update(contents)
        except Exception as e:
            psg.popup(f'Error opening file: {e}')

    
    if event == psg.WIN_CLOSED or event == '-Exit-':
        break