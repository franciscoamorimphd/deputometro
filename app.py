import io
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title='Deputômetro | Piloto',page_icon='📊',layout='wide')
st.markdown('''<style>
.block-container {padding-top:1.6rem}
/* Cartões claros: texto escuro em qualquer tema do navegador/Streamlit */
[data-testid="stMetric"] {background:#f4f6f9;border:1px solid #e0e5ec;border-radius:12px;padding:14px}
[data-testid="stMetric"] [data-testid="stMetricLabel"],
[data-testid="stMetric"] [data-testid="stMetricLabel"] *,
[data-testid="stMetric"] [data-testid="stMetricValue"],
[data-testid="stMetric"] [data-testid="stMetricValue"] *,
[data-testid="stMetric"] [data-testid="stMetricDelta"],
[data-testid="stMetric"] [data-testid="stMetricDelta"] * {color:#172638 !important;opacity:1 !important}
[data-testid="stMetric"] [data-testid="stMetricLabel"] {font-weight:600}
h1{letter-spacing:-.035em}
</style>''',unsafe_allow_html=True)

SCHEMAS={
 'deputados':['deputado_id','deputado','partido','uf','legislatura'],
 'cotas':['deputado_id','ano','rubrica','fornecedor','valor'],
 'emendas':['deputado_id','ano','modalidade','beneficiario','valor'],
 'projetos':['deputado_id','ano','tipo','tema','situacao','proposicao_id'],
 'votacoes':['deputado_id','ano','votacao_id','voto','ementa']}

@st.cache_data
def demo():
 rng=np.random.default_rng(42)
 nomes=[f'Deputado demonstrativo {i:02d}' for i in range(1,41)]
 dep=pd.DataFrame({'deputado_id':range(1,41),'deputado':nomes,'partido':rng.choice(['Partido A','Partido B','Partido C','Partido D'],40),'uf':rng.choice(['RS','SP','RJ','MG','BA','PE'],40),'legislatura':57})
 cot=[]; eme=[]; pro=[]; vot=[]
 for d in dep.deputado_id:
  for a in range(2023,2027):
   for r in ['Divulgação','Passagens','Combustíveis','Escritório','Consultoria']:
    cot.append((d,a,r,f'Fornecedor fictício {rng.integers(1,60):02d}',round(float(rng.uniform(5000,120000)),2)))
   for _ in range(int(rng.integers(2,7))):
    eme.append((d,a,rng.choice(['Individual','Bancada','Comissão']),f'Beneficiário fictício {rng.integers(1,50):02d}',round(float(rng.uniform(50000,1800000)),2)))
   for j in range(int(rng.integers(2,11))):
    pro.append((d,a,rng.choice(['PL','PEC','PLP','REQ']),rng.choice(['Saúde','Educação','Segurança','Economia','Meio ambiente']),rng.choice(['Em tramitação','Aprovada','Arquivada']),f'DEMO-{d}-{a}-{j}'))
   for j in range(12):
    vot.append((d,a,f'DEMO-VOT-{a}-{j}',rng.choice(['Sim','Não','Abstenção','Obstrução']),f'Votação demonstrativa {j+1}'))
 return {'deputados':dep,'cotas':pd.DataFrame(cot,columns=SCHEMAS['cotas']),'emendas':pd.DataFrame(eme,columns=SCHEMAS['emendas']),'projetos':pd.DataFrame(pro,columns=SCHEMAS['projetos']),'votacoes':pd.DataFrame(vot,columns=SCHEMAS['votacoes'])}

def brl(v): return f'R$ {v:,.2f}'.replace(',','X').replace('.',',').replace('X','.')
def csv_button(df,label,key):
 st.download_button(label,df.to_csv(index=False,sep=';',decimal=',').encode('utf-8-sig'),file_name=f'deputometro_{key}.csv',mime='text/csv',key=f'dl_{key}')
def bar(df,x,y,title,orientation='h'):
 if df.empty: st.info('Sem registros para os filtros selecionados.');return
 fig=px.bar(df,x=x,y=y,orientation=orientation,title=title,color_discrete_sequence=['#3366a3'])
 fig.update_layout(height=410,margin=dict(l=10,r=10,t=55,b=20),plot_bgcolor='rgba(0,0,0,0)')
 st.plotly_chart(fig,use_container_width=True)
def merge_base(df,dep):return df.merge(dep,on='deputado_id',how='inner',validate='many_to_one')

