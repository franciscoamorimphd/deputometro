# Deputômetro 2.0 | Piloto Streamlit

Dashboard experimental com sete abas, filtros por legislatura, ano, partido, UF e deputado, comparações, rankings e exportação CSV.

## Executar localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Publicar na nuvem

1. Crie um repositório GitHub com `app.py` e `requirements.txt` na raiz.
2. Em https://share.streamlit.io/ escolha o repositório e `app.py` como arquivo principal.
3. Publique o aplicativo. A aplicação pode ser usada no navegador sem instalar Python.

## Fontes de dados

O aplicativo abre com **dados fictícios**, criados apenas para testar os recursos. Selecione **Importar CSVs reais** na barra lateral para carregar as tabelas.

Arquivos aceitos (um CSV por conjunto):

- `deputados.csv`: `deputado_id,deputado,partido,uf,legislatura`
- `cotas.csv`: `deputado_id,ano,rubrica,fornecedor,valor`
- `emendas.csv`: `deputado_id,ano,modalidade,beneficiario,valor`
- `projetos.csv`: `deputado_id,ano,tipo,tema,situacao,proposicao_id`
- `votacoes.csv`: `deputado_id,ano,votacao_id,voto,ementa`

`deputado_id` precisa ser consistente em todos os arquivos; idealmente usar o ID oficial da Câmara. Datas e valores devem ser revisados. O app aceita separadores CSV comuns e valores numéricos em formato brasileiro, mas recomendamos padronizar valores com ponto decimal. Os filtros de legislatura funcionam apenas quando os registros dos deputados estiverem associados corretamente à legislatura. Se o mesmo parlamentar atuar em mais de uma legislatura, a base de deputados deve ser modelada com uma chave composta ou registros por legislatura e os fatos também devem carregar essa dimensão; a versão piloto foi projetada para a 57ª legislatura.

**Privacidade:** no modo de upload do Streamlit, os CSVs são enviados ao servidor que hospeda o app. Não usar dados sigilosos em hospedagem pública.

## Limites do piloto

Não há sincronização automática com Flourish nem com a API da Câmara. A importação de CSV ocorre durante a sessão e não persiste após reinício. Rankings de emendas representam valores atribuídos segundo a base importada, não necessariamente execução financeira. Votações são contagens de registros e não indicadores de presença ou alinhamento. Valores e categorias dependem da qualidade dos arquivos fornecidos.
