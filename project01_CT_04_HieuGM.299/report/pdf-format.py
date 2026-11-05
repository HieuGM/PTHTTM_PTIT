"""Unicode academic PDF layout and safe Markdown conversion."""
from pathlib import Path
import re
import html
import hashlib
import textwrap
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Spacer, PageBreak, Table, TableStyle, Image, Preformatted, KeepTogether
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
WIDTH = 467
CHAPTER = '0'
FIGURES = 0
for name, file in [('Times', 'times.ttf'), ('Times-Bold','timesbd.ttf'),
                   ('Times-Italic','timesi.ttf'), ('Mono','consola.ttf')]:
    pdfmetrics.registerFont(TTFont(name, 'C:/Windows/Fonts/'+file))
pdfmetrics.registerFontFamily('Times',normal='Times',bold='Times-Bold',italic='Times-Italic')
STYLES = {key: ParagraphStyle(key,fontName='Times',fontSize=12,leading=16.5,
    spaceAfter=7,alignment=TA_JUSTIFY) for key in ['body','h1','h2','h3','cell','caption','toc']}
for key,size in [('h1',16),('h2',13),('h3',12)]:
    STYLES[key].fontName='Times-Bold';STYLES[key].fontSize=size
    STYLES[key].leading=size*1.25;STYLES[key].spaceBefore=12
    STYLES[key].keepWithNext=True;STYLES[key].alignment=0
STYLES['cell'].fontSize=10;STYLES['cell'].leading=13;STYLES['cell'].spaceAfter=0
STYLES['cell'].alignment=0
STYLES['caption'].fontName='Times-Italic';STYLES['caption'].fontSize=10.5
STYLES['caption'].leading=14;STYLES['caption'].alignment=TA_CENTER
STYLES['toc'].fontSize=11;STYLES['toc'].leading=15;STYLES['toc'].alignment=0


def math_path(formula):
    target=HERE/'figures/equations'/f'{hashlib.sha256(formula.encode()).hexdigest()[:16]}.png'
    if not target.exists():
        target.parent.mkdir(parents=True,exist_ok=True)
        value=formula.replace(r'\frac1B',r'\frac{1}{B}').replace(r'\operatorname{split}',r'\mathrm{split}')
        fig=plt.figure(figsize=(10,.65));fig.text(.01,.5,'$'+value+'$',fontsize=17,va='center')
        try:fig.savefig(target,dpi=180,bbox_inches='tight',pad_inches=.04,facecolor='white')
        finally:plt.close(fig)
    return target


def inline(text):
    tokens=re.split(r'(\$[^$]+\$|\[[^\]]+\]\(https?://[^)]+\))',text)
    result=[]
    for token in tokens:
        if token.startswith('$'):
            try:
                path=math_path(token[1:-1])
                from PIL import Image as PILImage
                w,h=PILImage.open(path).size
                scale=11.8/h
                result.append(f'<img src="{path.as_posix()}" width="{w*scale:.2f}" height="11.8" valign="middle"/>')
                continue
            except ValueError:
                token=token[1:-1].replace('\\','').replace('{','').replace('}','')
        match=re.fullmatch(r'\[([^\]]+)\]\((https?://[^)]+)\)',token)
        if match:
            result.append(f'<a href="{html.escape(match[2],quote=True)}" color="#000000">{html.escape(match[1])}</a>')
        else:
            token=html.escape(token)
            token=re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',token)
            token=re.sub(r'`([^`]+)`',r'<font name="Mono" size="9.5">\1</font>',token)
            token=re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)',r'<i>\1</i>',token)
            result.append(token)
    return ''.join(result)


def para(text,style='body'):
    return Paragraph(inline(text),STYLES[style])


def picture(path,caption=None,max_height=360):
    image=Image(str(path));scale=min(WIDTH/image.imageWidth,max_height/image.imageHeight)
    image.drawWidth=image.imageWidth*scale;image.drawHeight=image.imageHeight*scale
    return KeepTogether([image,Spacer(1,5),para(caption,'caption')]) if caption else image


def equation(formula):
    from PIL import Image as PILImage
    path=math_path(formula)
    with PILImage.open(path) as raster:
        dpi=raster.info.get('dpi',(180,180))[0]
    image=Image(str(path))
    # Keep mathematical type near 14 pt; short equations must not inflate to body width.
    scale=min(WIDTH/image.imageWidth,14*72/(dpi*17),90/image.imageHeight)
    image.drawWidth=image.imageWidth*scale;image.drawHeight=image.imageHeight*scale
    return image


def table(lines):
    rows=[line.strip().strip('|').split('|') for line in lines
          if not re.fullmatch(r'\|[\s:|\-]+\|',line.strip())]
    count=max(map(len,rows));rows=[row+['']*(count-len(row)) for row in rows]
    lengths=[min(75,max(len(row[i]) for row in rows)) for i in range(count)]
    ratios=[max(10,length)**.55 for length in lengths]
    widths=[WIDTH*r/sum(ratios) for r in ratios]
    data=[[para(cell.strip(),'cell') for cell in row] for row in rows]
    result=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT')
    result.setStyle(TableStyle([('GRID',(0,0),(-1,-1),.35,colors.HexColor('#D9D9D9')),
       ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e8edf1')),('VALIGN',(0,0),(-1,-1),'MIDDLE'),
       ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
       ('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6)]))
    return result


def parse(text):
    global CHAPTER, FIGURES
    lines=text.splitlines();out=[];i=0;chapter=CHAPTER;figures=FIGURES
    while i<len(lines):
        line=lines[i].strip();i+=1
        if not line or line=='---':continue
        if line=='<!-- pagebreak -->':out.append(PageBreak());continue
        if line.startswith('```'):
            code=[]
            while i<len(lines) and not lines[i].startswith('```'):
                code.extend(textwrap.wrap(lines[i],width=88,replace_whitespace=False,drop_whitespace=False) or [' ']);i+=1
            i+=1
            style=ParagraphStyle('code',fontName='Mono',fontSize=8.4,leading=11,spaceAfter=10)
            # One line per flowable allows code listings to split across pages.
            out.extend(Preformatted(value,style) for value in code);continue
        match=re.match(r'^(#{1,4})\s+(.*)',line)
        if match:
            level=min(len(match[1]),3);title=match[2]
            if level==1:
                out.append(PageBreak())
                ch=re.match(r'CHƯƠNG\s+(\d+)',title)
                chapter=ch[1] if ch else 'A';figures=0
            out.append(para(title,'h'+str(level)));continue
        match=re.fullmatch(r'!\[(.*?)\]\((.*?)\)',line)
        if match:
            figures+=1
            out.append(picture(HERE/match[2],f'Hình {chapter}.{figures}. {match[1]}'));continue
        if line.startswith('$$') and line.endswith('$$'):
            out.extend([equation(line[2:-2]),Spacer(1,9)]);continue
        if line.startswith('|'):
            rows=[line]
            while i<len(lines) and lines[i].strip().startswith('|'):rows.append(lines[i]);i+=1
            out.extend([table(rows),Spacer(1,10)]);continue
        line=re.sub(r'^[-*]\s+','• ',line);line=re.sub(r'^>\s*','',line)
        out.append(para(line))
    CHAPTER, FIGURES = chapter, figures
    return out
