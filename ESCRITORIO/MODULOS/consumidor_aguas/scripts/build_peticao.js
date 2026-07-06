/*
 * build_peticao.js — Gerador de petição inicial (DOCX) para ações contra ÁGUAS DO PARÁ.
 *
 * USO:
 *   1) npm install docx   (uma vez, no diretório de trabalho)
 *   2) Edite/gere um JSON `dados.json` com os dados do caso (ver ESQUEMA abaixo) OU
 *      monte o array `secoes` diretamente. A skill normalmente preenche `dados.json`
 *      a partir da pasta do cliente e roda:  node build_peticao.js dados.json saida.docx
 *
 * Este script é um ESQUELETO parametrizável: a skill injeta os parágrafos jurídicos
 * (fatos + direito + pedidos) já redigidos no campo `corpo` do JSON. Mantém a formatação
 * forense padrão (A4, Times New Roman 12, 1,5, justificado, paginação).
 *
 * ESQUEMA do dados.json:
 * {
 *   "comarca": "Parauapebas",
 *   "gratuidade": true,
 *   "nomeAcao": "AÇÃO DECLARATÓRIA DE INEXIGIBILIDADE DE DÉBITO C/C ... DANOS MORAIS ...",
 *   "qualificacaoAutor": "FULANO DE TAL, brasileiro, ... CPF ..., residente ...",
 *   "advogado": { "nome": "...", "oab": "...", "endereco": "...", "telefone": "...", "email": "..." },
 *   "valorCausaExtenso": "R$ 15.000,00 (quinze mil reais)",
 *   "corpo": [
 *      { "tipo": "H1", "texto": "I — DOS FATOS" },
 *      { "tipo": "H2", "texto": "I.1. ..." },
 *      { "tipo": "P",  "texto": "Parágrafo..." },
 *      { "tipo": "QUOTE", "texto": "Citação recuada..." },
 *      { "tipo": "BULLET", "texto": "item" },
 *      { "tipo": "NUM", "texto": "item numerado" }
 *   ],
 *   "rol": [ ["DOC. 01","Procuração"], ["DOC. 02","..."] ]
 * }
 */
const fs = require('fs');
const {
  Document, Packer, Paragraph, TextRun, AlignmentType,
  HeadingLevel, LevelFormat, Footer, PageNumber, PageBreak,
} = require('docx');

const F = 'Times New Roman';
const SZ = 24; // 12pt

const args = process.argv.slice(2);
const dadosPath = args[0] || 'dados.json';
const saidaPath = args[1] || 'PETICAO_INICIAL.docx';
const d = JSON.parse(fs.readFileSync(dadosPath, 'utf8'));

function P(texto, opts = {}) {
  return new Paragraph({
    alignment: opts.align || AlignmentType.JUSTIFIED,
    spacing: { line: 360, before: opts.before || 0, after: opts.after == null ? 120 : opts.after },
    indent: opts.indent === false ? undefined : { firstLine: 720 },
    children: [new TextRun({ text: texto, bold: opts.bold, italics: opts.italic, font: F, size: opts.size || SZ })],
  });
}
function H1(t){return new Paragraph({heading:HeadingLevel.HEADING_1,alignment:AlignmentType.CENTER,spacing:{before:360,after:240,line:360},children:[new TextRun({text:t,bold:true,font:F,size:26})]});}
function H2(t){return new Paragraph({heading:HeadingLevel.HEADING_2,spacing:{before:280,after:160,line:360},children:[new TextRun({text:t,bold:true,font:F,size:25})]});}
function H3(t){return new Paragraph({heading:HeadingLevel.HEADING_3,spacing:{before:200,after:120,line:360},children:[new TextRun({text:t,bold:true,italics:true,font:F,size:24})]});}
function QUOTE(t){return new Paragraph({alignment:AlignmentType.JUSTIFIED,spacing:{line:276,before:120,after:160},indent:{left:1700,right:600},children:[new TextRun({text:t,italics:true,font:F,size:22})]});}
function BULLET(t){return new Paragraph({numbering:{reference:'bul',level:0},alignment:AlignmentType.JUSTIFIED,spacing:{line:360,after:80},children:[new TextRun({text:t,font:F,size:SZ})]});}
function NUM(t){return new Paragraph({numbering:{reference:'num',level:0},alignment:AlignmentType.JUSTIFIED,spacing:{line:360,after:120},children:[new TextRun({text:t,font:F,size:SZ})]});}
function BLANK(){return new Paragraph({children:[new TextRun('')],spacing:{line:360}});}

const children = [];
// Endereçamento
children.push(new Paragraph({ spacing:{line:360,after:480}, children:[new TextRun({ text:
  `EXCELENTÍSSIMO(A) SENHOR(A) DOUTOR(A) JUIZ(ÍZA) DE DIREITO DO JUIZADO ESPECIAL CÍVEL DA COMARCA DE ${(d.comarca||'PARAUAPEBAS').toUpperCase()} — ESTADO DO PARÁ.`,
  bold:true, font:F, size:SZ })]}));
children.push(new Paragraph({ spacing:{line:360,after:240}, children:[new TextRun({ text:
  `Pedido de gratuidade da justiça: ${d.gratuidade?'SIM':'NÃO'}. Pedido de tutela de urgência inaudita altera parte: SIM.`,
  bold:true, font:F, size:22 })]}));
