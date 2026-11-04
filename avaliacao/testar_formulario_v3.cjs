const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const spec=JSON.parse(fs.readFileSync(__dirname+'/instrumento_v3.json','utf8'));
const source=fs.readFileSync(__dirname+'/criar_formulario_v3.gs','utf8');
let created=0;const props=new Map(),nodes=[],pages=[{items:[],Title:'Abertura'}];let current=pages[0];
function node(type){const n={type};nodes.push(n);for(const method of ['setTitle','setRequired','setHelpText','setChoiceValues','setRows','setColumns','setChoices','setGoToPage','showOtherOption'])n[method]=function(v){this[method==='showOtherOption'?'Other':method.slice(3)]=v;return this;};n.createChoice=(label,target)=>({label,target});return n;}
const form={getId:()=> 'limpo-id',getEditUrl:()=> 'https://example.invalid/edit'};
for(const method of ['setCollectEmail','setProgressBar','setShuffleQuestions','setPublishingSummary','setConfirmationMessage','setDescription'])form[method]=function(v){this[method.slice(3)]=v;return this;};
for(const [method,type] of Object.entries({addMultipleChoiceItem:'choice',addCheckboxItem:'checks',addParagraphTextItem:'paragraph',addGridItem:'grid',addSectionHeaderItem:'header'}))form[method]=()=>{const n=node(type);current.items.push(n);return n;};
form.addPageBreakItem=()=>{const n=node('page');n.items=[];pages.push(n);current=n;return n;};
const context={FormApp:{create:(title,published)=>{assert.equal(published,false);created++;return form;},openById:()=>form,PageNavigationType:{SUBMIT:'SUBMIT'}},PropertiesService:{getScriptProperties:()=>({getProperty:k=>props.get(k),setProperty:(k,v)=>props.set(k,v)})},LockService:{getScriptLock:()=>({waitLock:()=>{},releaseLock:()=>{}})},Logger:{log:()=>{}}};
vm.createContext(context);vm.runInContext(source,context);context.criarFormularioAlumniViewLimpo();const count=nodes.length;context.criarFormularioAlumniViewLimpo();assert.equal(created,1);assert.equal(nodes.length,count);assert.equal(form.CollectEmail,false);
const grids={UP:'Utilidade percebida',FUP:'Facilidade de uso percebida',XP:'Avaliação das explicações',IU:'Intenção de uso'};
for(const q of spec.items){
 const prefix=Object.keys(grids).find(k=>q.id.startsWith(k));
 if(prefix){const n=nodes.find(n=>n.Title===grids[prefix]);assert(n.Rows.includes(q.display_title));assert.deepEqual(Array.from(n.Columns),spec.grid_columns);assert.equal(n.Required,false);(n.ids??=[]).push(q.id);}
 else {const matches=nodes.filter(n=>n.Title===q.display_title);assert.equal(matches.length,1,q.id);const n=matches[0];n.ids=[q.id];assert.equal(n.Required,q.required);}
}
const d3=nodes.find(n=>n.ids?.includes('D3'));assert.equal(d3.Other,true);assert.deepEqual(Array.from(d3.ChoiceValues),['A cada ano','A cada três anos','A cada cinco anos','Sem periodicidade definida','Não sei informar']);
for(const [id,title] of Object.entries({C0:'Você concorda em participar voluntariamente?',U0:'Você conseguiu experimentar a Alumni View?',X0:'Você conseguiu visualizar resultados no Laboratório XAI?',UT:'Como foi a realização das tarefas?'})){const n=nodes.find(n=>n.Title===title);assert(n,title);n.ids=[id];}
assert.equal(nodes.filter(n=>n.type==='grid').length,5);assert.equal(nodes.find(n=>n.ids?.includes('UT')).Rows.length,7);
assert.equal(nodes.flatMap(n=>n.ids||[]).filter(id=>spec.items.some(q=>q.id===id)).length,43);
assert(!nodes.some(n=>/^(UP|FUP|XP|XC|IU|D)\d\./.test(n.Title||'')));
function path(choices){let page=pages[0];const seen=[],visited=new Set();while(page){assert(!visited.has(page));visited.add(page);let jump;for(const n of page.items){seen.push(...n.ids||[]);if(n.Choices){const id=n.ids[0];jump=n.Choices[choices[id]??0].target;}}if(jump==='SUBMIT')break;if(jump){page=jump;continue;}const next=pages[pages.indexOf(page)+1];if(!next||next.GoToPage==='SUBMIT')break;page=next.GoToPage||next;}return seen;}
assert.deepEqual(path({C0:1}),['C0']);
let seen=path({D1:2,U0:1});assert(seen.includes('D7')&&seen.includes('N1')&&!seen.includes('D2')&&!seen.includes('UP1'));
seen=path({D1:0,U0:0,X0:0});assert(seen.includes('D3')&&seen.includes('XP1')&&seen.includes('XC3')&&seen.includes('IU2')&&seen.includes('A3')&&!seen.includes('XN1')&&!seen.includes('N1'));
for(const option of [1,2]){seen=path({D1:3,U0:0,X0:option});assert(seen.includes('XN1')&&seen.includes('UP1')&&seen.includes('IU1')&&!seen.includes('D2')&&!seen.includes('XP1')&&!seen.includes('N1'));}
const d4=nodes.find(n=>n.ids?.includes('D4'));assert.equal(d4.Other,true);assert(d4.ChoiceValues.includes('Google Forms')&&d4.ChoiceValues.includes('Microsoft Forms')&&d4.ChoiceValues.includes('LimeSurvey'));assert(!nodes.some(n=>/código da sessão|informa.*organizad/i.test(n.Title||'')));
console.log('OK: periodicidade com intervalos uniformes, ausência/desconhecimento separados, Outro com campo livre; quatro matrizes de avaliação e 43 itens; campo Código da sessão removido; D4 avalia ferramentas; desvios e idempotência verificados.');
