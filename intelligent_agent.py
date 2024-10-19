import heapq,math,sys,random,collections,functools

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
        return sorted(self.pawns) == sorted(other.pawns) and \
                   self.rook == other.rook and \
                   self.bishop == other.bishop and \
                   self.knight == other.knight
        return False
#modifying the hash property so that nodes with the same configuration habe the same name. 
    def __hash__(self):        
        return hash((tuple(sorted(self.pawns)), self.rook, self.bishop, self.knight)) 

    def __str__(self):
        return hash((tuple(sorted(self.pawns)), self.rook, self.bishop, self.knight)) 

#similar to __eq__, we have to make the nodes comparable
    def __lt__(self, other):
        return self.cost < other.cost  

#minimum spanning tree algorithm is used for h2 heuristic function. 
#mode determines whether it is being used for rook or bishop
              

arguments = sys.argv 
file_name,input_file_name,output_file_name,method,heuristic=arguments
table=[i.strip().split() for i in open(input_file_name,"r+").readlines()]
N=len(table)
  
copied=[[i for i in j] for j in table]   

#possible moves with the required orders
knight_move=[[2,-1],[1,-2],[-1,-2],[-2,-1],[-2,1],[-1,2],[1,2],[2,1]]

bishop_move=[[(1*i,-1*i) for i in range(1,N+1)],[(-1*i,-1*i) for i in range(1,N+1)],
    [(-1*i,1*i) for i in range(1,N+1)],[(1*i,1*i) for i in range(1,N+1)]]

rook_move=[[(i,0) for i in range(1,N+1)],[(0,-i) for i in range(1,N+1)],
    [(-i,0) for i in range(1,N+1)],[(0,i) for i in range(1,N+1)]]

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
        elif table[i][j]=='x':
            obstacles.add((i,j))            
        elif table[i][j].isdigit():
            initial.pawns.add((i,j)) 

#a trick to avoid passing the value to all the function that need it
total_expanded_nodes=[0]             
order=[0]

@functools.cache
def shortestPath(start,end,mode):    
    queue=collections.deque([start])
    seen=set()  
    cur=0  
    while queue:
        for _ in range(len(queue)):
            x,y=queue.popleft()
            if (x,y) in seen:
                continue 
            if (x,y)==end:
                return cur
            seen.add((x,y))            
            for direction in [rook_move,bishop_move][mode]:
                for dx,dy in direction:
                    nx,ny=x+dx,y+dy 
                    if (nx,ny) in obstacles or nx<0 or nx>=N or ny<0 or ny>=N:
                        break
                    if (nx,ny) in seen:
                        continue 
                    queue.append((nx,ny))
        cur+=1
    return math.inf  


#iterative search algorithm
def search():
    queue=[(0,0,initial)]    
    seen=set()
    while queue:     
        _,_,node=heapq.heappop(queue)                        
        if len(node.pawns)==0:
            return node 
        if node in seen:
            continue             
        #we first need to expand knight,then bishop and rook,as required          
        if node.knight:
            expand_knight(node,seen,queue)
        if node.bishop:
            expand_bishop(node,seen,queue)
        if node.rook:
            expand_rook(node,seen,queue)  
        total_expanded_nodes[0]+=1    
        seen.add(node)                                    

    return None  

#implemtation of the expand_knight algorithm used in the search algorithm
def expand_knight(node,seen,queue):
    x,y=node.knight        
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
        new_cost=findCost(new_node)      #find the h-cost of the node
        order[0]+=1
        heapq.heappush(queue,(new_cost,order[0],new_node)) #add the new node to the priority queue   

#implementation of the expand_rook algorithm used in the search algorithm
def expand_rook(node,seen,queue):
    x,y=node.rook    
    for change in rook_move:
        for dx,dy in change:
            new_x=x+dx
            new_y=y+dy            
            if not (0<=new_x<N and 0<=new_y<N):
                break #do not get out of the table
            if (new_x,new_y) in obstacles or (new_x,new_y)==node.bishop or (new_x,new_y)==node.knight:
                break #do not hit into other stones or the obstacles
            new_pawns=set(pos for pos in node.pawns if pos!=(new_x,new_y))                                                             
            new_rook=(new_x,new_y)   
            #create the new configuration         
            new_node=Node(new_pawns,new_rook,node.bishop,node.knight,node.cost+8,node)
            new_cost=findCost(new_node)       
            order[0]+=1          
            heapq.heappush(queue,(new_cost,order[0],new_node))  
            if (new_x,new_y) in node.pawns: #if the stone hit into a pawn, then it cannot go on further 
                break 

