import heapq,math,sys,random

class Node:
    def __init__(self, pawns, rook, bishop, knight, cost, parent):
        self.pawns = pawns
        self.rook = rook
        self.bishop = bishop
        self.knight = knight
        self.cost = cost
        self.parent = parent

    def __eq__(self, other):
        if isinstance(other, Node):            
            return sorted(self.pawns) == sorted(other.pawns) and \
                   self.rook == other.rook and \
                   self.bishop == other.bishop and \
                   self.knight == other.knight
        return False

    def __hash__(self):        
        return hash((tuple(sorted(self.pawns)), self.rook, self.bishop, self.knight)) 

    def __lt__(self, other):
        return self.cost < other.cost           

def minimumSpanningTree(node,mode):
    m=len(node)          
    graph=[]

    for i in range(m):
        for j in range(i+1,m):
            cost=0
            if mode==1:
                cost=1 if node[i][0]==node[j][0] or node[i][1]==node[j][1] else 2                       
            elif mode==2: 
                cost=1 if abs(node[i][0]-node[j][0])==abs(node[i][1]-node[j][1]) else 2
            graph+=[(cost,i,j)]             


    rank=[1]*(m+1)
    parent=[i for i in range(m+1)]

    def find(x):        
        while x!=parent[x]:
            x=parent[x]
        return parent[x]

    def union(x,y):
        px,py=find(x),find(y)
        if px==py:return False
        if rank[px]<rank[py]:x,y=y,x
        rank[px]+=rank[py]
        parent[py]=px 
        return True 

    total_cost=0
    for cost,i,j in sorted(graph):
        if union(i,j):
            total_cost+=cost 
                
    return total_cost

def generate():
    return [['.', '.', 'x', 'x', '1', '.', 'x'], ['.', 'x', 'x', '.', '.', '.', 'R'], ['1', '1', '.', '.', '1', '.', '.'], ['x', 'x', '1', '.', '.', '1', '.'], ['.', '.', '.', '.', 'x', '.', 'x'], ['.', '.', 'x', '.', 'x', '.', '.'], ['.', '.', 'x', '.', '1', '.', '.']]

arguments = sys.argv 
file_name,input_file_name,output_file_name,method,heuristic=arguments
table=generate()
N=len(table)
  
copied=[[i for i in j] for j in table]   



knight_move=[[-1,2],[-2,1],[-2,-1],[-1,-2],[1,-2],[2,-1],[2,1],[1,2]]

bishop_move=[[(-1*i,1*i) for i in range(1,N+1)],[(-1*i,-1*i) for i in range(1,N+1)],
    [(1*i,-1*i) for i in range(1,N+1)],[(1*i,1*i) for i in range(1,N+1)]]

rook_move=[[(0,1*i) for i in range(1,N+1)],[(-1*i,0) for i in range(1,N+1)],
    [(0,-1*i) for i in range(1,N+1)],[(i,0) for i in range(1,N+1)]]

obstacles=set()

initial=Node(set(),None,None,None,0,None)
for i in range(N):
    for j in range(N):
        if table[i][j]=='R':
            initial.rook=(i,j)
        elif table[i][j]=='B':
            initial.bishop=(i,j)
        elif table[i][j]=="K":
            initial.knight=(i,j)
        elif table[i][j]=='.':
            continue
        elif table[i][j]=='x':
            obstacles.add((i,j))            
        else:
            initial.pawns.add((i,j))  

total_expanded_nodes=[0]             

def search():
    queue=[(0,0,initial)]    
    seen=set()

    while queue:     
        _,_,node=heapq.heappop(queue)                        
        if len(node.pawns)==0:
            return node  
        if node.knight:
            expand_knight(node,seen,queue)
        if node.bishop:
            expand_bishop(node,seen,queue)
        if node.rook:
            expand_rook(node,seen,queue)                                 

    return None  

def expand_knight(node,seen,queue):
    x,y=node.knight
    if node in seen:
        return
    total_expanded_nodes[0]+=1    
    seen.add(node)  
    for dx,dy in knight_move:
        new_x,new_y=x+dx,y+dy  
        if not (0<=new_x<N and 0<=new_y<N):
            continue
        if any([(new_x,new_y)==(i,j) for i,j in obstacles]) or (new_x,new_y)==node.bishop or (new_x,new_y)==node.rook:
            continue                     
        new_pawns=tuple(pos for pos in node.pawns if pos!=(new_x,new_y)) 
        new_knight=(new_x,new_y)                
        new_node=Node(new_pawns,node.rook,node.bishop,new_knight,node.cost+6,node)
        if new_node not in seen:   
            new_cost=findCost(new_node)      
            heapq.heappush(queue,(new_cost,total_expanded_nodes[0],new_node))   

