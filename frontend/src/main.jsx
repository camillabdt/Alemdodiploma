import React, { useEffect, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  GraduationCap,
  LayoutDashboard,
  BriefcaseBusiness,
  Route,
  MapPin,
  GitCompareArrows,
  Sparkles,
  Database,
  BookOpen,
  ArrowUpRight,
  ArrowRight,
  Download,
  Upload,
  SlidersHorizontal,
  X,
  Check,
  ChevronRight,
  RefreshCcw,
  ShieldCheck,
  Info,
  Menu,
  FileSpreadsheet,
  LoaderCircle,
  CircleHelp,
  LogOut,
  Clock3,
  Users,
  Building2,
  Search,
  TrendingUp,
} from "lucide-react";
import "./styles.css";
import Papa from "papaparse";

const columns = {
  Curso_de_Graduacao: "Curso",
  Periodo_Conclusao: "Período de conclusão",
  Genero: "Gênero",
  Faixa_Etaria: "Faixa etária",
  Categoria_Cargo: "Categoria do cargo",
  Tipo_Instituicao: "Tipo de instituição",
};
const indicatorLabels = {
  Indicador_Lideranca: "Liderança ou gerência",
  Indicador_Progressao: "Progressão interna",
  Indicador_Empreendedorismo: "Empreendedorismo",
  Indicador_Mudanca_Area: "Mudança de área",
};
const nav = [
  ["overview", "Visão geral", LayoutDashboard],
  ["ai", "Laboratório XAI", Sparkles],
  ["insertion", "Inserção profissional", BriefcaseBusiness],
  ["trajectory", "Trajetórias", Route],
  ["geography", "Origem geográfica", MapPin],
  ["relations", "Relações e evidências", GitCompareArrows],
];
const pageCopy = {
  overview: [
    "O que acontece depois do diploma?",
    "Explore o perfil e as trajetórias profissionais dos egressos.",
  ],
  insertion: [
    "Da formação à atuação profissional",
    "Conheça as áreas de atuação e os tipos de instituição da base.",
  ],
  trajectory: [
    "Cada trajetória conta uma história",
    "Observe liderança, progressão e outros marcos ao longo do tempo.",
  ],
  geography: [
    "De onde vêm os egressos?",
    "Uma leitura da origem geográfica, por estado e região de nascimento.",
  ],
  relations: [
    "Transforme dados em perguntas",
    "Explore associações estatísticas e interprete as evidências com contexto.",
  ],
  ai: [
    "Da associação à explicação",
    "Compare modelos e entenda suas contribuições, com validação fora da amostra.",
  ],
  data: [
    "Uma boa análise começa pela base",
    "Importe um CSV preparado e configure o contexto da sua instituição.",
  ],
  methodology: [
    "Como interpretar este painel",
    "Entenda as definições, os cuidados e os limites da análise.",
  ],
};
const fmt = (value, digits = 0) =>
  value == null
    ? "—"
    : Number(value).toLocaleString("pt-BR", {
        maximumFractionDigits: digits,
        minimumFractionDigits: digits,
      });
const pct = (value) => (value == null ? "Suprimido" : `${fmt(value, 1)}%`);
const pvalue = (value) => (value < 0.001 ? "< 0,001" : fmt(value, 3));
const API_ORIGIN = (import.meta.env.VITE_API_ORIGIN || "").replace(/\/+$/, "");
const apiUrl = (path) => `${API_ORIGIN}/api${path}`;