#same implementation for the expand_bishop part of the search algorithms
def expand_bishop(node,seen,queue):
    x,y=node.bishop
    for change in bishop_move:
        for dx,dy in change:
            new_x=x+dx
            new_y=y+dy 
            if not (0<=new_x<N and 0<=new_y<N):
                break #do not get out of the table 
            if (new_x,new_y) in obstacles or (new_x,new_y)==node.knight or (new_x,new_y)==node.rook:
                break #do not hit into other stones or obstacles
            new_pawns=set(pos for pos in node.pawns if pos!=(new_x,new_y))
            new_bishop=(new_x,new_y)            
            #create the new configuration
            new_node=Node(new_pawns,node.rook,new_bishop,node.knight,node.cost+10,node) 
            new_cost=findCost(new_node)      
            order[0]+=1               
            heapq.heappush(queue,(new_cost,order[0],new_node))   
            if (new_x,new_y) in node.pawns: #if the stone hit into a pawn, it cannot go on further
                break    

#fuunction to find the f-cost associated with the new node
def findCost(node):
    if method=="UCS":
        return node.cost 
    elif method=="GS" and heuristic=="h2":        
        return h2(node) 
    elif method=="GS" and heuristic=="h1":
        rook_x,rook_y=node.rook 
        random=any([px==rook_x or py==rook_y for px,py in node.pawns])
        return 8*(len(node.pawns)+1 if not random else len(node.pawns)) 
    elif method=="AS" and heuristic=="h2":
        return h2(node) +node.cost
    elif method=="AS" and heuristic=="h1":
        (rook_x,rook_y)=node.rook if node.rook else (0,0)
        random=any([px==rook_x and py==rook_y for px,py in node.pawns])
        return 8*(len(node.pawns)+1 if not random else len(node.pawns))+node.cost       

#my heuristic function h2
def h2(node):     
    pawns={(i[0],i[1]) for i in node.pawns}
    if not pawns: return 0 #the search is over as there is no pawn left  
    cost=0
    (kx,ky)=node.knight or (-1,-1)
    (rx,ry)=node.rook or (-1,-1) 
    (bx,by)=node.bishop or (-1,-1)
    if node.knight:
        go=True 
        while go:
            for dx,dy in knight_move:
                nx,ny=kx+dx,ky+dy 
                if (nx,ny) in pawns:
                    pawns.remove((nx,ny))
                    kx,ky=nx,ny 
                    cost+=6 
            else:
                go=False         
    if node.bishop:
        go=True 
        while go:
            tot=0
            for direction in bishop_move:
                for dx,dy in direction:
                    nx,ny=bx+dx,by+dy 
                    if (nx,ny) in obstacles or (nx,ny)==node.rook or (nx,ny)==node.knight:
                        break
                    if (nx,ny) in pawns:
                        pawns.remove((nx,ny))
                        bx,by=nx,ny
                        tot+=1
                        cost+=10
            if not tot:
                go=False 
    if node.rook:
        A=[(0,rx,ry)]+sorted((abs(x-rx)+abs(y-ry),x,y) for x,y in pawns)        
        cost+=sum(shortestPath(A[i][1:],A[i+1][1:],0) for i in range(len(A)-1))*8
        return cost  
    if node.bishop:
        A=[(0,bx,by)]+sorted((abs(x-bx)+abs(y-by),x,y) for x,y in pawns)
        cost+=sum(shortestPath(A[i][1:],A[i+1][1:],1) for i in range(len(A)-1))*10
        return cost       
    return cost+sum(abs(x-kx)+abs(y-ky) for x,y in pawns)*3              

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

fw=open("output.txt","w")
fw.write("expanded: "+str(total_expanded_nodes[0])+'\n')
fw.write("path cost: "+str(total_cost)+'\n')
heuristic="h1"
fw.write("h1: "+str(findCost(initial))+'\n')
heuristic="h2"
fw.write("h2: "+str(findCost(initial))+'\n')
for table in tables[::-1]:
    for t in table:
        for tt in t:
            fw.write(str(tt)+" ")
        fw.write("\n")            
    fw.write("*************************\n")    

fw.flush()
fw.close()    




 



        
          