children.push(BLANK());
// Qualificação autor
children.push(P(d.qualificacaoAutor, {}));
children.push(BLANK());
// Nome da ação
children.push(new Paragraph({ alignment:AlignmentType.CENTER, spacing:{line:360,before:240,after:240}, children:[new TextRun({ text:d.nomeAcao, bold:true, font:F, size:SZ })]}));
children.push(BLANK());
// Ré (fixa)
children.push(P('em face de ÁGUAS DO PARÁ D SPE S.A., concessionária do serviço público de abastecimento de água e esgotamento sanitário, pessoa jurídica de direito privado, inscrita no CNPJ/MF sob o nº 61.067.904/0001-29, com endereço na Av. Potiguá, Galeria Diamond, Sala 05 / R.A-613, Bairro Primavera, Parauapebas/PA, CEP 68.515-000, telefone 0800 091 0091, pelos fatos e fundamentos a seguir.'));

// CORPO (fatos + direito + pedidos) — injetado pela skill
const map = { H1, H2, H3, P:(o)=>P(o.texto,o), QUOTE:(o)=>QUOTE(o.texto), BULLET:(o)=>BULLET(o.texto), NUM:(o)=>NUM(o.texto) };
(d.corpo||[]).forEach(b => {
  if (b.tipo==='H1') children.push(H1(b.texto));
  else if (b.tipo==='H2') children.push(H2(b.texto));
  else if (b.tipo==='H3') children.push(H3(b.texto));
  else if (b.tipo==='QUOTE') children.push(QUOTE(b.texto));
  else if (b.tipo==='BULLET') children.push(BULLET(b.texto));
  else if (b.tipo==='NUM') children.push(NUM(b.texto));
  else children.push(P(b.texto, b));
});

// Valor da causa
children.push(H2('DO VALOR DA CAUSA'));
children.push(P(`Dá-se à causa o valor de ${d.valorCausaExtenso}.`));
children.push(BLANK());
children.push(P('Termos em que, pede e espera deferimento.', { indent:false }));
children.push(BLANK());
children.push(P(`${d.comarca||'Parauapebas'}/PA, ____ de __________ de 2026.`, { indent:false, align:AlignmentType.RIGHT }));
children.push(BLANK()); children.push(BLANK());
const ADV_PADRAO = { nome:'Herbeth Matheus Mendonça do Nascimento', oab:'39.261', endereco:'Rua D, nº 410-B, Cidade Nova, Parauapebas/PA', telefone:'(94) 99214-7889', email:'herbethmatheus.adv@gmail.com' };
const adv = Object.assign({}, ADV_PADRAO, d.advogado||{});
[`__________________________________________________`, (adv.nome||'[NOME]').toUpperCase(), `ADVOGADO — OAB/PA nº ${adv.oab||'[PREENCHER]'}`, adv.endereco||'[Endereço profissional]', `${adv.telefone||'[Telefone]'} — ${adv.email||'[e-mail]'}`]
  .forEach((t,i)=> children.push(new Paragraph({ alignment:AlignmentType.CENTER, spacing:{line:360,after:80}, children:[new TextRun({text:t, bold:i===1, font:F, size:i>1?22:24})]})));

// Anexo único
children.push(new Paragraph({ children:[new PageBreak()] }));
children.push(new Paragraph({ alignment:AlignmentType.CENTER, spacing:{line:360,after:240}, children:[new TextRun({text:'ANEXO ÚNICO — ROL DE DOCUMENTOS INSTRUTÓRIOS', bold:true, font:F, size:26})]}));
(d.rol||[]).forEach(([id,desc])=> children.push(new Paragraph({ alignment:AlignmentType.JUSTIFIED, indent:{left:720,hanging:720}, spacing:{line:360,after:80}, children:[new TextRun({text:`${id} — `,bold:true,font:F,size:SZ}), new TextRun({text:desc,font:F,size:SZ})]})));

const doc = new Document({
  creator: (adv.nome||'Advogado'),
  styles: { default:{document:{run:{font:F,size:SZ}}}, paragraphStyles:[
    {id:'Heading1',name:'Heading 1',basedOn:'Normal',next:'Normal',quickFormat:true,run:{size:26,bold:true,font:F},paragraph:{spacing:{before:360,after:240},outlineLevel:0}},
    {id:'Heading2',name:'Heading 2',basedOn:'Normal',next:'Normal',quickFormat:true,run:{size:25,bold:true,font:F},paragraph:{spacing:{before:280,after:160},outlineLevel:1}},
    {id:'Heading3',name:'Heading 3',basedOn:'Normal',next:'Normal',quickFormat:true,run:{size:24,bold:true,italics:true,font:F},paragraph:{spacing:{before:200,after:120},outlineLevel:2}},
  ]},
  numbering: { config:[
    {reference:'bul',levels:[{level:0,format:LevelFormat.BULLET,text:'•',alignment:AlignmentType.LEFT,style:{paragraph:{indent:{left:1080,hanging:360}}}}]},
    {reference:'num',levels:[{level:0,format:LevelFormat.LOWER_ROMAN,text:'(%1)',alignment:AlignmentType.LEFT,style:{paragraph:{indent:{left:1080,hanging:540}}}}]},
  ]},
  sections: [{
    footers:{ default:new Footer({children:[new Paragraph({alignment:AlignmentType.RIGHT,children:[new TextRun({text:'Página ',font:F,size:20}),new TextRun({children:[PageNumber.CURRENT],font:F,size:20})]})]}) },
    children,
  }],
});

Packer.toBuffer(doc).then(function(buf){ fs.writeFileSync(saidaPath, buf); console.log('OK', saidaPath, buf.length, 'bytes'); })
  .catch(function(e){ console.error('FAIL', e); process.exit(1); });