st.title('Deputômetro')
st.caption('Piloto em Streamlit | Consulta, comparação e rankings parlamentares')
with st.sidebar:
 st.header('Dados e filtros')
 source=st.radio('Fonte', ['Dados demonstrativos','Importar CSVs reais'],help='Os dados demonstrativos são inteiramente fictícios.')
 bases=demo()
 if source=='Importar CSVs reais':
  st.caption('Envie os CSVs separadamente. Arquivos devem conter os campos indicados no README. Sem arquivos, as seções ficam vazias.')
  for name,cols in SCHEMAS.items():
   f=st.file_uploader(name.capitalize(),type=['csv'],key=f'up_{name}')
   if f:
    try:
     content=f.getvalue()
     try: df=pd.read_csv(io.BytesIO(content),sep=None,engine='python',encoding='utf-8-sig')
     except UnicodeDecodeError: df=pd.read_csv(io.BytesIO(content),sep=None,engine='python',encoding='latin-1')
     missing=set(cols)-set(df.columns)
     if missing: st.error(f'{name}: faltam colunas: {", ".join(sorted(missing))}')
     else:
      df=df[cols].copy()
      if name in ['cotas','emendas']:
       df['valor']=pd.to_numeric(df['valor'].astype(str).str.replace(r'[^\d,.-]','',regex=True).str.replace('.','',regex=False).str.replace(',','.',regex=False),errors='coerce') if df['valor'].dtype=='object' else pd.to_numeric(df['valor'],errors='coerce')
      bases[name]=df
    except Exception as e: st.error(f'Erro na leitura de {name}: {e}')
   else: bases[name]=pd.DataFrame(columns=cols)
 dep=bases['deputados'].copy()
 if not dep.empty:
  dep['deputado_id']=dep['deputado_id'].astype(str)
  dep['legislatura']=pd.to_numeric(dep['legislatura'],errors='coerce')
 for name in ['cotas','emendas','projetos','votacoes']:
  df=bases[name].copy()
  if not df.empty:
   df['deputado_id']=df['deputado_id'].astype(str)
   df['ano']=pd.to_numeric(df['ano'],errors='coerce')
  bases[name]=df
 legs=sorted(dep['legislatura'].dropna().unique().tolist()) if not dep.empty else []
 leg=st.selectbox('Legislatura',['Todas']+legs,index=0)
 if leg!='Todas':dep=dep[dep.legislatura==leg]
 anos=sorted(set().union(*[set(bases[n]['ano'].dropna().astype(int).tolist()) for n in ['cotas','emendas','projetos','votacoes']]))
 years=st.multiselect('Ano',anos,default=anos)
 parties=st.multiselect('Partido',sorted(dep.partido.dropna().unique()),default=[])
 ufs=st.multiselect('UF',sorted(dep.uf.dropna().unique()),default=[])
 if parties:dep=dep[dep.partido.isin(parties)]
 if ufs:dep=dep[dep.uf.isin(ufs)]
 names=st.multiselect('Deputado (filtro geral)',sorted(dep.deputado.unique()),default=[])
 if names:dep=dep[dep.deputado.isin(names)]
 st.caption('Filtros vazios de partido, UF e deputado significam todos. Ano vazio significa nenhum ano.')

if source=='Dados demonstrativos':st.warning('AMBIENTE DE DEMONSTRAÇÃO: todos os nomes, valores, votos, projetos e emendas exibidos são fictícios. Não utilizar para publicação.',icon='⚠️')
else:st.info('Dados importados nesta sessão. Confirme procedência, período de referência e consistência antes de publicar.')

filtered={}
for name in ['cotas','emendas','projetos','votacoes']:
 d=bases[name]
 filtered[name]=merge_base(d[d.ano.isin(years)].copy(),dep) if not d.empty and not dep.empty else pd.DataFrame(columns=SCHEMAS[name]+['deputado','partido','uf','legislatura'])
c,e,p,v=[filtered[n] for n in ['cotas','emendas','projetos','votacoes']]
tabs=st.tabs(['Visão geral','Cotas','Emendas','Projetos','Votações','Comparar deputados','Rankings'])
with tabs[0]:
 a,b,cc,dd=st.columns(4)
 a.metric('Deputados no filtro',len(dep));b.metric('Cotas',brl(c.valor.sum()));cc.metric('Emendas',brl(e.valor.sum()));dd.metric('Proposições',len(p))
 t1,t2=st.columns(2)
 with t1:
  if not c.empty:bar(c.groupby('ano',as_index=False).valor.sum(),'ano','valor','Despesas com cotas por ano',orientation='v')
 with t2:
  if not e.empty:bar(e.groupby('ano',as_index=False).valor.sum(),'ano','valor','Emendas por ano',orientation='v')
 st.caption('Totais condicionados aos filtros e à cobertura das bases importadas.')
