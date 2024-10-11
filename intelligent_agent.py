import heapq,math,sys

class Node:
    def __init__(self,pawns,rook,bishop,knight,cost,parent):
        self.pawns=pawns
        self.rook=rook 
        self.bishop=bishop 
        self.knight=knight 
        self.cost=cost
        self.parent=parent 

    def __eq__(self,other):
        if isinstance(other, Node):
            return self.pawns == other.pawns and self.rook == other.rook and \
                self.bishop==other.bishop and self.knight==other.knight 
        return False

    def __hash__(self):
        return hash((str(self.pawns),self.rook,self.bishop,self.knight))    

    def __eq__(self, other):
        if isinstance(other, Node):
            return self.cost == other.cost
        return 0        

arguments = sys.argv 
file_name,input_file_name,output_file_name,method,heuristic=arguments

N=7

table=[[".",".",".","x","R",".","."],
        [".",".","x","x",".",".","x"],
        [".",".",".",".",".",".","."],
        [".",".","x","1",".","2","x"],
        ["5",".",".",".",".",".","."],
        [".",".",".",".",".","3","."],
        [".",".","4",".",".",".","."]]
copied=[[i for i in j] for j in table]        

knight_move=[[-1,2],[-2,1],[-2,-1],[-1,-2],[1,-2],[2,-1],[2,1],[1,2]]

bishop_move=[[(1*i,1*i) for i in range(1,N+1)],[(-1*i,1*i) for i in range(1,N+1)],
    [(1*i,-1*i) for i in range(1,N+1)],[(-1*i,-1*i) for i in range(1,N+1)]]

rook_move=[[(1*i,0) for i in range(1,N+1)],[(-1*i,0) for i in range(1,N+1)],
    [(0,1*i) for i in range(1,N+1)],[(0,-1*i) for i in range(1,N+1)]]

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
        print(node.rook)                          
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
        new_cost=knight_find_cost(node,new_x,new_y)        
        new_node=Node(new_pawns,node.rook,node.bishop,new_knight,node.cost+6,node)
        if new_node not in seen:         
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
            new_cost=rook_find_cost(node,new_x,new_y)
            new_node=Node(new_pawns,new_rook,node.bishop,node.knight,node.cost+8,node)
            if new_node not in seen:    
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
            new_cost=bishop_find_cost(node,new_x,new_y)
            new_node=Node(new_pawns,node.rook,new_bishop,node.knight,node.cost+10,node)
            if new_node not in seen:                     
                heapq.heappush(queue,(new_cost,total_expanded_nodes[0],new_node))   
                if (new_x,new_y) in node.pawns:
                    break    

def rook_find_cost(node,new_x,new_y):    
    if method=="UCS":
        return node.cost+8
    elif method=="GS" and heuristic=="h1":
        random=any([new_x==pi or new_y==pj for pi,pj in node.pawns])
        return 8*((len(node.pawns)+(1 if not random else 0)))      
    elif method=="GS" and heuristic=="h2":
        new_cost=0
        for pi,pj in node.pawns:
            new_cost+=8 if pi==new_x or pj==new_y else 16
        return new_cost    
    elif method=="AS" and heuristic=="h1":
        random=any([new_x==pi or new_y==pj for pi,pj in node.pawns])
        return (node.cost+8)+8*((len(node.pawns)+(1 if not random else 0)))              
    elif method=="AS" and heuristic=="h2":
        new_cost=node.cost+8 
        for pi,pj in node.pawns:
            new_cost+=8 if pi==new_x or pj==new_y else 16   
        return new_cost           

def bishop_find_cost(node,new_x,new_y):    
    if method=="UCS":
        return node.cost+10  
    elif method=="GS" and heuristic=="h2":
        new_cost=0
        for pi,pj in node.pawns:
            new_cost+=10 if pi==new_x or pj==new_y else 20
        return new_cost
    elif method=="AS" and heuristic=="h2":
        new_cost=node.cost+10
        for pi,pj in node.pawns:
            new_cost+=10 if pi==new_x or pj==new_y else 20
        return new_cost        


def knight_find_cost(node,new_x,new_y):
    if method=="UCS":
        return node.cost+6 
    elif method=="GS" and heuristic=="h2":
        new_cost=0
        for pi,pj in node.pawns:
            cur=abs(pi-new_x)+abs(pj-new_y)
            new_cost+=math.ceil(cur/3)
        return new_cost    
    elif method=="AS" and heuristic=="h2":
        new_cost=node.cost+6
        for pi,pj in node.pawns:
            cur=abs(pi-new_x)+abs(pj-new_y)
            new_cost+=math.ceil(cur/3)
        return new_cost         

res=search()
print(res.cost,total_expanded_nodes[0])

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
    for t in table:        
        print(t)
    print("********************")        
    res=res.parent    



 



        
          






 



        
          





 



        
          




