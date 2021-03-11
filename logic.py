from asteval import Interpreter
aeval = Interpreter()
def textupdate(newtext):
    # pos=[(m.start()) for m in re.finditer("\n",newtext)]
    # pos.insert(0,-1)
    # lines = []
    # for i in range(len(pos)-1):
    #     lines.append(newtext[pos[i]+1:pos[i+1]])

    lines=newtext.split("\n")
    math=[i for i in range(len(lines)) if lines[i].startswith("eval::")]
    for i in math:
        mathstring=lines[i][6:]
        evalout=aeval(mathstring)
        lines.insert(i+1, "output;;;;"+str(evalout))#make a special character so people can't just input this in text
    return lines