async function api(path, { token, body, ...options } = {}) {
  const headers = {
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };
  if (body && !(body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
    body = JSON.stringify(body);
  }
  const response = await fetch(apiUrl(path), { ...options, headers, body });
  if (!response.ok) {
    let detail;
    try {
      detail = (await response.json()).detail;
    } catch {
      detail = "Não foi possível concluir a operação.";
    }
    throw new Error(
      typeof detail === "string"
        ? detail
        : "Confira os campos e tente novamente.",
    );
  }
  return response;
}

function Notice({ children, kind = "" }) {
  return (
    <div
      className={`notice ${kind}`}
      role={kind === "error" ? "alert" : undefined}
    >
      <Info size={17} />
      <div>{children}</div>
    </div>
  );
}
function Empty({ children = "Nenhum grupo pode ser exibido neste recorte." }) {
  return (
    <div className="empty">
      <Search size={25} />
      <p>{children}</p>
    </div>
  );
}
function Panel({ title, subtitle, children, action, className = "" }) {
  return (
    <section className={`panel ${className}`}>
      <header className="panel-heading">
        <div>
          <h2>{title}</h2>
          {subtitle && <p>{subtitle}</p>}
        </div>
        {action}
      </header>
      {children}
    </section>
  );
}
function Bars({ distribution, color = "green", suffix = "%", max = 100 }) {
  if (!distribution?.rows?.length) return <Empty />;
  return (
    <>
      <div className={`bars ${color}`}>
        {distribution.rows.map((row) => (
          <div className="bar-row" key={row.label}>
            <div className="bar-label">
              <span title={row.label}>{row.label}</span>
              <strong>
                {suffix === "%" ? pct(row.value) : `${fmt(row.value, 1)} ${suffix}`}
                <small>
                  {row.count != null ? `${fmt(row.count)} egressos` : ""}
                </small>
              </strong>
            </div>
            <div className="bar-track">
              <div
                style={{
                  width: `${Math.min(100, Math.max(0, (row.value / max) * 100))}%`,
                }}
              />
            </div>
          </div>
        ))}
      </div>
      {distribution.omitted > 0 && (
        <p className="chart-note">
          {distribution.omitted} categoria(s) com menos de 5 egressos
          omitida(s).
        </p>
      )}
    </>
  );
}
function IndicatorCard({ item, index }) {
  const icons = [BriefcaseBusiness, TrendingUp, Building2, Route],
    Icon = icons[index];
  return (
    <article className={`metric indicator-${index}`}>
      <div className="metric-top">
        <span>{item.label}</span>
        <span className="metric-icon">
          <Icon size={18} />
        </span>
      </div>
      <strong>{pct(item.value)}</strong>
      <p>
        {item.count == null
          ? "Contagem protegida por privacidade"
          : `${fmt(item.count)} egressos com evidência`}
      </p>
    </article>
  );
}
function DistributionPanel({ data, column, title, subtitle, color }) {
  return (
    <Panel title={title} subtitle={subtitle}>
      <Bars color={color} distribution={data.distributions[column]} />
    </Panel>
  );
}

function Overview({ data, session, setPage }) {
  const courses = data.distributions.Curso_de_Graduacao;
  return (
    <>
      <section className="welcome-banner">
        <div>
          <div className="eyebrow">
            <span /> INTELIGÊNCIA ARTIFICIAL EXPLICÁVEL
          </div>
          <h2>
            Como os modelos interpretam
            <br />
            as trajetórias?
          </h2>
          <p>
            Compare modelos, examine as contribuições dos fatores
            <br className="desktop-break" /> e interprete os resultados com contexto.
          </p>
          <button className="banner-link" onClick={() => setPage("ai")}>
            Explorar laboratório XAI <ArrowUpRight size={17} />
          </button>
        </div>
        <div className="banner-art" aria-hidden="true">
          <div className="orbit one" />
          <div className="orbit two" />
          <div className="orbit three" />
          <div className="art-line a" />
          <div className="art-line b" />
          <div className="art-node main">
            <GraduationCap size={38} />
          </div>
          <div className="art-node work">
            <BriefcaseBusiness size={25} />
          </div>
          <div className="art-node people">
            <Users size={24} />
          </div>
          <div className="art-node star">
            <Sparkles size={19} />
          </div>
          <i className="dot d1" />
          <i className="dot d2" />
          <i className="dot d3" />
        </div>
      </section>
      <div className="section-heading">
        <div>
          <h2>O recorte em perspectiva</h2>
          <p>Indicadores calculados a partir dos filtros selecionados.</p>
        </div>
        <span className="subtle-pill">
          <ShieldCheck size={14} /> Dados agregados
        </span>
      </div>
      <div className="metrics">
        <article className="metric total">
          <div className="metric-top">
            <span>Egressos no recorte</span>
            <span className="metric-icon">
              <Users size={18} />
            </span>
          </div>
          <strong>{fmt(data.total)}</strong>
          <p>de {fmt(data.base_total)} registros na base</p>
        </article>
        <article className="metric">
          <div className="metric-top">
            <span>Cursos no recorte</span>
            <span className="metric-icon">
              <GraduationCap size={18} />
            </span>
          </div>
          <strong>{fmt(courses.rows.length)}</strong>
          <p>com grupos visíveis no painel</p>
        </article>
        <article className="metric">
          <div className="metric-top">
            <span>Tempo desde a conclusão</span>
            <span className="metric-icon">
              <Clock3 size={18} />
            </span>
          </div>
          <strong>
            {fmt(data.median_years, 1)} <em>anos</em>
          </strong>
          <p>mediana do recorte selecionado</p>
        </article>
      </div>
      <div className="panel-grid">
        <DistributionPanel
          data={data}
          column="Curso_de_Graduacao"
          title="Egressos por curso"
          subtitle="Distribuição dos registros no recorte"
        />
        <DistributionPanel
          data={data}
          column="Periodo_Conclusao"
          title="Período de conclusão"
          subtitle="Uma visão das turmas representadas"
          color="gold"
        />
      </div>
      <div className="section-heading">
        <div>
          <h2>Marcos da trajetória profissional</h2>
          <p>O perfil registra evidências, não a totalidade da trajetória.</p>
        </div>
        <button className="text-button" onClick={() => setPage("trajectory")}>
          Ver detalhes <ArrowRight size={15} />
        </button>
      </div>
      <div className="metrics four">
        {data.indicators.map((item, i) => (
          <IndicatorCard key={item.key} item={item} index={i} />
        ))}
      </div>
      {data.coverage.length > 0 && (
        <Panel
          title="Cobertura institucional"
          subtitle="Base analítica em relação aos totais informados, sem filtros"
        >
          <Bars distribution={{ rows: data.coverage }} />
        </Panel>
      )}
      <Notice>
        Estes resultados descrevem a base disponível. Perfis públicos podem
        estar incompletos ou desatualizados e não representam, necessariamente,
        todos os egressos.
      </Notice>
    </>
  );
}
function Insertion({ data }) {
  return (
    <>
      <div className="panel-grid">
        <DistributionPanel
          data={data}
          column="Categoria_Cargo"
          title="Áreas de atuação"
          subtitle="Categorias do cargo informado · exclui registros sem informação"
        />
        <DistributionPanel
          data={data}
          column="Tipo_Instituicao"
          title="Onde atuam"
          subtitle="Tipos de instituição · exclui registros sem vínculo informado"
          color="gold"
        />
      </div>
      <div className="panel-grid">
        <DistributionPanel
          data={data}
          column="Genero"
          title="Gênero registrado"
          subtitle="Distribuição conforme os dados preparados"
        />
        <DistributionPanel
          data={data}
          column="Faixa_Etaria"
          title="Faixa etária"
          subtitle="Perfil dos registros no recorte"
          color="gold"
        />
      </div>
      <Notice>
        “Tipo de instituição” é a categoria do vínculo profissional. A
        localização atual do trabalho não é inferida a partir do local de
        nascimento.
      </Notice>
    </>
  );
}
function Trajectory({ data }) {
  const [indicator, setIndicator] = useState("Indicador_Lideranca");
  const item = data.indicators.find((i) => i.key === indicator);
  return (
    <>
      <div className="metrics four">
        {data.indicators.map((item, i) => (
          <IndicatorCard key={item.key} item={item} index={i} />
        ))}
      </div>
      <div className="section-heading">
        <div>
          <h2>Compare um indicador</h2>
          <p>Percentual com evidência dentro de cada grupo.</p>
        </div>
        <select
          aria-label="Indicador de trajetória"
          value={indicator}
          onChange={(e) => setIndicator(e.target.value)}
        >
          {Object.entries(indicatorLabels).map(([k, v]) => (
            <option key={k} value={k}>
              {v}
            </option>
          ))}
        </select>
      </div>
      <div className="panel-grid">
        <Panel
          title={`${item.label} por curso`}
          subtitle="Percentual calculado em cada curso"
        >
          <Bars distribution={{ rows: item.by_course }} />
        </Panel>
        <Panel
          title="Por período de conclusão"
          subtitle="Grupos pequenos e células sensíveis são omitidos"
        >
          <Bars color="gold" distribution={{ rows: item.by_period }} />
        </Panel>
      </div>
      <Panel
        title="Tempo desde a conclusão e trajetória"
        subtitle="Mediana de anos com e sem evidência · teste de Mann–Whitney U"
      >
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Indicador</th>
                <th>Com evidência</th>
                <th>Sem evidência</th>
                <th>p ajustado · Holm</th>
              </tr>
            </thead>
            <tbody>
              {data.time.map((row) => (
                <tr key={row.label}>
                  <td>{row.label}</td>
                  <td>{fmt(row.mediana_sim, 1)} anos</td>
                  <td>{fmt(row.mediana_nao, 1)} anos</td>
                  <td>{pvalue(row.p_holm)}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {!data.time.length && <Empty />}
        </div>
      </Panel>
      <Notice>
        Comparações entre pessoas com diferentes tempos desde a conclusão são
        transversais. Elas não demonstram uma evolução individual nem
        estabelecem causalidade.
      </Notice>
    </>
  );
}
function Geography({ data }) {
  return (
    <>
      <Notice>
        O painel mostra <strong>estado e região de nascimento</strong>. Estes
        dados não indicam residência atual nem localização do trabalho.
      </Notice>
      <div className="panel-grid">
        <DistributionPanel
          data={data}
          column="Regiao_Nascimento"
          title="Regiões de origem"
          subtitle="Percentual dos egressos por região de nascimento"
        />
        <DistributionPanel
          data={data}
          column="UF_Nascimento"
          title="Estados de nascimento"
          subtitle="Somente estados com pelo menos 5 registros"
          color="gold"
        />
      </div>
    </>
  );
}
function Relations({ data }) {
  return (
    <>
      <Panel
        title="Associação entre indicadores"
        subtitle="Fisher para tabelas 2 × 2; qui-quadrado para tabelas maiores. Correção de Holm na família de comparações."
      >
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Indicadores</th>
                <th>Teste</th>
                <th>Efeito</th>
                <th>p ajustado</th>
              </tr>
            </thead>
            <tbody>
              {data.associations.map((row) => (
                <tr key={row.a + row.b}>
                  <td>
                    <strong>{row.a}</strong>
                    <span className="table-secondary">× {row.b}</span>
                  </td>
                  <td>{row.teste}</td>
                  <td>
                    <span className="effect-pill">
                      {row.medida_efeito} {fmt(row.efeito, 3)}
                    </span>
                  </td>
                  <td>{pvalue(row.p_holm)}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {!data.associations.length && (
            <Empty>
              Não há comparações com células suficientes neste recorte.
            </Empty>
          )}
        </div>
      </Panel>
      <div className="panel-grid">
        <Panel title="O que significa o efeito?">
          <p className="body-copy">
            Phi descreve associação entre duas variáveis binárias. V de Cramér
            descreve a intensidade da associação em tabelas maiores. A magnitude
            deve ser interpretada junto ao contexto e ao tamanho da base.
          </p>
        </Panel>
        <Panel title="O que significa o valor de p?">
          <p className="body-copy">
            O valor de p é calculado sob a hipótese de independência. Não mede a
            importância prática da relação nem a probabilidade de a hipótese ser
            verdadeira. O ajuste de Holm considera as múltiplas comparações
            exibidas.
          </p>
        </Panel>
      </div>
      <Notice>
        Uma associação não demonstra causa. Comparações com células de 1 a 4
        registros são omitidas nesta tela.
      </Notice>
    </>
  );
}
function SignedContributions({ rows }) {
  if (!rows?.length) return <Empty>Não há grupos suficientes para exibir contribuições com privacidade.</Empty>;
  const extent = Math.max(...rows.map(r => Math.abs(r.Efeito)), 1);
  return <div className="signed-chart" aria-label="Contribuições médias por grupo">
    <div className="signed-legend"><span>Reduz a estimativa</span><span>Aumenta a estimativa</span></div>
    {rows.map(r => <div className="signed-row" key={r.Valor}>
      <div className="signed-label"><span>{r.Valor}</span><small>n = {r.n}</small></div>
      <div className="signed-track"><span className="zero-line" />
        <span className={r.Efeito >= 0 ? "positive" : "negative"} style={{left: `${r.Efeito >= 0 ? 50 : 50 + r.Efeito / extent * 48}%`, width: `${Math.abs(r.Efeito) / extent * 48}%`}} />
      </div><strong>{r.Efeito > 0 ? "+" : ""}{fmt(r.Efeito, 2)} pp</strong>
    </div>)}<p className="chart-note">A direção descreve a saída dos modelos. A barra não estima um efeito causal. Grupos de menos de cinco registros e supressões complementares não são exibidos.</p>
  </div>;
}
function Explanations({ session }) {
  const [indicator, setIndicator] = useState("Indicador_Lideranca");
  const [result, setResult] = useState(null), [error, setError] = useState("");
  const [busy, setBusy] = useState(false), [exportBusy, setExportBusy] = useState(false);
  const [model, setModel] = useState("Regressão logística"), [factor, setFactor] = useState("Anos de formado");
  const request = useRef(0);
  useEffect(() => {
    request.current++; setResult(null); setError(""); setBusy(false);
    return () => { request.current++; };
  }, [session.token, indicator]);
  async function calculate() {
    const id = ++request.current; setBusy(true); setError("");
    try {
      const r = await api(`/explanations/${indicator}`, { method: "POST", token: session.token });
      const value = await r.json(); if(id === request.current) setResult(value);
    } catch(e) { if(id === request.current) setError(e.message); }
    finally { if(id === request.current) setBusy(false); }
  }
  async function downloadXai() {
    setExportBusy(true); setError("");
    try {
      const r = await api(`/explanations/${indicator}/export`, {token: session.token});
      const url = URL.createObjectURL(await r.blob());
      const a = document.createElement('a'); a.href = url; a.download = 'alumni-view-xai.json'; a.click();
      setTimeout(()=>URL.revokeObjectURL(url),1000);
    } catch(e) {setError(e.message);} finally {setExportBusy(false);}
  }
  const rows = result?.effects[model][factor] || [];
  const selected = indicatorLabels[indicator];
  return <>
    <section className="xai-intro">
      <div><span className="eyebrow">LABORATÓRIO DE EXPLICABILIDADE</span><h2>O que os modelos aprenderam<br/>sobre as trajetórias?</h2>
      <p>Comece pela qualidade da previsão. Depois investigue a contribuição dos fatores para as estimativas dos modelos.</p></div>
      <div className="xai-steps"><span><b>01</b> Comparar modelos</span><span><b>02</b> Ler contribuições</span><span><b>03</b> Registrar evidências</span></div>
    </section>
    <Panel title="Escolha o indicador" subtitle="O XAI considera a base completa; os filtros das outras páginas não são aplicados aqui.">
      <div className="ai-controls"><label>Indicador a explicar<select value={indicator} disabled={busy} onChange={e=>setIndicator(e.target.value)}>
        {Object.entries(indicatorLabels).filter(([k])=>k!=="Indicador_Mudanca_Area").map(([k,v])=><option key={k} value={k}>{v}</option>)}
      </select></label><button className="primary" disabled={busy} onClick={calculate}>{busy?<LoaderCircle className="spin" size={18}/>:<Sparkles size={18}/>} {busy?"Analisando a base…":"Calcular e comparar"}</button></div>
      <p className="chart-note">{fmt(session.total)} registros · referência temporal: {session.reference_year} · cinco partições × três repetições. As explicações usam registros fora do treino na primeira repetição. O cálculo fica disponível nesta sessão.</p>
    </Panel>
    {busy && <div className="xai-progress" role="status"><LoaderCircle className="spin" size={20}/><div><strong>Treinando, validando e calculando contribuições…</strong><p>Esta análise é executada no servidor da plataforma. Pode levar alguns minutos, conforme a base.</p></div></div>}
    {error && <Notice kind="error">{error}</Notice>}
    {!result && !busy && <div className="panel-grid"><Panel title="O que entra nos modelos"><p className="body-copy">Curso, anos desde a conclusão, UF de nascimento e tipo de instituição. Gênero, nome e categoria do cargo não entram. Categorias raras são agrupadas usando apenas os dados de treino.</p></Panel><Panel title="O que esta análise permite"><p className="body-copy">Inspecionar associações aprendidas e comparar dois modelos com uma referência baseada apenas na prevalência. As saídas são agregadas e não classificam pessoas individualmente.</p></Panel></div>}
    {result && <>
      <div className="xai-context"><div><span>INDICADOR</span><strong>{selected}</strong></div><div><span>BASE ANALISADA</span><strong>{result.n} registros</strong></div><div><span>COM EVIDÊNCIA OBSERVADA</span><strong>{pct(result.prevalence)}</strong></div><span className="subtle-pill"><ShieldCheck size={14}/> Fora da amostra</span></div>
      <Panel title="01 · Os modelos conseguem discriminar os grupos?" subtitle="Média ± desvio padrão entre partições. Esse desvio não é um intervalo de confiança.">
        <div className="table-wrap"><table className="model-table"><thead><tr><th>Modelo</th><th>AUC ROC ↑</th><th>Precisão média (AP) ↑</th><th>Brier ↓</th></tr></thead><tbody>
          {Object.entries(result.metrics).map(([name,v])=><tr key={name} className={name.startsWith('Referência')?'baseline-row':''}><td><strong>{name}</strong>{name.startsWith('Referência')&&<span className="table-secondary">Não usa os fatores da trajetória</span>}</td>{['auc','ap','brier'].map(k=><td key={k}>{fmt(v[k].mean,3)}<small className="table-secondary">± {fmt(v[k].sd,3)}</small></td>)}</tr>)}
        </tbody></table></div>
        <div className="metric-guide"><p><b>AUC ROC</b> mede discriminação; 0,5 é a referência sem discriminação.</p><p><b>AP</b> resume precisão e recuperação. Compare com a referência de prevalência.</p><p><b>Brier</b> mede erro das probabilidades. Menor é melhor.</p></div>
        {result.warnings.filter(w=>w.startsWith('Ao menos')).map(w=><Notice key={w}>{w}</Notice>)}
      </Panel>
      <div className="section-heading"><div><h2>02 · Como os fatores contribuíram?</h2><p>Contribuições em pontos percentuais para a estimativa de {selected.toLowerCase()}.</p></div><select aria-label="Modelo explicável" value={model} onChange={e=>setModel(e.target.value)}>{Object.keys(result.auc).map(n=><option key={n}>{n}</option>)}</select></div>
      {result.warnings.filter(w=>w.startsWith('Fatores limitados')).map(w=><Notice key={w}>{w}</Notice>)}
      <div className="panel-grid">
        <Panel title="Importância global" subtitle="Média de |Shapley|. Mostra magnitude, sem direção.">
          <Bars suffix="pp" max={Math.max(...result.importance.map(r=>r[model]),1)} distribution={{rows:[...result.importance].sort((a,b)=>b[model]-a[model]).map(r=>({label:r.Fator,value:r[model]}))}}/>
          <p className="chart-note">Um fator importante pode contribuir para aumentar algumas estimativas e reduzir outras. Importância não é correlação nem causa.</p>
        </Panel>
        <Panel title="Contribuição média por grupo" action={<select aria-label="Fator explicado" value={factor} onChange={e=>setFactor(e.target.value)}>{Object.keys(result.effects[model]).map(f=><option key={f}>{f}</option>)}</select>}>
          <SignedContributions rows={rows}/>
        </Panel>
      </div>
      <details className="panel xai-details"><summary>Como os modelos diferem na importância dos fatores?</summary><div className="table-wrap"><table><thead><tr><th>Fator</th>{Object.keys(result.auc).map(n=><th key={n}>{n} · pp</th>)}</tr></thead><tbody>{result.importance.map(r=><tr key={r.Fator}><td>{r.Fator}</td>{Object.keys(result.auc).map(n=><td key={n}>{fmt(r[n],2)}</td>)}</tr>)}</tbody></table></div><p className="chart-note">Modelos distintos podem distribuir contribuições de modo diferente. A divergência é informação para análise, não um erro a esconder.</p></details>
      <Panel title="03 · Registre uma análise reproduzível" subtitle="Exportação agregada com métricas, contribuições, parâmetros e identificação da base.">
        <div className="xai-repro"><dl><dt>Procedimento</dt><dd>{result.protocol.version} · semente {result.protocol.seed}</dd><dt>Verificação de aditividade</dt><dd>{Math.max(...Object.values(result.additivity_error)) < 1e-7 ? 'Verificada para os dois modelos' : 'Requer revisão'}</dd><dt>Explicações</dt><dd>Cinco partições fora da amostra, fundo de até {result.protocol.background_max} registros de treino por partição</dd></dl><button className="primary" disabled={exportBusy} onClick={downloadXai}><Download size={17}/>{exportBusy?'Preparando…':'Exportar análise XAI'}</button></div>
        <details><summary>Parâmetros e identificação técnica da base</summary><p className="fingerprint">SHA-256: {result.protocol.data_sha256}</p><p className="chart-note">scikit-learn {result.protocol.sklearn} · vocabulário categórico e agrupamento de categorias raras definidos no treino. O arquivo exportado não contém linhas individuais.</p></details>
      </Panel>
      <Notice>As explicações descrevem modelos de associação. Não demonstram que alterar um fator mudaria a trajetória de alguém. O uso de fatores intervencionais pode criar combinações pouco frequentes entre variáveis correlacionadas.</Notice>
      <details className="panel xai-details"><summary>Fundamentação e limites do método</summary><p className="body-copy">Calculamos valores de Shapley exatos por quatro fatores, com média sobre um conjunto de referência do treino. Cada registro é explicado pelo modelo da partição que o deixou de fora. As médias combinam esses modelos, e não um único modelo final. Esse desenho não elimina viés de presença digital, erro de codificação ou desatualização da fonte.</p><p className="body-copy"><a href={result.references[0]} target="_blank" rel="noreferrer">Lundberg e Lee (2017): SHAP</a> · <a href={result.references[1]} target="_blank" rel="noreferrer">Documentação das métricas scikit-learn</a></p></details>
    </>}
  </>;
}

function DataPage({ onLoad, session, onForget, onDemo }) {
  const [file, setFile] = useState(null),
    [institution, setInstitution] = useState(""),
    [population, setPopulation] = useState({}),
    [courses, setCourses] = useState([]),
    [busy, setBusy] = useState(false),
    [error, setError] = useState("");
  async function submit(e) {
    e.preventDefault();
    if (!file) return;
    setBusy(true);
    setError("");
    try {
      const body = new FormData();
      body.append("file", file);
      body.append("institution", institution);
      body.append("population", JSON.stringify(Object.fromEntries(Object.entries(population).filter(([,v])=>v!=="").map(([k,v])=>[k,Number(v)]))));
      const response = await api("/import", { method: "POST", body });
      await onLoad(await response.json());
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <>
      <div className="panel-grid import-grid">
        <Panel
          title="Importar base de egressos"
          subtitle="CSV preparado · até 5 MB e 10.000 registros"
        >
          <form onSubmit={submit}>
            <label className="upload-area">
              <FileSpreadsheet size={34} />
              <strong>{file ? file.name : "Selecione seu arquivo CSV"}</strong>
              <span>
                Separador vírgula ou ponto e vírgula · codificação UTF-8
              </span>
              <input
                aria-label="Arquivo CSV"
                type="file"
                accept=".csv,text/csv"
                required
                onChange={async (e) => {
                  const next=e.target.files?.[0] || null; setError(""); setPopulation({}); setCourses([]);
                  if(next && next.size>5*1024*1024){setError("O CSV excede o limite de 5 MB.");setFile(null);return;}
                  setFile(next);
                  if(next){ const parsed=Papa.parse(await next.text(),{header:true,skipEmptyLines:true});
                    setCourses([...new Set(parsed.data.map(r=>r.Curso_de_Graduacao?.trim()).filter(Boolean))].sort()); }
                }}
              />
            </label>
            <label className="form-label">
              Instituição ou contexto da análise
              <input
                placeholder="Ex.: UNIPAMPA · Campus Alegrete"
                maxLength={120}
                value={institution}
                onChange={(e) => setInstitution(e.target.value)}
              />
            </label>
            <fieldset className="population-fields"><legend>População de referência por curso <small>Opcional</small></legend>
              <p className="chart-note">Se você conhece o total institucional de egressos, informe-o para calcular a cobertura. Sem esse dado, o painel mostra apenas a base analisada.</p>
              {!courses.length && <p className="chart-note">Selecione o CSV para listar os cursos.</p>}
              {courses.map(course=><label className="form-label" key={course}>{course}<input type="number" min="1" step="1" placeholder="Total institucional" value={population[course]??""} onChange={e=>setPopulation({...population,[course]:e.target.value})}/></label>)}
            </fieldset>
            {error && <Notice kind="error">{error}</Notice>}
            <button className="primary" type="submit" disabled={busy || !file}>
              {busy ? (
                <LoaderCircle size={17} className="spin" />
              ) : (
                <Upload size={17} />
              )}{" "}
              {busy ? "Validando os dados…" : "Importar e abrir painel"}
            </button>
          </form>
        </Panel>
        <div>
          <Panel
            title="Prepare os dados antes de começar"
            subtitle="A ferramenta recebe uma base analítica, com indicadores já codificados."
          >
            <ol className="steps">
              <li>
                <span>1</span>
                <div>
                  <strong>Use o formato esperado</strong>
                  <p>
                    Baixe o modelo e mantenha os nomes das colunas. Campos
                    obrigatórios precisam estar preenchidos.
                  </p>
                </div>
              </li>
              <li>
                <span>2</span>
                <div>
                  <strong>Classifique as informações</strong>
                  <p>
                    Defina categoria do cargo, tipo de instituição e indicadores
                    0/1. Os indicadores seguem o protocolo de codificação da pesquisa.
                  </p>
                </div>
              </li>
              <li>
                <span>3</span>
                <div>
                  <strong>Remova identificadores</strong>
                  <p>
                    O CSV usa um código por egresso. Nomes, URLs de perfis,
                    empresas e cargos por extenso não devem ser importados.
                  </p>
                </div>
              </li>
            </ol>
            <a className="secondary" href={apiUrl("/template")} download>
              <Download size={16} /> Baixar modelo CSV
            </a>
            <button type="button" className="text-button demo-button" onClick={onDemo}><RefreshCcw size={15}/> Usar demonstração fictícia</button>
          </Panel>
          {session && (
            <Panel title="Base ativa" subtitle={session.institution}>
              <div className="active-base">
                <Database size={23} />
                <div>
                  <strong>{fmt(session.total)} registros</strong>
                  <p>
                    {session.source === "exemplo"
                      ? "Dados fictícios de demonstração"
                      : "Base importada nesta sessão"}
                  </p>
                </div>
              </div>
              <button className="text-button danger" onClick={onForget}>
                <LogOut size={15} /> Encerrar e descartar a sessão
              </button>
            </Panel>
          )}
        </div>
      </div>
      <Notice>
        O arquivo é enviado à API Python e permanece em memória durante a
        sessão, que expira após quatro horas. A sessão é descartada ao encerrar
        ou reiniciar o servidor. A base não é salva no navegador nem no
        repositório. A implantação para acesso público exige autenticação e uma
        política de armazenamento própria.
      </Notice>
    </>
  );
}
function Methodology() {
  return (
    <>
      <div className="panel-grid">
        <Panel title="O que cada indicador representa">
          <dl className="definitions">
            <dt>Liderança ou gerência</dt>
            <dd>
              Evidência explícita de função de liderança ou gestão no material
              analisado.
            </dd>
            <dt>Progressão interna</dt>
            <dd>
              Evidência de mudança de cargo ou responsabilidade na mesma
              organização.
            </dd>
            <dt>Empreendedorismo</dt>
            <dd>
              Evidência de atuação como fundador, sócio ou responsável por
              negócio próprio.
            </dd>
            <dt>Mudança de área</dt>
            <dd>
              Transição documentada entre Computação e uma área não relacionada,
              em qualquer direção, segundo as regras da pesquisa. A definição precisa ser adaptada a cada curso.
            </dd>
          </dl>
        </Panel>
        <Panel title="Regras de leitura">
          <ul className="reading-rules">
            <li>
              <ShieldCheck size={20} />
              <div>
                <strong>Privacidade por agregação</strong>
                <p>
                  Recortes com menos de 10 egressos são bloqueados. Contagens de
                  grupos menores que 5 são omitidas ou mascaradas.
                </p>
              </div>
            </li>
            <li>
              <CircleHelp size={20} />
              <div>
                <strong>
                  Ausência de evidência não é ausência do fenômeno
                </strong>
                <p>
                  Um perfil incompleto pode não registrar liderança, progressão
                  ou um vínculo profissional.
                </p>
              </div>
            </li>
            <li>
              <GitCompareArrows size={20} />
              <div>
                <strong>Associação não implica causalidade</strong>
                <p>
                  As análises descrevem os dados disponíveis. A coleta é observacional e usa histórias profissionais autodeclaradas;
                  não é um experimento nem um acompanhamento prospectivo.
                </p>
              </div>
            </li>
          </ul>
        </Panel>
      </div>
      <Panel title="Sobre a pesquisa">
        <p className="body-copy">
          A Alumni View integra o projeto Além do Diploma, sobre trajetórias
          profissionais de egressos. O estudo de origem considera Ciência da
          Computação e Engenharia de Software da UNIPAMPA. A interface aceita
          outros cursos, mas as regras de classificação, a coleta e a
          interpretação precisam ser adequadas à realidade de cada instituição.
        </p>
        <p className="body-copy">
          Os cálculos estatísticos continuam em Python. Os modelos explicáveis
          consideram curso, anos desde a conclusão, UF de nascimento e tipo
          de instituição. Gênero e categoria de cargo não entram como fatores
          preditores. Os valores de Shapley representam contribuições para a
          saída dos modelos, não causas dos resultados.
        </p>
      </Panel>
      <Panel title="Colunas do CSV">
        <p className="body-copy">
          ID_Egresso, Curso_de_Graduacao, Ano_de_Conclusao, Periodo_Conclusao,
          Tempo_desde_Conclusao, Genero, Faixa_Etaria, UF_Nascimento,
          Regiao_Nascimento, Categoria_Cargo, Tipo_Instituicao,
          Indicador_Lideranca, Indicador_Progressao, Indicador_Empreendedorismo
          e Indicador_Mudanca_Area.
        </p>
        <p className="chart-note">
          Use 0 ou 1 nos quatro indicadores. Ano e tempo desde a conclusão devem
          ser inteiros. O período deve ser preparado previamente no CSV; a
          importação não o recalcula.
        </p>
      </Panel>
    </>
  );
}
function useDialogFocus() {
  const ref = useRef(null);
  useEffect(() => {
    const previous = document.activeElement;
    const panel = ref.current;
    const candidates = () => [
      ...panel.querySelectorAll(
        "button:not(:disabled), a[href], input, select, textarea",
      ),
    ];
    candidates()[0]?.focus();
    function trap(event) {
      if (event.key !== "Tab") return;
      const controls = candidates();
      const first = controls[0],
        last = controls.at(-1);
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last?.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first?.focus();
      }
    }
    panel.addEventListener("keydown", trap);
    const overflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      panel.removeEventListener("keydown", trap);
      document.body.style.overflow = overflow;
      previous?.focus();
    };
  }, []);
  return ref;
}

function FilterDrawer({
  session,
  filters,
  setFilters,
  years,
  setYears,
  indicators,
  setIndicators,
  onClose,
}) {
  const dialog = useDialogFocus();
  return (
    <div className="modal-backdrop" onClick={onClose}>
      <aside
        ref={dialog}
        className="filter-drawer"
        role="dialog"
        aria-modal="true"
        aria-label="Filtros do painel"
        onClick={(e) => e.stopPropagation()}
      >
        <header>
          <div>
            <h2>Personalize o recorte</h2>
            <p>Os filtros se aplicam às análises do painel.</p>
          </div>
          <button
            className="icon-button"
            aria-label="Fechar filtros"
            onClick={onClose}
          >
            <X size={21} />
          </button>
        </header>
        <button
          className="text-button"
          onClick={() => {
            setFilters({});
            setYears(session.years);
            setIndicators([]);
          }}
        >
          <RefreshCcw size={15} /> Limpar todos os filtros
        </button>
        {Object.entries(columns).map(([column, label]) => (
          <fieldset key={column}>
            <legend>{label}</legend>
            {session.options[column].map((value) => (
              <label className="check-option" key={value}>
                <input
                  type="checkbox"
                  checked={(
                    filters[column] ?? session.options[column]
                  ).includes(value)}
                  onChange={(e) => {
                    const current = filters[column] ?? session.options[column];
                    setFilters({
                      ...filters,
                      [column]: e.target.checked
                        ? [...current, value]
                        : current.filter((v) => v !== value),
                    });
                  }}
                />
                <span>{value}</span>
              </label>
            ))}
          </fieldset>
        ))}
        <fieldset>
          <legend>Ano de conclusão</legend>
          <div className="year-inputs">
            <input
              aria-label="Ano inicial"
              type="number"
              min={session.years[0]}
              max={session.years[1]}
              value={years[0]}
              onChange={(e) => setYears([Number(e.target.value), years[1]])}
            />
            <span>até</span>
            <input
              aria-label="Ano final"
              type="number"
              min={session.years[0]}
              max={session.years[1]}
              value={years[1]}
              onChange={(e) => setYears([years[0], Number(e.target.value)])}
            />
          </div>
        </fieldset>
        <fieldset>
          <legend>Exigir evidência de</legend>
          <p className="chart-note">
            Com mais de um indicador, todos devem estar presentes.
          </p>
          {Object.entries(indicatorLabels).map(([key, label]) => (
            <label className="check-option" key={key}>
              <input
                type="checkbox"
                checked={indicators.includes(key)}
                onChange={(e) =>
                  setIndicators(
                    e.target.checked
                      ? [...indicators, key]
                      : indicators.filter((v) => v !== key),
                  )
                }
              />
              <span>{label}</span>
            </label>
          ))}
        </fieldset>
        <div className="drawer-footer">
          <button className="primary" onClick={onClose}>
            <Check size={16} /> Ver resultados
          </button>
        </div>
      </aside>
    </div>
  );
}
function ExportDialog({ session, query, onClose }) {
  const dialog = useDialogFocus();
  const [busy, setBusy] = useState(""),
    [error, setError] = useState("");
  async function download(format) {
    setBusy(format);
    setError("");
    try {
      const response = await api(`/export/${format}`, {
        method: "POST",
        token: session.token,
        body: query,
      });
      const url = URL.createObjectURL(await response.blob());
      const a = document.createElement("a");
      a.href = url;
      a.download = `alumni-view-relatorio.${format === "csv" ? "zip" : format}`;
      a.click();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy("");
    }
  }
  return (
    <div className="modal-backdrop centered" onClick={onClose}>
      <section
        ref={dialog}
        className="export-dialog"
        role="dialog"
        aria-modal="true"
        aria-label="Exportar relatório"
        onClick={(e) => e.stopPropagation()}
      >
        <header>
          <div>
            <h2>Leve as análises com você</h2>
            <p>Relatório agregado do recorte selecionado.</p>
          </div>
          <button
            className="icon-button"
            aria-label="Fechar exportação"
            onClick={onClose}
          >
            <X size={20} />
          </button>
        </header>
        <div className="export-options">
          {[
            ["pdf", "Documento PDF"],
            ["html", "Página HTML"],
            ["csv", "Tabelas CSV · ZIP"],
            ["json", "Dados JSON"],
            ["md", "Texto Markdown"],
          ].map(([format, label]) => (
            <button
              disabled={!!busy}
              key={format}
              onClick={() => download(format)}
            >
              {busy === format ? (
                <LoaderCircle className="spin" size={20} />
              ) : (
                <Download size={20} />
              )}
              <span>{label}</span>
              <ChevronRight size={16} />
            </button>
          ))}
        </div>
        {error && <Notice kind="error">{error}</Notice>}
        <p className="chart-note">
          Nenhum formato contém registros individuais. A análise de IA é
          consultada separadamente e não está incluída neste relatório.
        </p>
      </section>
    </div>
  );
}
function App() {
  const [page, setPage] = useState("overview"),
    [session, setSession] = useState(null),
    [data, setData] = useState(null),
    [filters, setFilters] = useState({}),
    [years, setYears] = useState([2010, 2025]),
    [indicators, setIndicators] = useState([]),
    [loading, setLoading] = useState(true),
    [error, setError] = useState(""),
    [drawer, setDrawer] = useState(false),
    [exportOpen, setExportOpen] = useState(false),
    [mobile, setMobile] = useState(false);
  const generation = useRef(0);
  async function loadSession(next) {
    const previous = session;
    setSession(next);
    setFilters({});
    setYears(next.years);
    setIndicators([]);
    setData(null);
    setPage("overview");
    setError("");
    if (previous)
      api("/session", { method: "DELETE", token: previous.token }).catch(
        () => {},
      );
  }
  async function loadDemo() {
    setLoading(true);
    setError("");
    try {
      const r = await api("/demo", { method: "POST" });
      await loadSession(await r.json());
    } catch (e) {
      setError(`Não foi possível conectar à API. ${e.message}`);
      setLoading(false);
    }
  }
  useEffect(() => {
    loadDemo();
  }, []);
  const query = { filters, years, indicators };
  const queryKey = JSON.stringify(query);
  useEffect(() => {
    if (!session) return;
    const controller = new AbortController();
    const current = ++generation.current;
    setLoading(true);
    setError("");
    api("/dashboard", {
      method: "POST",
      token: session.token,
      body: query,
      signal: controller.signal,
    })
      .then((r) => r.json())
      .then((value) => {
        if (current === generation.current) setData(value);
      })
      .catch((e) => {
        if (e.name !== "AbortError" && current === generation.current) {
          setError(e.message);
          setData(null);
        }
      })
      .finally(() => {
        if (current === generation.current) setLoading(false);
      });
    return () => controller.abort();
  }, [session?.token, queryKey]);
  useEffect(() => {
    document.title = `${pageCopy[page][0]} · Alumni View`;
    window.scrollTo({ top: 0 });
  }, [page]);
  useEffect(() => {
    function close(e) {
      if (e.key === "Escape") {
        setDrawer(false);
        setExportOpen(false);
        setMobile(false);
      }
    }
    window.addEventListener("keydown", close);
    return () => window.removeEventListener("keydown", close);
  }, []);
  const active =
    Object.entries(filters).filter(
      ([k, v]) => v.length !== session?.options[k]?.length,
    ).length +
    (session && JSON.stringify(years) !== JSON.stringify(session.years)
      ? 1
      : 0) +
    indicators.length;
  const title =
    nav.find((n) => n[0] === page)?.[1] ||
    { data: "Base de dados", methodology: "Metodologia" }[page];
  const noFilters = ["data", "methodology", "ai"].includes(page);
  async function forget() {
    try {
      await api("/session", { method: "DELETE", token: session.token });
      setSession(null);
      setData(null);
      setPage("data");
    } catch (e) {
      setError(e.message);
    }
  }
  function navigate(id) {
    setPage(id);
    setMobile(false);
  }
  return (
    <div className="app-shell">
      <a href="#main" className="skip-link">
        Ir para o conteúdo
      </a>
      {mobile && (
        <div className="sidebar-shade" onClick={() => setMobile(false)} />
      )}
      <aside className={`sidebar ${mobile ? "open" : ""}`}>
        <a
          className="brand"
          href="#"
          onClick={(e) => {
            e.preventDefault();
            navigate("overview");
          }}
        >
          <span className="brand-icon">
            <GraduationCap size={26} />
          </span>
          <span>
            <strong>
              alumni<span>view</span>
              <i />
            </strong>
            <small>ALÉM DO DIPLOMA</small>
          </span>
        </a>
        <div className="workspace-label">ESPAÇO DE ANÁLISE</div>
        <nav aria-label="Principal">
          {nav.map(([id, label, Icon]) => (
            <button
              key={id}
              className={page === id ? "selected" : ""}
              onClick={() => navigate(id)}
            >
              <Icon size={18} />
              <span>{label}</span>
              {id === "ai" && <span className="new-badge">XAI</span>}
              {page === id && id !== "ai" && <span className="nav-dot" />}
            </button>
          ))}
        </nav>
        <div className="workspace-label manage-label">ORGANIZAÇÃO</div>
        <nav aria-label="Organização">
          <button
            className={page === "data" ? "selected" : ""}
            onClick={() => navigate("data")}
          >
            <Database size={18} />
            <span>Base de dados</span>
          </button>
          <button
            className={page === "methodology" ? "selected" : ""}
            onClick={() => navigate("methodology")}
          >
            <BookOpen size={18} />
            <span>Metodologia</span>
          </button>
        </nav>
        <div className="sidebar-bottom">
          <div className="research-card">
            <span>
              <GraduationCap size={18} /> PESQUISA QUE CONECTA
            </span>
            <p>
              Conhecer trajetórias.
              <br />
              Ampliar possibilidades.
            </p>
            <button onClick={() => navigate("methodology")}>
              Sobre o projeto <ArrowUpRight size={15} />
            </button>
          </div>
          <div className="institution">
            <span className="institution-icon">
              <Building2 size={18} />
            </span>
            <div>
              <strong>{session?.institution || "Seu espaço de análise"}</strong>
              <small>
                {session?.source === "exemplo"
                  ? "Ambiente de demonstração"
                  : "Acompanhamento de egressos"}
              </small>
            </div>
          </div>
        </div>
      </aside>
      <div className="main-shell">
        <header className="topbar">
          <div className="breadcrumb">
            <button
              className="icon-button mobile-menu"
              aria-label="Abrir navegação"
              onClick={() => setMobile(true)}
            >
              <Menu size={22} />
            </button>
            <span>Espaço de análise</span>
            <ChevronRight size={13} />
            <strong>{title}</strong>
          </div>
          <div className="topbar-right">
            <span className="status-dot" />
            <span>
              {session?.source === "exemplo" ? "Demonstração" : "Sessão de análise"}
            </span>
            <button
              className="help-button"
              title="Como interpretar o painel"
              aria-label="Ajuda e metodologia"
              onClick={() => navigate("methodology")}
            >
              <CircleHelp size={20} />
            </button>
          </div>
        </header>
        <main id="main">
          <div className="page-heading">
            <div>
              <div className="eyebrow page-eyebrow">
                ALUMNI VIEW <span>/</span> {title.toUpperCase()}
              </div>
              <h1>{pageCopy[page][0]}</h1>
              <p>{pageCopy[page][1]}</p>
            </div>
            {!noFilters && session && (
              <div className="heading-actions">
                <button className="secondary" onClick={() => setDrawer(true)}>
                  <SlidersHorizontal size={16} /> Filtros{" "}
                  {active > 0 && <b className="count-badge">{active}</b>}
                </button>
                <button
                  className="primary"
                  disabled={!data || data.blocked || loading}
                  onClick={() => setExportOpen(true)}
                >
                  <Download size={16} /> Exportar
                </button>
              </div>
            )}
          </div>
          {session?.source === "exemplo" && page !== "data" && (
            <div className="demo-notice">
              <span>
                <span className="demo-icon">
                  <Info size={15} />
                </span>{" "}
                Você está explorando{" "}
                <strong>dados fictícios de demonstração.</strong>
              </span>
              <button onClick={() => navigate("data")}>
                Importar minha base <ArrowRight size={15} />
              </button>
            </div>
          )}
          {!noFilters && session && (
            <div className="filter-summary">
              <span>
                <span className="live-dot" />{" "}
                {active ? "Recorte personalizado" : "Base completa"}{" "}
                <span className="summary-divider">·</span> {fmt(session.total)}{" "}
                registros na base
              </span>
              {active > 0 ? (
                <button
                  className="text-button"
                  onClick={() => {
                    setFilters({});
                    setYears(session.years);
                    setIndicators([]);
                  }}
                >
                  Limpar filtros <X size={13} />
                </button>
              ) : (
                <span>
                  {session.years[0]} — {session.years[1]}
                </span>
              )}
            </div>
          )}
          {error && (
            <Notice kind="error">
              {error}{" "}
              <button className="text-button" onClick={loadDemo}>
                Abrir demonstração
              </button>
            </Notice>
          )}
          {page === "data" ? (
            <DataPage
              onLoad={loadSession}
              session={session}
              onForget={forget}
              onDemo={loadDemo}
            />
          ) : page === "methodology" ? (
            <Methodology />
          ) : page === "ai" ? (
            session ? (
              <Explanations session={session} />
            ) : (
              <Empty>
                Abra uma demonstração ou importe sua base para começar.
              </Empty>
            )
          ) : loading ? (
            <div className="loading-state" role="status">
              <LoaderCircle className="spin" size={25} />
              <p>Preparando as análises…</p>
            </div>
          ) : data?.blocked ? (
            <Panel title="Vamos ampliar esse olhar?">
              <Empty>{data.message}</Empty>
              <button className="secondary" onClick={() => setDrawer(true)}>
                Ajustar filtros
              </button>
            </Panel>
          ) : data ? (
            page === "overview" ? (
              <Overview data={data} session={session} setPage={setPage} />
            ) : page === "insertion" ? (
              <Insertion data={data} />
            ) : page === "trajectory" ? (
              <Trajectory data={data} />
            ) : page === "geography" ? (
              <Geography data={data} />
            ) : (
              <Relations data={data} />
            )
          ) : !error ? (
            <Empty>
              Importe sua base ou{" "}
              <button className="text-button" onClick={loadDemo}>
                abra a demonstração
              </button>
              .
            </Empty>
          ) : null}
          <footer className="footer">
            <span>
              Alumni View <span>·</span> Além do Diploma
            </span>
            <span>
              <ShieldCheck size={13} /> Análises agregadas, trajetórias
              respeitadas.
            </span>
          </footer>
        </main>
      </div>
      {drawer && session && (
        <FilterDrawer
          session={session}
          filters={filters}
          setFilters={setFilters}
          years={years}
          setYears={setYears}
          indicators={indicators}
          setIndicators={setIndicators}
          onClose={() => setDrawer(false)}
        />
      )}{" "}
      {exportOpen && session && (
        <ExportDialog
          session={session}
          query={query}
          onClose={() => setExportOpen(false)}
        />
      )}
    </div>
  );
}

createRoot(document.getElementById("root")).render(<App />);
