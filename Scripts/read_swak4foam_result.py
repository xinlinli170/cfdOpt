class Swak4FoamResult(object):
    """ Class for reading the results of function objects """
    def __init__(self, path):
        self.filePath = path
        self.getResult()
    
    def setPath(self,path):
        self.filePath = path
    
    def getLastResult(self):
        #Check the availability of file path 
        if self.filePath == "":
            print "No file path!"
    
        rawData = open(self.filePath).readlines()
        
        
        firstLine = rawData.pop(0) #The header of the table
        lastLine = rawData.pop()   #The latest data of the table
        
        firstLine = firstLine.split(' ')
        lastLine = lastLine.split(' ')    
        
        header = []
        data = []
        
        for word in firstLine:
            if word != "":
                if word[-1] == '\n':
                    header.append(word[:-1])
                else:
                    header.append(word)
        header.remove('#')
        
        for word in lastLine:
            if word != "":
                if word[-1] == '\n':
                    data.append(word[:-1])
                else:
                    data.append(word)
        self.data = dict(zip(header,data))

    def getResult(self):
    
        #Check the availability of the file path
        if self.filePath == "":
            print "No file path!"
        
        #Read the raw data
        rawData = open(self.filePath).readlines()
        
        #Pop the first line as the header of the data
        firstLine = rawData.pop(0)
        firstLine = firstLine.split(' ')
        
        header = []
        data = []

        for word in firstLine:
            if word != "":
                if word[-1] == '\n':
                    header.append(word[:-1])
                else:
                    header.append(word)
        header.remove('#')
        
        averageSteps = 300

        #Initialize the data
        lastLine = rawData.pop()
        lastLine = lastLine.split(' ')
        
        for word in lastLine:
            if word != "":
                if word[-1] == "\n":
                    data.append(float(word[:-1]))
                else:
                    data.append(float(word))

        for i in range(1, averageSteps):
            #Pop the last line of the raw data one by one
            data_tmp = []
            lastLine = rawData.pop()
            lastLine = lastLine.split(' ')

            for word in lastLine:
                if word != "":
                    if word[-1] == "\n":
                        data_tmp.append(float(word[:-1]))
                    else:
                        data_tmp.append(float(word))
            #Accmulate the data
            for j in range(len(data_tmp)):
                data[j] += data_tmp[j]
        #Calculate the average number as the result
        for j in range(len(data)):
            data[j] = data[j] / float(averageSteps)

        self.data = dict(zip(header,data))