def expand_rook(node,seen,queue):
    x,y=node.rook
    if node in seen:
        return
    total_expanded_nodes[0]+=1    
    seen.add(node)
    for change in rook_move:
        for dx,dy in change:
            new_x=x+dx
            new_y=y+dy            
            if not (0<=new_x<N and 0<=new_y<N):
                break
            if any([(new_x,new_y)==(i,j) for i,j in obstacles]) or (new_x,new_y)==node.bishop or (new_x,new_y)==node.knight:
                break
            new_pawns=tuple(pos for pos in node.pawns if pos!=(new_x,new_y))
            new_rook=(new_x,new_y)            
            new_node=Node(new_pawns,new_rook,node.bishop,node.knight,node.cost+8,node)
            if new_node not in seen: 
                new_cost=findCost(new_node)   
                heapq.heappush(queue,(new_cost,total_expanded_nodes[0],new_node))  
                if (new_x,new_y) in node.pawns:
                    break 

def expand_bishop(node,seen,queue):
    x,y=node.bishop
    if node in seen:
        return
    seen.add(node)  
    total_expanded_nodes[0]+=1  
    for change in bishop_move:
        for dx,dy in change:
            new_x=x+dx
            new_y=y+dy 
            if not (0<=new_x<N and 0<=new_y<N):
                break
            if any([(new_x,new_y)==(i,j) for i,j in obstacles]) or (new_x,new_y)==node.knight or (new_x,new_y)==node.rook:
                break
            new_pawns=tuple(pos for pos in node.pawns if pos!=(new_x,new_y))
            new_bishop=(new_x,new_y)            
            new_node=Node(new_pawns,node.rook,new_bishop,node.knight,node.cost+10,node)            
            if new_node not in seen:
                new_cost=findCost(new_node)                     
                heapq.heappush(queue,(new_cost,total_expanded_nodes[0],new_node))   
                if (new_x,new_y) in node.pawns:
                    break    


def findCost(node):
    if method=="UCS":
        return node.cost 
    elif method=="GS" and heuristic=="h1":
        rook_x,rook_y=node.rook
        random=any([rook_x==pi or rook_y==pj for pi,pj in node.pawns])
        return (node.cost+8)+8*((len(node.pawns)+(1 if not random else 0)))
    elif method=="GS" and heuristic=="h2":        
        return h2(node) 
    elif method=="GS" and heuristic=="h1":
        rook_x,rook_y=node.rook 
        random=any([px==rook_x and py==rook_y for px,py in node.pawns])
        return 8*(len(node.pawns)+1 if not random else len(node.pawns)) 
    elif method=="AS" and heuristic=="h2":
        return h2(node)+node.cost 
    elif method=="AS" and heuristic=="h1":
        rook_x,rook_y=node.rook
        random=any([px==rook_x and py==rook_y for px,py in node.pawns])
        return 8*(len(node.pawns)+1 if not random else len(node.pawns))+node.cost       

def h2(node):     
    pawns=node.pawns
    if not pawns:return 0
    res=0
    divide=0
    if node.rook:
        nx,ny=node.rook 
        span=minimumSpanningTree(list(pawns),1)
        go=min(1 if nx==px or ny==py else 2 for px,py in pawns)
        res+=8*(span+go)
        divide+=1
    if node.bishop:
        bx,by=node.bishop
        span=minimumSpanningTree(list(pawns),2)
        go=min(1 if abs(bx-px)==abs(by-py) else 2 for px,py in pawns)
        res+=(span+go)*10
        divide+=1
    return res/divide    

res=search()  
print(res.cost,total_expanded_nodes[0])
     
""" 
f=open("output.txt","w+") 
if res:     
    f.write(str(total_expanded_nodes[0])+'\n')
    f.write(str(res.cost)+'\n')
    f.write(str()+'\n')
    heuristic="h1"
    f.write(str(findCost(initial))+"\n")
    heuristic="h2"
    f.write(str(findCost(initial))+"\n")

    while res.parent:
        table=[["." for _ in range(N)] for _ in range(N)]
        for i,j in res.pawns:
            table[i][j]=copied[i][j]
        for i,j in obstacles:
            table[i][j]="x"
        if res.knight:
            table[res.knight[0]][res.knight[1]]="K"
        if res.rook:
            table[res.rook[0]][res.rook[1]]="R"
        if res.bishop:
            table[res.bishop[0]][res.bishop[1]]="B"
        res=res.parent   
        f.write(str(table)+'\n')
        res=res.parent 
else:
    f.write("No solution can be found\n")

f.flush()
f.close() """    







 



        
          






          






 



        
          





 



        
          




