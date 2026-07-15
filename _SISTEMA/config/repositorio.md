# Repositório — regras da casa (condição 1b do advogado, 15/07/2026)

- Este repositório vive **dentro do OneDrive** (`OneDrive\Documentos\NASCIMENTO`).
  O sync de `.git` pelo OneDrive é um risco real: em 09/07/2026 um `index.lock`
  órfão ficou 6 dias travando commits (removido em 15/07/2026).
- **REGRA DA CASA: toda sessão termina com `git commit` + `git push`.**
  O remoto privado é a rede de segurança real; o OneDrive é só transporte.
- Remoto: GitHub privado `herbethmatheusadv-star/NASCIMENTO`
  (2FA na conta é responsabilidade do advogado).
- `AUTOS/` fica **fora do git** (PDFs dos autos). Backup próprio: zip cifrado
  semanal em `G:\Meu Drive\BACKUP_SOJ\AUTOS` (Google Drive — provedor diferente
  do OneDrive, de propósito). **A senha do zip fica com o advogado; nunca em
  texto neste repositório.** Script de backup: Etapa 5.
- `RADAR/relatorios/` e `RADAR/.cache_datajud.json` também ficam fora do git
  (gerados diariamente; contêm dados de cliente em HTML).
- Histórico: git órfão em `C:\Users\nasci` (0 commits, 0 stashes) removido em
  15/07/2026 com autorização expressa.
