import json
import matplotlib.pyplot as plt

with open('ban.json',encoding='utf8') as f:
    ban = json.load(f)
with open('pick.json',encoding='utf8') as ddd:
    pick = json.load(ddd)



def draw_BAN():
    BAN = []
    for x in ban:
        if len(BAN)<5:  BAN.append(x)
    #用來正常顯示中文標籤的 
    plt.rcParams[ 'font.sans-serif'] =['Microsoft YaHei']
    # #解決保存圖像是符號'-'顯示為方塊的問題 
    plt.rcParams[ 'axes.unicode_minus'] = False

    class1 = [float(ban[x].replace('%','')) for x in BAN]
    class2 = [float(pick[y].replace('%','')) for y in BAN]

    
    plt.bar(BAN,class1  , label = '禁用率', align = "edge", width = 0.35)
    plt.bar(BAN,class2 , label = '選用率', align = "edge", width = -0.35)
    plt.legend() #要使用label要加這行
    plt.title("禁用率前五名")
    plt.xlabel("英雄")
    plt.ylabel("%")
    for i in range(len(class1)):
        plt.text(i, class1[i]+0.5, str(class1[i]))
    plt.savefig('Ban_rank.png')
    plt.close()
    #plt.show()

def draw_PICK():

    PICK = []
    for x in pick:
        if len(PICK)<5:  PICK.append(x)

    #用來正常顯示中文標籤的 
    plt.rcParams[ 'font.sans-serif'] =['Microsoft YaHei']
    # #解決保存圖像是符號'-'顯示為方塊的問題 
    plt.rcParams[ 'axes.unicode_minus'] = False

    class3 = [float(pick[y].replace('%','')) for y in PICK]
    class4 = [float(ban[x].replace('%','')) for x in PICK]
    
    
    plt.bar(PICK,class3 , label = '選用率', align = "edge", width = 0.35)
    plt.bar(PICK,class4  , label = '禁用率', align = "edge", width = -0.35)
    
    plt.legend() #要使用label要加這行
    plt.title("選用率前五名")
    plt.xlabel("英雄")
    plt.ylabel("%")
    for i in range(len(class3)):
        plt.text(i, class3[i]+0.5, str(class3[i]))
    plt.savefig('Pick_rank.png')
    plt.close()
    #plt.show()

if __name__=='__main__':
    draw_BAN()
    draw_PICK()