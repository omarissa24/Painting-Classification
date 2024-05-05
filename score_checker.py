import argparse

class Scorer():

    def __init__(self,input_file,sub_file):

        self.frameglasses = {}
        self.usedframeglasses = {}
        self.sub = open(sub_file,"r")
        self.actual_frameglass = []
        self.prev_frameglass = []
        self.score = 0
        self.debug = False

        f = open(input_file, "r")
        for count, i in enumerate(f.readlines()[1:]):
            self.frameglasses[count] = i.split()
            self.usedframeglasses[count] = False

    def frameglass_checking(self,frameglass_elements):

        if len(frameglass_elements) == 1:
            if self.frameglasses[int(frameglass_elements[0])][0] == "L":
                if (self.usedframeglasses[int(frameglass_elements[0])] == True):
                    raise Exception('Error:', 'Multiple use of frameglasses ' + frameglass_elements[0])
                tags = self.frameglasses[int(frameglass_elements[0])][2:]
                self.usedframeglasses[int(frameglass_elements[0])] = True
                return tags
            else:
                raise Exception('Error:', 'THE TYPE OF PAINTING')
        elif len(frameglass_elements) == 2:
            if self.frameglasses[int(frameglass_elements[0])][0] == "P" and self.frameglasses[int(frameglass_elements[1])][0] == "P":
                if self.usedframeglasses[int(frameglass_elements[0])] == True:
                    raise Exception('Error:', 'Multiple use of frameglasses ' + frameglass_elements[0])
                if self.usedframeglasses[int(frameglass_elements[1])] == True:
                    raise Exception('Error:', 'Multiple use of frameglasses ' + frameglass_elements[1])
                tags = list(set(self.frameglasses[int(frameglass_elements[0])][2:]+self.frameglasses[int(frameglass_elements[1])][2:]))
                self.usedframeglasses[int(frameglass_elements[0])] = True
                self.usedframeglasses[int(frameglass_elements[1])] = True
                return tags
            else:
                raise Exception('Error:', 'THE TYPE OF PAINTING')
        else:
            raise Exception('Error:', 'THE TYPE OF PAINTING')

    def exhibition_walk(self):

        for frame in self.sub.readlines()[1:]:

            self.actual_frameglass = self.frameglass_checking(frame.strip().split())
            if self.prev_frameglass != []:
                self.scorer(self.actual_frameglass, self.prev_frameglass)
            self.prev_frameglass = self.actual_frameglass

    def scorer(self,frame1,frame2):

        intersection = list(set(frame1).intersection(frame2))
        val1 = len(intersection)
        val2 = len(frame1)-len(intersection)
        val3 = len(frame2)-len(intersection)
        self.score += min(val1,val2,val3)

def main():
    parser = argparse.ArgumentParser(description="Script to check the score")
    parser.add_argument("input", type=str, help="The path to the input file")
    parser.add_argument("submit", type=str, help="The path to the submitted file")

    args = parser.parse_args()

    score = Scorer(args.input, args.submit)
    score.exhibition_walk()
    print("Final score = %s" %score.score)



if __name__ == "__main__":
    try:
        main()
    except Exception as err:
        print(err)          # __str__ allows args to be printed directly,
