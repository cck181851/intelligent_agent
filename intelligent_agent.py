import heapq,math,sys,random

#node representing the real-world configuration
class Node:
    def __init__(self, pawns, rook, bishop, knight, cost, parent):
        self.pawns = pawns
        self.rook = rook
        self.bishop = bishop
        self.knight = knight
        self.cost = cost
        self.parent = parent

#we have to make the node  class comparable to be able to put them in the queue
    def __eq__(self, other):
        if isinstance(other, Node):            
            return sorted(self.pawns) == sorted(other.pawns) and \
                   self.rook == other.rook and \
                   self.bishop == other.bishop and \
                   self.knight == other.knight
        return False
#modifying the hash property so that nodes with the same configuration habe the same name. 
    def __hash__(self):        
        return hash((tuple(sorted(self.pawns)), self.rook, self.bishop, self.knight)) 

#similar to __eq__, we have to make the nodes comparable
    def __lt__(self, other):
        return self.cost < other.cost           

#minimum spanning tree algorithm is used for h2 heuristic function. 
#mode determines whether it is being used for rook or bishop
def minimumSpanningTree(node,mode):
    m=len(node)          
    graph=[]

    for i in range(m):
        for j in range(i+1,m):
            cost=0
            if mode==1:
                cost=1 if node[i][0]==node[j][0] or node[i][1]==node[j][1] else 2  #two or one moves to reach pawn                    
            elif mode==2: 
                cost=1 if abs(node[i][0]-node[j][0])==abs(node[i][1]-node[j][1]) else 2 #two or one moves to reach pawn
            graph+=[(cost,i,j)]             


    rank=[1]*(m+1)
    parent=[i for i in range(m+1)]

#union-find part of the MST algorithm    
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

#connecting all the parts with the lowest cost
    total_cost=0
    for cost,i,j in sorted(graph):
        if union(i,j):
            total_cost+=cost 
                
    return total_cost

#used for test purposes
def generate():
    return [[".","R",".",".","."],[".","1","x",".","."],[".","2","x",".","."],[".","3","x",".","."],
            [".","4","5","6","."]]

arguments = sys.argv 
#file_name,input_file_name,output_file_name,method,heuristic=arguments
heuristic,method="h1","UCS"
table=generate()
N=len(table)
  
copied=[[i for i in j] for j in table]   

#possible moves with the required orders
knight_move=[[-1,2],[-2,1],[-2,-1],[-1,-2],[1,-2],[2,-1],[2,1],[1,2]]

bishop_move=[[(-1*i,1*i) for i in range(1,N+1)],[(-1*i,-1*i) for i in range(1,N+1)],
    [(1*i,-1*i) for i in range(1,N+1)],[(1*i,1*i) for i in range(1,N+1)]]

rook_move=[[(0,1*i) for i in range(1,N+1)],[(-1*i,0) for i in range(1,N+1)],
    [(0,-1*i) for i in range(1,N+1)],[(i,0) for i in range(1,N+1)]]

obstacles=set()

#creating the tree from the given graph 
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

#a trick to avoid passing the value to all the function that need it
total_expanded_nodes=[0]             

#iterative search algorithm
def search():
    queue=[(0,0,initial)]    
    seen=set()

    while queue:     
        _,_,node=heapq.heappop(queue)                        
        if len(node.pawns)==0:
            return node 
        #we first need to expand knight,then bishop and rook,as required  
        if node.knight:
            expand_knight(node,seen,queue)
        if node.bishop:
            expand_bishop(node,seen,queue)
        if node.rook:
            expand_rook(node,seen,queue)                                 

    return None  

#implemtation of the expand_knight algorithm used in the search algorithm
def expand_knight(node,seen,queue):
    x,y=node.knight
    if node in seen:
        return #avoid loopy path
    total_expanded_nodes[0]+=1    
    seen.add(node) #add the node to the seen to avoid loopy paths 
    for dx,dy in knight_move:
        new_x,new_y=x+dx,y+dy  #directions
        if not (0<=new_x<N and 0<=new_y<N):
            continue # do not get out of the board
        if any([(new_x,new_y)==(i,j) for i,j in obstacles]) or (new_x,new_y)==node.bishop or (new_x,new_y)==node.rook:
            continue #avoid hitting into another stone or obstacles                    
        new_pawns=set(pos for pos in node.pawns if pos!=(new_x,new_y)) 
        new_knight=(new_x,new_y)     
        #create the new configuration           
        new_node=Node(new_pawns,node.rook,node.bishop,new_knight,node.cost+6,node)
        if new_node not in seen:   #node is not in the seen set,thus go on,
            new_cost=findCost(new_node)      #find the h-cost of the node
            heapq.heappush(queue,(new_cost,total_expanded_nodes[0],new_node)) #add the new node to the priority queue   

