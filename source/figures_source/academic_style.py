"""Shared typography, semantic colors and vector primitives for thesis figures."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch, Ellipse
S = Path(__file__).resolve().parents[1]
OUT = S / 'image'
BLUE = '#3498DB'
GREEN = '#42B874'
ORANGE = '#D7962E'
PURPLE = '#9B59B6'
RED = '#E74C3C'
MRI = '#DCEBFA'
RADIOMICS = '#E2F1E3'
CLINICAL = '#FFF1CD'
FUSION = '#EAE2F5'
TEMPORAL = '#DDEFF1'
SURVIVAL = '#E9ECEF'
INK = '#28313C'
NAVY = '#172C46'
GRAY = INK
PALE = '#F5F6F8'
WHITE = '#FFFFFF'
RULE = '#B1BBC5'
plt.rcParams.update({'font.family':['Arial', 'DejaVu Sans'],'font.size':10,
 'text.color':INK,'axes.labelcolor':INK,'pdf.fonttype':42,
 'svg.fonttype':'none','mathtext.fontset':'dejavusans',
 'axes.spines.top':False,'axes.spines.right':False})

def scene(w=7.2,h=3.6):
    fig, ax = plt.subplots(figsize=(w,h))
    ax.set(xlim=(0,1),ylim=(0,1)); ax.axis('off')
    fig.subplots_adjust(left=.02,right=.98,bottom=.025,top=.975)
    return fig,ax

def text(ax,x,y,t,size=10,weight='normal',ha='center',color=INK,va='center',**kw):
    return ax.text(x,y,t,fontsize=size,fontweight=weight,ha=ha,color=color,
                   va=va,clip_on=False,zorder=5,**kw)

def panel(ax,x,y,w,h,title='',col=BLUE,size=10):
    ax.add_patch(Rectangle((x,y),w,h,facecolor=col,edgecolor='none',
                           alpha=.075,zorder=-5))
    if title: text(ax,x+.018,y+h-.037,title,size,'bold',ha='left',va='top')

def box(ax,x,y,w,h,t,col=BLUE,size=10):
    ax.add_patch(Rectangle((x-w/2,y-h/2),w,h,facecolor=col,
                           edgecolor=NAVY,linewidth=.7,zorder=2))
    return text(ax,x,y,t,size)

def arrow(ax,a,b,color=GRAY,lw=1.15,style='-|>',ls='-',**kw):
    ax.add_patch(FancyArrowPatch(a,b,arrowstyle=style,mutation_scale=11,
        lw=lw,color=color,linestyle=ls,shrinkA=0,shrinkB=0,clip_on=False,zorder=1,**kw))

def line(ax,a,b,color=GRAY,lw=1,ls='-'):
    ax.plot([a[0],b[0]],[a[1],b[1]],color=color,lw=lw,ls=ls,zorder=1,clip_on=False)

def route(ax,points,color=GRAY,lw=1.15):
    for a,b in zip(points[:-2],points[1:-1]): line(ax,a,b,color,lw)
    arrow(ax,points[-2],points[-1],color,lw)

def vector(ax,x,y,w,h,col,n=8):
    for i in range(n):
        ax.add_patch(Rectangle((x+i*w/n,y),w/n,h,fc=col,
          ec=NAVY,lw=.35,zorder=2))

def matrix(ax,x,y,w,h,col,n=6,m=6):
    for i in range(n):
        for j in range(m):
            ax.add_patch(Rectangle((x+j*w/m,y+i*h/n),w/m,h/n,
                fc=col,ec=NAVY,lw=.35,zorder=2))

def op(ax,x,y,label,col=PURPLE,r=.023,size=15):
    ratio=ax.figure.get_figwidth()*.96/(ax.figure.get_figheight()*.95)
    ax.add_patch(Ellipse((x,y),2*r,2*r*ratio,fc='white',ec=col,lw=1.2,zorder=3))
    text(ax,x,y,label,size)

def save(fig,name):
    OUT.mkdir(exist_ok=True)
    for ext in ['pdf','svg','png']:
        fig.savefig(OUT/f'{name}.{ext}',dpi=300,bbox_inches='tight',pad_inches=.15,facecolor='white')
    plt.close(fig)