with tabs[1]:
 st.subheader('Cotas parlamentares')
 a,b=st.columns(2)
 with a:
  if not c.empty:bar(c.groupby('rubrica',as_index=False).valor.sum().sort_values('valor'),'valor','rubrica','Despesas por rubrica')
 with b:
  if not c.empty:bar(c.groupby('deputado',as_index=False).valor.sum().nlargest(10,'valor').sort_values('valor'),'valor','deputado','Dez maiores totais')
 st.dataframe(c,use_container_width=True,hide_index=True);csv_button(c,'Exportar cotas','cotas')
with tabs[2]:
 st.subheader('Emendas parlamentares')
 if not e.empty:bar(e.groupby('modalidade',as_index=False).valor.sum().sort_values('valor'),'valor','modalidade','Valores por modalidade')
 st.dataframe(e,use_container_width=True,hide_index=True);csv_button(e,'Exportar emendas','emendas')
with tabs[3]:
 st.subheader('Proposições')
 if not p.empty:bar(p.groupby('tema',as_index=False).size().rename(columns={'size':'quantidade'}).sort_values('quantidade'),'quantidade','tema','Quantidade por tema')
 st.dataframe(p,use_container_width=True,hide_index=True);csv_button(p,'Exportar projetos','projetos')
with tabs[4]:
 st.subheader('Votações nominais')
 if not v.empty:
  st.plotly_chart(px.histogram(v,x='voto',color='voto',title='Distribuição de votos registrados'),use_container_width=True)
 st.dataframe(v,use_container_width=True,hide_index=True);csv_button(v,'Exportar votações','votacoes')
with tabs[5]:
 st.subheader('Comparar deputados')
 chosen=st.multiselect('Selecione de 2 a 5 deputados',sorted(dep.deputado.unique()),max_selections=5,key='comparison')
 if len(chosen)<2:st.info('Escolha pelo menos dois deputados para comparar.')
 else:
  stats=dep[dep.deputado.isin(chosen)][['deputado','partido','uf']].copy()
  for name,d,col in [('Cotas (R$)',c,'valor'),('Emendas (R$)',e,'valor'),('Proposições',p,None),('Votos registrados',v,None)]:
   sums=d[d.deputado.isin(chosen)].groupby('deputado').valor.sum() if col else d[d.deputado.isin(chosen)].groupby('deputado').size()
   stats[name]=stats.deputado.map(sums).fillna(0)
  st.dataframe(stats,use_container_width=True,hide_index=True)
  metric=st.selectbox('Comparar indicador',['Cotas (R$)','Emendas (R$)','Proposições','Votos registrados'])
  bar(stats,metric,'deputado',f'Comparação: {metric}')
  csv_button(stats,'Exportar comparação','comparacao')
with tabs[6]:
 st.subheader('Rankings')
 indicator=st.selectbox('Indicador',['Cotas (R$)','Emendas (R$)','Quantidade de proposições','Votos registrados'])
 top=st.selectbox('Mostrar',[10,20,50,'Todos'])
 ascending=st.toggle('Ordem crescente',value=False)
 mapping={'Cotas (R$)':(c,'valor'),'Emendas (R$)':(e,'valor'),'Quantidade de proposições':(p,None),'Votos registrados':(v,None)}
 d,col=mapping[indicator]
 if not d.empty:
  series=d.groupby('deputado').valor.sum() if col else d.groupby('deputado').size()
  ranking=dep[['deputado','partido','uf']].drop_duplicates().copy()
  ranking['indicador']=ranking.deputado.map(series).fillna(0)
  ranking=ranking.sort_values(['indicador','deputado'],ascending=[ascending,True]).reset_index(drop=True)
  ranking.insert(0,'posição',range(1,len(ranking)+1))
  shown=ranking if top=='Todos' else ranking.head(top)
  bar(shown.sort_values('indicador'),'indicador','deputado',indicator)
  st.dataframe(shown,use_container_width=True,hide_index=True)
  csv_button(ranking,'Exportar ranking completo','ranking')
 else:st.info('Não há dados para construir o ranking.')
st.divider()
st.caption('Piloto v0.1 | Indicadores descritivos não medem qualidade legislativa. Comparações devem considerar duração de mandato, cobertura e regras de atribuição de emendas.')
