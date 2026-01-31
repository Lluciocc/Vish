# Hi there! If you're reading this, you're probably interested in how the graph layout engine works.
# This module provides a simple yet effective way to automatically arrange nodes in the graph.
# You should look at compute to have an idea of the overall flow.
# NOTE: Im using something call "Barycentric coordinate system" for minimizing edge crossings. and HELL YEAH it works pretty well!
# If you want to learn more about it, check out: https://en.wikipedia.org/wiki/Barycentric_coordinate_system
from __future__ import annotations
from dataclasses import dataclass
from collections import defaultdict,deque
from typing import Dict,List,Tuple,Set
from core.port_types import PortType

PORT_PRIORITY:Dict[PortType,int]={PortType.EXEC:100,PortType.CONDITION:80,getattr(PortType,"DATA",PortType.STRING):60,PortType.STRING:50,getattr(PortType,"INT",PortType.STRING):45,getattr(PortType,"FLOAT",PortType.STRING):45}
BASE_X_SPACING=260
BASE_Y_SPACING=140
DATA_PROXIMITY_PULL=0.25
MAX_COLLISION_ITER=2000

@dataclass
class _LEdge:
    src:str
    tgt:str
    port_type:PortType
    weight:int

class _LNode:
    __slots__=("id","node","in_edges","out_edges","x","y","w_hint","h_hint")
    def __init__(self,node):
        self.node=node
        self.id=node.id
        self.in_edges=[]
        self.out_edges=[]
        self.x=0
        self.y=0
        self.w_hint=int(getattr(node,"width",200)or 200)
        self.h_hint=int(getattr(node,"height",120)or 120)
    def max_in_weight(self)->int:
        return max((e.weight for e in self.in_edges),default=0)

class GraphLayoutEngine:
    def __init__(self,graph,*,x_spacing=BASE_X_SPACING,y_spacing=BASE_Y_SPACING):
        self.graph=graph
        self.x_spacing=int(x_spacing)
        self.y_spacing=int(y_spacing)
        self.nodes:Dict[str,_LNode]={}
        self.edges:List[_LEdge]=[]

    def compute(self)->Dict[str,Tuple[int,int]]:
        self._build()
        self._compute_x()
        self._compute_y()
        self._minimize_crossings()
        self._refine_data_proximity()
        self._resolve_collisions()
        self._center_layout()
        return{nid:(n.x,n.y)for nid,n in self.nodes.items()}

    def _build(self):
        self.nodes.clear()
        self.edges.clear()
        for node in self.graph.nodes.values():
            self.nodes[node.id]=_LNode(node)
        for edge in self.graph.edges.values():
            pt=edge.source.port_type
            w=int(PORT_PRIORITY.get(pt,30))
            le=_LEdge(edge.source.node.id,edge.target.node.id,pt,w)
            self.edges.append(le)
            if le.src in self.nodes and le.tgt in self.nodes:
                self.nodes[le.src].out_edges.append(le)
                self.nodes[le.tgt].in_edges.append(le)

    def _compute_x(self):
        indegree=defaultdict(int)
        out_map=defaultdict(list)
        for e in self.edges:
            indegree[e.tgt]+=1
            out_map[e.src].append(e)
        q=deque([nid for nid in self.nodes if indegree[nid]==0])
        if not q:
            q=deque(self.nodes.keys())
        while q:
            nid=q.popleft()
            n=self.nodes[nid]
            for e in out_map.get(nid,[]):
                tgt=self.nodes[e.tgt]
                step=1 if e.port_type==PortType.EXEC else max(1,e.weight//40)
                px=n.x+step*self.x_spacing
                if px>tgt.x:
                    tgt.x=px
                indegree[e.tgt]-=1
                if indegree[e.tgt]==0:
                    q.append(e.tgt)
        self._relax_x_constraints(6)
        self._snap_x_to_columns()

    def _relax_x_constraints(self,max_passes=6):
        for _ in range(max_passes):
            changed=False
            for e in self.edges:
                src=self.nodes[e.src]
                tgt=self.nodes[e.tgt]
                step=1 if e.port_type==PortType.EXEC else max(1,e.weight//40)
                px=src.x+step*self.x_spacing
                if px>tgt.x:
                    tgt.x=px
                    changed=True
            if not changed:
                break

    def _snap_x_to_columns(self):
        s=self.x_spacing
        for n in self.nodes.values():
            n.x=int(round(n.x/s))*s
        xs=sorted({n.x for n in self.nodes.values()})
        remap={x:i*s for i,x in enumerate(xs)}
        for n in self.nodes.values():
            n.x=remap[n.x]

    def _compute_y(self):
        cols=defaultdict(list)
        for n in self.nodes.values():
            cols[n.x].append(n)
        for x in sorted(cols):
            col=cols[x]
            col.sort(key=lambda n:(-n.max_in_weight(),str(n.id)))
            y=0
            for n in col:
                n.y=y
                y+=self.y_spacing

    def _refine_data_proximity(self):
        for _ in range(4):
            for e in self.edges:
                if e.port_type==PortType.EXEC:
                    continue
                src=self.nodes[e.src]
                tgt=self.nodes[e.tgt]
                tgt.y+=int((src.y-tgt.y)*DATA_PROXIMITY_PULL)
        self._restack_columns()

    def _restack_columns(self):
        cols=defaultdict(list)
        for n in self.nodes.values():
            cols[n.x].append(n)
        for x in sorted(cols):
            col=cols[x]
            col.sort(key=lambda n:(n.y,-n.max_in_weight(),str(n.id)))
            y=0
            for n in col:
                n.y=y
                y+=self.y_spacing

    def _resolve_collisions(self):
        cols=defaultdict(list)
        for n in self.nodes.values():
            cols[n.x].append(n)
        for x,col in cols.items():
            col.sort(key=lambda n:(n.y,str(n.id)))
            used:Set[int]=set()
            it=0
            for n in col:
                row=int(round(n.y/self.y_spacing))
                y=row*self.y_spacing
                while y in used:
                    y+=self.y_spacing//2
                    it+=1
                    if it>MAX_COLLISION_ITER:
                        break
                used.add(y)
                n.y=y
        min_y=min((n.y for n in self.nodes.values()),default=0)
        if min_y<0:
            for n in self.nodes.values():
                n.y-=min_y

    def _center_layout(self):
        xs=[n.x for n in self.nodes.values()]
        ys=[n.y for n in self.nodes.values()]
        if not xs or not ys:
            return
        cx=(min(xs)+max(xs))//2
        cy=(min(ys)+max(ys))//2
        for n in self.nodes.values():
            n.x-=cx
            n.y-=cy

    def _minimize_crossings(self, passes=4):
        cols=defaultdict(list)
        for n in self.nodes.values():
            cols[n.x].append(n)
        xs=sorted(cols)
        for _ in range(passes):
            for i in range(1,len(xs)):
                left=cols[xs[i-1]]
                cur=cols[xs[i]]
                index={n.id:j for j,n in enumerate(left)}
                def bary(n):
                    ys=[]
                    for e in n.in_edges:
                        if self.nodes[e.src].x==xs[i-1]:
                            ys.append(index.get(e.src,0))
                    return sum(ys)/len(ys) if ys else float("inf")
                cur.sort(key=bary)
                y=0
                for n in cur:
                    n.y=y
                    y+=self.y_spacing