#implementation of the expand_rook algorithm used in the search algorithm
def expand_rook(node,seen,queue):
    x,y=node.rook
    if node in seen: # it is visited before, thus skip it to avoid loopy paths
        return
    total_expanded_nodes[0]+=1 #increase the number of nodes expanded thus far    
    seen.add(node)
    for change in rook_move:
        for dx,dy in change:
            new_x=x+dx
            new_y=y+dy            
            if not (0<=new_x<N and 0<=new_y<N):
                break #do not get out of the table
            if any([(new_x,new_y)==(i,j) for i,j in obstacles]) or (new_x,new_y)==node.bishop or (new_x,new_y)==node.knight:
                break #do not hit into other stones or the obstacles
            new_pawns=set(pos for pos in node.pawns if pos!=(new_x,new_y))                                                             
            new_rook=(new_x,new_y)   
            #create the new configuration         
            new_node=Node(new_pawns,new_rook,node.bishop,node.knight,node.cost+8,node)
            if new_node not in seen: 
                new_cost=findCost(new_node)   
                heapq.heappush(queue,(new_cost,total_expanded_nodes[0],new_node))  
                if (new_x,new_y) in node.pawns: #if the stone hit into a pawn, then it cannot go on further 
                    break 

#same implementation for the expand_bishop part of the search algorithms
def expand_bishop(node,seen,queue):
    x,y=node.bishop
    if node in seen: #avoid loopy paths 
        return
    seen.add(node)  
    total_expanded_nodes[0]+=1  #increase the number of the nodes expanded  
    for change in bishop_move:
        for dx,dy in change:
            new_x=x+dx
            new_y=y+dy 
            if not (0<=new_x<N and 0<=new_y<N):
                break #do not get out of the table 
            if any([(new_x,new_y)==(i,j) for i,j in obstacles]) or (new_x,new_y)==node.knight or (new_x,new_y)==node.rook:
                break #do not hit into other stones or obstacles
            new_pawns=set(pos for pos in node.pawns if pos!=(new_x,new_y))
            new_bishop=(new_x,new_y)            
            #create the new configuration
            new_node=Node(new_pawns,node.rook,new_bishop,node.knight,node.cost+10,node)            
            if new_node not in seen:
                new_cost=findCost(new_node)                     
                heapq.heappush(queue,(new_cost,total_expanded_nodes[0],new_node))   
                if (new_x,new_y) in node.pawns: #if the stone hit into a pawn, it cannot go on further
                    break    

#fuunction to find the f-cost associated with the new node
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

#my heuristic function h2
def h2(node):     
    pawns=node.pawns
    if not pawns:return 0 #the search is over as there is no pawn left
    res=0
    divide=0 #this is used to get the mean of the calculated cost
    k_check=0 #this is used to find the number of pawns adjacent to the knight
    if node.knight:
        kx,ky=node.knight
        for dx,dy in knight_move:
            new_kx,new_ky=kx+dx,ky+dy
            if (new_kx,new_ky) in pawns: #adjacent pawn found
                pawns.remove((new_kx,new_ky)) #remove it from the set
                k_check+=1 
                divide+=1
            if k_check==2: #do not go on further as this will increase the cost as hitting into each pawn takes 2 actions 
                break    
    if node.rook:
        nx,ny=node.rook 
        span=minimumSpanningTree(list(pawns),1) #find the minimum cost of connection all the points,which reduces to  
        go=min(1 if nx==px or ny==py else 2 for px,py in pawns) #reaching all the pawns with minimum cost
        res+=8*(span+go) #each action takes 8 points
        divide+=1 #number of components increased
    if node.bishop:
        bx,by=node.bishop #the same process for bishop
        span=minimumSpanningTree(list(pawns),2)
        go=min(1 if abs(bx-px)==abs(by-py) else 2 for px,py in pawns)
        res+=(span+go)*10
        divide+=1
    return res/divide+k_check*6  # multiply the k_check by 6 as each action takes 6 points for the knight  

#return the result and print it on the screen
res=search()
total_cost=res.cost  
tables=[]
while res:
    temp=[["." for _ in range(N)] for _ in range(N)]
    for x,y in res.pawns:
        temp[x][y]=copied[x][y]
    if res.knight:
        temp[res.knight[0]][res.knight[1]]="K"
    if res.bishop:
        temp[res.bishop[0]][res.bishop[1]]="B"
    if res.rook:
        temp[res.rook[0]][res.rook[1]]="R"
    for x,y in obstacles:
        temp[x][y]="x"
    tables+=[temp]
    res=res.parent 

fw=open("output.txt","w+")
fw.write("expanded:"+str(total_expanded_nodes[0])+'\n')
fw.write("path cost:"+str(total_cost)+'\n')
heuristic="h1"
fw.write("h1:"+str(findCost(initial))+'\n')
heuristic="h2"
fw.write("h2:"+str(findCost(initial))+'\n')
for table in tables[::-1]:
    for t in table:
        fw.write(str(t)+'\n')        
    fw.write("*************************\n")    

fw.flush()
fw.close()  


 



        
          




