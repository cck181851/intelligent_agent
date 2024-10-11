import heapq,math

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

N=5 

table=[[".","R",".",".","."],[".","1","x",".","."],[".","2","x",".","."],[".","3","x",".","."],[".","4","5","6","."]]

knight_move=[[-1,2],[-2,1],[-2,-1],[-1,-2],[1,-2],[2,-1],[2,1],[1,2]]

bishop_move=[[(-i,i) for i in range(1,N+1)],[(-i,-i) for i in range(1,N+1)],
            [(i,-i) for i in range(1,N+1)],[(i,i) for i in range(1,N+1)]]

rook_move=[[(0,i) for i in range(1,N+1)],[(-i,0) for i in range(1,N+1)],
            [(0,-i) for i in range(1,N+1)],[(i,0) for i in range(1,N+1)]]

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

def search(mode):
    queue=[(0,0,initial)]    
    seen={initial}

    while queue:        
        _,_,node=heapq.heappop(queue)                           
        if len(node.pawns)==0:
            return node  
        if node.knight:
            expand_knight(node,seen,queue,mode)
        if node.bishop:
            expand_bishop(node,seen,queue,mode)
        if node.rook:
            expand_rook(node,seen,queue,mode)                                 

    return None  

def expand_knight(node,seen,queue,mode):
    x,y=node.knight
    for dx,dy in knight_move:
        new_x,new_y=x+dx,y+dy  
        if not (0<=new_x<N and 0<=new_y<N):
            continue
        if any([target and ((new_x,new_y)==target or (new_x,new_y) in target) for target in 
            [obstacles,node.rook,node.bishop]]):
            continue
        new_pawns=tuple(pos for pos in node.pawns if pos!=(new_x,new_y)) 
        new_knight=(new_x,new_y)
        new_cost=knight_find_cost(mode,node,new_x,new_y)        
        new_node=Node(new_pawns,node.rook,node.bishop,new_knight,node.cost+6,node)
        if new_node not in seen: 
            seen.add(node) 
            total_expanded_nodes[0]+=1
            heapq.heappush(queue,(new_cost,total_expanded_nodes[0],new_node))   

def expand_rook(node,seen,queue,mode):
    x,y=node.rook
    for direction in rook_move:
        for dx,dy in direction:
            new_x=x+dx
            new_y=y+dy            
            if not (0<=new_x<N and 0<=new_y<N):
                break
            if any([target and ((new_x,new_y) in target or (new_x,new_y)==target) for target in 
            [obstacles,node.rook,node.bishop,node.knight]]):
                break
            new_pawns=tuple(pos for pos in node.pawns if pos!=(new_x,new_y))
            new_rook=(new_x,new_y)
            new_cost=rook_find_cost(mode,node,new_x,new_y)
            new_node=Node(new_pawns,new_rook,node.bishop,node.knight,node.cost+8,node)
            if new_node not in seen:            
                seen.add(node) 
                total_expanded_nodes[0]+=1
                heapq.heappush(queue,(new_cost,total_expanded_nodes[0],new_node))   

def expand_bishop(node,seen,queue,mode):
    x,y=node.bishop
    for direction in bishop_move:
        for dx,dy in direction:
            new_x=x+dx
            new_y=y+dy 
            if not (0<=new_x<N and 0<=new_y<N):
                break
            if any([target and ((new_x,new_y) in target or (new_x,new_y)==target) for target in 
                    [obstacles,node.rook,node.bishop,node.knight]]):
                break
            new_pawns=tuple(pos for pos in node.pawns if pos!=(new_x,new_y))
            new_bishop=(new_x,new_y)
            new_cost=bishop_find_cost(mode,node,new_x,new_y)
            new_node=Node(new_pawns,node.rook,new_bishop,node.knight,node.cost+10,node)
            if new_node not in seen:
                seen.add(node) 
                total_expanded_nodes[0]+=1
                heapq.heappush(queue,(new_cost,total_expanded_nodes[0],new_node))   

def rook_find_cost(mode,node,new_x,new_y):
    new_cost=0
    if mode==1:
        new_cost=node.cost+8
    elif mode==2:
        random=any(pi==new_x or pj==new_y for pi,pj in node.pawns) 
        new_cost=node.cost+6+8*(len(node.pawns) if random else 1+(len(node.pawns)))
    else:   
        new_cost+=node.cost+8 
        for i,j in node.pawns:
            cur=8 if new_x==i or new_y==j else 16
            new_cost+=cur
    return new_cost

def bishop_find_cost(mode,node,new_x,new_y):
    new_cost=0
    if mode==1:
        new_cost=node.cost+10  
    elif mode==2:
        new_cost=node.cost
    else:
        new_cost+=node.cost+10
        for i,j in node.pawns:
            cur=10 if i==new_x or j==new_y else 20
            new_cost+=cur
    return new_cost 

def knight_find_cost(mode,node,new_x,new_y):
    new_cost=0
    if mode==1:
        new_cost=node.cost+6 
    elif mode==2:
        new_cost=node.cost
    else:
        new_cost+=node.cost+6
        for i,j in node.pawns:
            dist=abs(new_x-i)+abs(new_y-j)
            new_cost+=math.ceil(dist/3)*6
    return new_cost 

res=search(3)
print(res.cost,total_expanded_nodes[0])

while res.parent:
    table=[["." for _ in range(N)] for _ in range(N)]
    for i,j in res.pawns:
        table[i][j]="1"
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



 



        
          








